"""Render exchange frames or Gate A views. Safe for a clean background process."""
import bpy,json,sys,runpy,argparse,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];cfg=json.loads((ROOT/'config/project.json').read_text())
p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--views',action='store_true');p.add_argument('--frame',type=int);args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
scene_file=ROOT/cfg['renderPaths']['scene']
inputs=[ROOT/'config/project.json',Path(__file__).with_name('build_scene.py')]
if not scene_file.exists() or max(f.stat().st_mtime for f in inputs)>scene_file.stat().st_mtime:runpy.run_path(str(Path(__file__).with_name('build_scene.py')),run_name='__main__')
else:bpy.ops.wm.open_mainfile(filepath=str(scene_file))
sc=bpy.context.scene
sc.render.resolution_x=cfg['previewWidth'] if args.preview else cfg['width'];sc.render.resolution_y=cfg['previewHeight'] if args.preview else cfg['height'];sc.render.resolution_percentage=100
if args.views:
 dest=ROOT/cfg['renderPaths']['modelPreviews'];dest.mkdir(parents=True,exist_ok=True);sc.frame_set(150);sc.render.resolution_x=960;sc.render.resolution_y=960;sc.camera.data.animation_data_clear();sc.camera.data.ortho_scale=4.7
 for name,loc in [('front',(0,-8,3.4)),('three-quarter',(5,-7,3.8)),('side',(8,0,3.1))]:
  sc.camera.location=loc;sc.camera.rotation_euler=(Vector((0,0,1.7))-sc.camera.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(dest/(name+'.png'));bpy.ops.render.render(write_still=True)
else:
 dest=ROOT/cfg['renderPaths']['previewFrames' if args.preview else 'frames'];dest.mkdir(parents=True,exist_ok=True)
 for frame in ([args.frame] if args.frame else range(1,round(cfg['duration']*cfg['fps'])+1)):
  sc.frame_set(frame);sc.render.filepath=str(dest/('frame_%06d.png'%frame));bpy.ops.render.render(write_still=True)
 if not args.frame:
  digest=hashlib.sha256(b''.join(f.read_bytes() for f in inputs)).hexdigest()
  (dest/'manifest.json').write_text(json.dumps({'sourceHash':digest,'frames':round(cfg['duration']*cfg['fps']),'width':sc.render.resolution_x,'height':sc.render.resolution_y,'fps':cfg['fps'],'alpha':True},indent=2))
