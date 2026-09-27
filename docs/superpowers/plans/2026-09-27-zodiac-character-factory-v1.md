# Zodiac Character Factory V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a resumable orchestration layer that turns reference inputs and Hunyuan provider jobs into a versioned character workspace, invokes the existing Component Puppet Pipeline V1.2 as a black box, pauses at H1/H2/H3, and writes one `factory_run.json` telemetry record.

**Architecture:** `character_factory/` owns job state, provider adapters, archiving, human gates, timing, hashes, and failure quarantine. The existing `tools/component_puppet/rebuild_pipeline.py` remains the only implementation of the G0–G6 character build path; Factory calls it through a subprocess boundary and reads its reports. Fixture manifests for Snake, Rabbit, and Dragon exercise orchestration without generating a fourth character.

**Tech Stack:** Python 3.14 standard library, JSON manifests, subprocess, urllib-based provider contract, existing Blender/Python Component Puppet tools.

---

### Task 1: Define Factory contracts and fixture registry

**Files:**
- Create: `character_factory/__init__.py`
- Create: `character_factory/models.py`
- Create: `character_factory/fixtures.json`
- Create: `character_factory/README.md`

- [x] Define `FactoryRequest`, `StageRecord`, `HumanGate`, `SourceAsset`, and `FactoryRun` dataclasses. Every record includes UTC timestamps, elapsed seconds, status, intervention count, source hashes, and output paths.
- [x] Define fixture entries for `zodiac_snake`, `zodiac_rabbit`, and `zodiac_dragon` with accepted source GLB, component reference, config, mapping, and existing runtime evidence paths. Do not add a fourth-character fixture.
- [x] Document the stage contract, H1/H2/H3 semantics, failure quarantine, and the black-box boundary around `tools/component_puppet/rebuild_pipeline.py`.

### Task 2: Implement provider adapters

**Files:**
- Create: `character_factory/providers.py`
- Create: `character_factory/provider_contract.json`

- [x] Implement `FixtureProvider` that returns existing fixture paths without copying or mutating frozen assets.
- [x] Implement `HttpJobProvider` with `submit`, `poll`, and `download` methods using `urllib.request`, configurable endpoint/token, bounded polling, and explicit failure records. The adapter accepts provider-specific JSON field mappings from `provider_contract.json` rather than embedding Hunyuan API assumptions.
- [x] Record every provider request, response status, elapsed time, downloaded path, and SHA-256 in the run telemetry.

### Task 3: Implement workspace, archive, and human-gate state machine

**Files:**
- Create: `character_factory/orchestrator.py`
- Create: `character_factory/telemetry.py`
- Create: `character_factory/gates.py`

- [x] Create run directories under `characters/<character_id>/factory_runs/<run_id>/` with `inputs/`, `rejected/`, `stages/`, and `outputs/`.
- [x] Archive every accepted/rejected input with SHA-256 before any build step. Rejected input stays under `rejected/` and is never promoted.
- [x] Implement resumable stage transitions: `H1_REFERENCE_REVIEW`, `H2_SEMANTIC_REVIEW`, `H3_ACTION_REVIEW`, `COMPLETE`, and `FAILED`. A run pauses with a machine-readable approval request instead of guessing human approval.
- [x] Increment `manual_intervention_count` only for explicit `approve_gate()` calls or operator corrections recorded through the CLI.
- [x] Never mark a failed or partial run as a production output. Preserve its logs and artifacts in the run directory.

### Task 4: Invoke Component Puppet Pipeline V1.2 as a black box

**Files:**
- Modify: `character_factory/orchestrator.py`
- Create: `character_factory/pipeline_adapter.py`

- [x] Build the exact `rebuild_pipeline.py` command from the fixture/config paths and isolated output directories.
- [x] Capture stdout/stderr, return code, elapsed time, report paths, G1.5 gate values, validation status, roundtrip status, and output hashes.
- [x] Refuse to continue if the Component Puppet report is not `PASS` or if any G1.5 sub-gate is not `PASS`; do not duplicate G0–G6 logic in Factory.

### Task 5: Add CLI and dry/fixture execution modes

**Files:**
- Create: `character_factory/cli.py`
- Create: `character_factory/__main__.py`
- Modify: `character_factory/README.md`

- [x] Support `python -m character_factory run --fixture zodiac_dragon --stop-at-human-review`.
- [x] Support `--approve H1`, `--approve H2`, and `--approve H3` as explicit resumptions; do not enable unattended approvals by default.
- [x] Support `--provider fixture|http`, `--run-id`, `--poll-interval`, `--max-poll-seconds`, and `--execute-puppet`.
- [x] Always write one final or paused `factory_run.json` containing timings, gates, interventions, source hashes, provider events, rejected inputs, and output paths.

### Task 6: Verify with the three frozen fixtures

**Files:**
- Create: `reports/zodiac_character_factory_v1_fixture_runs.md`
- Create: `reports/zodiac_character_factory_v1_fixture_runs.json`

- [x] Run fixture dry/paused flows for Snake, Rabbit, and Dragon; verify each stops at the requested Human Gate and can resume from the saved run state.
- [x] Run the Factory adapter against the existing V1.2 regression reports without rebuilding a fourth character.
- [x] Verify source hashes, no failed-asset promotion, `factory_run.json` schema, and elapsed telemetry.
- [x] Stop at Human Review. Do not enable unattended production, start a fourth zodiac character, commit, or push until the Factory output is reviewed.
