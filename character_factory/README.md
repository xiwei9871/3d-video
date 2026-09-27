# Zodiac Character Factory V1

Factory V1 owns orchestration. The Component Puppet Skill owns character
production. Factory never reimplements G0–G6 or G1.5; it calls the existing
pipeline through `pipeline_adapter.py`, records its reports, and stops at
explicit human gates.

Telemetry stages are `reference_generation`, `visual_asset_generation`,
`component_split`, `archive_inputs`, `g0_g1_evidence`,
`g1_5_semantic_review`, and `g2_g6_component_puppet`.

## Human gates

- **H1** — four-view and source-model visual review;
- **H2** — semantic ownership, controller isolation, and action eligibility;
- **H3** — final action QA, runtime GLB, and Three.js review.

Start a fixture run:

```bash
python3 -m character_factory run --fixture zodiac_dragon
```

The command writes a resumable `factory_run.json` and stops at H1. Resume with
explicit approvals:

```bash
python3 -m character_factory run --fixture zodiac_dragon --run-id <id> --approve H1 H2 H3
```

The initial provider is a fixture provider for Snake, Rabbit, and Dragon. The
HTTP provider contract is isolated in `providers.py` and
`provider_contract.json`; it is not enabled for unattended production.

Failed or rejected inputs remain under the run's `rejected/` or `stages/`
directories and are never promoted automatically.
