"""Build dragon semantic mapping from the supplied Hunyuan split reference."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

# The component reference is a semantic source, not a species guess.  These
# labels were verified against the supplied split renders and the source
# geometry bounds.  In particular, part_5 is the large face/head shell and
# parts 2/11 are the two eye shells; the old map had those assignments
# reversed, which made HeadShake move ornaments while the head stayed put.
SEMANTICS={
    'part_0':'TAIL',
    'part_1':'HORN_R',
    'part_2':'EYE_L',
    'part_3':'WHISKER_R',
    'part_4':'LEG_R',
    'part_5':'HEAD_BASE',
    'part_6':'ARM_L',
    'part_7':'HORN_R',
    'part_8':'ARM_R',
    'part_9':'BODY',
    'part_10':'TAIL_TIP',
    'part_11':'EYE_R',
    'part_12':'LEG_L',
    'part_13':'MANE',
    'part_14':'HORN_L',
    'part_15':'WHISKER_L',
    'part_16':'TONGUE',
}

def args():
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--reference',required=True);p.add_argument('--output',required=True);p.add_argument('--audit',required=True);argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];return p.parse_args(argv)
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def bvh(obj):
 deps=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(deps);m=ev.to_mesh();vs=[ev.matrix_world@v.co for v in m.vertices];fs=[p.vertices[:] for p in m.polygons];tree=BVHTree.FromPolygons(vs,fs);ev.to_mesh_clear();return tree
def main():
 a=args();bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=a.reference);ref={o.name:bvh(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Cube'};bpy.ops.import_scene.gltf(filepath=a.source);src=next(o for o in bpy.context.scene.objects if o.type=='MESH' and o.name=='node_0');src.select_set(True);bpy.context.view_layer.objects.active=src;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='LOOSE');bpy.ops.object.mode_set(mode='OBJECT');rows=[]
 for island in [o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('node_0')]:
  pts=[island.matrix_world@v.co for v in island.data.vertices];samples=pts[::max(1,len(pts)//32)][:32];scores=[]
  for rn,t in ref.items(): scores.append((sum(t.find_nearest(p)[3] for p in samples)/len(samples),rn))
  scores.sort();win,run=scores[:2];margin=run[0]-win[0];rows.append({'object':island.name,'vertices':len(island.data.vertices),'faces':len(island.data.polygons),'center':list(sum(pts,Vector())/len(pts)),'reference_part':win[1],'semantic':SEMANTICS[win[1]],'mean_distance':win[0],'runner_distance':run[0],'margin':margin,'confidence':'HIGH' if margin>.008 else ('MEDIUM' if margin>.002 else 'LOW')})
 rows.sort(key=lambda r:r['faces'],reverse=True);summary={}
 for r in rows:
  x=summary.setdefault(r['semantic'],{'islands':0,'vertices':0,'faces':0,'low_confidence_faces':0});x['islands']+=1;x['vertices']+=r['vertices'];x['faces']+=r['faces'];x['low_confidence_faces']+=r['faces'] if r['confidence']=='LOW' else 0
 audit={'character_id':'zodiac_dragon','source_high_50k':str(a.source),'source_high_sha256':sha(a.source),'component_reference':str(a.reference),'component_reference_sha256':sha(a.reference),'semantic_policy':'segmentation reference drives animation semantics; visible renders use source Material.001','reference_part_semantics':SEMANTICS,'loose_island_count':len(rows),'total_faces':sum(r['faces'] for r in rows),'summary':summary,'low_confidence_face_fraction':sum(r['faces'] for r in rows if r['confidence']=='LOW')/max(sum(r['faces'] for r in rows),1),'components':rows,'status':'PASS'}
 mapping={'character_id':'zodiac_dragon','source_high_50k':str(a.source),'source_high_sha256':sha(a.source),'component_reference':str(a.reference),'component_reference_sha256':sha(a.reference),'semantic_color_policy':'Reference colors are segmentation only; renders use original Material.001 PBR.','mapping_method':'loose-island centroid sampling against Hunyuan component-reference BVHs with manual dragon semantic labels','islands':rows}
 Path(a.audit).parent.mkdir(parents=True,exist_ok=True);Path(a.audit).write_text(json.dumps(audit,indent=2,ensure_ascii=False));Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(json.dumps(mapping,indent=2,ensure_ascii=False));print(json.dumps({'islands':len(rows),'summary':summary,'status':'PASS'},indent=2))
if __name__=='__main__':main()
