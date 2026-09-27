# SECOND CHARACTER REPLICATION BENCHMARK — Zodiac Rabbit

## Final gates

```text
G0 ASSET AUDIT = PASS
G1 COMPONENT MAP = PASS
G2 PUPPET BUILD = PASS
G3 CORE ACTIONS = PASS
G4 VISUAL QA = PASS
G5 EXPORT / ROUNDTRIP = PASS
G5.5 RUNTIME ASSET = PASS
G6 THREE.JS RUNTIME = PASS
RABBIT CHARACTER V1 = PASS
SECOND CHARACTER REPLICATION BENCHMARK = PASS
```

The Rabbit V1 character passes the technical gates. End-to-end elapsed production time is approximately **2 hours**, reported by the operator as an approximation rather than instrumented timing. This is not an exact 120-minute measurement.

## Inputs

- Accepted visual source: `characters/zodiac_rabbit/01_visual_master/rabbit_source_50k.glb`
- Accepted semantic component reference: `characters/zodiac_rabbit/02_components/rabbit_source_b.glb`
- Rejected supplementary input: `20260926115338_6298f48d.fbx` — audit showed a snake auxiliary mesh, 4,031 vertices / 8,068 triangles, no UV/material.
- Corrected 50K source SHA-256: `66277b2709e6faa7062702803ab814113695e1cdfdf366c3a8016c5a1c0a996e`

## Measured asset and runtime result

```text
50K visual source: 33,636 vertices / 50,394 triangles / Material.001 / 3 PBR images
component reference: 12 semantic parts
puppet controls: 11
core actions: 6
runtime meshes: 10
runtime triangles: 50,394
Three.js draw calls: 10
Three.js average FPS: 60.007–60.717 on HeadlessChrome r180, 1280×720, DPR 1
```

Clean rebuild/export/roundtrip baseline from the instrumented pipeline: **6.167 seconds**, **0 manual interventions after generic capability fixes**.

## Gate timings

| Gate | Automation | Human time | Interventions | Failures | Result |
|---|---:|---:|---:|---:|---|
| G0 Asset Audit | Not instrumented | Included in ~2h operator estimate | 1 input correction | 1 rejected FBX | PASS |
| G1 Component Map | 2.1s measured Blender mapping run | Included in ~2h operator estimate | 0 | 0 | PASS |
| G2 Puppet Build | 2.013s build + assign measured inside pipeline | Included in ~2h operator estimate | 0 after generic fix | 1 initial missing-controller blocker | PASS |
| G3 Core Actions | 0.606s action build | Included in ~2h operator estimate | 0 | 0 | PASS |
| G4 Visual QA | Not instrumented | Included in ~2h operator estimate | 0 | 0 | PASS |
| G5 Export / Roundtrip | Included in 6.167s clean pipeline | Included in ~2h operator estimate | 0 | 0 | PASS |
| G6 Three.js Runtime | Browser timings recorded below | Included in ~2h operator estimate | 0 | 0 | PASS |

```text
End-to-end elapsed production time ≈ 2 hours
Measurement quality = operator-reported approximation, not instrumented timing.
```

G6 browser measurements:

- GLB: 29,159,444 bytes;
- parse/decode: 142.9 ms;
- first visible: 333.1 ms;
- 10 meshes, 0 skinned meshes, 11 bones, 6 clips;
- 10 draw calls, 50,394 triangles, 10 geometries, 3 textures;
- zero sampled ROOT drift;
- Hover→HeadTilt→Idle and Click→Bounce→Idle passed.

## Generic reuse

The existing orchestration was reused. Generic changes were required only to add reusable configuration capabilities:

1. `build_rig.py` — optional config-driven `bone_layout`;
2. `assign_components.py` — config-driven `semantic_controllers` aliases;
3. `validate_character.py` — list-aware controller validation;
4. `render_qa.py` — config-driven QA actions and preview controls;
5. `roundtrip_check.py` — config-driven bones/actions/component counts;
6. `validate_consolidation.py` — config-driven regression action/bone sets;
7. `render_consolidation_review.py` — config-driven action list;
8. `compose_consolidation_review.py` — configurable action list;
9. `render_roundtrip.py` — config-driven runtime evidence actions.

No rabbit geometry, object name, or spatial shortcut was hardcoded into Generic Tool. Rabbit-specific work is in `character_config.json`, `component_mapping.json`, the G0 audit, and review evidence.

The recorded Snake regression evidence is validation PASS, roundtrip PASS, 8.587 seconds, 0 manual interventions. A fresh isolated rerun also passed validation and roundtrip in 6.095 seconds with 0 manual interventions; the frozen Snake checkpoint itself was not modified.

Generic changes contain no rabbit-specific geometry branch, hard-coded rabbit coordinates, or Rabbit object names outside config/mapping.

## Action and runtime evidence

- [Rabbit action QA](../characters/zodiac_rabbit/04_rig/RABBIT_CHARACTER_V1_ACTION_QA.md)
- [Rabbit runtime GLB](../characters/zodiac_rabbit/06_export/zodiac_rabbit_character_v1_runtime.glb)
- [Rabbit runtime gate](../characters/zodiac_rabbit/07_web_demo/THREEJS_RUNTIME_GATE.md)
- [Runtime metrics](../characters/zodiac_rabbit/07_web_demo/runtime_metrics.json)
- [G0 audit](../characters/zodiac_rabbit/RABBIT_ASSET_AUDIT.md)

## Conclusion

Rabbit is the second Component Puppet reference implementation. Snake proved the architecture; Rabbit proved replication. The pipeline supports a different component topology (head, ears, body, arms, carrot, tail, accessory) through config and mapping rather than a new rabbit-only rig branch. The next character can reuse the same G0–G6 flow, with time instrumentation enabled from the first command.

Stop at Human Review. Do not commit or push this Rabbit benchmark until review approval.
