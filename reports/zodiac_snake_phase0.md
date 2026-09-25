# 乙巳灵蛇数字角色 — Phase 0

## Gate

```text
PIPELINE BASELINE FROZEN = PASS
```

The Native Snake Rig MVP is frozen at:

```text
experiments/snake-b-route/native_rig_mvp/blender/snake_native_rig_mvp_v001.blend
```

It remains an immutable technical proof. Production work will use versioned files under `characters/zodiac_snake/`.

## Source checksums

| Role | Path | SHA-256 |
|---|---|---|
| Visual Master | `0bb5679922f839930887017be0479527.glb` | `4990af1153307e8b3bf46a6c8f45b933e8ce5ca1c2637b70547ea3d69f227ec0` |
| Semantic Components | `experiments/snake-b-route/raw/component_artifact_v001.glb` | `d7223904d93bc1ba0befa92d24d82e6c9044d1e111342eda75d59d8e4ce94556` |
| Animation Mesh | `experiments/snake-b-route/game_ready/blender/snake_animation_mesh_v001.blend` | `bc0bfe754de90ff857c379d4ebd1788f794787dcd1e6a8207559e146a7915fd0` |
| Native Rig MVP | `experiments/snake-b-route/native_rig_mvp/blender/snake_native_rig_mvp_v001.blend` | `5cc1c3321273bbd43bdc880716a4fd1e9dc5f1e0f44af454de03e08dfcfb9f23` |
| MVP Motion Video | `experiments/snake-b-route/native_rig_mvp/renders/snake_native_rig_mvp_v001.mp4` | `e7e0a1f4626167f51ca18aaa2d7023f818a4ec3cadb63948d27fbdc94d175f26` |

The fresh verification command checked all required files and matched the two immutable GLB hashes against the manifest.

## Next Gate

`GAME MESH SHAPE GATE` is the next allowed phase. It must create `snake_game_mesh_v001` as a new versioned asset and leave all Phase 0 sources untouched.
