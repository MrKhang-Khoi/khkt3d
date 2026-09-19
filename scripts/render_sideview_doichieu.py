import bpy, math
from mathutils import Vector, Euler

cam_name = 'Camera_Side_Orthographic_Blueprint'
cam = bpy.data.objects.get(cam_name)
if not cam:
    cam_data = bpy.data.cameras.new(cam_name)
    cam = bpy.data.objects.new(cam_name, cam_data)
    bpy.context.scene.collection.objects.link(cam)

cam.data.type = 'PERSP'
cam.data.lens = 55.0
# Đặt camera bên mạn thuyền nhìn thẳng ngang vào lính
cam.location = Vector((-6.25, -49.2, 1.35))
# Hướng nhìn về vị trí lính
cam.rotation_euler = Euler((math.radians(82.0), 0, math.radians(0.0)))

bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
out_path = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_kiemchung_sideview_doichieu.png'
bpy.context.scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("Rendered sideview to:", out_path)
