import bpy, bmesh, math, os, sys, traceback
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/build_coc_log.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== TẠO SCENE RIÊNG VÀ RENDER 4 GÓC NHÌN CỌC BẠCH ĐẰNG 938 ===\n")

try:
    # 1. TẠO SCENE MỚI SẠCH SẼ
    scene_name = "Scene_Coc_BachDang_938"
    scene = bpy.data.scenes.get(scene_name)
    if not scene:
        scene = bpy.data.scenes.new(scene_name)
    
    bpy.context.window.scene = scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720

    # Xóa hết objects cũ trong scene mới nếu có
    for o in list(scene.collection.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # 2. LẤY CÁC OBJECT TỪ Export_Coc_BachDang_Master
    src_col = bpy.data.collections.get("Export_Coc_BachDang_Master")
    for obj in src_col.objects:
        if obj.name not in scene.collection.objects:
            scene.collection.objects.link(obj)

    # Đảm bảo tắt ẩn khối nước nếu làm tối hình
    mat_water_obj = bpy.data.objects.get("MatNuoc_Song_TrieuRut")
    if mat_water_obj:
        # Làm nước trong suốt và mỏng hơn
        mat_w = mat_water_obj.data.materials[0]
        if mat_w and mat_w.use_nodes:
            bsdf = mat_w.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Alpha"].default_value = 0.35
                bsdf.inputs["Roughness"].default_value = 0.1

    # 3. THÊM ÁNH SÁNG MẶT TRỜI & ÁNH SÁNG MÔI TRƯỜNG
    sun_name = "Sun_Light_Coc_Scene"
    sun_obj = bpy.data.objects.get(sun_name)
    if not sun_obj:
        sun_data = bpy.data.lights.new(sun_name, 'SUN')
        sun_data.energy = 4.0
        sun_data.color = (1.0, 0.98, 0.92)
        sun_obj = bpy.data.objects.new(sun_name, sun_data)
        scene.collection.objects.link(sun_obj)
    sun_obj.location = Vector((-2.0, -4.0, 5.0))
    sun_obj.rotation_euler = Euler((math.radians(50.0), math.radians(20.0), math.radians(-35.0)))

    # Point light trợ sáng cho mũi sắt
    point_name = "Point_Light_MuiSat"
    point_obj = bpy.data.objects.get(point_name)
    if not point_obj:
        point_data = bpy.data.lights.new(point_name, 'POINT')
        point_data.energy = 120.0
        point_data.color = (0.9, 0.95, 1.0)
        point_obj = bpy.data.objects.new(point_name, point_data)
        scene.collection.objects.link(point_obj)
    point_obj.location = Vector((1.2, -1.0, 2.2))

    # 4. HÀM TẠO CAMERA VÀ RENDER TỪ SCENE MỚI
    def do_render(cam_name, pos, target, filename, lens=50.0):
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(cam_name)
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            scene.collection.objects.link(cam_obj)
            
        cam_obj.location = pos
        look_dir = target - pos
        rot_quat = look_dir.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_obj.data.lens = lens
        
        scene.camera = cam_obj
        
        out_path = os.path.join(r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh', filename)
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True, scene=scene.name)
        
        artifact_path = os.path.join(r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c', filename)
        import shutil
        shutil.copyfile(out_path, artifact_path)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Render xong {filename} -> {out_path}\n")

    # Góc 1: Side View trực giao đối chiếu bản phác thảo 2D
    # Cọc nghiêng quanh X, nhìn từ hướng -Y thẳng vào cọc
    do_render("Cam_Coc_SideView_Final", Vector((0.45, -4.5, 0.6)), Vector((0.45, 0.0, 0.6)), "anh_coc_goc_nhin_sideview.png", lens=48.0)
    
    # Góc 2: Cận cảnh đầu bịt sắt 4 cạnh (Iron Cap Closeup)
    do_render("Cam_Coc_DauSat_Final", Vector((0.7, -1.2, 1.8)), Vector((0.95, 0.0, 1.6)), "anh_coc_cancanh_dau_sat.png", lens=70.0)
    
    # Góc 3: Cận cảnh gốc cọc cắm bùn (Sediment Anchor Closeup)
    do_render("Cam_Coc_GocCam_Final", Vector((-0.6, -1.8, 0.3)), Vector((0.15, 0.0, -0.2)), "anh_coc_cancanh_goc_cam_bun.png", lens=65.0)
    
    # Góc 4: Toàn cảnh phối cảnh bãi cọc nhô lên mặt nước sông Bạch Đằng
    do_render("Cam_Coc_ToanCanh_Final", Vector((-2.6, -3.2, 2.4)), Vector((0.5, 0.0, 0.6)), "anh_bai_coc_toan_canh_ngam_nuoc.png", lens=38.0)

    print("HOÀN THÀNH RENDER TỪ SCENE RIÊNG BIỆT THÀNH CÔNG!")

except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"LỖI: {traceback.format_exc()}\n")
    print("LỖI:", e)
