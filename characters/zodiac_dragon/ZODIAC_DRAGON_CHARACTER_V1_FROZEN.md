# ZODIAC DRAGON CHARACTER V1 — FROZEN

**Checkpoint:** `ZODIAC_DRAGON_CHARACTER_V1_FROZEN`

## Final gates

```text
G0 ASSET AUDIT                 = PASS
G1 COMPONENT MAP               = PASS
G1.5 SEMANTIC OWNERSHIP        = PASS
G1.5 CONTROLLER ISOLATION      = PASS
G1.5 ACTION ELIGIBILITY        = PASS
G2 PUPPET BUILD                = PASS
G3 CORE ACTIONS                = PASS
G4 VISUAL / DEFORMATION QA     = PASS
G5 EXPORT / ROUNDTRIP          = PASS
G5.5 RUNTIME ASSET             = PASS
G6 THREE.JS RUNTIME            = PASS

DRAGON CHARACTER V1            = PASS
COMPONENT PUPPET PIPELINE V1.2 = PASS
```

## Reference implementation

```text
50,856 triangles
14 controls/bones
7 clips
12 runtime meshes
12 Three.js draw calls
60–60.714 FPS in the measured desktop browser
ROOT drift = 0
SkinnedMesh = 0
```

The final V1.2 runtime asset is
`06_export/v1_2_final/zodiac_dragon_character_v1_runtime.glb`.

## G1.5 semantic gate

```text
SEMANTIC OWNERSHIP      = PASS
CONTROLLER ISOLATION    = PASS
ACTION ELIGIBILITY      = PASS
WINGFLAP                = INELIGIBLE
```

The supplied split initially allowed mechanically valid but semantically wrong
actions. The repaired map assigns the head shell, mane, horns, eyes, whiskers,
tongue, body, limbs, tail, and tail tip to explicit semantic owners. G1.5 is a
mandatory gate before G3 for all future characters.

## Known limitations

- Blink remains a fallback because production eyelid geometry is absent.
- Ears are not independently segmented in the supplied component reference.
- The tail seam is a close-range review item and is accepted at normal runtime
  viewing distance.

These limitations do not block Dragon V1.

## Evidence

- `DRAGON_G1_5_SEMANTIC_GATE.md`
- `04_rig/review/g1_5/semantic_ownership_audit.json`
- `04_rig/rebuild/v1_2_final/semantic_ownership_audit.json`
- `04_rig/review/g1_5/semantic_ownership_contact_sheet.png`
- `04_rig/review/g1_5/semantic_controller_isolation_contact_sheet.png`
- `04_rig/review/g1_5/dragon_actions_contact_sheet_g1_5.png`
- `06_export/v1_2_final/runtime_gate.json`
- `07_web_demo/review/g1_5/THREEJS_RUNTIME_GATE.md`

## Freeze rule

Do not modify the Dragon V1 mesh, Puppet rig, actions, UVs, PBR, runtime
consolidation, or web runtime in place. Future work must use a new version or a
separate optimization gate. Do not start a fourth character under this
checkpoint.
