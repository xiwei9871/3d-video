from __future__ import annotations

from pathlib import Path

from .models import HumanGateRecord
from .telemetry import utc_now, write_json


GATE_ORDER = ("H1", "H2", "H3")


class HumanReviewRequired(RuntimeError):
    def __init__(self, gate: str, request_path: Path) -> None:
        super().__init__(f"Human review required at {gate}: {request_path}")
        self.gate = gate
        self.request_path = request_path


def require_gate(run: dict, gate: str, approvals: set[str], run_dir: Path, prompt: str) -> None:
    gate_records = run.setdefault("human_gates", [])
    record = next((item for item in gate_records if item.get("name") == gate), None)
    if record is None:
        record = HumanGateRecord(name=gate).to_dict()
        gate_records.append(record)
    if record.get("status") == "APPROVED":
        run["current_gate"] = gate
        return
    if gate in approvals:
        record["status"] = "APPROVED"
        record["approved_utc"] = utc_now()
        run["manual_intervention_count"] = int(run.get("manual_intervention_count", 0)) + 1
        run["current_gate"] = gate
        return
    record["status"] = "WAITING"
    record["requested_utc"] = record.get("requested_utc") or utc_now()
    record["notes"] = prompt
    run["current_gate"] = gate
    run["status"] = f"WAITING_{gate}"
    request_path = run_dir / f"HUMAN_GATE_{gate}.md"
    request_path.write_text(f"# Human Gate {gate}\n\n{prompt}\n\nApprove by resuming with `--approve {gate}`.\n")
    run.setdefault("outputs", {})[f"human_gate_{gate}"] = str(request_path)
    raise HumanReviewRequired(gate, request_path)
