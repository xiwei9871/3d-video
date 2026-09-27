# SECOND CHARACTER REPLICATION BENCHMARK — Rabbit

Started UTC: 2026-09-26 14:14:59 UTC

| Gate | Automation time | Human time | Manual interventions | Failures | Generic tool changes | Config/mapping-only changes | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| G0 Asset Audit | UNKNOWN / NOT INSTRUMENTED | Included in ~2h operator estimate | 1 input correction | 1 rejected FBX | 0 | 0 | PASS |
| G1 Component Map | 2.1s measured Blender run | Included in ~2h operator estimate | 0 | 0 | 0 | 1 rabbit mapping file | PASS |
| G2 Puppet Build | 2.559s measured rebuild/assign | Included in ~2h operator estimate | 0 after generic fix | 1 initial missing-controller blocker | 2 generic files | 0 | PASS |
| G3 Core Actions | 0.606s measured action build | Included in ~2h operator estimate | 0 | 0 | 0 | 1 rabbit config | PASS |
| G4 Visual QA | UNKNOWN / NOT INSTRUMENTED | Included in ~2h operator estimate | 0 | 0 | 1 generic QA extension | 1 rabbit config | PASS |
| G5 Export / Roundtrip | 6.167s measured clean rebuild/export/roundtrip | Included in ~2h operator estimate | 0 | 0 | 5 generic config/runtime extensions | 1 rabbit config | PASS |
| G6 Three.js Runtime | browser load/parse metrics recorded; automation wall time UNKNOWN | Included in ~2h operator estimate | 0 | 0 | 0 | 1 rabbit semantic mapping | PASS |

Generic code changes so far: 9 files, all config-driven/general capabilities (bone_layout, semantic controller aliases, config-aware validation/roundtrip/QA helpers, character-derived output names). No rabbit-only branch or hardcoded rabbit geometry was added to Generic Tool.

Input correction failure: 1. The first supplementary FBX was audited and rejected because it was a snake auxiliary mesh, not a rabbit 50K source. The corrected textured rabbit GLB was accepted.
Character-specific files: rabbit `character_config.json`, `component_mapping.json`, audit and evidence files.

Snake regression after Generic changes: PASS; recorded baseline 8.587s / 0 manual interventions. Fresh isolated confirmation: 6.095s / 0 manual interventions.

End-to-end elapsed production time ≈ 2 hours.
Measurement quality = operator-reported approximation, not instrumented timing.
