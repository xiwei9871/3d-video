# Zodiac Snake Component Puppet V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with verification checkpoints.

**Goal:** Turn the proven 50K original-material Component Puppet prototype into a clean-rebuildable Character V1 with six readable actions, fresh GLB roundtrip evidence, and a reusable pipeline Skill.

**Architecture:** Keep the 50K source mesh and all frozen 8K/50K/500K assets immutable. Rebuild a derived scene by separating loose component islands, parenting them rigidly to a small semantic armature, and authoring named actions from `character_config.json`. Validate the authored `.blend`, export a GLB, import it in a fresh Blender process, and report the remaining Blink/TailWag limitations explicitly.

**Tech Stack:** Blender 5.2.1 LTS, Python `bpy`, GLB/glTF, FFmpeg, JSON/Markdown.

---

### Task 1: Clean rebuild and Character V1 motion QA

**Files:**
- Modify: `/Users/xiwei/video making/tools/component_puppet/build_actions.py`
- Modify: `/Users/xiwei/video making/tools/component_puppet/validate_character.py`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/rebuild/clean_rig.blend`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/rebuild/clean_assigned.blend`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/rebuild/clean_actions.blend`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/rebuild/character_validation.json`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/review/character_v1/`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/05_animations/component_puppet_v1/`

- [ ] Rebuild the armature and component parenting from the immutable 50K GLB and current mapping.
- [ ] Create fake-user-backed actions for idle, head shake, head tilt, body sway, tail wag, and tongue flick; keep Blink as an explicit fallback.
- [ ] Validate required bones, 460 parented components, original material/images, finite transforms, action names and frame ranges.
- [ ] Render critical pose/contact-sheet evidence and a 60-frame/30fps preview video from the clean scene.

### Task 2: GLB export and fresh-import roundtrip

**Files:**
- Modify: `/Users/xiwei/video making/tools/component_puppet/export_character.py`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/zodiac_snake_character_v1.glb`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/roundtrip_check.py`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/roundtrip_validation.json`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/reports/glb_roundtrip.md`

- [ ] Export only the derived armature and mesh components with materials and actions.
- [ ] Import the GLB in a fresh factory-startup Blender process.
- [ ] Compare bones, component count, material/image inventory, parent relationships, action names, frame ranges, bounds, and sampled motion against the authored scene.
- [ ] Mark any unsupported glTF behavior as a warning rather than silently treating export as production-ready.

### Task 3: Automation report and reusable Skill

**Files:**
- Create: `/Users/xiwei/video making/reports/automation_rebuild_report.md`
- Create: `/Users/xiwei/video making/skills/component-puppet-character/SKILL.md`
- Modify: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/README.md`
- Modify: `/Users/xiwei/video making/characters/zodiac_snake/05_animations/README.md`

- [ ] Record clean-rebuild commands, elapsed time, intervention count, source immutability, current human-review items, and reuse boundaries for rabbit/dragon/horse.
- [ ] Document the generic gates G0 Asset Audit through G6 Runtime, with rigid-parent/minimal-deform/morph/two-bone-tail fallback hierarchy and Blink fallback hierarchy.
- [ ] Separate generic pipeline behavior from this snake's component mapping, source paths, action amplitudes, and known TailWag/Blink limitations.
- [ ] Re-run the final validation commands and stop at Human Review without Git, UV, texture, PBR, Three.js, or final production animation work.

### Task 4: G5.5 runtime component consolidation

**Files:**
- Create: `/Users/xiwei/video making/tools/component_puppet/consolidate_runtime.py`
- Create: `/Users/xiwei/video making/tools/component_puppet/validate_consolidation.py`
- Create: `/Users/xiwei/video making/tools/component_puppet/render_consolidation_review.py`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/04_rig/rebuild/runtime_consolidated.blend`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/zodiac_snake_character_v1_runtime.glb`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/runtime_consolidation_metrics.json`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/runtime_gate.json`
- Create: `/Users/xiwei/video making/characters/zodiac_snake/06_export/review/consolidation/`

- [ ] Merge only components sharing the same Puppet controller, preserving world geometry, UVs, Material.001 and parent bone.
- [ ] Compare before/after object, material, triangle and file-size metrics.
- [ ] Compare neutral and six action evaluated vertex hashes to detect visual/action regression.
- [ ] Export and fresh-import the runtime GLB, then render the neutral and action comparison evidence.
- [ ] Stop at `RUNTIME ASSET GATE = PASS / PARTIAL / FAIL`; do not start Three.js in this phase.

---

## Verification commands

```bash
blender --background --factory-startup --python tools/component_puppet/build_rig.py -- --config characters/zodiac_snake/character_config.json --source experiments/snake-b-route/raw/snake_unsplit_50k.glb --output characters/zodiac_snake/04_rig/rebuild/clean_rig.blend
blender --background --factory-startup --python tools/component_puppet/assign_components.py -- --blend characters/zodiac_snake/04_rig/rebuild/clean_rig.blend --mapping characters/zodiac_snake/component_mapping.json --config characters/zodiac_snake/character_config.json --output characters/zodiac_snake/04_rig/rebuild/clean_assigned.blend
blender --background --factory-startup --python tools/component_puppet/build_actions.py -- --blend characters/zodiac_snake/04_rig/rebuild/clean_assigned.blend --config characters/zodiac_snake/character_config.json --output characters/zodiac_snake/04_rig/rebuild/clean_actions.blend
blender --background --factory-startup --python tools/component_puppet/validate_character.py -- --blend characters/zodiac_snake/04_rig/rebuild/clean_actions.blend --config characters/zodiac_snake/character_config.json --output characters/zodiac_snake/04_rig/rebuild/character_validation.json
blender --background --factory-startup --python tools/component_puppet/export_character.py -- --blend characters/zodiac_snake/04_rig/rebuild/clean_actions.blend --output characters/zodiac_snake/06_export/zodiac_snake_character_v1.glb
blender --background --factory-startup --python characters/zodiac_snake/06_export/roundtrip_check.py -- --input characters/zodiac_snake/06_export/zodiac_snake_character_v1.glb --output characters/zodiac_snake/06_export/roundtrip_validation.json
```

G5.5 verification adds:

```bash
blender --background --factory-startup --python tools/component_puppet/consolidate_runtime.py -- --input characters/zodiac_snake/04_rig/rebuild/clean_actions.blend --output characters/zodiac_snake/04_rig/rebuild/runtime_consolidated.blend --metrics characters/zodiac_snake/06_export/runtime_consolidation_metrics.json
blender --background --factory-startup --python tools/component_puppet/export_character.py -- --blend characters/zodiac_snake/04_rig/rebuild/runtime_consolidated.blend --output characters/zodiac_snake/06_export/zodiac_snake_character_v1_runtime.glb
blender --background --factory-startup --python tools/component_puppet/validate_consolidation.py -- --before-blend characters/zodiac_snake/04_rig/rebuild/clean_actions.blend --after-blend characters/zodiac_snake/04_rig/rebuild/runtime_consolidated.blend --before-glb characters/zodiac_snake/06_export/zodiac_snake_character_v1.glb --after-glb characters/zodiac_snake/06_export/zodiac_snake_character_v1_runtime.glb --metrics-output characters/zodiac_snake/06_export/runtime_consolidation_metrics.json --output characters/zodiac_snake/06_export/runtime_gate.json
```
