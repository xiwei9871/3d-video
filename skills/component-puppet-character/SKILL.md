---
name: component-puppet-character
description: Build and validate a modular character animation layer from a textured GLB by combining rigid component parenting, minimal deformation, morph targets, and small semantic action clips.
---

# Component Puppet Character

Use this Skill when a character needs readable actions but continuous full-body skinning is unstable, unnecessarily expensive, or visually inappropriate. The method keeps high-value visual geometry and its original materials while moving only semantic modules with a small controller rig.

## Contract

The pipeline consumes:

- a source character GLB or Blender scene;
- a semantic component reference or face/object map;
- a character config containing controller names, component modes, and action specs;
- optional reference images for human visual review.

It produces a derived `.blend`, action evidence, a GLB export, a fresh-import roundtrip report, and a human-review gate. Never overwrite the source asset.

## G0 — Asset Audit

1. Record absolute source paths and SHA-256 values.
2. Confirm the source material policy. Preserve the original material and packed/source PBR images in visible renders. Treat segmentation colors as mapping evidence only.
3. Inspect object count, mesh count, loose islands, UV/material/image inventory, bounds, invalid transforms, and existing animation data.
4. Confirm which assets are frozen. Create all derived outputs under a versioned review/rebuild directory.

Minimum audit output:

```json
{
  "source_sha256": "...",
  "mesh_objects": 1,
  "material_policy": "preserve_source_material; segmentation_colors_audit_only",
  "frozen_inputs": true
}
```

## G1 — Component Map

Map loose islands or faces to semantic regions. Prefer explicit face IDs or authored component names. If the only available map is a colored segmentation GLB, sample it to produce a durable mapping JSON with:

- source object name;
- semantic region;
- reference part;
- vertex/face counts;
- centroid or anchor;
- confidence and method.

Keep the generic semantic vocabulary small: `HEAD`, `BODY_NECK`, `COIL_BASE` or `BODY_BASE`, `TAIL`, `EYES`, `TONGUE`, `FLOWER`/`ACCESSORY`, and `MEDALLION`/`PROP`. Character configs may add species-specific names, but must state the mapping explicitly.

## G2 — Puppet Build

Create a derived armature and parent modules by semantic ownership.

### Control hierarchy

```text
ROOT
└── BODY_BASE / COIL_BASE
    └── BODY_NECK
        └── HEAD
            ├── EYE_L
            ├── EYE_R
            └── TONGUE
        └── MEDALLION / PROP
    └── TAIL_ROOT
        └── TAIL_TIP
```

### Fallback hierarchy

Choose the least complex method that meets the named motion need:

1. **Rigid parent** — default for head assemblies, eyes, flowers, brows, medallions, coils, and detached accessories.
2. **Minimal deform** — use one B-Bone, two semantic deformation zones, or a short two-bone chain only for a region that must visibly bend.
3. **Morph / shape key** — use for blink, smile, squash, cheek, mouth, or corrective volume where a rigid transform cannot describe the expression.
4. **Two-bone tail fallback** — use `TAIL_ROOT → TAIL_TIP` before adding a longer tail chain or spline IK. Keep coil/body parenting isolated from distal tail motion.

Do not introduce full-body smooth weights merely because the source is one mesh. Separate islands or semantic components are valid if the intended camera cannot expose the boundary. If a component must remain one mesh, use a local deformation method and document its region mask.

### Parenting rules

- Preserve each object's world transform when assigning bone parenting.
- Use semantic region ownership rather than nearest-bone distance for coils and tails.
- Do not let tail controls influence the coil base unless the config explicitly permits it.
- Keep eyes, flowers, brows, tongue and medallions on the head/prop controller that owns them.
- Mark helpers and controller bones with stable names before authoring actions.

## G3 — Core Actions

Author short, named clips from config. Key only channels that the action needs; keep the action fake-user-backed so Blender does not purge unassigned clips.

The generic core set is:

- `Idle`
- `HeadTilt`
- `HeadShake` or `LookLeft`/`LookRight`
- `BodySway`
- `Bounce`
- `TailWag`
- `TongueFlick`
- `Blink` when eyelid geometry or a documented morph exists.

Each action spec must define duration, FPS, affected controls, and channel values. The validator must distinguish a fallback action from an absent action; a placeholder must never be reported as a successful Blink.

## G4 — Visual / Deformation QA

Render the neutral pose and the maximum readable pose for every core action. Use the same camera, lights, color management, and material policy across the sheet.

Check:

- head tilt and shake read at a glance;
- body sway preserves the intended silhouette;
- bounce does not detach the coil or props;
- tail wag remains legible without pulling the coil;
- tongue and accessories follow their owner;
- no explosion, NaN transform, unexpected scale, or obvious intersection;
- the source material remains recognizable.

Classify each action as `PASS`, `PARTIAL`, or `FAIL`. A rigid seam that is visible only at close range is a review item, not evidence that the whole architecture failed. If fewer than six design actions are readable, stop and repair the action layer before export.

Create a 60-frame, 30fps or character-configured preview when motion timing matters. A contact sheet is evidence for pose readability; it does not replace viewing the video.

## G5 — Export / Roundtrip

Export the derived armature, component meshes, source materials/images, and actions to GLB. Then start a fresh Blender process with factory settings and import the GLB.

Verify separately for the authored scene and fresh import:

- controller bone names and parent map;
- semantic component mesh count;
- bone-parent relationships;
- material/image inventory;
- action names and time ranges;
- bounds, scale, orientation, and finite transforms;
- one neutral and at least two action renders from the imported file.

glTF stores animation time in seconds. A fresh Blender scene may use a different FPS and therefore display converted frame numbers. Compare action durations in seconds and report the scene FPS instead of treating that conversion as data loss. Importer-generated armature display meshes must be counted separately from authored component meshes.

## G6 — Web Runtime

Use this gate when Three.js is the requested target runtime. Load the exported GLB in an actual browser with `GLTFLoader`, create an `AnimationMixer`, use a neutral light rig, enable OrbitControls for review, and keep the canvas responsive. Shadow rendering is optional and should remain off unless the asset needs it.

After loading, write `runtime_asset_inspection.json` with:

- mesh and skinned-mesh counts;
- bone count and names;
- triangle count;
- material names and texture count;
- actual animation clip count, names, durations, and semantic mapping;
- GLB byte size;
- HTTP load status, transfer bytes/time, parse/decode time, and first-visible time.

Map actual GLB clip names to semantic API names such as `head_tilt` and `tail_wag`. UI controls must call semantic names, never assume Blender Action names survived glTF export unchanged. Autoplay `Idle` with repeat. Crossfade action changes over a short interval; non-loop actions return to Idle after the mixer's finished event.

Test the brief's real interactions, such as hover→HeadTilt and click→Bounce. Check the idle loop boundary and root drift. Record non-loop action completion and return-to-idle events.

Measure the live renderer during Idle and representative actions with the actual `renderer.info` fields:

```js
renderer.info.render.calls
renderer.info.render.triangles
renderer.info.render.points
renderer.info.render.lines
renderer.info.memory.geometries
renderer.info.memory.textures
```

Also report average FPS, frame time, viewport/DPR, browser, GLB transfer bytes/time, parse time, and first-visible time in `runtime_metrics.json`. Do not infer draw calls from mesh count, and do not set a performance verdict from polygon or file-size budgets alone. Record the device and network context because desktop localhost performance does not establish mobile or deployed-server performance.

For components with a known seam limitation, record a normal whole-character viewing-distance video and review that framing. Mark an acceptable limitation when it is only apparent at close inspection; do not reopen modeling solely to satisfy a close-up standard outside the brief.

The runtime gate report must include `GLB LOAD`, `PBR RUNTIME`, `ANIMATION CLIPS`, `IDLE LOOP`, `ACTION SWITCHING`, the requested interactions, `RUNTIME PERFORMANCE`, and any normal-distance visual review. A fresh Blender import is not a Web Runtime pass.

## G5.5 — Runtime Component Consolidation

Run this gate after Character V1 actions and the authored GLB roundtrip pass.

1. Group only loose islands with the same existing armature parent bone.
2. Join each group while preserving world-space geometry, UVs, material slots, and the bone-parent relationship.
3. Keep separate runtime meshes when controllers differ, such as `EYE_L`/`EYE_R` and `TAIL_ROOT`/`TAIL_TIP`.
4. Record before/after mesh objects, vertices, polygons, triangles, materials, images, bones, and GLB byte size.
5. Compare neutral and every core action using evaluated world-space vertex hashes or equivalent geometry evidence.
6. Export a separate runtime GLB and fresh-import it in Blender. Count importer helper meshes separately from runtime components.

The target is usually 8–15 runtime mesh objects. A successful consolidation must keep triangle count, UV coverage, material/image inventory, action timing, and controller ownership unchanged. This is an object-count/draw-call preparation gate, not a license to retopologize or redesign the rig.

## First reference implementation — Zodiac Snake V1

The snake is the first reference implementation of this Skill. Its measured pipeline is:

```text
50K source
→ 460 loose islands
→ semantic component mapping
→ 10 Puppet controls
→ 7 exported actions
→ 9 runtime meshes
→ 49,916 triangles
→ 9 Three.js draw calls
→ approximately 60 FPS in the measured desktop browser
→ G6 PASS
```

The clean rebuild baseline is 5.683 seconds with 0 manual interventions. These are reference measurements, not hard budgets for other characters.

## Lessons learned

- Prefer rigid semantic components for head assemblies, accessories, coils, and other modules whose motion is rigid by design.
- Add minimal deformation only where a named motion requires it; motion requirements should drive rig complexity.
- Avoid full-body smooth skinning by default for stylized component characters when rigid ownership communicates the intended motion.
- Use component segmentation to define animation semantics. Segmentation colors are audit/mapping data and do not replace the source material policy.
- Consolidate loose islands by controller before runtime export so object traversal and draw-call behavior are measured on the actual runtime asset.
- Validate actual Three.js draw calls, triangles, memory, load time, parse time, and FPS before choosing KTX2, Meshopt, Draco, LOD, or geometry changes.
- `ACCEPTABLE_LIMITATION` is a valid V1 outcome for a non-critical visual defect that is not apparent at the intended viewing distance. Record the limitation and stop the gate instead of reopening the asset for close-up perfection.

## Blink fallback hierarchy

Use the first available option:

1. authored eyelid geometry with `Blink_L`, `Blink_R`, and `Blink_Both` morphs;
2. separate eyelid objects rigidly parented to `HEAD`, animated by hide/show or scale only when the asset contract allows it;
3. eye-object squash or lid proxy as an explicitly named placeholder;
4. documented `NOT_IMPLEMENTED` fallback.

Never silently animate the eyeball as if it were an eyelid. The report must state which fallback is active.

## Generic vs character-specific boundary

### Generic

- source hashing and frozen-input handling;
- loose-island separation;
- semantic mapping JSON schema;
- armature creation and world-transform-preserving bone parenting;
- config-driven rotation/location action authoring;
- validation, rendering, GLB export, and fresh-import inspection;
- timing report and human-review gate format.

### Character-specific

- source paths and material names;
- segmentation-to-semantic mapping;
- bone placement and local axes;
- action amplitude, timing, and review camera;
- tail/coil boundary acceptance;
- blink geometry availability;
- species-specific accessories and runtime clip names.

For a rabbit, dragon, horse, or another zodiac character, reuse the scripts and replace the config, mapping, source, controller layout, and review thresholds. Do not copy snake-specific centroids or tail rules without auditing the new asset.

## Required deliverables

At minimum, leave:

```text
<character>/04_rig/rebuild/clean_actions.blend
<character>/04_rig/rebuild/character_validation.json
<character>/05_animations/<character>_action_contact_sheet.png
<character>/05_animations/<character>_preview.mp4
<character>/06_export/<character>.glb
<character>/06_export/roundtrip_validation.json
reports/automation_rebuild_report.md
```

End at `HUMAN_REVIEW` when the requested action layer is validated. Do not enter UV, texture, PBR bake, final production animation, runtime integration, or Git commit unless a later task explicitly opens that gate.
