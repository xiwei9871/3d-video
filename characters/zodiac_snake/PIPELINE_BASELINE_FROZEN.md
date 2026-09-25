# Pipeline Baseline Frozen

The Native Snake Rig MVP is the technical baseline for the production character pipeline.

Frozen artifact:

```text
experiments/snake-b-route/native_rig_mvp/blender/snake_native_rig_mvp_v001.blend
```

It demonstrates the minimum viable native Armature + Body Spline IK + Tail Spline IK + rigid head + skinned deformation path. This file is immutable for production work; later work must create a new versioned file under `characters/zodiac_snake/`.

The Hunyuan 500K asset remains the visual master. The clean Animation Mesh remains the deformation reference. These roles are deliberately separate.

```text
PIPELINE BASELINE FROZEN = PASS
```
