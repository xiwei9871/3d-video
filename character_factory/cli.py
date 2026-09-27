from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import FactoryRequest
from .orchestrator import run_factory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m character_factory")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run or resume a Factory V1 orchestration")
    run.add_argument("--fixture", required=True, choices=["zodiac_snake", "zodiac_rabbit", "zodiac_dragon"])
    run.add_argument("--provider", choices=["fixture"], default="fixture")
    run.add_argument("--run-id")
    run.add_argument("--approve", nargs="*", choices=["H1", "H2", "H3"], default=[])
    run.add_argument("--execute-puppet", action="store_true")
    run.add_argument("--stop-at-human-review", action="store_true", default=True)
    run.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        result = run_factory(args.root.resolve(), FactoryRequest(character_id=args.fixture, fixture=args.fixture, provider=args.provider, run_id=args.run_id, execute_puppet=args.execute_puppet, approve_gates=tuple(args.approve), stop_at_human_review=args.stop_at_human_review))
        print(json.dumps({"run_id": result["run_id"], "status": result["status"], "current_gate": result.get("current_gate"), "elapsed_seconds": result.get("elapsed_seconds"), "manual_intervention_count": result.get("manual_intervention_count")}, indent=2, ensure_ascii=False))
        return 0 if result["status"] in {"COMPLETE", "WAITING_H1", "WAITING_H2", "WAITING_H3"} else 1
    return 2
