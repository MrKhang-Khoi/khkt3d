import bpy
import os
import shutil

cam = bpy.data.objects.get("Camera_CanCanh_DV01")
if cam:
    bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
out_path = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_blender_cancanh_dv01.png'
scene.render.filepath = out_path
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

bpy.ops.render.render(write_still=True)
print("Rendered to:", out_path)

art_path = r'C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c\anh_blender_cancanh_dv01.png'
shutil.copyfile(out_path, art_path)
print("Copied to artifact:", art_path)
