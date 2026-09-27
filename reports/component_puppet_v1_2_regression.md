# Component Puppet Pipeline V1.2 Regression

Fresh regressions were run after G1.5 became a hard pre-G3 gate. Each run used
an isolated output directory and left the frozen V1 runtime assets untouched.

| Character | G1.5 | Validation | Roundtrip | Elapsed | Manual interventions |
|---|---|---|---|---:|---:|
| Snake | PASS | PASS | PASS | 12.280 s | 0 |
| Rabbit | PASS | PASS | PASS | 15.677 s | 0 |

The orchestrator stops before `build_actions.py` when semantic ownership,
controller isolation, or action eligibility is not PASS.
