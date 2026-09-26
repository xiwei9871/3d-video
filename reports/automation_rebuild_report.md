# Component Puppet Character V1 Automation Rebuild Report

## Scope

This report covers the three requested parts:

1. implement and validate the snake baby's design actions;
2. extract the process into rerunnable scripts;
3. perform a clean rebuild, action QA, GLB roundtrip, and Skill documentation.

No frozen source asset was overwritten. The generated scene is derived from the 50K original-material GLB.

## Clean rebuild

The one-command entry point is:

```bash
python3 tools/component_puppet/rebuild_pipeline.py -- \
  --project-root "/Users/xiwei/video making" \
  --blender /opt/homebrew/bin/blender
```

It runs, in order:

1. `build_rig.py` — splits the source into 460 loose component islands and builds 10 semantic controller bones;
2. `assign_components.py` — parents all 460 islands to the correct puppet bones using `component_mapping.json`;
3. `build_actions.py` — creates fake-user-backed actions from `character_config.json`;
4. `validate_character.py` — checks controllers, parented components, materials, images, finite transforms, and action presence;
5. `export_character.py` — exports the derived armature/components/actions as GLB;
6. `06_export/roundtrip_check.py` — imports the GLB in a fresh factory-startup Blender process and checks survival.

The measured clean rebuild run on 2026-09-26 took **5.683 seconds** across six Blender invocations. The recorded machine report is `reports/component_puppet_rebuild_run.json`. Manual intervention count was **0**.

## Current outputs

- Authored scene: `characters/zodiac_snake/04_rig/rebuild/clean_actions.blend`
- Character validation: `characters/zodiac_snake/04_rig/rebuild/character_validation.json`
- GLB: `characters/zodiac_snake/06_export/zodiac_snake_character_v1.glb`
- Roundtrip validation: `characters/zodiac_snake/06_export/roundtrip_validation.json`
- Action QA: `characters/zodiac_snake/05_animations/CHARACTER_V1_ACTION_QA.md`
- Action preview: `characters/zodiac_snake/05_animations/component_puppet_v1/snake_character_v1_preview.mp4`

## Design action gate

Six non-idle design actions are available: HeadTilt, HeadShake, BodySway, Bounce, TailWag, and TongueFlick. HeadTilt, HeadShake, BodySway, Bounce, and TongueFlick are readable in the static evidence. TailWag remains **PARTIAL** because the rigid component boundary can be seen at close range. Blink remains a fallback because the supplied segmentation has no eyelid component.

The overall Character V1 decision is therefore:

```text
COMPONENT PUPPET CHARACTER V1 = PARTIAL / HUMAN REVIEW
```

The architecture is still suitable as the action layer because the six-action requirement is met without returning to full-body smooth skinning.

Technical asset inspection reports zero degenerate faces, zero invalid vertices, full UV coverage, one textured Material.001, three source images, ten bones, and seven actions. The 10,370 boundary/non-manifold edge count is expected for the intentionally separated component islands; it is not a claim of a closed single mesh.

## Generic pipeline boundary

Reusable behavior lives in `tools/component_puppet/`:

- `common.py` — shared Blender helpers;
- `build_rig.py` — source import, loose-island split, armature creation;
- `assign_components.py` — semantic mapping and rigid parenting;
- `build_actions.py` — config-driven rotation and location keyframes;
- `validate_character.py` — machine gate;
- `render_qa.py` — static actions and 60-frame evidence;
- `export_character.py` — GLB export;
- `06_export/roundtrip_check.py` — fresh Blender import gate;
- `render_roundtrip.py` — visual evidence from the imported GLB;
- `rebuild_pipeline.py` — one-command orchestration and timing report.

The generic part assumes a source GLB, a semantic component map, controller names, and action specs. A rabbit, dragon, or horse can reuse the orchestration and validators by supplying a new config, mapping, source, controller layout, and semantic action amplitudes. Species-specific geometry decisions, attachment names, blink implementation, tail mechanics, and review thresholds remain character-specific.

## Human review items

- decide whether the visible TailWag seam is acceptable for the intended camera distance;
- decide whether to add a dedicated eyelid component before claiming Blink;
- confirm that the GLB's seconds-based actions are consumed with the target runtime's intended FPS;
- do not promote this gate to final production animation until those decisions are made.

## G5.5 runtime consolidation

The derived runtime pass merges components by existing Puppet parent bone:

```text
460 mesh objects → 9 runtime mesh objects
49,916 triangles → 49,916 triangles
1 Material.001 → 1 Material.001
3 PBR images → 3 PBR images
```

The six action world-space hashes match before and after consolidation. The runtime GLB is `characters/zodiac_snake/06_export/zodiac_snake_character_v1_runtime.glb`; its fresh Blender import and independent asset inspection both pass. See `characters/zodiac_snake/06_export/reports/runtime_asset_gate.md`.

## G6 Three.js runtime validation

The derived runtime GLB was loaded in a real Three.js r180 browser demo using `GLTFLoader`, `AnimationMixer`, `OrbitControls`, and `WebGLRenderer.info` sampling. No model, rig, action, UV, texture, or compression change was made.

Measured on HeadlessChrome 153 at 1280×720, DPR 1, localhost:

```text
GLB LOAD = PASS
PBR RUNTIME = PASS
ANIMATION CLIPS = PASS
IDLE LOOP = PASS
ACTION SWITCHING = PASS
HOVER INTERACTION = PASS
CLICK INTERACTION = PASS
RUNTIME PERFORMANCE = PASS
TAILWAG NORMAL-DISTANCE REVIEW = ACCEPTABLE_LIMITATION
THREE.JS RUNTIME GATE = PASS
```

Runtime measurements:

- 29,736,608 GLB bytes;
- 17.8 ms fetch/body and 159.2 ms parse/decode in this localhost run;
- 349.8 ms first visible;
- 9 render calls, 49,916 triangles, 9 geometries and 3 textures;
- 59.999–60.717 average FPS across Idle, HeadShake, BodySway, TailWag and Bounce;
- zero measured ROOT position drift during action windows;
- all seven clips mapped by semantic names;
- Hover→HeadTilt→Idle and Click→Bounce→Idle recorded.

Evidence and machine reports are under `characters/zodiac_snake/07_web_demo/`. This is a desktop localhost measurement; deployed cold-cache and mobile performance remain open for a later runtime-specific review.

## Explicitly out of scope

UV, texture, PBR bake, Three.js, Seedance, Minimax H3, final production animation, and Git commit were not performed.
