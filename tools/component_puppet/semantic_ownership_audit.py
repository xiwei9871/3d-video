"""Config-driven G1.5 semantic ownership, isolation, and action eligibility audit.

The audit is deliberately separate from action authoring. It answers whether a
controller owns the intended semantic components before any action curves are
trusted. The source blend is opened read-only and no input asset is saved.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy
from mathutils import Vector


COLORS = {
    "HEAD_BASE": (0.95, 0.25, 0.25, 1),
    "MANE": (0.10, 0.75, 0.85, 1),
    "HORN_L": (0.95, 0.62, 0.10, 1),
    "HORN_R": (1.00, 0.82, 0.18, 1),
    "WHISKER_L": (0.95, 0.72, 0.25, 1),
    "WHISKER_R": (1.00, 0.90, 0.35, 1),
    "EYE_L": (0.30, 0.45, 1.00, 1),
    "EYE_R": (0.55, 0.65, 1.00, 1),
    "TONGUE": (0.95, 0.25, 0.55, 1),
    "BODY": (0.25, 0.72, 0.45, 1),
    "ARM_L": (0.15, 0.45, 0.95, 1),
    "ARM_R": (0.25, 0.60, 1.00, 1),
    "LEG_L": (0.55, 0.35, 0.95, 1),
    "LEG_R": (0.70, 0.45, 1.00, 1),
    "TAIL": (0.95, 0.35, 0.15, 1),
    "TAIL_TIP": (1.00, 0.50, 0.20, 1),
    "ACCESSORY": (0.85, 0.85, 0.85, 1),
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--review-dir", required=True)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    return parser.parse_args(argv)


def mesh_objects():
    return [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and obj.get("puppet_semantic")]


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


def setup_render(scene, objects):
    # Blender 5.2 exposes this engine as BLENDER_EEVEE in background mode.
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 640
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.fps = 30
    world = bpy.data.worlds.get("G1_5_Audit.World") or bpy.data.worlds.new("G1_5_Audit.World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.018, 0.025, 0.04, 1.0)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    for old in list(scene.objects):
        if old.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(old, do_unlink=True)
    for name, loc, energy, size in [
        ("G1_5_Key", (-4.0, -6.0, 6.0), 900.0, 5.0),
        ("G1_5_Fill", (4.0, -3.0, 4.0), 420.0, 4.0),
        ("G1_5_Rim", (0.0, 4.0, 5.0), 620.0, 4.0),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = loc
    lo, hi = bounds(objects)
    target = (lo + hi) * 0.5
    camera_data = bpy.data.cameras.new("G1_5_Camera")
    camera = bpy.data.objects.new("G1_5_Camera", camera_data)
    scene.collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(hi.x - lo.x, hi.z - lo.z) * 1.42
    camera.location = (5.0, -8.0, target.z + 0.18)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera


def audit_materials():
    result = {}
    for semantic, color in COLORS.items():
        name = f"G1_5_AUDIT_{semantic}"
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.diffuse_color = color
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = 0.58
        result[semantic] = mat
    return result


def apply_audit_materials(objects, materials):
    for obj in objects:
        mat = materials.get(obj.get("puppet_semantic"), materials["BODY"])
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            for index in range(len(obj.data.materials)):
                obj.data.materials[index] = mat


def render(scene, path):
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def object_semantics(objects):
    return {obj.name: str(obj.get("puppet_semantic")) for obj in objects}


def bone_parent_map(arm):
    return {bone.name: (bone.parent.name if bone.parent else None) for bone in arm.data.bones}


def ancestors(bone_name, parents):
    out = []
    current = bone_name
    while current:
        out.append(current)
        current = parents.get(current)
    return out


def ownership_rows(objects, arm, config, mapping):
    by_sem = defaultdict(list)
    for obj in objects:
        by_sem[str(obj.get("puppet_semantic"))].append(obj)
    ownership_cfg = config.get("semantic_ownership", {})
    rows = []
    for semantic in sorted(by_sem):
        group = by_sem[semantic]
        bones = [obj.parent_bone for obj in group if obj.parent_type == "BONE" and obj.parent]
        controller = Counter(bones).most_common(1)[0][0] if bones else None
        mapping_rows = [row for row in mapping.get("islands", []) if row.get("semantic") == semantic]
        refs = sorted({row.get("reference_part") for row in mapping_rows})
        confidence = "HIGH"
        if any(row.get("confidence") == "LOW" for row in mapping_rows):
            confidence = "LOW"
        elif any(row.get("confidence") == "MEDIUM" for row in mapping_rows):
            confidence = "MEDIUM"
        cfg = ownership_cfg.get(semantic, {})
        rows.append({
            "object_name": group[0].name if len(group) == 1 else f"{len(group)} objects",
            "source_component_id": refs,
            "semantic_label": semantic,
            "controller": controller,
            "config_controller": cfg.get("controller"),
            "parent_controller": arm.data.bones[controller].parent.name if controller in arm.data.bones and arm.data.bones[controller].parent else None,
            "motion_mode": cfg.get("motion_mode", "rigid"),
            "confidence": confidence,
            "object_count": len(group),
            "face_count": sum(len(obj.data.polygons) for obj in group),
        })
    return rows, by_sem


def action_eligibility(config, available):
    report = {}
    for name, rule in config.get("action_eligibility", {}).items():
        required = sorted(set(str(v).upper() for v in rule.get("required_components", [])))
        missing = sorted(set(required) - available)
        declared_ineligible = rule.get("eligible", True) is False
        fallback = bool(rule.get("fallback"))
        eligible = not declared_ineligible and not missing and not fallback
        valid = eligible or declared_ineligible or fallback
        report[name] = {
            "required_components": required,
            "missing_components": missing,
            "eligible": eligible,
            "declared_ineligible": declared_ineligible,
            "status": "ELIGIBLE" if eligible else ("FALLBACK" if fallback else "INELIGIBLE"),
            "valid": valid,
            "reason": rule.get("reason"),
        }
    return report


def action_gate_status(eligibility):
    return "PASS" if eligibility and all(item.get("valid") for item in eligibility.values()) else "FAIL"


def matrix_snapshot(objects):
    return {obj.name: tuple(round(float(v), 7) for row in obj.matrix_world for v in row) for obj in objects}


def moved_semantics(before, after, objects):
    moved = set()
    for obj in objects:
        if before.get(obj.name) != after.get(obj.name):
            moved.add(str(obj.get("puppet_semantic")))
    return moved


def main():
    args = parse_args()
    config = json.loads(Path(args.config).read_text())
    mapping = json.loads(Path(args.mapping).read_text())
    review_dir = Path(args.review_dir)
    review_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend))
    arm = next((obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"), None)
    objects = mesh_objects()
    if arm is None or not objects:
        raise RuntimeError("G1.5 requires an armature and semantic mesh objects")
    scene = bpy.context.scene
    setup_render(scene, objects)
    materials = audit_materials()
    apply_audit_materials(objects, materials)
    semantics = object_semantics(objects)
    available = set(semantics.values())
    rows, by_sem = ownership_rows(objects, arm, config, mapping)
    parents = bone_parent_map(arm)

    expected_labels = [
        "HEAD_BASE", "HORN_L", "HORN_R", "WHISKER_L", "WHISKER_R", "MANE",
        "EAR_L", "EAR_R", "EYE_L", "EYE_R", "TONGUE", "BODY", "ARM_L",
        "ARM_R", "LEG_L", "LEG_R", "TAIL", "TAIL_TIP", "WING_L", "WING_R",
    ]
    component_presence = {
        label: {"present": label in available, "object_count": len(by_sem.get(label, []))}
        for label in expected_labels
    }

    # Head assembly is allowed to use child controls, but the configured base
    # semantic must be owned by the configured head controller. This catches
    # the original accessory-only failure and works for legacy HEAD configs.
    head_group = set(config.get("semantic_groups", {}).get("HEAD_ASSEMBLY", []))
    base_candidates = config.get("head_base_semantics", ["HEAD_BASE", "HEAD"])
    head_base_semantic = next((name for name in base_candidates if name in available), None)
    semantic_controllers = config.get("semantic_controllers", {})
    if not semantic_controllers:
        legacy = config.get("controllers", {})
        semantic_controllers = {"HEAD": legacy.get("head"), "HEAD_BASE": legacy.get("head")}
    head_cfg_controller = semantic_controllers.get(head_base_semantic) if head_base_semantic else None
    if isinstance(head_cfg_controller, dict):
        head_cfg_controller = head_cfg_controller.get("controller")
    if not head_group and head_base_semantic:
        head_group = {head_base_semantic}
    head_group.update(name for name in available if name in {"EYE_L", "EYE_R", "LEFT_EYE", "RIGHT_EYE", "TONGUE", "FLOWER", "LEFT_BROW", "RIGHT_BROW"})
    head_rows = [row for row in rows if row["semantic_label"] in head_group]
    head_ok = bool(head_base_semantic and by_sem.get(head_base_semantic) and head_cfg_controller)
    for row in head_rows:
        bone = row.get("controller")
        if not bone or head_cfg_controller not in ancestors(bone, parents):
            head_ok = False
    head_assembly = {
        "members": sorted(head_group),
        "present_members": sorted(available & head_group),
        "missing_members": sorted(head_group - available),
        "base_semantic": head_base_semantic,
        "head_base_controller": head_cfg_controller,
        "status": "PASS" if head_ok else "FAIL",
    }

    eligibility = action_eligibility(config, available)
    baseline = matrix_snapshot(objects)
    isolation = {}
    isolation_dir = review_dir / "isolation"
    isolation_dir.mkdir(exist_ok=True)
    test_controllers = config.get("isolation_controllers") or [
        "HEAD_CTRL", "ARM_L_CTRL", "ARM_R_CTRL", "LEG_L_CTRL", "LEG_R_CTRL",
        "TAIL_CTRL", "TAIL_TIP_CTRL", "WHISKERS_CTRL",
    ]
    for controller in test_controllers:
        clear_pose(arm)
        if controller not in arm.pose.bones:
            isolation[controller] = {"status": "FAIL", "reason": "missing_controller"}
            continue
        arm.pose.bones[controller].rotation_mode = "XYZ"
        arm.pose.bones[controller].rotation_euler[2] = math.radians(10.0)
        bpy.context.view_layer.update()
        after = matrix_snapshot(objects)
        moved = sorted(moved_semantics(baseline, after, objects))
        expected = sorted(
            semantic for semantic, row in ((r["semantic_label"], r) for r in rows)
            if row.get("controller") and controller in ancestors(row["controller"], parents)
        )
        if not expected:
            isolation[controller] = {
                "angle_degrees": 10,
                "expected_semantics": [],
                "moved_semantics": [],
                "unexpected_semantics": [],
                "status": "SKIPPED",
                "reason": "no mapped semantic component uses this controller",
            }
            clear_pose(arm)
            continue
        unexpected = sorted(set(moved) - set(expected))
        isolation[controller] = {
            "angle_degrees": 10,
            "expected_semantics": expected,
            "moved_semantics": moved,
            "unexpected_semantics": unexpected,
            "status": "PASS" if moved and not unexpected else "FAIL",
        }
        for obj in objects:
            obj.hide_render = False
        scene.frame_set(1)
        render(scene, isolation_dir / f"{controller}.png")
    clear_pose(arm)
    for obj in objects:
        obj.hide_render = False

    # Render the whole head assembly with semantic colors and every other
    # component hidden. This is the primary human-review image.
    for obj in objects:
        obj.hide_render = str(obj.get("puppet_semantic")) not in head_group
    render(scene, review_dir / "head_assembly_audit.png")
    for obj in objects:
        obj.hide_render = False
    render(scene, review_dir / "semantic_ownership_neutral.png")
    for obj in objects:
        obj.hide_render = False

    isolation_status = "PASS" if isolation and all(item.get("status") in {"PASS", "SKIPPED"} for item in isolation.values()) else "FAIL"
    report = {
        "gate": "G1.5 SEMANTIC OWNERSHIP / ACTION ELIGIBILITY",
        "blend": str(args.blend),
        "config": str(args.config),
        "mapping": str(args.mapping),
        "available_semantic_components": sorted(available),
        "component_presence": component_presence,
        "ownership": rows,
        "head_assembly": head_assembly,
        "action_eligibility": eligibility,
        "controller_isolation": isolation,
        "gates": {
            "HEAD_ASSEMBLY": head_assembly["status"],
            "CONTROLLER_ISOLATION": isolation_status,
            "ACTION_ELIGIBILITY": action_gate_status(eligibility),
            "ineligible_actions": sorted(name for name, item in eligibility.items() if item.get("status") == "INELIGIBLE"),
        },
        "outputs": {
            "head_assembly_audit": str(review_dir / "head_assembly_audit.png"),
            "neutral": str(review_dir / "semantic_ownership_neutral.png"),
            "isolation_dir": str(isolation_dir),
        },
        "status": "PASS" if head_assembly["status"] == "PASS" and isolation_status == "PASS" and action_gate_status(eligibility) == "PASS" else "PARTIAL",
        "human_review": [
            "Verify the colored head assembly image against the original textured source.",
            "Unavailable semantic components are explicitly absent or ineligible when the supplied split has no separate component.",
            "Do not author an action whose required_components are missing.",
        ],
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({"status": report["status"], "gates": report["gates"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
