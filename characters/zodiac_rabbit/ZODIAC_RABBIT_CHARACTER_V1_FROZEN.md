# ZODIAC RABBIT CHARACTER V1 — FROZEN

**Checkpoint:** `RABBIT_CHARACTER_V1_FROZEN`

## Final gates

```text
G0 ASSET AUDIT        = PASS
G1 COMPONENT MAP      = PASS
G2 PUPPET BUILD       = PASS
G3 CORE ACTIONS       = PASS
G4 VISUAL QA          = PASS
G5 EXPORT / ROUNDTRIP = PASS
G5.5 RUNTIME ASSET    = PASS
G6 THREE.JS RUNTIME   = PASS

RABBIT CHARACTER V1 = PASS
SECOND CHARACTER REPLICATION BENCHMARK = PASS
```

## Reference implementation

```text
Rabbit source:       33,636 vertices
Triangle count:      50,394
Puppet controls:     11
Core actions:        6
Runtime meshes:      10
Three.js draw calls: 10
Three.js performance: approximately 60 FPS
ROOT drift:          0
Clean rebuild:       6.167 seconds
Manual interventions: 0 after config/mapping and generic capability fixes
```

End-to-end elapsed production time is **approximately 2 hours**, an operator-reported approximation and not an instrumented 120-minute measurement.

## Actions

```text
rabbit_idle
rabbit_head_tilt
rabbit_head_shake
rabbit_ear_wiggle
rabbit_bounce
rabbit_carrot_happy
```

Blink remains a documented fallback because the supplied split does not provide production eyelid geometry.

## Replication conclusion

Snake proved the architecture. Rabbit proved replication.

Rabbit-specific work is limited to `character_config.json`, `component_mapping.json`, input auditing and evidence review. Generic Tool changes provide reusable capabilities:

- config-driven bone layout;
- semantic controller aliases;
- character-derived export naming;
- config-aware validation;
- config-driven actions;
- config-driven QA;
- config-driven roundtrip;
- consolidation regression;
- configurable runtime evidence actions.

The Generic Tool contains no Rabbit-specific geometry branch, hard-coded Rabbit coordinates or Rabbit object names outside config/mapping.

## Snake regression

```text
Snake validation = PASS
Snake roundtrip = PASS
recorded clean rebuild baseline = 8.587 seconds
fresh isolated confirmation = 6.095 seconds
manual interventions = 0
```

The regression used an isolated output directory and did not modify the frozen Snake checkpoint.

## Freeze rule

Do not modify this Rabbit V1 asset in place. Future changes must use a new version or a separate optimization gate. Do not start Dragon in this task.
