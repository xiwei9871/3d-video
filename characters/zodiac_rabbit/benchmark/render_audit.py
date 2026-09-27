"""Rabbit-specific G0 evidence render; does not modify the source GLBs."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


PALETTE = [
    (0.90, 0.20, 0.20, 1),
    (0.20, 0.55, 0.95, 1),
    (0.20, 0.80, 0.40, 1),
    (0.95, 0.65, 0.12, 1),
    (0.70, 0.25, 0.85, 1),
    (0.10, 0.75, 0.78, 1),
    (0.95, 0.35, 0.65, 1),
    (0.55, 0.80, 0.20, 1),
    (0.85, 0.35, 0.10, 1),
    (0.35, 0.35, 0.90, 1),
    (0.85, 0.20, 0.50, 1),
    (0.35, 0.75, 0.35, 1),
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--components", required=True)
    p.add_argument("--visual", required=True)
    p.add_argument("--fbx", required=True)
    p.add_argument("--output-dir", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return p.parse_args(argv)


def studio(scene, objects, target, scale):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 720
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    world = bpy.data.worlds.get("RabbitAudit.World") or bpy.data.worlds.new("RabbitAudit.World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.045, 0.06, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    for old in list(scene.objects):
        if old.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(old, do_unlink=True)
    for name, location, energy in [("AuditKey", (-4, -6, 6), 850), ("AuditFill", (4, -3, 4), 400), ("AuditRim", (0, 4, 5), 500)]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.size = 5
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()
    camera_data = bpy.data.cameras.new("AuditCamera")
    camera = bpy.data.objects.new("AuditCamera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = scale
    camera.location = (5, -8, target.z + 0.2)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera


def render_asset(path, output, segmentation=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    suffix = Path(path).suffix.lower()
    before = set(bpy.context.scene.objects)
    if suffix in {".glb", ".gltf"}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        bpy.ops.wm.fbx_import(filepath=str(path))
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.name not in {"Cube"}]
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    target = (lo + hi) * 0.5
    scale = max(hi.x - lo.x, hi.z - lo.z) * 1.35
    if segmentation:
        for index, obj in enumerate(sorted(objects, key=lambda item: item.name)):
            material = bpy.data.materials.new(f"RabbitAuditPart{index:02d}")
            material.diffuse_color = PALETTE[index % len(PALETTE)]
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = PALETTE[index % len(PALETTE)]
            obj.data.materials.clear()
            obj.data.materials.append(material)
    studio(bpy.context.scene, objects, target, scale)
    bpy.context.scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)


def main():
    args = parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    render_asset(args.visual, out / "visual_master.png")
    render_asset(args.components, out / "components_segmentation.png", segmentation=True)
    render_asset(args.fbx, out / "fbx_auxiliary.png")
    print({"output_dir": str(out), "status": "HUMAN_REVIEW"})


if __name__ == "__main__":
    main()
