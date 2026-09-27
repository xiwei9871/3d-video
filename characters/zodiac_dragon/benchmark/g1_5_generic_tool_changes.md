# Dragon G1.5 — Generic Tool Change Record

The generic pipeline was changed only where the G1.5 requirement exposed a
reusable blocker. No Dragon geometry branch, Dragon coordinate, or Dragon
object name was added to generic logic.

## Changes and reasons

- `tools/component_puppet/semantic_ownership_audit.py` — new reusable audit
  for ownership rows, head assembly, isolated controller poses, component
  presence, and `required_components` eligibility. This is the implementation
  of the new mandatory G1.5 gate.
- `tools/component_puppet/build_actions.py` — accepts the component mapping
  and skips an action whose declared required components are absent or whose
  config marks it ineligible. This prevents a species template from creating
  unsupported anatomy clips such as Dragon `WingFlap`.
- `tools/component_puppet/rebuild_pipeline.py` — passes mapping and writes the
  eligibility report, runs the full semantic audit before `build_actions.py`,
  and fails closed so a clean rebuild cannot bypass G1.5 action filtering.
- `tools/component_puppet/render_consolidation_review.py` — de-duplicates
  config action aliases before rendering comparison evidence. This keeps
  config-driven action aliases from producing duplicate review rows.

All Dragon-specific ownership, controller aliases, required components, and
action choices remain in:

```text
characters/zodiac_dragon/character_config.json
characters/zodiac_dragon/component_mapping.json
characters/zodiac_dragon/benchmark/build_dragon_mapping.py
```

## Negative checks

```text
rabbit-specific geometry branch = none
hard-coded Dragon coordinates in generic tools = none
hard-coded Dragon object names in generic logic = none
G3 action generation before a passing G1.5 gate = blocked
missing required component without explicit ineligible declaration = G1.5 FAIL
```
