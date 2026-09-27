# Dragon G1.5 — Semantic Ownership / Action Eligibility Gate

## Status

```text
HEAD_ASSEMBLY          = PASS
CONTROLLER_ISOLATION   = PASS
ACTION_ELIGIBILITY     = PASS
WINGFLAP               = INELIGIBLE
DRAGON G1.5 GATE       = PASS / HUMAN REVIEW
```

## Repaired ownership

The supplied component split was audited against the textured 50K source. The
previous map assigned the large head shell to `ARM_L` and one eye shell to
`HEAD_BASE`. The repaired map records:

```text
part_5   -> HEAD_BASE
part_13  -> MANE
part_1/7 -> HORN_R
part_14  -> HORN_L
part_2/11 -> EYE_L / EYE_R
part_3/15 -> WHISKER_R / WHISKER_L
part_16  -> TONGUE
part_9   -> BODY
part_6/8 -> ARM_L / ARM_R
part_12/4 -> LEG_L / LEG_R
part_0/10 -> TAIL / TAIL_TIP
```

All head members inherit `HEAD_CTRL`; optional child controls remain available
for secondary motion. Eight isolated controller poses were checked with no
unexpected semantic movement.

## Eligibility

`WingFlap` requires `WING_L` and `WING_R`. Neither exists in the supplied
component map, so the action is recorded as `INELIGIBLE`; no clip or web button
was generated. `DragonProud` and `Roar` use verified head components instead.
`Blink` remains a documented fallback because eyelid geometry is absent.

## Evidence

- `04_rig/review/g1_5/semantic_ownership_audit.json`
- `04_rig/review/g1_5/semantic_ownership_contact_sheet.png`
- `04_rig/review/g1_5/head_assembly_audit.png`
- `04_rig/review/g1_5/semantic_controller_isolation_contact_sheet.png`
- `04_rig/review/g1_5/dragon_actions_contact_sheet_g1_5.png`
- `05_animations/g1_5/dragon_character_g1_5_preview.mp4`
- `06_export/g1_5/runtime_gate.json`
- `06_export/v1_2_final/runtime_gate.json`
- `07_web_demo/review/g1_5/THREEJS_RUNTIME_GATE.md`
- `benchmark/g1_5_generic_tool_changes.md`

Stop point: Human Review. No model regeneration, UV, texture, PBR, Three.js
optimization, or Git commit was performed for this gate.
