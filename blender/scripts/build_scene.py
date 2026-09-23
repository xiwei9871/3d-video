"""Rebuild the complete stylized snake scene from a factory-empty Blender."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
CFG=json.loads((ROOT/'config/project.json').read_text())
def frame(authored):
 """Map authored storyboard frame markers to the configured clip length."""
 return round(1+(authored-1)/173*(round(CFG['fps']*CFG['duration'])-1))
def mat(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 return m
def collection(name):
 c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c
def move(obj,name,c,material=None,parent=None):
 obj.name=name
 for old in list(obj.users_collection):old.objects.unlink(obj)
 c.objects.link(obj)
 if material:obj.data.materials.append(material)
 if parent:obj.parent=parent
 return obj
def sphere(name,loc,scale,m,c,parent=None):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc);o=bpy.context.object;o.scale=scale
 for p in o.data.polygons:p.use_smooth=True
 return move(o,name,c,m,parent)
def curve(name,points,radius,m,c,parent=None):
 d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.resolution_u=16;d.bevel_depth=radius;d.bevel_resolution=5;d.use_fill_caps=True
 s=d.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
 for b,p in zip(s.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,d);c.objects.link(o);d.materials.append(m)
 if parent:o.parent=parent
 return o
def empty(name,c,parent=None):
 o=bpy.data.objects.new(name,None);c.objects.link(o);o.parent=parent;return o
def key(o,prop,values,action):
 for f,v in values:setattr(o,prop,v);o.keyframe_insert(data_path=prop,frame=frame(f))
 if o.animation_data and o.animation_data.action:o.animation_data.action.name=action
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def build():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 sc=bpy.context.scene;chars=collection('CHARACTERS');env=collection('ENVIRONMENT');fx=collection('FX');lights=collection('LIGHTS');cams=collection('CAMERA')
 green=mat('Snake • pistachio velvet',(.43,.64,.26),.58);cream=mat('Snake • vanilla belly',(.9,.83,.60),.55);spot=mat('Snake • sage spots',(.28,.48,.18),.6)
 eye=mat('Eyes • espresso glass',(.025,.012,.009),.13);white=mat('Eyes • ivory',(.99,.94,.82),.25);blush=mat('Cheeks • rose',(.92,.39,.37),.64)
 red=mat('Scarf • vermilion',(.65,.045,.025),.56);gold=mat('Charm • brushed gold',(.8,.44,.10),.27,.65);mouth=mat('Smile • warm umber',(.19,.08,.035),.5);tongue=mat('Tongue • coral',(.8,.12,.14),.42)
 stage=mat('Stage • porcelain',(.86,.76,.59),.6);cloud=mat('Clouds • milk',(.97,.9,.76),.66);petal=mat('Flower • blush',(.97,.57,.49),.62)
 root=empty('Snake.Root',chars);body=empty('Snake.BodyChain',chars,root);neck=empty('Snake.Neck',chars,body);head=empty('Snake.Head',chars,neck);head.location=(0,-.13,2.50)
 # Broad coil, rising neck and cream belly are deliberately simple controllable forms.
 pts=[]
 for i in range(31):
  t=i/30*math.pi*2.05;pts.append((math.cos(t)*.87,math.sin(t)*.54+.18,.59+.05*i/30))
 coil=curve('Snake.Coil',pts,.33,green,chars,body)
 sphere('Snake.CoilBelly',(0,-.38,.49),(.79,.22,.27),cream,chars,body)
 curve('Snake.NeckStem',[(.55,.3,.7),(.3,.05,1.05),(.02,-.03,1.55),(0,-.03,2.3)],.40,green,chars,neck)
 sphere('Snake.Belly',(0,-.36,1.45),(.35,.10,.7),cream,chars,neck)
 for i in range(5):curve('Snake.BellySeam.%02d'%i,[(-.28,-.425,1.02+i*.20),(0,-.46,.98+i*.20),(.28,-.425,1.02+i*.20)],.008,stage,chars,neck)
 curve('Snake.Tail',[(.6,.48,.63),(1.0,.48,.79),(1.08,.32,1.02),(.98,.3,1.18)],.16,green,chars,body)
 sphere('Snake.TailTip',(.98,.3,1.18),(.15,.15,.18),green,chars,body)
 sphere('Snake.HeadShape',(0,0,0),(.95,.69,.83),green,chars,head)
 sphere('Snake.FaceCream',(0,-.46,-.22),(.81,.30,.51),cream,chars,head)
 eye_controls=[]
 for side,x in [('L',-.42),('R',.42)]:
  e=empty('Snake.Eye.'+side,chars,head);e.location=(x,-.576,.10);eye_controls.append(e)
  sphere('Snake.EyeWhite.'+side,(0,0,0),(.31,.15,.36),white,chars,e)
  sphere('Snake.EyeIris.'+side,(.015,-.119,-.015),(.235,.105,.28),eye,chars,e)
  sphere('Snake.EyeGlint.'+side,(-.065,-.211,.102),(.074,.026,.089),white,chars,e)
  sphere('Snake.EyeGlintSmall.'+side,(.08,-.212,-.11),(.026,.012,.03),white,chars,e)
  sphere('Snake.Cheek.'+side,(x*1.43,-.641,-.24),(.16,.027,.085),blush,chars,head)
  curve('Snake.Brow.'+side,[(x-.10,-.53,.48),(x,-.565,.51),(x+.11,-.53,.48)],.019,mouth,chars,head)
 sphere('Snake.Nostril.L',(-.092,-.757,-.2),(.018,.012,.024),mouth,chars,head);sphere('Snake.Nostril.R',(.092,-.757,-.2),(.018,.012,.024),mouth,chars,head)
 curve('Snake.Smile',[(-.21,-.741,-.34),(-.12,-.774,-.39),(0,-.789,-.40),(.13,-.771,-.38),(.22,-.735,-.33)],.019,mouth,chars,head)
 tc=empty('Snake.Tongue',chars,head);tc.location=(0,-.79,-.405)
 sphere('Snake.TongueMesh',(0,-.035,-.07),(.065,.028,.10),tongue,chars,tc)
 for i,(x,z,s) in enumerate([(-.64,.42,.10),(-.29,.66,.16),(.12,.72,.17),(.54,.52,.13)]):sphere('Snake.ForeheadSpot.%02d'%i,(x,-.32,z),(s,.025,s*.62),spot,chars,head)
 for i in range(9):
  a=i/9*math.pi*1.7;sphere('Snake.CoilSpot.%02d'%i,(.87*math.cos(a),.54*math.sin(a)+.18,.88),(.13,.12,.035),spot,chars,body)
 # Flower follows head; small red scarf and coin establish zodiac character.
 flower=(-.74,-.2,.5)
 for i in range(5):
  a=i/5*math.tau;sphere('Snake.FlowerPetal.%02d'%i,(flower[0]+math.cos(a)*.13,flower[1]-.12,flower[2]+math.sin(a)*.13),(.105,.055,.105),petal,chars,head)
 sphere('Snake.FlowerCenter',(flower[0],flower[1]-.18,flower[2]),(.07,.035,.07),gold,chars,head)
 curve('Snake.Scarf',[(math.cos(i/24*math.tau)*.44,math.sin(i/24*math.tau)*.35,1.98) for i in range(25)],.09,red,chars,neck)
 sphere('Snake.ScarfKnot',(.30,-.25,1.87),(.16,.09,.20),red,chars,neck)
 charm=empty('Snake.Charm',chars,neck);charm.location=(0,-.49,1.78)
 sphere('Snake.GoldCharm',(0,0,0),(.20,.06,.23),gold,chars,charm);sphere('Snake.CharmInset',(0,-.059,0),(.16,.013,.185),cream,chars,charm)
 curve('Snake.CharmGlyph',[(-.055,-.077,-.09),(-.055,-.077,.08),(.06,-.077,.08),(.06,-.077,-.09),(-.055,-.077,-.09)],.017,red,chars,charm)
 curve('Snake.CharmBar',[(-.075,-.08,0),(.08,-.08,0)],.014,red,chars,charm)
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1.65,depth=.16,location=(0,0,.12));o=move(bpy.context.object,'Stage.Porcelain',env,stage);be=o.modifiers.new('Soft rounded edge','BEVEL');be.width=.08;be.segments=4;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 for side in [-1,1]:
  for i in range(3):sphere('Cloud.%s.%d'%('L' if side<0 else 'R',i),(side*(1.1+i*.16),.16,.34+(i%2)*.09),(.27,.22,.20),cloud,env)
 # Named, independently editable actions on separate controls.
 key(root,'location',[(1,(0,0,0)),(25,(0,0,0)),(43,(0,0,.10)),(59,(0,0,0)),(90,(0,0,.04)),(120,(0,0,0)),(174,(0,0,0))],'snake_bob')
 key(body,'rotation_euler',[(1,(0,0,-.02)),(55,(0,0,.025)),(105,(0,0,-.025)),(145,(0,0,0)),(174,(0,0,0))],'snake_idle')
 key(neck,'location',[(1,(0,0,-.22)),(25,(0,0,-.22)),(47,(0,0,.04)),(65,(0,0,0)),(145,(0,0,0)),(174,(0,0,0))],'snake_hero_pose')
 key(head,'rotation_euler',[(1,(0,0,.06)),(45,(0,-.06,.03)),(75,(0,.09,-.06)),(106,(0,-.08,.06)),(135,(0,0,0)),(174,(0,0,0))],'snake_head_sway')
 for e in eye_controls:key(e,'scale',[(1,(1,1,1)),(67,(1,1,1)),(70,(1,1,.06)),(74,(1,1,1)),(174,(1,1,1))],'snake_blink.'+e.name[-1])
 key(tc,'scale',[(1,(.01,.01,.01)),(100,(.01,.01,.01)),(104,(1,1,1)),(109,(1,1,.75)),(114,(.01,.01,.01)),(174,(.01,.01,.01))],'snake_tongue')
 for name,loc,power,size,color in [('Key',(-3,-4,6),650,5,(1,.84,.65)),('Fill',(4,-2,4),450,4,(.8,.91,1)),('Rim',(0,3,5),750,3,(1,.91,.72))]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new('Light.'+name,d);lights.objects.link(o);o.location=loc;aim(o,(0,0,1.5))
 d=bpy.data.cameras.new('Camera.Main');cam=bpy.data.objects.new('Camera.Main',d);cams.objects.link(cam);cam.location=(.12,-8,4.0);aim(cam,(0,0,1.5));d.type='ORTHO';d.ortho_scale=8.8;sc.camera=cam
 d.keyframe_insert(data_path='ortho_scale',frame=frame(1));d.ortho_scale=8.8/1.06;d.keyframe_insert(data_path='ortho_scale',frame=frame(150));d.keyframe_insert(data_path='ortho_scale',frame=frame(174))
 sc.render.engine='BLENDER_EEVEE';sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.image_settings.color_depth='8';sc.render.fps=CFG['fps'];sc.frame_start=1;sc.frame_end=round(CFG['fps']*CFG['duration']);sc.render.resolution_x=CFG['width'];sc.render.resolution_y=CFG['height'];sc.render.resolution_percentage=100
 sc.render.image_settings.compression=30;sc.world=bpy.data.worlds.new('World.Studio');sc.world.color=(.3,.3,.3);sc.view_settings.view_transform='AgX';sc.frame_set(150)
 dest=ROOT/CFG['renderPaths']['scene'];dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(dest));print('BUILT',dest,len(bpy.data.objects),'objects')
 return sc
if __name__=='__main__':build()
