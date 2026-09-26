"""Merge Component Puppet loose islands by their existing controller bone.

This creates a derived runtime scene. It never edits the authored Character V1
blend in place and never introduces smooth skinning.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--metrics", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def component_meshes():
    return [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and obj.parent_type == "BONE" and obj.parent is not None
    ]


def action_ranges():
    return {action.name: list(action.frame_range) for action in bpy.data.actions}


def mesh_stats(objects):
    vertices = 0
    polygons = 0
    triangles = 0
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


def group_key(obj):
    return (obj.parent.name, obj.parent_bone)


def merge_group(objects, controller):
    objects = list(objects)
    if len(objects) == 1:
        obj = objects[0]
        obj.name = f"RUNTIME_{controller}"
        obj["runtime_controller"] = controller
        obj["runtime_source_component_count"] = 1
        return obj
    # Join only objects with the same armature parent and parent bone. Blender
    # applies each object's local transform into the active object's mesh data,
    # so their world-space geometry remains unchanged.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    active = max(objects, key=lambda obj: len(obj.data.polygons))
    bpy.context.view_layer.objects.active = active
    bpy.ops.object.join()
    active.name = f"RUNTIME_{controller}"
    active["runtime_controller"] = controller
    active["runtime_source_component_count"] = len(objects)
    return active


def main():
    args = parse_args()
    bpy.ops.wm.open_mainfile(filepath=str(args.input))
    before_objects = component_meshes()
    if not before_objects:
        raise RuntimeError("No bone-parented Component Puppet mesh objects found")
    before = mesh_stats(before_objects)
    groups = {}
    for obj in before_objects:
        key = group_key(obj)
        groups.setdefault(key, []).append(obj)
    group_report = [
        {
            "armature": armature,
            "controller": controller,
            "source_objects": len(objects),
            "source_names": sorted(obj.name for obj in objects),
        }
        for (armature, controller), objects in sorted(groups.items())
    ]
    merged = [merge_group(objects, controller) for (_, controller), objects in sorted(groups.items())]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in merged:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = merged[0]
    after_objects = component_meshes()
    after = mesh_stats(after_objects)
    after["controllers"] = sorted(obj.parent_bone for obj in after_objects)
    after["runtime_objects"] = sorted(obj.name for obj in after_objects)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    report = {
        "input_blend": str(args.input),
        "output_blend": str(output),
        "before": before,
        "after": after,
        "controller_groups": group_report,
        "merge_policy": "one runtime mesh per existing armature parent bone; no smooth skinning",
        "material_policy": "preserve source Material.001 and PBR images",
        "status": "PASS" if after["mesh_objects"] <= 15 and after["triangles"] == before["triangles"] else "FAIL",
    }
    metrics = Path(args.metrics)
    metrics.parent.mkdir(parents=True, exist_ok=True)
    metrics.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
