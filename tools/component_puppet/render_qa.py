"""Render Character V1 action evidence from a clean Component Puppet blend."""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib
from pathlib import Path

import bpy
from mathutils import Vector


ACTION_ORDER = [
    ("HeadTilt", "snake_head_tilt"),
    ("HeadShake", "snake_head_shake"),
    ("BodySway", "snake_body_sway"),
    ("Bounce", "snake_bounce"),
    ("TailWag", "snake_tail_wag"),
    ("TongueFlick", "snake_tongue_flick"),
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--preview-frames", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--config")
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def clear_pose(arm):
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0.0, 0.0, 0.0)
        bone.location = (0.0, 0.0, 0.0)


def ensure_render_setup(scene, objects):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.fps = 30

    world = bpy.data.worlds.get("CharacterV1.World") or bpy.data.worlds.new("CharacterV1.World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.026, 0.034, 0.050, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.35

    for old in list(scene.objects):
        if old.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(old, do_unlink=True)

    for name, loc, power, size in [
        ("V1_Key", (-4.0, -6.0, 6.0), 900.0, 5.0),
        ("V1_Fill", (4.0, -3.0, 4.0), 420.0, 4.0),
        ("V1_Rim", (0.0, 4.0, 5.0), 620.0, 4.0),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = power
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = loc

    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    target = (lo + hi) * 0.5
    camera_data = bpy.data.cameras.new("V1_Camera")
    camera = bpy.data.objects.new("V1_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(hi.x - lo.x, hi.z - lo.z) * 1.38
    camera.location = (5.0, -8.0, target.z + 0.18)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera


def render_action(scene, arm, action_name, path):
    action = bpy.data.actions.get(action_name)
    if action is None:
        raise RuntimeError(f"Missing action {action_name}")
    arm.animation_data_create()
    arm.animation_data.action = action
    start, end = action.frame_range
    frame = int(round((start + end) * 0.5))
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    return frame


def make_contact_sheet(paths, output_path, columns=3):
    loaded = [bpy.data.images.load(str(path), check_existing=False) for path in paths]
    if not loaded:
        return
    cell_w = loaded[0].size[0]
    cell_h = loaded[0].size[1]
    rows = (len(loaded) + columns - 1) // columns
    out_w = cell_w * columns
    out_h = cell_h * rows
    rgba = bytearray(out_w * out_h * 4)
    for index, image in enumerate(loaded):
        col = index % columns
        row_from_top = index // columns
        pixels = list(image.pixels[:])
        for y_top in range(cell_h):
            src_y = cell_h - 1 - y_top
            for x in range(cell_w):
                src = (src_y * cell_w + x) * 4
                dst = (((row_from_top * cell_h + y_top) * out_w) + col * cell_w + x) * 4
                for channel in range(4):
                    value = max(0.0, min(1.0, float(pixels[src + channel])))
                    if channel < 3:
                        value = value ** (1.0 / 2.2)
                    rgba[dst + channel] = int(round(value * 255.0))

    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    scanlines = bytearray()
    for y in range(out_h):
        scanlines.append(0)
        start = y * out_w * 4
        scanlines.extend(rgba[start : start + out_w * 4])
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", out_w, out_h, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(scanlines), 9))
    png += chunk(b"IEND", b"")
    Path(output_path).write_bytes(png)
    for image in loaded:
        bpy.data.images.remove(image)


def key_preview_pose(arm, frame, values):
    clear_pose(arm)
    for bone_name, channels in values.items():
        bone = arm.pose.bones[bone_name]
        if "rotation" in channels:
            bone.rotation_euler = channels["rotation"]
        if "location" in channels:
            bone.location = channels["location"]
        bone.keyframe_insert("rotation_euler", frame=frame)
        bone.keyframe_insert("location", frame=frame)


def build_preview_action(arm, config=None):
    action = bpy.data.actions.get("AN_ComponentPuppet_V1_Preview")
    if action:
        bpy.data.actions.remove(action)
    action = bpy.data.actions.new("AN_ComponentPuppet_V1_Preview")
    action.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = action
    deg = math.radians
    if config:
        c = config.get("controllers", {})
        frames = {1: {}, 8: {}, 16: {}, 24: {}, 32: {}, 40: {}, 48: {}, 56: {}, 60: {}}
        def add(frame, key, rotation=None, location=None):
            if key in arm.pose.bones:
                frames[frame][key] = {}
                if rotation is not None: frames[frame][key]["rotation"] = rotation
                if location is not None: frames[frame][key]["location"] = location
        head = c.get("head")
        body = c.get("body") or c.get("body_neck")
        ear_l = c.get("ear_l")
        ear_r = c.get("ear_r")
        carrot = c.get("carrot")
        arm_l = c.get("arm_l")
        arm_r = c.get("arm_r")
        tail = c.get("tail")
        if head: add(8, head, rotation=(0.0, deg(8), 0.0)); add(56, head, rotation=(0.0, 0.0, deg(10)))
        if body: add(16, body, rotation=(0.0, deg(-7), 0.0)); add(32, body, location=(0.0, 0.035, 0.0))
        if ear_l: add(24, ear_l, rotation=(deg(10), 0.0, 0.0))
        if ear_r: add(24, ear_r, rotation=(deg(-8), 0.0, 0.0))
        if carrot: add(40, carrot, rotation=(0.0, 0.0, deg(12)))
        if arm_l: add(40, arm_l, rotation=(deg(6), 0.0, 0.0))
        if arm_r: add(40, arm_r, rotation=(deg(-6), 0.0, 0.0))
        if tail: add(48, tail, rotation=(0.0, deg(12), 0.0))
    else:
        frames = None
    if frames is None:
      frames = {
        1: {},
        6: {"HEAD": {"rotation": (0.0, deg(8.0), 0.0)}},
        12: {},
        16: {"BODY_NECK": {"rotation": (0.0, deg(-8.0), 0.0)}},
        22: {},
        26: {"COIL_BASE": {"location": (0.0, 0.035, 0.0)}},
        32: {},
        36: {
            "TAIL_ROOT": {"rotation": (0.0, deg(8.0), 0.0)},
            "TAIL_TIP": {"rotation": (0.0, deg(-14.0), 0.0)},
        },
        42: {},
        46: {"TONGUE": {"rotation": (0.0, deg(12.0), 0.0)}},
        52: {},
        56: {"HEAD": {"rotation": (0.0, 0.0, deg(10.0))}},
        60: {},
      }
    for frame, values in frames.items():
        key_preview_pose(arm, frame, values)
    fcurves = []
    if hasattr(action, "fcurves"):
        fcurves = list(action.fcurves)
    elif action.layers and action.layers[0].strips:
        strip = action.layers[0].strips[0]
        if strip.channelbags:
            fcurves = list(strip.channelbags[0].fcurves)
    for fcurve in fcurves:
        for point in fcurve.keyframe_points:
            point.interpolation = "BEZIER"
    return action


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = Path(args.preview_frames)
    preview_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend))
    config = json.loads(Path(args.config).read_text()) if args.config else None
    scene = bpy.context.scene
    arm = next((obj for obj in scene.objects if obj.type == "ARMATURE"), None)
    objects = [obj for obj in scene.objects if obj.type == "MESH"]
    if arm is None or not objects:
        raise RuntimeError("Expected Component Puppet armature and mesh objects")
    ensure_render_setup(scene, objects)

    pose_dir = output_dir / "poses"
    pose_dir.mkdir(exist_ok=True)
    static = []
    action_order = ACTION_ORDER
    if config and config.get("qa_actions"):
        action_order = [(str(item[0]), str(item[1])) for item in config["qa_actions"]]
    for label, action_name in action_order:
        path = pose_dir / f"{label}.png"
        frame = render_action(scene, arm, action_name, path)
        static.append({"label": label, "action": action_name, "frame": frame, "path": str(path)})

    contact_path = output_dir / "snake_actions_contact_sheet.png"
    make_contact_sheet([Path(row["path"]) for row in static], contact_path)

    preview_action = build_preview_action(arm, config)
    scene.frame_start = 1
    scene.frame_end = 60
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(preview_dir / "frame_")
    scene.frame_set(1)
    bpy.ops.render.render(animation=True)
    arm.animation_data.action = bpy.data.actions.get("snake_idle")
    scene.frame_set(1)

    manifest = {
        "source_blend": str(args.blend),
        "static_actions": static,
        "contact_sheet": str(contact_path),
        "preview_action": preview_action.name,
        "preview_frames": 60,
        "fps": 30,
        "preview_frame_dir": str(preview_dir),
        "material_policy": "Original Material.001 PBR retained; segmentation colors are not rendered.",
        "status": "HUMAN_REVIEW",
    }
    Path(args.manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
