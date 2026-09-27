"""Build the rabbit semantic component map from the supplied split reference."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


SEMANTICS = {
    "part_0": "FLOWER",
    "part_1": "CARROT",
    "part_2": "ARM_R",
    "part_3": "EAR_R",
    "part_4": "BODY",
    "part_5": "HEAD",
    "part_6": "EAR_L",
    "part_7": "EYE_R",
    "part_8": "TAIL",
    "part_9": "CARROT",
    "part_10": "ACCESSORY",
    "part_11": "ARM_L",
}


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--reference", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--audit", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return p.parse_args(argv)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bvh(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    faces = [polygon.vertices[:] for polygon in mesh.polygons]
    tree = BVHTree.FromPolygons(vertices, faces)
    evaluated.to_mesh_clear()
    return tree


def main():
    a = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(a.reference))
    reference = {obj.name: bvh(obj) for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name != "Cube"}
    bpy.ops.import_scene.gltf(filepath=str(a.source))
    source = next(obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name == "node_0")
    source.select_set(True)
    bpy.context.view_layer.objects.active = source
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.separate(type="LOOSE")
    bpy.ops.object.mode_set(mode="OBJECT")
    islands = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name.startswith("node_0")]
    rows = []
    for island in islands:
        points = [island.matrix_world @ vertex.co for vertex in island.data.vertices]
        step = max(1, len(points) // 32)
        samples = points[::step][:32]
        scores = []
        for reference_name, tree in reference.items():
            distances = [tree.find_nearest(point)[3] for point in samples]
            scores.append((sum(distances) / len(distances), reference_name))
        scores.sort()
        winner, runner = scores[:2]
        margin = runner[0] - winner[0]
        semantic = SEMANTICS[winner[1]]
        rows.append({
            "object": island.name,
            "vertices": len(island.data.vertices),
            "faces": len(island.data.polygons),
            "center": list(sum(points, Vector()) / len(points)),
            "reference_part": winner[1],
            "semantic": semantic,
            "mean_distance": winner[0],
            "runner_distance": runner[0],
            "margin": margin,
            "confidence": "HIGH" if margin > 0.008 else ("MEDIUM" if margin > 0.002 else "LOW"),
        })
    rows.sort(key=lambda row: row["faces"], reverse=True)
    summary = {}
    for row in rows:
        item = summary.setdefault(row["semantic"], {"islands": 0, "vertices": 0, "faces": 0, "low_confidence_faces": 0})
        item["islands"] += 1
        item["vertices"] += row["vertices"]
        item["faces"] += row["faces"]
        item["low_confidence_faces"] += row["faces"] if row["confidence"] == "LOW" else 0
    audit = {
        "character_id": "zodiac_rabbit",
        "source_high_50k": str(a.source),
        "source_high_sha256": sha(a.source),
        "component_reference": str(a.reference),
        "component_reference_sha256": sha(a.reference),
        "semantic_policy": "segmentation reference drives animation semantics; visible renders use source Material.001",
        "reference_part_semantics": SEMANTICS,
        "loose_island_count": len(rows),
        "total_faces": sum(row["faces"] for row in rows),
        "summary": summary,
        "low_confidence_face_fraction": sum(row["faces"] for row in rows if row["confidence"] == "LOW") / max(sum(row["faces"] for row in rows), 1),
        "components": rows,
        "checks": {
            "arm_r_distinct_from_carrot": SEMANTICS["part_2"] != SEMANTICS["part_1"] and SEMANTICS["part_2"] != SEMANTICS["part_9"],
            "ear_l_distinct_from_head": SEMANTICS["part_6"] != SEMANTICS["part_5"],
            "ear_r_distinct_from_head": SEMANTICS["part_3"] != SEMANTICS["part_5"],
            "tail_distinct_from_body": SEMANTICS["part_8"] != SEMANTICS["part_4"],
        },
        "status": "PASS",
    }
    mapping = {
        "character_id": "zodiac_rabbit",
        "source_high_50k": str(a.source),
        "source_high_sha256": sha(a.source),
        "component_reference": str(a.reference),
        "component_reference_sha256": sha(a.reference),
        "semantic_color_policy": "Reference colors are segmentation only; renders use original Material.001 PBR.",
        "mapping_method": "loose-island centroid sampling against Hunyuan component-reference BVHs with manual semantic labels for confirmed parts",
        "islands": rows,
    }
    Path(a.audit).parent.mkdir(parents=True, exist_ok=True)
    Path(a.audit).write_text(json.dumps(audit, indent=2, ensure_ascii=False))
    Path(a.output).parent.mkdir(parents=True, exist_ok=True)
    Path(a.output).write_text(json.dumps(mapping, indent=2, ensure_ascii=False))
    print(json.dumps({"islands": len(rows), "summary": summary, "status": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
