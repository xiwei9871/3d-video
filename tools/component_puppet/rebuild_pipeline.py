"""One-command clean rebuild for a Component Puppet character."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=Path(__file__).resolve().parents[2], type=Path)
    parser.add_argument("--blender", default=os.environ.get("BLENDER_BIN", "blender"))
    parser.add_argument("--config", default="characters/zodiac_snake/character_config.json")
    parser.add_argument("--mapping", default="characters/zodiac_snake/component_mapping.json")
    parser.add_argument("--source", default="experiments/snake-b-route/raw/snake_unsplit_50k.glb")
    parser.add_argument("--rebuild-root", default="characters/zodiac_snake/04_rig/rebuild")
    parser.add_argument("--export-root", default="characters/zodiac_snake/06_export")
    parser.add_argument("--report", default="reports/component_puppet_rebuild_run.json")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def run_blender(blender, script, args, project_root):
    command = [
        blender,
        "--background",
        "--factory-startup",
        "--python",
        str(project_root / script),
        "--",
        *[str(item) for pair in args for item in pair],
    ]
    start = time.perf_counter()
    result = subprocess.run(command, cwd=project_root, text=True, capture_output=True)
    elapsed = time.perf_counter() - start
    if result.returncode:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return {
        "script": script,
        "elapsed_seconds": round(elapsed, 3),
        "returncode": result.returncode,
        "last_output_lines": (result.stdout + result.stderr).splitlines()[-8:],
    }


def main():
    args = parse_args()
    root = args.project_root.resolve()
    rebuild = root / args.rebuild_root
    export = root / args.export_root
    rebuild.mkdir(parents=True, exist_ok=True)
    export.mkdir(parents=True, exist_ok=True)
    config = root / args.config
    mapping = root / args.mapping
    source = root / args.source
    paths = {
        "clean_rig": rebuild / "clean_rig.blend",
        "clean_assigned": rebuild / "clean_assigned.blend",
        "clean_actions": rebuild / "clean_actions.blend",
        "validation": rebuild / "character_validation.json",
        "glb": export / "zodiac_snake_character_v1.glb",
        "roundtrip": export / "roundtrip_validation.json",
    }
    steps = []
    started = time.perf_counter()
    steps.append(
        run_blender(
            args.blender,
            "tools/component_puppet/build_rig.py",
            [("--config", config), ("--source", source), ("--output", paths["clean_rig"])],
            root,
        )
    )
    steps.append(
        run_blender(
            args.blender,
            "tools/component_puppet/assign_components.py",
            [("--blend", paths["clean_rig"]), ("--mapping", mapping), ("--config", config), ("--output", paths["clean_assigned"])],
            root,
        )
    )
    steps.append(
        run_blender(
            args.blender,
            "tools/component_puppet/build_actions.py",
            [("--blend", paths["clean_assigned"]), ("--config", config), ("--output", paths["clean_actions"])],
            root,
        )
    )
    steps.append(
        run_blender(
            args.blender,
            "tools/component_puppet/validate_character.py",
            [("--blend", paths["clean_actions"]), ("--config", config), ("--output", paths["validation"])],
            root,
        )
    )
    steps.append(
        run_blender(
            args.blender,
            "tools/component_puppet/export_character.py",
            [("--blend", paths["clean_actions"]), ("--output", paths["glb"])],
            root,
        )
    )
    steps.append(
        run_blender(
            args.blender,
            "characters/zodiac_snake/06_export/roundtrip_check.py",
            [("--input", paths["glb"]), ("--source-blend", paths["clean_actions"]), ("--output", paths["roundtrip"])],
            root,
        )
    )
    elapsed = time.perf_counter() - started
    validation = json.loads(paths["validation"].read_text())
    roundtrip = json.loads(paths["roundtrip"].read_text())
    report = {
        "pipeline": "component_puppet_character_v1",
        "project_root": str(root),
        "blender": args.blender,
        "inputs": {"config": str(config), "mapping": str(mapping), "source": str(source)},
        "outputs": {key: str(path) for key, path in paths.items()},
        "steps": steps,
        "elapsed_seconds": round(elapsed, 3),
        "manual_intervention_count": 0,
        "validation_status": validation.get("status"),
        "roundtrip_status": roundtrip.get("status"),
        "status": "PASS" if validation.get("status") == "PASS" and roundtrip.get("status") == "PASS" else "PARTIAL",
        "human_review_items": [
            "TailWag remains a rigid component boundary review item.",
            "Blink remains a documented fallback because the supplied segmentation has no eyelid component.",
            "Fresh GLB import is validated in Blender; Three.js runtime is intentionally out of scope for this gate.",
        ],
    }
    report_path = root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
