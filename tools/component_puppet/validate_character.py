"""Machine-readable Character V1 validation."""
import argparse,bpy,json,math,sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_json,get_armature
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--config',required=True);ap.add_argument('--output',required=True);argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];args=ap.parse_args(argv);bpy.ops.wm.open_mainfile(filepath=str(args.blend));cfg=load_json(args.config);arm=get_armature();mesh=[o for o in bpy.context.scene.objects if o.type=='MESH'];actions={a.name:list(a.frame_range) for a in bpy.data.actions}
 required=set()
 for value in cfg.get('controllers',{}).values():
  required.update(value if isinstance(value,list) else [value])
 bones=set(b.name for b in arm.data.bones) if arm else set();parents=[o for o in mesh if o.parent_type=='BONE'];materials=sum(len(o.data.materials) for o in mesh);images=len(bpy.data.images)
 result={'blend':args.blend,'controllers':{'required':sorted(required),'present':sorted(required&bones),'missing':sorted(required-bones)},'mesh_objects':len(mesh),'parented_component_objects':len(parents),'materials':materials,'images':images,'actions':actions,'frame_range':list(bpy.context.scene.frame_start,end:=bpy.context.scene.frame_end) if False else [bpy.context.scene.frame_start,bpy.context.scene.frame_end],'checks':{'controllers':required<=bones,'components_parented':len(parents)>0,'actions_present':all(name in actions for name in cfg['actions'].values() if not cfg['action_specs'].get(name,{}).get('fallback')),'materials_present':materials>0,'no_nan_transforms':all(all(math.isfinite(float(v)) for v in o.location) for o in bpy.context.scene.objects)} }
 result['status']='PASS' if all(result['checks'].values()) else 'PARTIAL';open(args.output,'w').write(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
