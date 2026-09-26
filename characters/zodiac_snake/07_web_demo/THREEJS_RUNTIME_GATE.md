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
TAILWAG NORMAL-DISTANCE REVIEW = ACCEPTABLE_LIMITATION
THREE.JS RUNTIME GATE = PASS
```

## Runtime inspection

- Three.js revision: r180
- GLB transfer: 29,736,608 bytes; localhost fetch/body time 17.8 ms; parse/decode 159.2 ms; first visible 349.8 ms.
- Scene: 9 Mesh, 0 SkinnedMesh, 10 bones, 49,916 triangles.
- Material/textures: Material.001; 3 textures.
- Actual GLB clips (7): snake_body_sway, snake_bounce, snake_head_shake, snake_head_tilt, snake_idle, snake_tail_wag, snake_tongue_flick.
- FPS across five measured states: 59.999–60.717 average FPS; renderer.info draw calls 9–9; 49,916 triangles per frame.
- renderer.info memory: 9 geometries and 3 textures.
- Idle boundary: max bone position delta 0; max rotation delta 0.02998°; ROOT boundary drift 0; sampled ROOT drift 0.
- Runtime action-window ROOT position drift: 0.0.
- Hover produced HeadTilt and returned to Idle; click produced Bounce and returned to Idle. Action buttons use semantic names mapped to the actual GLB clips.
- TailWag is not visibly broken at normal whole-character framing; retain the known close-view component-boundary limitation.

## Evidence

- `runtime_neutral.png`, `runtime_idle.png`, `runtime_head_tilt.png`, `runtime_head_shake.png`, `runtime_body_sway.png`, `runtime_tail_wag.png`, `runtime_bounce.png`, `runtime_tongue_flick.png`
- `interaction_hover.mp4`, `interaction_click.mp4`, `tailwag_runtime_normal_distance.mp4`
- `runtime_asset_inspection.json`, `runtime_metrics.json`

## Measurement limits

This is a real Three.js/WebGL browser run on localhost. It confirms the runtime asset loads, all seven clips are exposed and mapped, and measured calls/FPS are acceptable on this desktop browser. It does not measure a deployed server, a cold-cache remote transfer, or a mobile device.

**Stop point:** Human Review. No model, rig, texture, geometry, or animation source was changed. No compression optimization was applied.
