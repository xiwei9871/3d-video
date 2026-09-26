# ZODIAC SNAKE CHARACTER V1 — FROZEN

**Checkpoint:** `ZODIAC_SNAKE_CHARACTER_V1_FROZEN`

**Date:** 2026-09-26

## Final gates

```text
ZODIAC SNAKE CHARACTER V1 = PASS
COMPONENT PUPPET PIPELINE V1 = PASS
THREE.JS RUNTIME GATE = PASS
```

| Gate | Result |
|---|---|
| G0 Asset Audit | PASS |
| G1 Component Map | PASS |
| G2 Puppet Build | PASS |
| G3 Core Actions | PASS |
| G4 Visual / Deformation QA | PASS WITH KNOWN LIMITATION |
| G5 Export / Roundtrip | PASS |
| G5.5 Runtime Asset Gate | PASS |
| G6 Three.js Runtime | PASS |

## Reference implementation

```text
50K original-material source
→ 460 loose islands
→ semantic component mapping
→ 10 Puppet controls
→ 7 exported actions
→ 9 runtime meshes
→ 49,916 triangles
→ 9 Three.js draw calls
→ approximately 60 FPS in measured desktop browser
→ G6 PASS
```

Automation baseline:

```text
clean rebuild = 5.683 seconds
manual intervention = 0
```

The runtime GLB is [`zodiac_snake_character_v1_runtime.glb`](06_export/zodiac_snake_character_v1_runtime.glb). The browser evidence and measured metrics are in [`07_web_demo/`](07_web_demo/).

## Frozen limitations

- TailWag's component boundary is visible only at close inspection and is accepted at normal runtime viewing distance.
- Blink remains a fallback because no production eyelid component was supplied.

These limitations do not reopen the V1 modeling or rigging gate.

## Frozen rules

Do not modify the V1 mesh, Puppet rig, weights, actions, UVs, PBR, or runtime consolidation in place. Do not start KTX2, Meshopt, Draco, LOD, texture-size reduction, additional actions, 500K work, or TailWag polish under this checkpoint. Any future work must create a new version or a separate optimization gate.

## Pipeline lessons recorded

1. Prefer rigid semantic components for visual modules and accessories.
2. Add minimal deformation only where a named motion truly requires it.
3. Avoid full-body smooth skinning by default for stylized component characters.
4. Let the motion requirements determine rig complexity.
5. Treat segmentation as animation semantics, not visible material art direction.
6. Consolidate loose islands before runtime export.
7. Measure actual Three.js draw calls and FPS before optimizing geometry or textures.
8. Allow `ACCEPTABLE_LIMITATION` for non-critical defects that disappear at the intended viewing distance.

## Next character

The next validation target is a rabbit as a separate task. It should reuse the generic Component Puppet Skill and report elapsed time from G0 through G6. It must not modify this frozen snake asset.
