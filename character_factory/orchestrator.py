from __future__ import annotations

import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from .gates import HumanReviewRequired, require_gate
from .models import FactoryRequest, FactoryRun
from .pipeline_adapter import run_component_puppet
from .providers import FixtureProvider, ProviderError
from .telemetry import read_json, sha256_file, timed_stage, utc_now, write_json


def _load_fixtures(root: Path) -> dict[str, Any]:
    return read_json(root / "character_factory" / "fixtures.json")


def _run_path(root: Path, character_id: str, run_id: str) -> Path:
    path = root / "characters" / character_id / "factory_runs" / run_id
    for sub in ("inputs", "rejected", "stages", "outputs"):
        (path / sub).mkdir(parents=True, exist_ok=True)
    return path


def _archive_inputs(root: Path, fixture: dict[str, Any], run_dir: Path, run: dict[str, Any]) -> None:
    if run.get("source_assets"):
        return
    for asset in fixture["source_assets"]:
        source = root / asset["path"]
        destination = run_dir / "inputs" / source.name
        shutil.copy2(source, destination)
        run["source_assets"].append({"role": asset["role"], "source": str(source), "archived": str(destination), "sha256": sha256_file(destination), "bytes": destination.stat().st_size, "accepted": True})
    for asset in fixture.get("rejected_assets", []):
        source = root / asset["path"]
        if not source.exists():
            continue
        destination = run_dir / "rejected" / source.name
        shutil.copy2(source, destination)
        run["source_assets"].append({"role": asset["role"], "source": str(source), "archived": str(destination), "sha256": sha256_file(destination), "bytes": destination.stat().st_size, "accepted": False, "reason": asset.get("reason", "rejected by fixture policy")})


def _record_stage(run: dict[str, Any], record: Any) -> None:
    run.setdefault("stages", []).append(record.to_dict())


def _write_run(run_dir: Path, run: dict[str, Any]) -> None:
    write_json(run_dir / "factory_run.json", run)


def _stage_done(run: dict[str, Any], name: str) -> bool:
    return any(item.get("name") == name and item.get("status") == "PASS" for item in run.get("stages", []))


def run_factory(root: Path, request: FactoryRequest) -> dict[str, Any]:
    fixtures = _load_fixtures(root)
    character_id = request.fixture or request.character_id
    run_id = request.run_id or f"{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{uuid.uuid4().hex[:8]}"
    run_dir = _run_path(root, character_id, run_id)
    started = time.perf_counter()
    existing_path = run_dir / "factory_run.json"
    prior_elapsed = 0.0
    if request.run_id and existing_path.exists():
        run = read_json(existing_path)
        prior_elapsed = float(run.get("elapsed_seconds", 0.0) or 0.0)
        run["status"] = "RUNNING"
        run["failure"] = None
    else:
        run = FactoryRun(schema_version="zodiac-character-factory-v1", run_id=run_id, character_id=character_id, mode=request.mode, provider=request.provider, status="RUNNING", started_utc=utc_now()).to_dict()
    run["outputs"]["run_dir"] = str(run_dir)
    approvals = {item.upper() for item in request.approve_gates}
    try:
        provider = FixtureProvider(root, fixtures)
        fixture, events = provider.prepare(character_id)
        run["provider_events"].extend(events)

        for provider_stage, description in (
            ("reference_generation", "fixture reference/style inputs"),
            ("visual_asset_generation", "fixture textured 50K source"),
            ("component_split", "fixture semantic component reference"),
        ):
            if not _stage_done(run, provider_stage):
                with timed_stage(provider_stage) as stage:
                    stage.details = {"source": "fixture_reuse", "description": description, "status": "PASS"}
                _record_stage(run, stage)
        run["outputs"]["fixture_config"] = str(root / fixture["config"])

        if not _stage_done(run, "archive_inputs"):
            with timed_stage("archive_inputs") as stage:
                _archive_inputs(root, fixture, run_dir, run)
            _record_stage(run, stage)
        _write_run(run_dir, run)

        if not _stage_done(run, "g0_g1_evidence"):
            with timed_stage("g0_g1_evidence") as stage:
                existing_report = fixture.get("existing", {}).get("pipeline_report")
                report = read_json(root / existing_report) if existing_report else {}
                stage.details = {"source": "fixture_reuse", "status": report.get("status")}
                run["outputs"]["g0_g1_report"] = str(root / existing_report) if existing_report else ""
            _record_stage(run, stage)
        _write_run(run_dir, run)
        require_gate(run, "H1", approvals, run_dir, "Review four-view references and the textured/component source models for visual identity and gross errors.")
        _write_run(run_dir, run)

        if not _stage_done(run, "g1_5_semantic_review"):
            with timed_stage("g1_5_semantic_review") as stage:
                semantic_path = root / fixture["existing"]["semantic_audit"]
                semantic = read_json(semantic_path)
                required = {"HEAD_ASSEMBLY", "CONTROLLER_ISOLATION", "ACTION_ELIGIBILITY"}
                if semantic.get("status") != "PASS" or any(semantic.get("gates", {}).get(name) != "PASS" for name in required):
                    raise ProviderError(f"Fixture semantic evidence is not PASS: {semantic.get('gates')}")
                stage.details = {"source": "fixture_reuse", "gates": semantic.get("gates")}
                run["outputs"]["semantic_audit"] = str(semantic_path)
            _record_stage(run, stage)
        _write_run(run_dir, run)
        require_gate(run, "H2", approvals, run_dir, "Review semantic ownership, controller isolation, and required-component action eligibility before any action build.")
        _write_run(run_dir, run)

        if not _stage_done(run, "g2_g6_component_puppet"):
            with timed_stage("g2_g6_component_puppet") as stage:
                report = run_component_puppet(root, fixture, run_dir, request.execute_puppet)
                stage.details = {"status": report.get("status"), "semantic_gate": report.get("semantic_gate_gates")}
                run["outputs"]["component_puppet_report"] = str(report.get("outputs", {}).get("validation", report.get("outputs", {}).get("report", "")))
                run["outputs"]["runtime_asset"] = str(report.get("outputs", {}).get("glb", ""))
            _record_stage(run, stage)
        _write_run(run_dir, run)
        require_gate(run, "H3", approvals, run_dir, "Review final action QA, GLB/runtime evidence, and Three.js behavior before promoting this run.")
        run["status"] = "COMPLETE"
        run["current_gate"] = "H3"
        run["notes"].append("Factory V1 completed only with explicit H1/H2/H3 approvals.")
    except HumanReviewRequired:
        pass
    except Exception as exc:
        run["status"] = "FAILED"
        run["failure"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        run["ended_utc"] = utc_now()
        current_elapsed = time.perf_counter() - started
        stage_elapsed = sum(float(item.get("elapsed_seconds", 0.0) or 0.0) for item in run.get("stages", []))
        run["elapsed_seconds"] = round(max(prior_elapsed + current_elapsed, stage_elapsed), 3)
        _write_run(run_dir, run)
    return run
