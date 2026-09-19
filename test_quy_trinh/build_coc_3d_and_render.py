import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/build_coc_log.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== BẮT ĐẦU MÔ HÌNH HÓA CỌC BẠCH ĐẰNG 938 THEO BẢN PHÁC THẢO 2D ===\n")

try:
    # 1. TẠO COLLECTION RIÊNG
    col_name = "Export_Coc_BachDang_Master"
    if col_name in bpy.data.collections:
        old_col = bpy.data.collections[col_name]
        for o in list(old_col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old_col)
        
    coc_col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(coc_col)
    
    # 2. NẠP BLUEPRINT REFERENCE PLANE (GATE 1)
    sketch_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/references/phac_thao_coc_bach_dang_2d.png'
    img = bpy.data.images.load(sketch_path, check_existing=True)
    
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 3.5, 1.2))
    bp_plane = bpy.context.active_object
    bp_plane.name = "REFERENCE_BLUEPRINT_PLANE_COC"
    bp_plane.scale = Vector((4.8, 2.7, 1.0))
    bp_plane.rotation_euler = Euler((math.pi / 2.0, 0, 0))
    
    # Vật liệu bán trong suốt
    mat_bp = bpy.data.materials.new(name="Mat_Blueprint_Coc")
    mat_bp.use_nodes = True
    nodes = mat_bp.node_tree.nodes
    links = mat_bp.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    tex_node = nodes.new("ShaderNodeTexImage")
    tex_node.image = img
    links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat_bp.blend_method = 'BLEND'
    bp_plane.data.materials.append(mat_bp)
    
    coc_col.objects.link(bp_plane)
    for c in list(bp_plane.users_collection):
        if c != coc_col: c.objects.unlink(bp_plane)

    # 3. TẠO THÂN GỖ LIM CỌC BẠCH ĐẰNG (GATE 2)
    # Cọc dài 2.80m, đường kính gốc 28cm (R=0.14), ngọn 22cm (R=0.11)
    # Nghiêng 20 độ theo trục X (đón hướng nước chảy và tàu giặc)
    angle_rad = math.radians(20.0) # 20 độ nghiêng
    tilt_rot = Euler((0, angle_rad, 0)).to_matrix().to_4x4()
    
    # Chiều dài thân gỗ = 2.40m, chiều dài đầu sắt = 0.40m -> Tổng = 2.80m
    wood_len = 2.40
    iron_len = 0.40
    
    # Tâm thân gỗ cắm từ Z = -1.0m (đáy bùn) tới Z = 1.4m
    # Với cọc nghiêng 20 độ:
    dir_coc = Vector((math.sin(angle_rad), 0, math.cos(angle_rad))).normalized()
    p_goc = Vector((0, 0, -1.0)) # Gốc cắm sâu trong bùn 1.0m
    p_junction = p_goc + dir_coc * wood_len # Điểm nối giữa gỗ và sắt
    p_tip = p_junction + dir_coc * iron_len # Đỉnh nhọn mũi sắt
    
    # Dựng thân gỗ cọc
    bm_wood = bmesh.new()
    p_wood_center = p_goc + dir_coc * (wood_len * 0.5)
    rot_diff = Vector((0, 0, 1)).rotation_difference(dir_coc)
    mat_wood_trans = Matrix.Translation(p_wood_center) @ rot_diff.to_matrix().to_4x4()
    
    bmesh.ops.create_cone(
        bm_wood,
        cap_ends=True,
        radius1=0.11, # Đầu ngọn gỗ
        radius2=0.14, # Đáy gốc gỗ
        depth=wood_len,
        matrix=mat_wood_trans,
        segments=24
    )
    
    # Thêm độ gồ ghề thớ nứt tự nhiên
    for v in bm_wood.verts:
        # Độ gồ ghề ngẫu nhiên theo bán kính
        noise = 0.008 * math.sin(v.co.z * 15.0) * math.cos(v.co.x * 20.0)
        v.co += v.normal * noise
        
    m_wood = bpy.data.meshes.new("Mesh_Than_Coc_GoLim_938")
    bm_wood.to_mesh(m_wood)
    bm_wood.free()
    
    # Vật liệu PBR gỗ lim già ngâm nước mặn
    mat_wood = bpy.data.materials.new("Mat_GoLim_Coc_938")
    mat_wood.use_nodes = True
    w_nodes = mat_wood.node_tree.nodes
    w_bsdf = w_nodes.get("Principled BSDF")
    w_bsdf.inputs["Base Color"].default_value = (0.16, 0.11, 0.07, 1.0) # Nâu đen sẫm thớ già
    w_bsdf.inputs["Roughness"].default_value = 0.85
    m_wood.materials.append(mat_wood)
    
    obj_wood = bpy.data.objects.new("Coc_Than_GoLim_938", m_wood)
    coc_col.objects.link(obj_wood)

    # 4. TẠO ĐẦU BỊT SẮT 4 CẠNH (IRON CAP 4-FACETS) & ĐINH TÁN
    bm_iron = bmesh.new()
    p_iron_center = p_junction + dir_coc * (iron_len * 0.5)
    mat_iron_trans = Matrix.Translation(p_junction) @ rot_diff.to_matrix().to_4x4()
    
    # Mũi nhọn 4 cạnh hình kim tự tháp (pyramid 4-facet) dài 40cm, đáy rộng 22cm x 22cm
    bmesh.ops.create_cone(
        bm_iron,
        cap_ends=True,
        radius1=0.002, # Đỉnh nhọn sắc bén
        radius2=0.125, # Đáy bọc khít thân gỗ
        depth=iron_len,
        matrix=Matrix.Translation(p_junction + dir_coc * (iron_len * 0.5)) @ rot_diff.to_matrix().to_4x4(),
        segments=4 # Đúng 4 cạnh sắc bén
    )
    
    # Đai sắt ôm chân mũi sắt
    mat_band = Matrix.Translation(p_junction + dir_coc * 0.03) @ rot_diff.to_matrix().to_4x4()
    bmesh.ops.create_cone(
        bm_iron,
        cap_ends=True,
        radius1=0.13,
        radius2=0.13,
        depth=0.08,
        matrix=mat_band,
        segments=16
    )
    
    # 4 đinh tán sắt chốt xuyên
    for i in range(4):
        ang = i * (math.pi / 2.0)
        p_rivet = p_junction + dir_coc * 0.03 + Vector((math.cos(ang)*0.135, math.sin(ang)*0.135, 0))
        mat_rivet = Matrix.Translation(p_rivet)
        bmesh.ops.create_icosphere(bm_iron, subdivisions=2, radius=0.016, matrix=mat_rivet)
        
    m_iron = bpy.data.meshes.new("Mesh_Dau_Bit_Sat_938")
    bm_iron.to_mesh(m_iron)
    bm_iron.free()
    
    # Vật liệu PBR sắt rèn rỉ sét
    mat_iron = bpy.data.materials.new("Mat_DauBitSat_Ren_938")
    mat_iron.use_nodes = True
    i_nodes = mat_iron.node_tree.nodes
    i_bsdf = i_nodes.get("Principled BSDF")
    i_bsdf.inputs["Base Color"].default_value = (0.22, 0.20, 0.18, 1.0) # Xám đen ánh kim
    i_bsdf.inputs["Metallic"].default_value = 0.90
    i_bsdf.inputs["Roughness"].default_value = 0.50
    m_iron.materials.append(mat_iron)
    
    obj_iron = bpy.data.objects.new("Coc_Dau_Bit_Sat_938", m_iron)
    coc_col.objects.link(obj_iron)

    # 5. TẠO TẦNG BÙN SÉT ĐÁY SÔNG & MẶT NƯỚC BẠCH ĐẰNG (GATE 3)
    # Đáy bùn tại Z = 0.0m (cọc cắm sâu từ 0.0m xuống -1.0m)
    bm_ground = bmesh.new()
    bmesh.ops.create_cube(
        bm_ground,
        size=1.0,
        matrix=Matrix.Translation(Vector((0, 0, -0.6))) @ Matrix.Scale(6.0, 4, Vector((1,0,0))) @ Matrix.Scale(6.0, 4, Vector((0,1,0))) @ Matrix.Scale(1.2, 4, Vector((0,0,1)))
    )
    m_ground = bpy.data.meshes.new("Mesh_Tang_Bun_Set_DaySong")
    bm_ground.to_mesh(m_ground)
    bm_ground.free()
    
    mat_ground = bpy.data.materials.new("Mat_BunSet_DaySong")
    mat_ground.use_nodes = True
    g_bsdf = mat_ground.node_tree.nodes.get("Principled BSDF")
    g_bsdf.inputs["Base Color"].default_value = (0.18, 0.16, 0.13, 1.0) # Bùn sét nâu xám đậm
    g_bsdf.inputs["Roughness"].default_value = 0.95
    m_ground.materials.append(mat_ground)
    
    obj_ground = bpy.data.objects.new("DiaHinh_TangBun_DaySong", m_ground)
    coc_col.objects.link(obj_ground)

    # Mặt nước triều rút tại Z = 1.25m (để đầu cọc sắt nhô lên khỏi mặt nước 35cm)
    bm_water = bmesh.new()
    bmesh.ops.create_cube(
        bm_water,
        size=1.0,
        matrix=Matrix.Translation(Vector((0, 0, 0.6))) @ Matrix.Scale(5.8, 4, Vector((1,0,0))) @ Matrix.Scale(5.8, 4, Vector((0,1,0))) @ Matrix.Scale(1.2, 4, Vector((0,0,1)))
    )
    m_water = bpy.data.meshes.new("Mesh_Nuoc_Song_TrieuRut")
    bm_water.to_mesh(m_water)
    bm_water.free()
    
    mat_water = bpy.data.materials.new("Mat_NuocSong_TrongSuot")
    mat_water.use_nodes = True
    w_bsdf = mat_water.node_tree.nodes.get("Principled BSDF")
    w_bsdf.inputs["Base Color"].default_value = (0.15, 0.35, 0.45, 0.45) # Nước sông Bạch Đằng xanh phù sa
    w_bsdf.inputs["Roughness"].default_value = 0.15
    w_bsdf.inputs["Transmission Weight"].default_value = 0.85
    mat_water.blend_method = 'BLEND'
    m_water.materials.append(mat_water)
    
    obj_water = bpy.data.objects.new("MatNuoc_Song_TrieuRut", m_water)
    coc_col.objects.link(obj_water)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("Đã dựng hoàn chỉnh Cọc gỗ, Đầu bịt sắt, Tầng bùn đáy và Nước triều rút.\n")

    # 6. THIẾT LẬP CAMERA RENDER 4 GÓC NHÌN CHUẨN XÁC
    def render_view(cam_pos, look_target, filename, lens=50.0):
        cam_data = bpy.data.cameras.new("Cam_Temp")
        cam_obj = bpy.data.objects.new("Cam_Temp", cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
        
        cam_obj.location = cam_pos
        look_dir = look_target - cam_pos
        rot_quat = look_dir.to_track_quat('-Z', 'Y')
        cam_obj.rotation_euler = rot_quat.to_euler()
        cam_data.lens = lens
        
        bpy.context.scene.camera = cam_obj
        bpy.context.scene.render.resolution_x = 1280
        bpy.context.scene.render.resolution_y = 720
        out_path = os.path.join(r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh', filename)
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        
        # Copy sang thư mục artifact
        artifact_path = os.path.join(r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c', filename)
        import shutil
        shutil.copyfile(out_path, artifact_path)
        
        bpy.data.objects.remove(cam_obj, do_unlink=True)
        bpy.data.cameras.remove(cam_data)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Render xong {filename} -> {out_path}\n")

    # Góc 1: Side View trực giao (Đối chiếu phác thảo 2D)
    render_view(Vector((0.0, -4.5, 0.8)), Vector((0.4, 0.0, 0.6)), "anh_coc_goc_nhin_sideview.png", lens=45.0)
    
    # Góc 2: Cận cảnh đầu bịt sắt (Iron Cap Closeup)
    render_view(Vector((0.2, -1.2, 1.8)), Vector((0.95, 0.0, 1.6)), "anh_coc_cancanh_dau_sat.png", lens=70.0)
    
    # Góc 3: Cận cảnh gốc cọc cắm bùn (Sediment Anchor Closeup)
    render_view(Vector((-0.8, -1.8, 0.3)), Vector((0.1, 0.0, -0.2)), "anh_coc_cancanh_goc_cam_bun.png", lens=60.0)
    
    # Góc 4: Toàn cảnh phối cảnh 3D bãi cọc ngầm dưới nước (Perspective View)
    render_view(Vector((-2.8, -3.2, 2.5)), Vector((0.5, 0.0, 0.5)), "anh_bai_coc_toan_canh_ngam_nuoc.png", lens=35.0)

    # 7. XUẤT FILE GLB MÔ HÌNH CỌC
    bpy.ops.object.select_all(action='DESELECT')
    for o in [obj_wood, obj_iron, obj_ground, obj_water]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obj_wood
    
    out_glb = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/coc_bach_dang_938.glb'
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Xuất GLB thành công: {out_glb} ({os.path.getsize(out_glb)/1024:.1f} KB)\n")

    print("HOÀN TẤT BƯỚC 3: MÔ HÌNH HÓA 3D & RENDER 4 GÓC NHÌN THÀNH CÔNG!")

except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"LỖI: {traceback.format_exc()}\n")
    print("LỖI:", e)
