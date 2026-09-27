# G6 — Three.js Runtime Validation Gate

**THREE.JS RUNTIME GATE = PASS / HUMAN REVIEW**

## Gate status

```text
GLB LOAD = PASS
PBR RUNTIME = PASS
ANIMATION CLIPS = PASS
IDLE LOOP = PASS
ACTION SWITCHING = PASS
HOVER INTERACTION = PASS
CLICK INTERACTION = PASS
RUNTIME PERFORMANCE = PASS
TAIL NORMAL-DISTANCE REVIEW = ACCEPTABLE_LIMITATION
THREE.JS RUNTIME GATE = PASS
```

## Runtime inspection

- Three.js revision: r180
- GLB transfer: 36,810,788 bytes; localhost fetch/body time 25 ms; parse/decode 196.2 ms; first visible 461.2 ms.
- Scene: 12 Mesh, 0 SkinnedMesh, 14 bones, 50,856 triangles.
- Material/textures: Material.001; 3 textures.
- Actual GLB clips (7): dragon_bounce, dragon_head_shake, dragon_head_tilt, dragon_idle, dragon_proud, dragon_roar, dragon_tail_wag.
- FPS across 6 measured states: 60–60.714 average FPS; renderer.info draw calls 12–12; 50,856 triangles per frame.
- renderer.info memory: 12 geometries and 3 textures.
- Idle boundary: max bone position delta 0; max rotation delta 0.03778°; ROOT boundary drift 0; sampled ROOT drift 0.
- Runtime action-window ROOT position drift: 0.0.
- Hover produced HeadTilt and returned to Idle; click produced Bounce and returned to Idle. Action buttons use semantic names mapped to the actual GLB clips.
- Dragon has no verified WING_L/WING_R components; WingFlap is INELIGIBLE and is not exposed by the runtime UI.

## Evidence

- `runtime_neutral.png`, `runtime_idle.png`, `runtime_head_tilt.png`, `runtime_head_shake.png`, `runtime_dragon_proud.png`, `runtime_bounce.png`, `runtime_roar.png`, `runtime_tail_wag.png`
- `interaction_hover.mp4`, `interaction_click.mp4`, `tailwag_runtime_normal_distance.mp4`
- `runtime_asset_inspection.json`, `runtime_metrics.json`

## Measurement limits

This is a real Three.js/WebGL browser run on localhost. It confirms the runtime asset loads, the Dragon clips are exposed and mapped, and measured calls/FPS are acceptable on this desktop browser. It does not measure a deployed server, a cold-cache remote transfer, or a mobile device.

**Stop point:** Human Review. No model, rig, texture, geometry, or animation source was changed. No compression optimization was applied.
