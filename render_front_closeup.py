import bpy
import math

scene = bpy.context.scene

# Camera góc 3/4 phía trước mạn thuyền DV_01
cam_ta = bpy.data.cameras.get("Cam_CanCanh_Ta")
obj_cam_ta = bpy.data.objects.get("Camera_CanCanh_Ta")
if obj_cam_ta:
    # DV_01 tại (-9, -32, 0.85), mũi thuyền tại (-9, -27)
    obj_cam_ta.location = (-15.0, -25.0, 3.8)
    obj_cam_ta.rotation_euler = (math.radians(65), 0, math.radians(-145))
    scene.camera = obj_cam_ta

scene.render.filepath = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_goc_nghieng_thuy_thu_ta.png"
bpy.ops.render.render(write_still=True)

# Khôi phục camera chính
cam_main = bpy.data.objects.get("Camera_ChienTruong_Headon")
if cam_main:
    scene.camera = cam_main

print("Render góc nghiêng 3/4 thành công!")