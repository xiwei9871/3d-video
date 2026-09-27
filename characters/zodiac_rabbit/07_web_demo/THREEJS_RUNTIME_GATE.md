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
TAIL NORMAL-DISTANCE REVIEW = NOT_APPLICABLE
THREE.JS RUNTIME GATE = PASS
```

## Runtime inspection

- Three.js revision: r180
- GLB transfer: 29,159,444 bytes; localhost fetch/body time 20.9 ms; parse/decode 142.9 ms; first visible 333.1 ms.
- Scene: 10 Mesh, 0 SkinnedMesh, 11 bones, 50,394 triangles.
- Material/textures: Material.001; 3 textures.
- Actual GLB clips (6): rabbit_bounce, rabbit_carrot_happy, rabbit_ear_wiggle, rabbit_head_shake, rabbit_head_tilt, rabbit_idle.
- FPS across five measured states: 60.007–60.717 average FPS; renderer.info draw calls 10–10; 50,394 triangles per frame.
- renderer.info memory: 10 geometries and 3 textures.
- Idle boundary: max bone position delta 0; max rotation delta 0.03179°; ROOT boundary drift 0; sampled ROOT drift 0.
- Runtime action-window ROOT position drift: 0.0.
- Hover produced HeadTilt and returned to Idle; click produced Bounce and returned to Idle. Action buttons use semantic names mapped to the actual GLB clips.
- Rabbit has no TailWag blocker in this action set; carrot/ear semantic actions are reviewed instead.

## Evidence

- `runtime_neutral.png`, `runtime_idle.png`, `runtime_head_tilt.png`, `runtime_head_shake.png`, `runtime_ear_wiggle.png`, `runtime_bounce.png`, `runtime_carrot_happy.png`
- `interaction_hover.mp4`, `interaction_click.mp4`, `tailwag_runtime_normal_distance.mp4`
- `runtime_asset_inspection.json`, `runtime_metrics.json`

## Measurement limits

This is a real Three.js/WebGL browser run on localhost. It confirms the runtime asset loads, all six Rabbit clips are exposed and mapped, and measured calls/FPS are acceptable on this desktop browser. It does not measure a deployed server, a cold-cache remote transfer, or a mobile device.

**Stop point:** Human Review. No model, rig, texture, geometry, or animation source was changed. No compression optimization was applied.
