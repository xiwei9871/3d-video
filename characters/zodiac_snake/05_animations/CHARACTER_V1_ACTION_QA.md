# Zodiac Snake Character V1 Action QA

**Gate:** `COMPONENT PUPPET CHARACTER V1 = PARTIAL / HUMAN REVIEW`

## Contract

The deliverable is a reusable action-layer character built from the 50K original-material source. The visual segmentation GLB and color-coded reference are used only to decide semantic component ownership. All QA renders use the source `Material.001` PBR.

Frozen inputs remain untouched:

- `experiments/snake-b-route/raw/snake_unsplit_50k.glb`
- `20260924110430_581b611c.glb` semantic reference
- the 500K Visual Master
- the 8K Hunyuan low-poly asset and existing native rig assets

## Action results

| Action | Static evidence | Current result |
| --- | --- | --- |
| HeadTilt | `review/character_v1/poses/HeadTilt.png` | PASS / readable |
| HeadShake | `review/character_v1/poses/HeadShake.png` | PASS / readable |
| BodySway | `review/character_v1/poses/BodySway.png` | PASS / readable |
| Bounce | `review/character_v1/poses/Bounce.png` | PASS / readable |
| TailWag | `review/character_v1/poses/TailWag.png` | PARTIAL / rigid seam remains visible on close inspection |
| TongueFlick | `review/character_v1/poses/TongueFlick.png` | PASS / readable |

`snake_blink` is intentionally a fallback entry. The supplied component segmentation has no eyelid geometry, so no Blink claim is made.

## Evidence

- Six-action contact sheet: `review/character_v1/snake_actions_contact_sheet.png`
- 60-frame, 30fps preview: `component_puppet_v1/snake_character_v1_preview.mp4`
- Preview contact sheet: `component_puppet_v1/snake_character_v1_preview_contact_sheet.png`
- Machine QA manifest: `component_puppet_v1/qa_manifest.json`

## Review decision

The component-puppet architecture is suitable as the snake's Character V1 action layer. Human review is still required for the visible TailWag component boundary and the Blink fallback. No final PBR, Three.js, Seedance, Minimax H3, or production animation work is included in this gate.
