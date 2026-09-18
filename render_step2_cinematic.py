import bpy
import mathutils

scene = bpy.context.scene
scene.frame_set(140)
bpy.context.view_layer.update()

cam_pursuit = bpy.data.objects.get('Camera_CanCanh_TruyKich')
if not cam_pursuit:
    cam_data = bpy.data.cameras.new('Cam_CanCanh_TruyKich')
    cam_pursuit = bpy.data.objects.new('Camera_CanCanh_TruyKich', cam_data)
    scene.collection.objects.link(cam_pursuit)

# Dat camera o phia truoc mui thuyen dang thao chay (DV_01 chay ve -Y, mui thuyen o -Y)
# Camera dat o Y thap hon (-7.5, -68.5, 3.0), nhin nguoc lai ve huong Bac (+Y)
# Se thay: Thuyen DV_01 lao ve phia camera, va sau lung no la dai ham doi Nam Han dang cuon cuon truy duoi!
cam_pursuit.location = (-7.5, -70.0, 3.2)
target = mathutils.Vector((-7.5, -50.0, 2.5))
direction = target - cam_pursuit.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_pursuit.rotation_euler = rot_quat.to_euler()
cam_pursuit.data.lens = 32

scene.camera = cam_pursuit
scene.render.filepath = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_step2_cancanh_truy_kich.png"
bpy.ops.render.render(write_still=True)
print("Rendered anh_step2_cancanh_truy_kich.png successfully!")

# Tra ve camera chien truong
cam_main = bpy.data.objects.get('Camera_ChienTruong_Headon')
if cam_main:
    scene.camera = cam_main
scene.frame_set(1)
bpy.context.view_layer.update()
