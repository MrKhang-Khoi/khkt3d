import bpy
import math
from mathutils import Vector, Euler
import shutil

cam_beauty = bpy.data.objects.get("Camera_Beauty_Fleet")
if not cam_beauty:
    cam_data = bpy.data.cameras.new("Camera_Beauty_Fleet_Data")
    cam_beauty = bpy.data.objects.new("Camera_Beauty_Fleet", cam_data)
    bpy.context.scene.collection.objects.link(cam_beauty)

root = bpy.data.objects.get("Root_DV_01_SoaiTienPhong_Ta")
ship_pos = root.location if root else Vector((0,0,0))

# Góc chụp 3/4 từ phía trước bên phải, bao quát cả con thuyền, cánh buồm, lính chèo, tướng chỉ huy và cờ lệnh
cam_beauty.location = ship_pos + Vector((8.5, -7.5, 4.5))
target = ship_pos + Vector((-0.5, 0.0, 1.2))
direction = target - cam_beauty.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_beauty.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam_beauty
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
out_path = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_blender_live_upgraded.png'
scene.render.filepath = out_path
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

bpy.ops.render.render(write_still=True)
art_path = r'C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c\anh_blender_live_upgraded.png'
shutil.copyfile(out_path, art_path)
print("-> Beauty shot rendered and copied successfully!")
