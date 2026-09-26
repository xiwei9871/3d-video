"""Validate runtime consolidation, action hashes, and fresh GLB import."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


DEFAULT_ACTIONS = [
    "snake_head_tilt",
    "snake_head_shake",
    "snake_body_sway",
    "snake_bounce",
    "snake_tail_wag",
    "snake_tongue_flick",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before-blend", required=True)
    parser.add_argument("--after-blend", required=True)
    parser.add_argument("--before-glb", required=True)
    parser.add_argument("--after-glb", required=True)
    parser.add_argument("--metrics-output", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fps", type=float, default=30.0)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def component_meshes():
    return [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and (obj.name.startswith("node_0") or obj.name.startswith("RUNTIME_"))
    ]


def action_ranges():
    return {action.name: list(action.frame_range) for action in bpy.data.actions}


def mesh_stats(objects):
    vertices = polygons = triangles = 0
    materials = set()
    for obj in objects:
        mesh = obj.data
        mesh.calc_loop_triangles()
        vertices += len(mesh.vertices)
        polygons += len(mesh.polygons)
        triangles += len(mesh.loop_triangles)
        materials.update(slot.material.name for slot in obj.material_slots if slot.material)
    return {
        "mesh_objects": len(objects),
        "vertices": vertices,
        "polygons": polygons,
        "triangles": triangles,
        "materials": sorted(materials),
        "images": sorted(image.name for image in bpy.data.images),
        "actions": action_ranges(),
    }


def bones():
    arm = next((obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"), None)
    if not arm:
        return [], {}
    return (
        sorted(bone.name for bone in arm.data.bones),
        {bone.name: (bone.parent.name if bone.parent else None) for bone in arm.data.bones},
    )


def finite_scene():
    return all(
        math.isfinite(float(value))
        for obj in bpy.context.scene.objects
        for value in (*obj.location, *obj.scale, *obj.rotation_euler)
    )


def clear_pose(arm):
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0.0, 0.0, 0.0)
        bone.location = (0.0, 0.0, 0.0)


def evaluated_hash(action_name=None, frame=1):
    arm = next((obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"), None)
    if arm is not None:
        arm.animation_data_create()
        if action_name:
            action = bpy.data.actions.get(action_name)
            if action is None:
                raise RuntimeError(f"Missing action {action_name}")
            arm.animation_data.action = action
        else:
            arm.animation_data.action = None
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in component_meshes():
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            for vertex in mesh.vertices:
                world = evaluated.matrix_world @ vertex.co
                points.append((round(float(world.x), 5), round(float(world.y), 5), round(float(world.z), 5)))
        finally:
            evaluated.to_mesh_clear()
    points.sort()
    payload = json.dumps(points, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_blend(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    meshes = component_meshes()
    arm = next((obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"), None)
    if arm is None:
        raise RuntimeError(f"No armature in {path}")
    return {
        "mesh_stats": mesh_stats(meshes),
        "bones": bones(),
        "finite_transforms": finite_scene(),
        "armature": arm,
    }


def action_hashes(path, action_names):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    ranges = action_ranges()
    result = {"neutral": evaluated_hash(None, 1)}
    for action_name in action_names:
        if action_name not in ranges:
            result[action_name] = None
            continue
        start, end = ranges[action_name]
        frames = sorted({int(round(start)), int(round(start + (end - start) * 0.25)), int(round((start + end) * 0.5)), int(round(start + (end - start) * 0.75)), int(round(end))})
        result[action_name] = {"frames": frames, "hashes": {str(frame): evaluated_hash(action_name, frame) for frame in frames}}
    return result


def import_glb_snapshot(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    result = bpy.ops.import_scene.gltf(filepath=str(path))
    if result != {"FINISHED"}:
        raise RuntimeError(f"GLB import failed: {result}")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name.startswith("RUNTIME_")]
    arm = next((obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"), None)
    imported_actions = action_ranges()
    imported_bones = sorted(bone.name for bone in arm.data.bones) if arm else []
    return {
        "component_mesh_objects": len(meshes),
        "all_mesh_objects": len([obj for obj in bpy.context.scene.objects if obj.type == "MESH"]),
        "helper_mesh_objects": sorted(
            obj.name for obj in bpy.context.scene.objects if obj.type == "MESH" and not obj.name.startswith("RUNTIME_")
        ),
        "bones": imported_bones,
        "actions": imported_actions,
        "fps": bpy.context.scene.render.fps,
        "materials": sorted(material.name for material in bpy.data.materials),
        "images": sorted(image.name for image in bpy.data.images),
        "bone_parented_components": sum(
            1
            for obj in meshes
            if obj.parent_type == "BONE" and obj.parent is not None and obj.parent.type == "ARMATURE"
        ),
    }


def file_size(path):
    return Path(path).stat().st_size


def main():
    args = parse_args()
    before = load_blend(args.before_blend)
    before_hashes = action_hashes(args.before_blend, DEFAULT_ACTIONS)
    after = load_blend(args.after_blend)
    after_hashes = action_hashes(args.after_blend, DEFAULT_ACTIONS)

    before_ranges = before["mesh_stats"]["actions"]
    after_ranges = after["mesh_stats"]["actions"]
    hashes = {}
    for name in ["neutral", *DEFAULT_ACTIONS]:
        before_value = before_hashes.get(name)
        after_value = after_hashes.get(name)
        if name == "neutral":
            before_hash = before_value if isinstance(before_value, str) else None
            after_hash = after_value if isinstance(after_value, str) else None
            hashes[name] = {"before": before_hash, "after": after_hash, "equal": before_hash is not None and before_hash == after_hash}
        else:
            before_frames = (before_value or {}).get("frames", [])
            after_frames = (after_value or {}).get("frames", [])
            before_values = (before_value or {}).get("hashes", {})
            after_values = (after_value or {}).get("hashes", {})
            equal = before_frames == after_frames and bool(before_frames) and all(
                before_values.get(str(frame)) == after_values.get(str(frame)) for frame in before_frames
            )
            hashes[name] = {
                "frames": before_frames,
                "before": before_values,
                "after": after_values,
                "equal": equal,
            }

    imported = import_glb_snapshot(args.after_glb)
    before_materials = set(before["mesh_stats"]["materials"])
    after_materials = set(after["mesh_stats"]["materials"])
    checks = {
        "semantic_mesh_consolidation": after["mesh_stats"]["mesh_objects"] <= 15
        and after["mesh_stats"]["triangles"] == before["mesh_stats"]["triangles"],
        "pbr_preservation": before_materials == after_materials
        and "Material.001" in after_materials
        and len(after["mesh_stats"]["images"]) >= 3,
        "action_regression": all(item["equal"] for item in hashes.values())
        and set(DEFAULT_ACTIONS) <= set(after_ranges),
        "glb_roundtrip": imported["component_mesh_objects"] == after["mesh_stats"]["mesh_objects"]
        and imported["bone_parented_components"] == imported["component_mesh_objects"]
        and set(after["bones"][0]) <= set(imported["bones"])
        and set(DEFAULT_ACTIONS) <= set(imported["actions"])
        and len(imported["materials"]) >= 1
        and len(imported["images"]) >= 3,
        "finite_transforms": before["finite_transforms"] and after["finite_transforms"],
    }
    metric_report = {
        "before": {
            **before["mesh_stats"],
            "blend_size_bytes": file_size(args.before_blend),
            "glb_size_bytes": file_size(args.before_glb),
            "bone_count": len(before["bones"][0]),
        },
        "after": {
            **after["mesh_stats"],
            "blend_size_bytes": file_size(args.after_blend),
            "glb_size_bytes": file_size(args.after_glb),
            "bone_count": len(after["bones"][0]),
        },
        "delta": {
            "mesh_objects": after["mesh_stats"]["mesh_objects"] - before["mesh_stats"]["mesh_objects"],
            "materials": len(after_materials) - len(before_materials),
            "triangles": after["mesh_stats"]["triangles"] - before["mesh_stats"]["triangles"],
            "glb_size_bytes": file_size(args.after_glb) - file_size(args.before_glb),
        },
    }
    metrics_path = Path(args.metrics_output)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metric_report, indent=2, ensure_ascii=False))
    gate = {
        "before_blend": str(args.before_blend),
        "after_blend": str(args.after_blend),
        "before_glb": str(args.before_glb),
        "after_glb": str(args.after_glb),
        "metrics": str(metrics_path),
        "checks": checks,
        "labels": {
            "SEMANTIC_MESH_CONSOLIDATION": "PASS" if checks["semantic_mesh_consolidation"] else "FAIL",
            "PBR_PRESERVATION": "PASS" if checks["pbr_preservation"] else "FAIL",
            "ACTION_REGRESSION": "PASS" if checks["action_regression"] else "FAIL",
            "GLB_ROUNDTRIP": "PASS" if checks["glb_roundtrip"] else "FAIL",
        },
        "action_hashes": hashes,
        "roundtrip": imported,
        "status": "PASS" if all(checks.values()) else "PARTIAL",
        "human_review": [
            "Review neutral and six-action comparison sheets at normal webpage viewing distance.",
            "TailWag remains a normal-distance visual review item; no close-up sculpting pass was performed.",
            "Blink remains the documented fallback and was not changed.",
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(gate, indent=2, ensure_ascii=False))
    print(json.dumps(gate, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
