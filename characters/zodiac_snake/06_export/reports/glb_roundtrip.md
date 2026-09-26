# Zodiac Snake Character V1 GLB Roundtrip

## Artifact

- Exported GLB: `../zodiac_snake_character_v1.glb`
- Authored source: `../../04_rig/rebuild/clean_actions.blend`
- Machine result: `../roundtrip_validation.json`
- Fresh-import renders: `../review/`

## Checks

| Check | Result |
| --- | --- |
| One armature imported | PASS |
| Ten controller bone names and parent map | PASS |
| 460 component mesh nodes | PASS |
| 460 bone-parented component objects | PASS |
| Material.001 present | PASS |
| Three source PBR images present | PASS |
| Seven actions present | PASS |
| Action time ranges preserved in seconds | PASS |
| Finite transforms | PASS |

The importer can create an armature display helper mesh. The validator reports it separately and excludes it from `component_mesh_objects`. glTF stores animation time in seconds; the fresh scene's default 24fps therefore shows converted frame numbers (`snake_head_tilt` 0.8–24 instead of authored 1–30), while the seconds are preserved.

## Visual evidence

- `../review/glb_roundtrip_contact_sheet.png`
- `../review/snake_head_tilt_roundtrip.png`
- `../review/snake_body_sway_roundtrip.png`
- `../review/snake_tail_wag_roundtrip.png`

This is a Blender roundtrip gate. It does not certify a Three.js runtime, which remains outside the current task.

**Roundtrip gate:** `PASS / HUMAN REVIEW FOR RUNTIME HANDOFF`
