import bpy
import mathutils

scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()

root_dv = bpy.data.objects.get('Root_DV_01_SoaiTienPhong_Ta')
cam_obj = bpy.data.objects.get('Camera_CanCanh_Ta')

if not cam_obj:
    cam_data = bpy.data.cameras.new('Cam_CanCanh_Ta')
    cam_obj = bpy.data.objects.new('Camera_CanCanh_Ta', cam_data)
    scene.collection.objects.link(cam_obj)

if root_dv and cam_obj:
    # Bo sat vi tri frame 1 cua DV_01
    boat_pos = root_dv.matrix_world.translation
    print('Boat position at frame 1:', boat_pos)
    
    # Dat camera goc 3/4 phia truoc ben man trai cua thuyen:
    # Thuyen chay ve huong +Y. Mui thuyen o +Y, duoi thuyen o -Y.
    # Dat camera o phia truoc mui thuyen lech sang trai (X am hon, Y duong hon boat_pos.y)
    # De nhin thay ro ca thuyen, mui thuyen, cac tay cheo, va vien chi huy o duoi thuyen!
    cam_obj.location = (boat_pos.x - 6.5, boat_pos.y + 7.5, boat_pos.z + 3.2)
    
    # Nham thang vao tam than thuyen
    target = mathutils.Vector((boat_pos.x, boat_pos.y, boat_pos.z + 0.8))
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = 35
    
    scene.camera = cam_obj
    scene.render.filepath = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_goc_nghieng_thuy_thu_ta.png'
    bpy.ops.render.render(write_still=True)
    print('SUCCESS_RENDER_HERO_3_4')
    
    # Tra lai camera chinh
    cam_main = bpy.data.objects.get('Camera_ChienTruong_Headon')
    if cam_main:
        scene.camera = cam_main
