from __future__ import annotations

import hashlib
import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .models import StageRecord


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


@contextmanager
def timed_stage(name: str, details: dict | None = None) -> Iterator[StageRecord]:
    started = time.perf_counter()
    record = StageRecord(name=name, status="RUNNING", started_utc=utc_now(), details=details or {})
    try:
        yield record
    except Exception as exc:
        record.status = "FAILED"
        record.error = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        record.ended_utc = utc_now()
        record.elapsed_seconds = round(time.perf_counter() - started, 3)
        if record.status == "RUNNING":
            record.status = "PASS"
