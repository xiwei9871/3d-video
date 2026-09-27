from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from .telemetry import read_json


class PipelineError(RuntimeError):
    pass


def run_component_puppet(root: Path, fixture: dict[str, Any], run_dir: Path, execute: bool, blender: str = "blender") -> dict[str, Any]:
    report_path = run_dir / "stages" / "component_puppet_rebuild_report.json"
    if not execute:
        existing = fixture.get("existing", {}).get("pipeline_report")
        if not existing:
            raise PipelineError("Fixture has no existing pipeline report for reuse")
        report = read_json(root / existing)
        report["factory_execution"] = "fixture_reuse"
        return report
    config = root / fixture["config"]
    mapping = root / fixture["mapping"]
    source = root / fixture["source_assets"][0]["path"]
    rebuild_root = run_dir / "stages" / "rebuild"
    export_root = run_dir / "outputs" / "export"
    command = [sys.executable, str(root / "tools/component_puppet/rebuild_pipeline.py"), "--project-root", str(root), "--blender", blender, "--config", str(config), "--mapping", str(mapping), "--source", str(source), "--rebuild-root", str(rebuild_root), "--export-root", str(export_root), "--report", str(report_path)]
    started = time.perf_counter()
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    elapsed = round(time.perf_counter() - started, 3)
    (run_dir / "stages" / "component_puppet.stdout.txt").write_text(result.stdout)
    (run_dir / "stages" / "component_puppet.stderr.txt").write_text(result.stderr)
    if result.returncode != 0:
        raise PipelineError(f"Component Puppet pipeline failed after {elapsed}s: {result.stderr[-2000:]}")
    report = read_json(report_path)
    report["factory_execution"] = "subprocess"
    report["factory_elapsed_seconds"] = elapsed
    if report.get("status") != "PASS" or report.get("semantic_gate_status") != "PASS":
        raise PipelineError(f"Component Puppet report did not pass: {report}")
    return report
