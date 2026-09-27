# Rabbit G0 — Asset Audit

**Gate:** `G0 ASSET AUDIT = PASS`

## Accepted inputs

| Role | Path | SHA-256 | Size |
|---|---|---|---:|
| 50K textured visual source | `01_visual_master/rabbit_source_50k.glb` | `66277b2709e6faa7062702803ab814113695e1cdfdf366c3a8016c5a1c0a996e` | 29,190,586 bytes |
| Hunyuan component reference | `02_components/rabbit_source_b.glb` | `537db806ce6b87207fc2a1619ffe66d331504e2d4e23e28b922e261de7832f04` | 1,799,804 bytes |

The supplied `20260926115338_6298f48d.fbx` was rejected as a rabbit source after visual audit: it is a snake auxiliary mesh with 4,031 vertices, 8,068 triangles, no UV, and no material. It remains recorded in `benchmark_log.json` and is not used by the pipeline.

## Measurements

### 50K visual source

- 33,636 vertices;
- 50,394 triangles / polygons;
- one mesh object with 888 connected components;
- one `Material.001` node material;
- one UV layer;
- three PBR images: BaseColor, packed Metallic/Roughness, Normal;
- zero degenerate faces, zero invalid vertices;
- source transforms finite.

### Component reference

- 12 physically separated component objects;
- 34,360 vertices and 68,680 triangles;
- 12 component materials used as structural segmentation references;
- no UV layers or PBR maps are used for visible runtime output;
- two degenerate faces are present in the segmentation reference only and are not copied into the visual source.

## Visual review

- 50K textured source: `benchmark/g0/visual_master.png`;
- component segmentation review: `benchmark/g0/components_segmentation.png`;
- rejected FBX evidence: `benchmark/g0/fbx_auxiliary.png`;
- isolated component review: `benchmark/g0/parts_contact.png`.

The visual source preserves the rabbit form and original PBR. The component reference exposes independent ears, body, arms, carrot parts, tail, head, accessory and flower regions for semantic mapping.

## Decision

The rabbit uses the 50K GLB as its visual source and the Hunyuan split GLB as a semantic mapping reference. No retopo, decimation, UV rebuild, texture rebuild or PBR bake was performed.
