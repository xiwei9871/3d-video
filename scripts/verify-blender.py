import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];cfg=json.loads((ROOT/'config/project.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(ROOT/cfg['renderPaths']['scene']))
s=bpy.context.scene
assert s.render.film_transparent and s.render.image_settings.color_mode=='RGBA'
assert s.render.fps==cfg['fps'] and s.frame_end==round(cfg['fps']*cfg['duration'])
names=[a.name for a in bpy.data.actions]
for name in ['snake_bob','snake_idle','snake_hero_pose','snake_head_sway','snake_blink.L','snake_blink.R','snake_tongue']:assert name in names,name
for c in ['CHARACTERS','ENVIRONMENT','FX','LIGHTS','CAMERA']:assert c in bpy.data.collections
checks=[]
for frame in [1,43,70,74,104,114,150,174]:
 s.frame_set(frame);checks.append({'frame':frame,'eyeZ':bpy.data.objects['Snake.Eye.L'].scale.z,'tongueZ':bpy.data.objects['Snake.Tongue'].scale.z,'head':[round(v,4) for v in bpy.data.objects['Snake.Head'].rotation_euler]})
assert checks[2]['eyeZ']<.1 and checks[3]['eyeZ']>.9
assert checks[4]['tongueZ']>.9 and checks[5]['tongueZ']<.1
report={'status':'PASS','objects':len(bpy.data.objects),'actions':names,'checks':checks}
(ROOT/'outputs/blender-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
