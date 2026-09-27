"""Render isolated rabbit segmentation parts for semantic mapping review."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output-dir',required=True);argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];return p.parse_args(argv)

def mat(name):
    m=bpy.data.materials.new(name);m.diffuse_color=(0.72,0.72,0.72,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.72,0.72,0.72,1);return m

def setup(scene, obj):
    scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=480;scene.render.resolution_y=480;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    world=bpy.data.worlds.new('RabbitParts.World');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.03,.04,.05,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4
    for old in list(scene.objects):
        if old.type in {'CAMERA','LIGHT'}: bpy.data.objects.remove(old,do_unlink=True)
    data=bpy.data.lights.new('PartKey','AREA');data.energy=900;data.size=5;light=bpy.data.objects.new('PartKey',data);scene.collection.objects.link(light);light.location=(-4,-6,6)
    points=[obj.matrix_world@Vector(c) for c in obj.bound_box];lo=Vector((min(p.x for p in points),min(p.y for p in points),min(p.z for p in points)));hi=Vector((max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)));target=(lo+hi)/2;scale=max(hi.x-lo.x,hi.z-lo.z)*1.8
    camd=bpy.data.cameras.new('PartCamera');cam=bpy.data.objects.new('PartCamera',camd);scene.collection.objects.link(cam);camd.type='ORTHO';camd.ortho_scale=max(scale,.12);cam.location=(5,-8,target.z+.2);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam

def main():
    a=args();out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=a.input);parts=sorted([o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('part_')],key=lambda o:int(o.name.split('_')[1]));
    for p in parts:p.hide_render=True
    for p in parts:
        p.hide_render=False;p.data.materials.clear();p.data.materials.append(mat(p.name));setup(bpy.context.scene,p);bpy.context.scene.render.filepath=str(out/(p.name+'.png'));bpy.ops.render.render(write_still=True);p.hide_render=True
    print({'parts':[p.name for p in parts],'output_dir':str(out)})
if __name__=='__main__':main()
