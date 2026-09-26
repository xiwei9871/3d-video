"""Render a small visual check from a freshly imported Character V1 GLB."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manifest", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def setup(scene, objects):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.fps = 24
    world = bpy.data.worlds.new("Roundtrip.World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.026, 0.034, 0.050, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    for name, loc, energy in [
        ("RT_Key", (-4.0, -6.0, 6.0), 900.0),
        ("RT_Fill", (4.0, -3.0, 4.0), 420.0),
        ("RT_Rim", (0.0, 4.0, 5.0), 620.0),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = 5.0
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = loc
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    lo = Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points)))
    hi = Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points)))
    target = (lo + hi) * 0.5
    camera_data = bpy.data.cameras.new("RT_Camera")
    camera = bpy.data.objects.new("RT_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(hi.x - lo.x, hi.z - lo.z) * 1.38
    camera.location = (5.0, -8.0, target.z + 0.18)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(args.input))
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name.startswith("node_0")]
    arm = next((obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"), None)
    if arm is None or len(objects) != 460:
        raise RuntimeError(f"Expected armature and 460 component meshes, got armature={arm is not None}, meshes={len(objects)}")
    setup(bpy.context.scene, objects)
    rendered = []
    for name in ["snake_head_tilt", "snake_body_sway", "snake_tail_wag"]:
        action = bpy.data.actions.get(name)
        if action is None:
            raise RuntimeError(f"Missing action {name}")
        arm.animation_data_create()
        arm.animation_data.action = action
        frame = int(round(sum(action.frame_range) * 0.5))
        bpy.context.scene.frame_set(frame)
        path = output_dir / f"{name}_roundtrip.png"
        bpy.context.scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rendered.append({"action": name, "frame": frame, "path": str(path)})
    manifest = {
        "input_glb": str(args.input),
        "rendered": rendered,
        "component_mesh_count": len(objects),
        "status": "HUMAN_REVIEW",
    }
    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
