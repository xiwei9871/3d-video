"""Shared idempotent helpers for the reusable Component Puppet pipeline."""
from __future__ import annotations
import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path('/Users/xiwei/video making')

def load_json(path):
    return json.loads(Path(path).read_text())

def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))

def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']

def ensure_collection(name, parent=None):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll

def move_to_collection(obj, coll):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    coll.objects.link(obj)

def get_armature():
    return next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)

def clear_pose(arm, drop_action=True):
    for bone in arm.pose.bones:
        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = (0, 0, 0)
        bone.location = (0, 0, 0)
    if drop_action and arm.animation_data:
        arm.animation_data.action = None

def world_bounds(objects):
    points = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi
