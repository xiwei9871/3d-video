"""Build an idempotent Component Puppet armature from a character config."""
import argparse, bpy, math, sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, load_json, ensure_collection, move_to_collection, mesh_objects

def add_bone(edit, bones, name, head, tail, parent=None):
    bone = edit.new(name); bone.head=head; bone.tail=tail; bone.parent=bones.get(parent)
    bones[name]=bone; return bone

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',required=True); ap.add_argument('--source',required=True); ap.add_argument('--output',required=True); argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]; args=ap.parse_args(argv)
    cfg=load_json(args.config)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    before=set(bpy.context.scene.objects); bpy.ops.import_scene.gltf(filepath=str(args.source))
    imported=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in before]
    if len(imported)!=1: raise RuntimeError(f'Expected one source mesh, got {len(imported)}')
    high=imported[0]; high.name='node_0'; high['component_puppet_source']=str(args.source)
    high.select_set(True); bpy.context.view_layer.objects.active=high
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
    pieces=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in before and o.name.startswith('node_0')]
    # The original active object is included in the loose split output.
    if high not in pieces: pieces.append(high)
    component_coll=ensure_collection('PUPPET_COMPONENTS')
    for obj in pieces:
        obj['component_puppet_source']=str(args.source); move_to_collection(obj,component_coll)
    arm_data=bpy.data.armatures.new('ARM_ComponentPuppet'); arm=bpy.data.objects.new('ARM_ComponentPuppet',arm_data); bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm; arm.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); e=arm_data.edit_bones; B={}
    add_bone(e,B,'ROOT',(0,0,0),(0,0,.05))
    add_bone(e,B,'COIL_BASE',(0,0,.10),(0,0,.22),'ROOT')
    add_bone(e,B,'BODY_NECK',(0,0,.22),(0,0,.58),'COIL_BASE')
    add_bone(e,B,'HEAD',(0,0,.58),(0,0,.88),'BODY_NECK')
    add_bone(e,B,'EYE_L',(-.12,-.24,.70),(-.12,-.27,.70),'HEAD')
    add_bone(e,B,'EYE_R',(.12,-.24,.70),(.12,-.27,.70),'HEAD')
    add_bone(e,B,'TONGUE',(0,-.31,.57),(0,-.36,.57),'HEAD')
    add_bone(e,B,'MEDALLION',(0,-.18,.38),(0,-.22,.38),'BODY_NECK')
    add_bone(e,B,'TAIL_ROOT',(.20,.16,.16),(.29,.22,.24),'COIL_BASE')
    add_bone(e,B,'TAIL_TIP',(.29,.22,.24),(.38,.30,.34),'TAIL_ROOT')
    bpy.ops.object.mode_set(mode='OBJECT'); arm.show_in_front=True; arm['component_puppet_config']=str(args.config)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))
    print({'output':args.output,'pieces':len(pieces),'bones':[b.name for b in arm.data.bones]})
if __name__=='__main__': main()
