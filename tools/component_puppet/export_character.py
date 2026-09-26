"""Export the clean Component Puppet GLB with its action set."""
import argparse,bpy,sys
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--blend',required=True);ap.add_argument('--output',required=True);argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:];args=ap.parse_args(argv);bpy.ops.wm.open_mainfile(filepath=args.blend);bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type in {'ARMATURE','MESH'}:o.select_set(True)
 bpy.context.view_layer.objects.active=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');bpy.ops.export_scene.gltf(filepath=args.output,export_format='GLB',use_selection=True,export_materials='EXPORT',export_animations=True,export_all_influences=True);print(args.output)
if __name__=='__main__':main()
