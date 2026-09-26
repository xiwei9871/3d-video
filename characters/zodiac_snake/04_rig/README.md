# 04_rig

This directory contains the derived Component Puppet rig for the 50K original-material snake.

## Character V1 status

- Clean rebuild: `rebuild/clean_actions.blend`
- Controller set: ROOT, COIL_BASE, BODY_NECK, HEAD, EYE_L, EYE_R, TONGUE, MEDALLION, TAIL_ROOT, TAIL_TIP
- Components: 460 loose islands, rigidly parented to semantic puppet bones
- Material policy: source `Material.001` and its packed PBR images are retained; segmentation colors are audit-only
- Action QA: `review/character_v1/snake_actions_contact_sheet.png`
- Gate: `ZODIAC SNAKE CHARACTER V1 = PASS / FROZEN`

TailWag remains a rigid component-boundary known limitation accepted at normal runtime distance. Blink is a documented fallback because the supplied segmentation does not contain an eyelid component.

## Rebuild

```bash
python3 tools/component_puppet/rebuild_pipeline.py -- \
  --project-root "/Users/xiwei/video making" \
  --blender /opt/homebrew/bin/blender
```

The command creates the three derived `.blend` stages, `character_validation.json`, the Character V1 GLB, and the fresh-import roundtrip JSON. It never edits frozen source assets.
