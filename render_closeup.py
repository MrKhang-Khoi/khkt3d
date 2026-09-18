import bpy
import math

scene = bpy.context.scene

# Camera cận cảnh thuyền Đại Việt DV_01
cam_ta = bpy.data.cameras.new("Cam_CanCanh_Ta")
cam_ta.lens = 45.0
obj_cam_ta = bpy.data.objects.new("Camera_CanCanh_Ta", cam_ta)
# DV_01 tại (-9, -32, 0.85)
obj_cam_ta.location = (-9.0, -42.0, 4.5)
obj_cam_ta.rotation_euler = (math.radians(72), 0, 0)
scene.collection.objects.link(obj_cam_ta)
scene.camera = obj_cam_ta

scene.render.filepath = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_can_canh_thuy_thu_ta.png"
bpy.ops.render.render(write_still=True)

# Khôi phục camera chính
cam_main = bpy.data.objects.get("Camera_ChienTruong_Headon")
if cam_main:
    scene.camera = cam_main

print("Render cận cảnh thủy thủ thành công!")