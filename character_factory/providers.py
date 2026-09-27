from __future__ import annotations

import json
import os
import time
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from .telemetry import sha256_file, utc_now


class ProviderError(RuntimeError):
    pass


class FixtureProvider:
    name = "fixture"

    def __init__(self, root: Path, fixtures: dict[str, Any]) -> None:
        self.root = root
        self.fixtures = fixtures

    def prepare(self, character_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        if character_id not in self.fixtures:
            raise ProviderError(f"Unknown fixture: {character_id}")
        fixture = self.fixtures[character_id]
        events = [{"event": "fixture_prepare", "utc": utc_now(), "character_id": character_id}]
        for asset in fixture["source_assets"]:
            path = self.root / asset["path"]
            if not path.exists():
                raise ProviderError(f"Missing fixture asset: {path}")
            asset["sha256"] = sha256_file(path)
            asset["bytes"] = path.stat().st_size
        return fixture, events


class HttpJobProvider:
    """Provider-neutral submit/poll/download adapter.

    Endpoint and token are intentionally external configuration. Hunyuan API
    field names remain in provider_contract.json rather than in Factory logic.
    """

    name = "http"

    def __init__(self, endpoint: str, token_env: str = "HUNYUAN_API_TOKEN", contract: dict | None = None) -> None:
        if not endpoint:
            raise ProviderError("HTTP provider requires an endpoint")
        self.endpoint = endpoint.rstrip("/")
        self.token = os.environ.get(token_env)
        self.contract = contract or {}
        self.events: list[dict[str, Any]] = []

    def _request(self, method: str, url: str, payload: dict | None = None) -> dict:
        body = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(url, data=body, method=method, headers={"Content-Type": "application/json"})
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode())

    def submit(self, payload: dict) -> str:
        started = time.perf_counter()
        result = self._request("POST", self.endpoint, payload)
        job_id = result.get(self.contract.get("submit", {}).get("job_id_path", "job_id"))
        if not job_id:
            raise ProviderError(f"Provider response did not contain a job id: {result}")
        self.events.append({"event": "submit", "job_id": job_id, "elapsed_seconds": round(time.perf_counter() - started, 3)})
        return str(job_id)

    def poll(self, job_id: str, interval_seconds: float = 5, max_seconds: float = 1800) -> dict:
        started = time.perf_counter()
        while time.perf_counter() - started <= max_seconds:
            result = self._request("GET", f"{self.endpoint}/{job_id}")
            status = str(result.get(self.contract.get("poll", {}).get("status_path", "status"), "")).lower()
            if status in set(self.contract.get("poll", {}).get("terminal_success", ["completed"])):
                self.events.append({"event": "poll_complete", "job_id": job_id, "status": status, "elapsed_seconds": round(time.perf_counter() - started, 3)})
                return result
            if status in set(self.contract.get("poll", {}).get("terminal_failure", ["failed"])):
                raise ProviderError(f"Provider job failed: {result}")
            time.sleep(interval_seconds)
        raise ProviderError(f"Provider job timed out after {max_seconds}s: {job_id}")

    def download(self, url: str, output: Path) -> dict[str, Any]:
        output.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(url)
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")
        with urllib.request.urlopen(request, timeout=120) as response, output.open("wb") as handle:
            handle.write(response.read())
        event = {"event": "download", "url": url, "path": str(output), "bytes": output.stat().st_size, "sha256": sha256_file(output)}
        self.events.append(event)
        return event
