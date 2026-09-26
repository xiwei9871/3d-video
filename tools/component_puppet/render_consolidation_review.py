"""Render matched before/after evidence for runtime consolidation."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ACTIONS = [
    "snake_head_tilt",
    "snake_head_shake",
    "snake_body_sway",
    "snake_bounce",
    "snake_tail_wag",
    "snake_tongue_flick",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", required=True)
    parser.add_argument("--after", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def meshes():
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and (obj.name.startswith("node_0") or obj.name.startswith("RUNTIME_"))]


def clear_pose(arm):
    if arm is None:
        return
    arm.animation_data_create()
    arm.animation_data.action = None
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0.0, 0.0, 0.0)
        bone.location = (0.0, 0.0, 0.0)


def bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    lo = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    hi = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    return lo, hi


def setup_render(scene, objects, target, ortho_scale):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.fps = 30
    for old in list(scene.objects):
        if old.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(old, do_unlink=True)
    world = bpy.data.worlds.get("Consolidation.World") or bpy.data.worlds.new("Consolidation.World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.026, 0.034, 0.050, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    for name, loc, energy, size in [
        ("C_Key", (-4.0, -6.0, 6.0), 900.0, 5.0),
        ("C_Fill", (4.0, -3.0, 4.0), 420.0, 4.0),
        ("C_Rim", (0.0, 4.0, 5.0), 620.0, 4.0),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = loc
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    camera_data = bpy.data.cameras.new("C_Camera")
    camera = bpy.data.objects.new("C_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = ortho_scale
    camera.location = (5.0, -8.0, target.z + 0.18)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera


def render_file(path, side, output_dir, target, ortho_scale):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    objects = meshes()
    arm = next((obj for obj in scene.objects if obj.type == "ARMATURE"), None)
    setup_render(scene, objects, target, ortho_scale)
    outputs = []
    clear_pose(arm)
    scene.frame_set(1)
    neutral = output_dir / f"{side}_neutral.png"
    scene.render.filepath = str(neutral)
    bpy.ops.render.render(write_still=True)
    outputs.append(str(neutral))
    for action_name in ACTIONS:
        action = bpy.data.actions.get(action_name)
        if action is None:
            raise RuntimeError(f"Missing {action_name} in {path}")
        arm.animation_data.action = action
        frame = int(round(sum(action.frame_range) * 0.5))
        scene.frame_set(frame)
        out = output_dir / f"{side}_{action_name}.png"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        outputs.append(str(out))
    return outputs


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.before))
    original_objects = meshes()
    lo, hi = bounds(original_objects)
    target = (lo + hi) * 0.5
    ortho_scale = max(hi.x - lo.x, hi.z - lo.z) * 1.38
    before_outputs = render_file(args.before, "original", output_dir, target, ortho_scale)
    after_outputs = render_file(args.after, "consolidated", output_dir, target, ortho_scale)
    manifest = {
        "before": str(args.before),
        "after": str(args.after),
        "original_outputs": before_outputs,
        "consolidated_outputs": after_outputs,
        "actions": ACTIONS,
        "camera_policy": "same orthographic camera and lights derived from original neutral bounds",
        "status": "HUMAN_REVIEW",
    }
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
