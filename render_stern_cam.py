import bpy
import math
from mathutils import Vector, Euler

# Tạo camera góc nhìn đuôi thuyền (Stern Commander & Flag View)
cam_stern = bpy.data.objects.get("Camera_Stern_DV01")
if not cam_stern:
    cam_data = bpy.data.cameras.new("Camera_Stern_DV01_Data")
    cam_stern = bpy.data.objects.new("Camera_Stern_DV01", cam_data)
    bpy.context.scene.collection.objects.link(cam_stern)

ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
root = bpy.data.objects.get("Root_DV_01_SoaiTienPhong_Ta")
ship_pos = root.location if root else Vector((0,0,0))

# Đặt camera phía sau góc 3/4 đuôi tàu nhìn vào Commander và Cờ lệnh
cam_stern.location = ship_pos + Vector((-7.5, 3.5, 2.8))
# Hướng nhìn vào tướng chỉ huy (X = -3.6, Z = 1.2)
target = ship_pos + Vector((-3.6, 0.0, 1.2))
direction = target - cam_stern.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_stern.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam_stern
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
out_path = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_blender_cancanh_commander.png'
scene.render.filepath = out_path
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

bpy.ops.render.render(write_still=True)
print("Rendered commander shot to:", out_path)

import shutil
art_path = r'C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c\anh_blender_cancanh_commander.png'
shutil.copyfile(out_path, art_path)
print("Copied to artifact:", art_path)
