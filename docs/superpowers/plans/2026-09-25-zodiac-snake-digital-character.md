# Zodiac Snake Digital Character Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with verification checkpoints.

**Goal:** Build a reusable, interactive, animation-ready `乙巳灵蛇` character asset and use it as the reference implementation for a twelve-zodiac character pipeline.

**Architecture:** Freeze the proven Native Rig MVP as an immutable technical baseline. Build a new production asset under `characters/zodiac_snake/`, keeping the 500K Hunyuan model as visual master and the animation mesh as deformation source. Promote only assets that pass shape, PBR, rig, animation, GLB roundtrip, and web interaction gates.

**Tech Stack:** Blender 5.2.1 / Python bpy, Blender native Armature + Spline IK, GLB/glTF, FFmpeg for evidence video, Three.js + Vite for the interactive demo.

---

### Task 1: Freeze the pipeline baseline

**Files:**
- Create: `characters/zodiac_snake/00_reference/README.md`
- Create: `characters/zodiac_snake/01_visual_master/README.md`
- Create: `characters/zodiac_snake/02_game_mesh/README.md`
- Create: `characters/zodiac_snake/03_textures/README.md`
- Create: `characters/zodiac_snake/04_rig/README.md`
- Create: `characters/zodiac_snake/05_animations/README.md`
- Create: `characters/zodiac_snake/06_export/README.md`
- Create: `characters/zodiac_snake/07_web_demo/README.md`
- Create: `characters/zodiac_snake/08_video/README.md`
- Create: `characters/zodiac_snake/PIPELINE_BASELINE_FROZEN.md`
- Create: `characters/zodiac_snake/manifest.json`
- Create: `reports/zodiac_snake_phase0.md`

- [ ] Record immutable source paths and SHA-256 values for the 500K Visual Master, semantic component GLB, Animation Mesh, Native Rig MVP, and MVP video.
- [ ] State that `native_rig_mvp_v001.blend` is frozen and must not be edited in place.
- [ ] Create the production directory tree and role-specific README files.
- [ ] Verify every referenced artifact exists and the manifest hashes match fresh checksums.
- [ ] Mark `PIPELINE BASELINE FROZEN = PASS` only after the verification command exits successfully.

### Task 2: Build `snake_game_mesh_v001` and shape gate

**Files:**
- Create: `characters/zodiac_snake/02_game_mesh/build_game_mesh.py`
- Create: `characters/zodiac_snake/02_game_mesh/blender/snake_game_mesh_v001.blend`
- Create: `characters/zodiac_snake/02_game_mesh/exports/snake_game_mesh_v001.glb`
- Create: `characters/zodiac_snake/02_game_mesh/renders/shape_match/`
- Create: `characters/zodiac_snake/02_game_mesh/reports/game_mesh_shape_gate.md`

- [ ] Start from the existing clean animation mesh and rigid head assembly.
- [ ] Adjust only silhouette-critical proportions against the 500K master: head, neck, coil, tail, and attachment placement.
- [ ] Preserve ring topology and existing armature compatibility.
- [ ] Render front, 3/4, side, and back evidence.
- [ ] Pass only if silhouette and major proportions read as the same character.

### Task 3: Transfer visual detail to the game mesh

**Files:**
- Create: `characters/zodiac_snake/03_textures/bake_pbr.py`
- Create: `characters/zodiac_snake/03_textures/snake_basecolor.png`
- Create: `characters/zodiac_snake/03_textures/snake_normal.png`
- Create: `characters/zodiac_snake/03_textures/snake_roughness.png`
- Create: `characters/zodiac_snake/03_textures/snake_ao.png`
- Create: `characters/zodiac_snake/03_textures/reports/pbr_transfer_gate.md`

- [ ] Create UVs on the approved game mesh without modifying the frozen master.
- [ ] Bake Base Color, Normal, Roughness, and AO from the 500K master.
- [ ] Keep eyes and other rigid attachments as separate materials where needed.
- [ ] Compare master, clay game mesh, and PBR game mesh before marking the gate.

### Task 4: Promote the MVP rig to production rig

**Files:**
- Create: `characters/zodiac_snake/04_rig/build_production_rig.py`
- Create: `characters/zodiac_snake/04_rig/blender/snake_production_rig_v001.blend`
- Create: `characters/zodiac_snake/04_rig/reports/production_rig_gate.md`

- [ ] Reuse the proven native bone names and Spline IK architecture.
- [ ] Add only medallion, tongue, coil squash, and root-motion controls.
- [ ] Refine weights at head/neck, body/coil, and tail root.
- [ ] Test Head Tilt, Body C, Tail S, Coil Squash, and Bounce.

### Task 5: Create and validate Animation Library V1

**Files:**
- Create: `characters/zodiac_snake/05_animations/build_animation_library.py`
- Create: `characters/zodiac_snake/05_animations/preview/`
- Create: `characters/zodiac_snake/05_animations/reports/animation_library_v1.md`

- [ ] Produce named clips `Idle`, `LookLeft`, `LookRight`, `HeadTilt`, `TailWag`, `Happy`, `Bounce`, `Surprised`, `Enter`, and `Exit`.
- [ ] Make loopable clips loop cleanly and keep transitions safe.
- [ ] Render a preview sheet and verify each clip independently.

### Task 6: Export and GLB roundtrip

**Files:**
- Create: `characters/zodiac_snake/06_export/snake_game_asset_v001.glb`
- Create: `characters/zodiac_snake/06_export/roundtrip_check.py`
- Create: `characters/zodiac_snake/06_export/reports/glb_roundtrip.md`

- [ ] Export mesh, skeleton, skin weights, materials, textures, and actions.
- [ ] Import into an empty Blender scene.
- [ ] Play every action and verify object, material, and animation integrity.

### Task 7: Three.js interactive character MVP

**Files:**
- Create: `characters/zodiac_snake/07_web_demo/index.html`
- Create: `characters/zodiac_snake/07_web_demo/src/main.js`
- Create: `characters/zodiac_snake/07_web_demo/src/character-controller.js`
- Create: `characters/zodiac_snake/07_web_demo/package.json`
- Create: `characters/zodiac_snake/07_web_demo/reports/interactive_character_mvp.md`

- [ ] Load `snake_game_asset_v001.glb` and default to `Idle`.
- [ ] Map mouse movement to head look.
- [ ] Map hover to `HeadTilt`, click to `Happy`/`Bounce`, and a button to `TailWag`.
- [ ] Return to Idle after inactivity.
- [ ] Verify the demo manually in a local browser and record the result.

### Task 8: Twelve-zodiac production standard

**Files:**
- Create: `characters/ZODIAC_CHARACTER_SPEC_v1.md`
- Create: `characters/zodiac_shared/character-api.md`
- Create: `characters/zodiac_shared/clip-names.json`

- [ ] Standardize coordinates, root, skeleton names, material names, texture sizes, clip names, GLB settings, and web API.
- [ ] Document the shared clips and per-animal extension points.
- [ ] Keep `loadCharacter(name)` and `play(name)` independent of individual character implementation.

## Verification commands

Phase 0 must be verified with a fresh checksum and file-existence script. Later phases must add Blender CLI inspection, render evidence, GLB re-import checks, and browser checks before their respective gates are marked PASS.
