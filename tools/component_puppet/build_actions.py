"""Create standard Component Puppet actions from config, safely rerunnable."""
import argparse, bpy, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_json, get_armature, clear_pose

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--config',required=True);ap.add_argument('--output',required=True);ap.add_argument('--mapping');ap.add_argument('--eligibility-output');argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];args=ap.parse_args(argv)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend));cfg=load_json(args.config);arm=get_armature();
    if not arm:raise RuntimeError('ARM_ComponentPuppet missing')
    # Action eligibility is component-driven.  A species name is never a
    # sufficient reason to author a clip.  If a mapping is provided, use its
    # actual semantic labels; otherwise retain backwards compatibility and
    # defer to the config's explicit available_semantic_components list.
    available=set(str(v).upper() for v in cfg.get('available_semantic_components',[]))
    if args.mapping:
        mapping=load_json(args.mapping)
        available.update(str(row.get('semantic','')).upper() for row in mapping.get('islands',[]) if row.get('semantic'))
    eligibility_report={'available_components':sorted(available),'actions':{},'status':'PASS'}
    for name,spec in cfg['action_specs'].items():
        rule=cfg.get('action_eligibility',{}).get(name,{})
        required=set(str(v).upper() for v in rule.get('required_components',[]))
        missing=sorted(required-available) if available else []
        eligible=rule.get('eligible',True) is not False and not missing
        if spec.get('fallback') or (not spec.get('keys') and not spec.get('location_keys')):
            eligibility_report['actions'][name]={'eligible':False,'status':'FALLBACK' if spec.get('fallback') else 'EMPTY','reason':spec.get('fallback','no keyed channels')};continue
        if not eligible:
            eligibility_report['actions'][name]={'eligible':False,'status':'INELIGIBLE','required_components':sorted(required),'missing_components':missing,'reason':rule.get('reason','required semantic components are unavailable')};continue
        eligibility_report['actions'][name]={'eligible':True,'status':'ELIGIBLE','required_components':sorted(required)}
        old=bpy.data.actions.get(name)
        if old: bpy.data.actions.remove(old)
        action=bpy.data.actions.new(name);action.use_fake_user=True;arm.animation_data_create();arm.animation_data.action=action
        for frame in range(1,int(spec['duration_frames'])+1):
            clear_pose(arm,drop_action=False)
            for bone_name,keys in spec['keys'].items():
                if bone_name not in arm.pose.bones: raise RuntimeError(f'Action {name} references missing controller bone {bone_name}')
                values={int(k[0]):k[1:] for k in keys};
                before=max((k for k in values if k<=frame),default=min(values));after=min((k for k in values if k>=frame),default=max(values));
                if before==after:v=values[before]
                else:
                    t=(frame-before)/(after-before);v=[values[before][i]*(1-t)+values[after][i]*t for i in range(3)]
                arm.pose.bones[bone_name].rotation_euler=v;arm.pose.bones[bone_name].keyframe_insert('rotation_euler',frame=frame)
            for bone_name,keys in spec.get('location_keys',{}).items():
                if bone_name not in arm.pose.bones: raise RuntimeError(f'Action {name} references missing controller bone {bone_name}')
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
    if args.eligibility_output:
        from pathlib import Path
        out=Path(args.eligibility_output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(__import__('json').dumps(eligibility_report,indent=2,ensure_ascii=False))
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output));print('actions',[a.name for a in bpy.data.actions])
if __name__=='__main__':main()
