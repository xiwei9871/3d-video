# Zodiac Dragon Character V1 — Three.js Runtime Gate

This is the isolated G6 runtime validation demo. It loads the derived runtime GLB without modifying the Blender source, exposes semantic actions, and records real `WebGLRenderer.info` values.

## Run

```bash
npm install
cp ../06_export/zodiac_dragon_character_v1_runtime.glb public/zodiac_dragon_character_v1_runtime.glb
npm run serve
```

Open `http://127.0.0.1:4174/` in a browser. The demo is intentionally plain: neutral lighting, OrbitControls, a canvas, action buttons, and a machine-readable audit panel.

## Semantic controls

- `Idle` autoplay with LoopRepeat;
- `HeadShake`, `HeadTilt`, `DragonProud`, `Bounce`, `Roar`, `TailWag` buttons;
- hover the character for HeadTilt;
- click the character for Bounce;
- non-loop actions crossfade back to Idle after `finished`.

The UI maps semantic names to actual exported clip names at runtime. It does not assume Blender action names remain unchanged.

## Browser evidence

The browser exposes `window.__dragonRuntime.getMetrics()` and `startBenchmark()`. The capture workflow saves `runtime_asset_inspection.json` and `runtime_metrics.json`, then records Hover and Click videos in `review/`.

Use this local browser QA sequence:

```bash
npm run serve
playwright-cli open http://127.0.0.1:4174/
playwright-cli run-code "async page => { await page.evaluate(() => window.__dragonRuntime.startBenchmark()); await page.waitForTimeout(8500); }"
npm run capture
```

Capture screenshots with `playwright-cli screenshot --filename=review/runtime_neutral.png`. Start a browser recording with `playwright-cli video-start review/interaction_hover.webm`, perform the interaction, then `playwright-cli video-stop`; transcode the WebM to H.264 MP4 with FFmpeg. The current runtime inspection and measured gate are recorded in `THREEJS_RUNTIME_GATE.md`.

The corrected G1.5 evidence is under `review/g1_5/` and is mirrored into the
top-level runtime reports. `WingFlap` is intentionally absent because the
component map has no verified `WING_L`/`WING_R`. The browser workflow can be
rerun after changing the runtime bundle or QA scene. Performance findings are
specific to the measured desktop browser and localhost server.
