"""Assign loose component islands to semantic Puppet bones."""
import argparse, bpy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import load_json, ensure_collection, move_to_collection, get_armature

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--mapping',required=True);ap.add_argument('--config');ap.add_argument('--output',required=True);argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];args=ap.parse_args(argv)
    bpy.ops.wm.open_mainfile(filepath=str(args.blend));mapping=load_json(args.mapping);cfg=load_json(args.config) if args.config else {};arm=get_armature()
    if not arm: raise RuntimeError('ARM_ComponentPuppet missing')
    bones=set(b.name for b in arm.data.bones)
    groups={}
    components=cfg.get('components',{})
    controllers=cfg.get('controllers',{})
    semantic_controllers=cfg.get('semantic_controllers',{})
    def component_controller(name, default=None):
        spec=components.get(name.lower(),{})
        if isinstance(spec,dict):
            return spec.get('controller') or spec.get('follow') or default
        return default
    def controller(semantic,row):
        direct=semantic_controllers.get(semantic)
        if isinstance(direct,str):
            return direct
        if isinstance(direct,dict) and direct.get('controller'):
            return direct['controller']
        if semantic=='TAIL':
            tail=components.get('tail',{}).get('controllers',[])
            if len(tail)>=2:
                return tail[0] if row['center'][1] < .25 else tail[-1]
            return component_controller('tail', controllers.get('tail_root'))
        if semantic in {'RIGHT_EYE','LEFT_EYE'}:
            eyes=components.get('eyes',{}).get('controllers',[])
            if len(eyes)>=2:
                return eyes[1] if semantic=='RIGHT_EYE' else eyes[0]
            return 'EYE_R' if semantic=='RIGHT_EYE' else 'EYE_L'
        if semantic in {'RIGHT_BROW','LEFT_BROW','FLOWER'}:
            return component_controller('brows' if 'BROW' in semantic else 'flower', controllers.get('head','HEAD'))
        lookup={'HEAD':'head','BODY_NECK':'body_neck','COIL_BASE':'coil','TONGUE':'tongue','MEDALLION':'medallion'}
        return component_controller(lookup.get(semantic,''), controllers.get(lookup.get(semantic,''), controllers.get('head','HEAD')))
    by_name={r['object']:r for r in mapping['islands']}
    for obj in [o for o in bpy.context.scene.objects if o.type=='MESH' and o.name in by_name]:
        row=by_name[obj.name]; semantic=row['semantic']; bone=controller(semantic,row)
        if bone not in bones: raise RuntimeError(f'Missing controller {bone}')
        matrix=obj.matrix_world.copy();obj.parent=arm;obj.parent_type='BONE';obj.parent_bone=bone;obj.matrix_world=matrix
        obj['puppet_semantic']=semantic;obj['puppet_bone']=bone
        coll=groups.setdefault(semantic,ensure_collection('PUPPET_'+semantic))
        move_to_collection(obj,coll)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))
    print({'output':args.output,'assigned_objects':sum(len(c.objects) for c in groups.values()),'groups':{k:len(v.objects) for k,v in groups.items()}})
if __name__=='__main__': main()
