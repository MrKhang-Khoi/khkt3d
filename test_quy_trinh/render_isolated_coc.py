import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/build_coc_log.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== CÔ LẬP VÀ RENDER CHUẨN XÁC MÔ HÌNH CỌC BẠCH ĐẰNG 938 ===\n")

try:
    # 1. TẮT ẨN TẤT CẢ CÁC COLLECTION KHÁC ĐỂ TRÁNH LẪN LỘN
    target_col_name = "Export_Coc_BachDang_Master"
    target_col = bpy.data.collections.get(target_col_name)
    if not target_col:
        raise Exception(f"Không tìm thấy collection {target_col_name}")

    # Ẩn tất cả collection khác khỏi render
    def set_col_render_exclude(col, exclude=True):
        for c in bpy.context.view_layer.layer_collection.children:
            if c.name == target_col_name:
                c.exclude = False
                c.hide_viewport = False
            else:
                c.exclude = exclude

    set_col_render_exclude(target_col, exclude=True)

    # 2. THÊM ĐÈN CHIẾU SÁNG TRỰC DIỆN VÀO CỌC
    light_name = "Light_Coc_Key"
    old_light = bpy.data.objects.get(light_name)
    if old_light:
        bpy.data.objects.remove(old_light, do_unlink=True)
        
    light_data = bpy.data.lights.new(name=light_name, type='SUN')
    light_data.energy = 3.5
    light_data.color = (1.0, 0.95, 0.88)
    light_obj = bpy.data.objects.new(light_name, light_data)
    target_col.objects.link(light_obj)
    light_obj.location = Vector((-2.0, -3.0, 4.0))
    light_obj.rotation_euler = Euler((math.radians(45.0), math.radians(15.0), math.radians(-30.0)))

    # Đèn phụ fill light màu xanh nước sông
    light_fill_name = "Light_Coc_Fill"
    old_fill = bpy.data.objects.get(light_fill_name)
    if old_fill:
        bpy.data.objects.remove(old_fill, do_unlink=True)
    fill_data = bpy.data.lights.new(name=light_fill_name, type='POINT')
    fill_data.energy = 80.0
    fill_data.color = (0.3, 0.6, 0.8)
    fill_obj = bpy.data.objects.new(light_fill_name, fill_data)
    target_col.objects.link(fill_obj)
    fill_obj.location = Vector((2.5, 2.0, 2.0))

    # 3. HÀM TẠO CAMERA VÀ RENDER CHUẨN
    def render_coc_view(cam_name, cam_pos, look_target, filename, lens=50.0):
        cam_obj = bpy.data.objects.get(cam_name)
        if not cam_obj:
            cam_data = bpy.data.cameras.new(cam_name)
            cam_obj = bpy.data.objects.new(cam_name, cam_data)
            target_col.objects.link(cam_obj)
            
        cam_obj.location = cam_pos
        look_dir = look_target - cam_pos
        rot_quat = look_dir.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_obj.data.lens = lens
        
        bpy.context.scene.camera = cam_obj
        bpy.context.view_layer.update()
        
        bpy.context.scene.render.resolution_x = 1280
        bpy.context.scene.render.resolution_y = 720
        out_path = os.path.join(r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh', filename)
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        
        # Copy sang thư mục artifact
        artifact_path = os.path.join(r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c', filename)
        import shutil
        shutil.copyfile(out_path, artifact_path)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Render xong {filename} -> {out_path}\n")

    # 1. Side View trực giao: Nhìn thẳng trục Y vào mặt phẳng cọc nghiêng X (đúng góc bản phác thảo 2D)
    render_coc_view("Camera_Coc_SideView", Vector((0.45, -4.2, 0.6)), Vector((0.45, 0.0, 0.6)), "anh_coc_goc_nhin_sideview.png", lens=48.0)
    
    # 2. Cận cảnh đầu bịt sắt 4 cạnh sắc nhọn (Close-up Iron Cap)
    render_coc_view("Camera_Coc_DauSat", Vector((0.65, -1.1, 1.7)), Vector((0.95, 0.0, 1.6)), "anh_coc_cancanh_dau_sat.png", lens=75.0)
    
    # 3. Cận cảnh gốc cọc cắm bùn sét (Close-up Sediment Anchor)
    render_coc_view("Camera_Coc_GocCam", Vector((-0.6, -1.8, 0.3)), Vector((0.15, 0.0, -0.2)), "anh_coc_cancanh_goc_cam_bun.png", lens=65.0)
    
    # 4. Toàn cảnh 3D phối cảnh bãi cọc nhô lên mặt nước sông Bạch Đằng
    render_coc_view("Camera_Coc_ToanCanh", Vector((-2.6, -3.2, 2.4)), Vector((0.5, 0.0, 0.6)), "anh_bai_coc_toan_canh_ngam_nuoc.png", lens=38.0)

    # 4. BẬT LẠI HIỂN THỊ CÁC COLLECTION CHO SCENE
    for c in bpy.context.view_layer.layer_collection.children:
        c.exclude = False

    print("HOÀN THÀNH RENDER 4 GÓC NHÌN CỌC BẠCH ĐẰNG 938 CHUẨN XÁC 100%!")

except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"LỖI: {traceback.format_exc()}\n")
    print("LỖI:", e)
