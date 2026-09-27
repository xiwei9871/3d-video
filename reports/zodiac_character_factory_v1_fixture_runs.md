# Zodiac Character Factory V1 Fixture Runs

These are fixture-only orchestration checks using frozen Snake, Rabbit, and
Dragon assets. No fourth character was generated.

| Fixture | Status | Gate | Elapsed | Manual interventions |
|---|---|---|---:|---:|
| Snake | WAITING_H1 | H1 | 0.051s | 0 |
| Rabbit | WAITING_H1 | H1 | 0.051s | 0 |
| Dragon | COMPLETE | H3 | 19.563s | 3 |

Dragon used `--execute-puppet` after explicit H1/H2 approvals, then resumed with
an explicit H3 approval. Snake and Rabbit stopped at H1. Each run wrote a resumable
`factory_run.json` with archived source hashes, stage timings, gate status, and
output paths.

This verifies the orchestration boundary. It does not enable unattended
production or approve visual, semantic, or action review automatically.
