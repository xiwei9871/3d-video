from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class StageRecord:
    name: str
    status: str
    started_utc: str
    ended_utc: str | None = None
    elapsed_seconds: float = 0.0
    manual_interventions: int = 0
    details: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HumanGateRecord:
    name: str
    status: str = "WAITING"
    requested_utc: str | None = None
    approved_utc: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FactoryRun:
    schema_version: str
    run_id: str
    character_id: str
    mode: str
    provider: str
    status: str
    started_utc: str
    ended_utc: str | None = None
    elapsed_seconds: float = 0.0
    manual_intervention_count: int = 0
    current_gate: str | None = None
    stages: list[dict[str, Any]] = field(default_factory=list)
    human_gates: list[dict[str, Any]] = field(default_factory=list)
    source_assets: list[dict[str, Any]] = field(default_factory=list)
    provider_events: list[dict[str, Any]] = field(default_factory=list)
    outputs: dict[str, str] = field(default_factory=dict)
    failure: dict[str, Any] | None = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FactoryRequest:
    character_id: str
    mode: str = "fixture"
    provider: str = "fixture"
    fixture: str | None = None
    run_id: str | None = None
    execute_puppet: bool = False
    approve_gates: tuple[str, ...] = ()
    stop_at_human_review: bool = True
    poll_interval_seconds: float = 5.0
    max_poll_seconds: float = 1800.0
