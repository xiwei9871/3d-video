import bpy
from pathlib import Path
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=32
scene.render.resolution_y=32
scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(0,0,5))
scene.camera=bpy.context.object
scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(Path(__file__).resolve().parents[1]/'work'/'doctor.png')
bpy.ops.render.render(write_still=True)
