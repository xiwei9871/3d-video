# 06_export

This directory contains the Character V1 GLB export and fresh Blender roundtrip evidence.

- Export: `zodiac_snake_character_v1.glb`
- Roundtrip metrics: `roundtrip_validation.json`
- Roundtrip renders: `review/`
- Roundtrip render manifest: `review/roundtrip_render_manifest.json`

## G5.5 Runtime Asset

- Runtime blend: `../04_rig/rebuild/runtime_consolidated.blend`
- Runtime GLB: `zodiac_snake_character_v1_runtime.glb`
- Consolidation metrics: `runtime_consolidation_metrics.json`
- Runtime gate: `runtime_gate.json`
- Runtime gate report: `reports/runtime_asset_gate.md`
- Neutral/action comparisons: `review/consolidation/`

The runtime GLB contains 9 controller-owned mesh objects instead of 460 loose-island objects. The consolidation is derived and does not replace the authored Character V1 source.

## G6 Three.js Runtime

- Demo: `../07_web_demo/`
- Browser asset inspection: `../07_web_demo/runtime_asset_inspection.json`
- Renderer metrics: `../07_web_demo/runtime_metrics.json`
- Runtime gate: `../07_web_demo/THREEJS_RUNTIME_GATE.md`
- Browser evidence: `../07_web_demo/review/`

G6 measured the actual WebGL renderer on a desktop browser. The gate passed for GLB loading, PBR maps, seven animation clips, Idle loop, action switching, Hover, and Click. TailWag is an acceptable known limitation at normal whole-character distance. Cold-cache deployment and mobile performance remain unmeasured.

The roundtrip checks 10 bone names, 460 component meshes, rigid bone parenting, Material.001, three PBR images, seven actions, finite transforms, and action time ranges. Blender's importer may add an armature display helper mesh and may display glTF seconds using its current scene FPS; both are recorded in the JSON rather than counted as component failures.
