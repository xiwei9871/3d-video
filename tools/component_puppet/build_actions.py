"""Create standard Component Puppet actions from config, safely rerunnable."""
import argparse, bpy, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_json, get_armature, clear_pose

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--config',required=True);ap.add_argument('--output',required=True);argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];args=ap.parse_args(argv)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend));cfg=load_json(args.config);arm=get_armature();
    if not arm:raise RuntimeError('ARM_ComponentPuppet missing')
    for name,spec in cfg['action_specs'].items():
        if spec.get('fallback') or (not spec.get('keys') and not spec.get('location_keys')):continue
        old=bpy.data.actions.get(name)
        if old: bpy.data.actions.remove(old)
        action=bpy.data.actions.new(name);action.use_fake_user=True;arm.animation_data_create();arm.animation_data.action=action
        for frame in range(1,int(spec['duration_frames'])+1):
            clear_pose(arm,drop_action=False)
            for bone_name,keys in spec['keys'].items():
                values={int(k[0]):k[1:] for k in keys};
                before=max((k for k in values if k<=frame),default=min(values));after=min((k for k in values if k>=frame),default=max(values));
                if before==after:v=values[before]
                else:
                    t=(frame-before)/(after-before);v=[values[before][i]*(1-t)+values[after][i]*t for i in range(3)]
                arm.pose.bones[bone_name].rotation_euler=v;arm.pose.bones[bone_name].keyframe_insert('rotation_euler',frame=frame)
            for bone_name,keys in spec.get('location_keys',{}).items():
                values={int(k[0]):k[1:] for k in keys};
                before=max((k for k in values if k<=frame),default=min(values));after=min((k for k in values if k>=frame),default=max(values));
                if before==after:v=values[before]
                else:
                    t=(frame-before)/(after-before);v=[values[before][i]*(1-t)+values[after][i]*t for i in range(3)]
                arm.pose.bones[bone_name].location=v;arm.pose.bones[bone_name].keyframe_insert('location',frame=frame)
        for fc in action.layers[0].strips[0].channelbags[0].fcurves if action.layers and action.layers[0].strips and action.layers[0].strips[0].channelbags else []:
            for kp in fc.keyframe_points:kp.interpolation='BEZIER'
    arm.animation_data.action=bpy.data.actions.get(cfg['actions'].get('idle','snake_idle')) or next(iter(bpy.data.actions),None)
    bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=90;bpy.context.scene.render.fps=30
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output));print('actions',[a.name for a in bpy.data.actions])
if __name__=='__main__':main()
