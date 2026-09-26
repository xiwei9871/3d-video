# 05_animations

This directory contains the Component Puppet Character V1 motion evidence.

## Actions

The clean rebuild creates these reusable actions:

- `snake_idle` — 90 frames at 30fps
- `snake_head_shake` — 30 frames
- `snake_head_tilt` — 30 frames
- `snake_body_sway` — 30 frames
- `snake_tail_wag` — 30 frames
- `snake_tongue_flick` — 24 frames
- `snake_bounce` — 30 frames

`snake_blink` remains a fallback entry in the character config; no eyelid geometry was supplied by the segmentation reference.

## QA outputs

- Static action sheet: `component_puppet_v1/snake_character_v1_preview_contact_sheet.png`
- 60-frame preview: `component_puppet_v1/snake_character_v1_preview.mp4`
- Frame sequence: `component_puppet_v1/preview_frames/`
- Machine manifest: `component_puppet_v1/qa_manifest.json`

The preview is an action-layer validation artifact, not final production animation.

## G6 handoff

The runtime version of this action library is validated in the independent Three.js demo at `../07_web_demo/`. The browser maps the seven exported clips to semantic controls and records the renderer metrics without changing the animation source.
