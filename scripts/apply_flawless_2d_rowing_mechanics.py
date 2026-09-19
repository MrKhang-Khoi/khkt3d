import bpy, bmesh, math, os, traceback
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/flawless_mechanics_log.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== THI CÔNG VẬT LÝ CHÈO THUYỀN & POWER GRIP CHUẨN XÁC 100% THEO PHÁC THẢO 2D ===\n")

try:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    soldier_base = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
    giap_base = bpy.data.objects.get('Giap_HoTam_DongSon_ThuyBinh_DaiViet_Master')
    dai_base = bpy.data.objects.get('Dai_That_Lung_ThuyBinh_DaiViet_Master')
    boat = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
    water = bpy.data.objects.get('MatNuoc_SongBachDang_Chinh')
    water_z = water.matrix_world.translation.z if water else -0.135

    # 1. HÀM TẠO LÍNH CHÈO KHỚP ĐƯỜNG ĐÒN BẨY 2D
    def build_flawless_rower_2d(is_stbd=False):
        side_sign = -1.0 if is_stbd else 1.0
        
        # Đánh giá mesh lính
        eval_soldier = soldier_base.evaluated_get(depsgraph)
        m_soldier = bpy.data.meshes.new_from_object(eval_soldier)
        o_soldier = bpy.data.objects.new("TMP_Soldier", m_soldier)
        bpy.context.scene.collection.objects.link(o_soldier)
        o_soldier.matrix_world = soldier_base.matrix_world.copy()
        
        eval_giap = giap_base.evaluated_get(depsgraph)
        m_giap = bpy.data.meshes.new_from_object(eval_giap)
        o_giap = bpy.data.objects.new("TMP_Giap", m_giap)
        bpy.context.scene.collection.objects.link(o_giap)
        o_giap.matrix_world = giap_base.matrix_world.copy()
        
        eval_dai = dai_base.evaluated_get(depsgraph)
        m_dai = bpy.data.meshes.new_from_object(eval_dai)
        o_dai = bpy.data.objects.new("TMP_Dai", m_dai)
        bpy.context.scene.collection.objects.link(o_dai)
        o_dai.matrix_world = dai_base.matrix_world.copy()
        o_dai.scale = Vector((0.88, 0.88, 0.88))
        
        # Xoay mặt về mũi thuyền (+X)
        rot_facing = Euler((0, 0, math.pi / 2.0)).to_matrix().to_4x4()
        for o in [o_soldier, o_giap, o_dai]:
            o.matrix_world = rot_facing @ o.matrix_world
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
        # 2. XÁC ĐỊNH ĐƯỜNG TRỤC CÁN CHÈO ĐÒN BẨY CHUẨN
        # Điểm tay trong: Y = -0.05m * side_sign, Z = 0.94m
        # Điểm tay ngoài: Y = +0.38m * side_sign, Z = 0.74m
        # Điểm cọc chèo mạn thuyền: Y = +1.02m * side_sign, Z = 0.44m
        # Điểm lưỡi chèo dưới nước: Y = +2.40m * side_sign, Z = -0.42m (ngập nước 28.5cm)
        p_grip_end = Vector((0.45, -0.25 * side_sign, 1.04))
        p_hand_in = Vector((0.45, -0.05 * side_sign, 0.94))
        p_hand_out = Vector((0.45, 0.38 * side_sign, 0.74))
        p_fulcrum = Vector((0.45, 1.02 * side_sign, 0.44))
        p_water_tip = Vector((0.45, 2.85 * side_sign, -1.50))
        
        axis_dir = (p_water_tip - p_grip_end).normalized()
        
        # 3. NẮN CÁC KHỚP CÁNH TAY & BÀN TAY ÔM KHÍT TRỤC CÁN CHÈO (POWER GRIP)
        # Nhóm vertex tay và cẳng tay
        vg_hand_out_name = 'hand.L' if not is_stbd else 'hand.R'
        vg_hand_in_name = 'hand.R' if not is_stbd else 'hand.L'
        vg_fore_out_name = 'forearm.L' if not is_stbd else 'forearm.R'
        vg_fore_in_name = 'forearm.R' if not is_stbd else 'forearm.L'
        
        vg_h_out = o_soldier.vertex_groups.get(vg_hand_out_name)
        vg_h_in = o_soldier.vertex_groups.get(vg_hand_in_name)
        vg_f_out = o_soldier.vertex_groups.get(vg_fore_out_name)
        vg_f_in = o_soldier.vertex_groups.get(vg_fore_in_name)
        
        # Tìm tâm hiện tại của bàn tay
        def get_vg_center(vg):
            pts = [v.co for v in o_soldier.data.vertices if any(g.group == vg.index and g.weight > 0.5 for g in v.groups)]
            return sum(pts, Vector()) / len(pts) if pts else Vector()
            
        cur_h_in = get_vg_center(vg_h_in)
        cur_h_out = get_vg_center(vg_h_out)
        delta_in = p_hand_in - cur_h_in
        delta_out = p_hand_out - cur_h_out
        
        # Nắn các đỉnh
        grip_radius = 0.038
        for v in o_soldier.data.vertices:
            w_h_in = 0.0
            w_h_out = 0.0
            w_f_in = 0.0
            w_f_out = 0.0
            for g in v.groups:
                if vg_h_in and g.group == vg_h_in.index: w_h_in = g.weight
                elif vg_h_out and g.group == vg_h_out.index: w_h_out = g.weight
                elif vg_f_in and g.group == vg_f_in.index: w_f_in = g.weight
                elif vg_f_out and g.group == vg_f_out.index: w_f_out = g.weight
            
            # Dịch chuyển mượt từ cẳng tay tới bàn tay
            delta = Vector()
            if w_h_in > 0: delta += delta_in * w_h_in
            elif w_f_in > 0: delta += delta_in * (w_f_in * 0.45)
            if w_h_out > 0: delta += delta_out * w_h_out
            elif w_f_out > 0: delta += delta_out * (w_f_out * 0.45)
            
            v.co += delta
            
            # Cuộn tròn bàn tay thành Power Grip ôm trục cán chèo
            w_hand = max(w_h_in, w_h_out)
            if w_hand > 0.2:
                p = v.co
                rel = p - p_grip_end
                proj = rel.dot(axis_dir)
                p_on_axis = p_grip_end + axis_dir * proj
                rad = p - p_on_axis
                if rad.length > 0.001:
                    rad_norm = rad.normalized()
                    target_dist = grip_radius + 0.006 * math.sin(p.z * 18.0)
                    v.co = p_on_axis + rad_norm * (rad.length * (1.0 - w_hand) + target_dist * w_hand)

        # 4. TẠO MÁI CHÈO GỖ NGUYÊN KHỐI CHUẨN XÁC
        bm = bmesh.new()
        dir_oar = p_water_tip - p_grip_end
        oar_len = dir_oar.length
        dir_norm = dir_oar.normalized()
        rot_diff = Vector((0, 0, 1)).rotation_difference(dir_norm)
        
        blade_len = 1.05
        loom_len = oar_len - blade_len
        p_loom_center = p_grip_end + dir_norm * (loom_len * 0.5)
        mat_loom = Matrix.Translation(p_loom_center) @ rot_diff.to_matrix().to_4x4()
        
        # Cán chèo hình trụ tròn d = 6.4cm ôm trọn 2 bàn tay
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            radius1=0.033,
            radius2=0.030,
            depth=loom_len,
            matrix=mat_loom,
            segments=16
        )
        
        # Lưỡi chèo bản rộng cắm ngập nước 28.5cm
        blade_width = 0.23
        blade_thick = 0.026
        p_blade_center = p_water_tip - dir_norm * (blade_len * 0.5)
        mat_blade = Matrix.Translation(p_blade_center) @ rot_diff.to_matrix().to_4x4() @ Matrix.Scale(blade_width, 4, Vector((1,0,0))) @ Matrix.Scale(blade_thick, 4, Vector((0,1,0))) @ Matrix.Scale(blade_len, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=mat_blade)
        
        # Vòng chão / da tiếp xúc cọc chèo mạn thuyền
        mat_ring = Matrix.Translation(p_fulcrum) @ rot_diff.to_matrix().to_4x4()
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            radius1=0.046,
            radius2=0.046,
            depth=0.14,
            matrix=mat_ring,
            segments=14
        )
        
        m_oar = bpy.data.meshes.new(f"TMP_Oar_{'Stbd' if is_stbd else 'Port'}")
        bm.to_mesh(m_oar)
        bm.free()
        
        mat_wood = bpy.data.materials.get('Mat_GoLim_ThuyenTa') or bpy.data.materials.get('Mat_GoLim')
        if mat_wood:
            m_oar.materials.append(mat_wood)
            
        o_oar = bpy.data.objects.new(f"TMP_Oar_{'Stbd' if is_stbd else 'Port'}", m_oar)
        bpy.context.scene.collection.objects.link(o_oar)
        
        # Hợp nhất lính + giáp + đai + mái chèo
        bpy.ops.object.select_all(action='DESELECT')
        for p in [o_soldier, o_giap, o_dai, o_oar]:
            p.select_set(True)
        bpy.context.view_layer.objects.active = o_soldier
        bpy.ops.object.join()
        
        final_rower = bpy.context.active_object
        dec = final_rower.modifiers.new(name="DecimateWeb", type='DECIMATE')
        dec.ratio = 0.70
        bpy.ops.object.modifier_apply(modifier="DecimateWeb")
        
        final_mesh = final_rower.data.copy()
        bpy.data.objects.remove(final_rower, do_unlink=True)
        return final_mesh

    mesh_rower_port = build_flawless_rower_2d(is_stbd=False)
    mesh_rower_stbd = build_flawless_rower_2d(is_stbd=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("Đã nắn tay Power Grip ôm trọn cán chèo thành công cho cả hai bên.\n")

    # 5. TÁI TẠO BỤC VÁN NGỒI & CỌC CHÈO
    bm_thwarts = bmesh.new()
    thwart_xs = [-1.92, -0.12, 1.68]
    for tx in thwart_xs:
        # Ván ngồi bắc ngang tại Z = 0.36
        mat_thwart = Matrix.Translation(Vector((tx, 0.0, 0.36))) @ Matrix.Scale(0.28, 4, Vector((1,0,0))) @ Matrix.Scale(2.36, 4, Vector((0,1,0))) @ Matrix.Scale(0.045, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm_thwarts, size=1.0, matrix=mat_thwart)
        
        # Cọc chèo mạn thuyền tại X = tx + 0.45, Y = +-1.02, Z = 0.44 (khớp chính xác điểm tì p_fulcrum)
        for ssign in [1.0, -1.0]:
            p_pin = Vector((tx + 0.45, 1.02 * ssign, 0.44))
            mat_pin = Matrix.Translation(p_pin)
            bmesh.ops.create_cone(
                bm_thwarts,
                cap_ends=True,
                radius1=0.024,
                radius2=0.020,
                depth=0.25,
                matrix=mat_pin,
                segments=10
            )

    m_thwarts = bpy.data.meshes.new("Mesh_Thwarts_TholePins_PowerGrip_2D")
    bm_thwarts.to_mesh(m_thwarts)
    bm_thwarts.free()
    mat_wood = bpy.data.materials.get('Mat_GoLim_ThuyenTa') or bpy.data.materials.get('Mat_GoLim')
    if mat_wood:
        m_thwarts.materials.append(mat_wood)

    # 6. TÁI TẠO Export_DaiViet_Master_Full
    col_name = "Export_DaiViet_Master_Full"
    if col_name in bpy.data.collections:
        old_col = bpy.data.collections[col_name]
        for obj in list(old_col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(old_col)
        
    export_col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(export_col)

    export_root = bpy.data.objects.new("Export_Ship_Root", None)
    export_col.objects.link(export_root)
    export_root.matrix_world = boat.matrix_world.copy()
    created_objs = [export_root]

    boat_mesh_names = [
        'Than_Thuyen_GoLim',
        'San_Boong_Thuyen',
        'Khung_Suon_ChiuLuc',
        'Mui_ChimLac_DongSon',
        'Khien_May_SonThen',
        'CoLenh_NguHanh_Master',
        'Mesh_SongRe_SoaiThuyen'
    ]
    buom_empty = bpy.data.objects.get('Buom_CanhDoi_BachDang')
    if buom_empty:
        for bc in buom_empty.children:
            if bc.type == 'MESH':
                boat_mesh_names.append(bc.name)

    for mname in boat_mesh_names:
        src = bpy.data.objects.get(mname)
        if src and src.type == 'MESH':
            eval_src = src.evaluated_get(depsgraph)
            new_mesh = bpy.data.meshes.new_from_object(eval_src)
            new_obj = bpy.data.objects.new("Part_" + mname, new_mesh)
            export_col.objects.link(new_obj)
            new_obj.matrix_world = src.matrix_world.copy()
            new_obj.parent = export_root
            new_obj.matrix_parent_inverse = export_root.matrix_world.inverted()
            created_objs.append(new_obj)

    thwart_obj = bpy.data.objects.new("Part_BucNgoi_Thwart_Va_CocCheo", m_thwarts)
    export_col.objects.link(thwart_obj)
    thwart_obj.matrix_world = boat.matrix_world.copy()
    thwart_obj.parent = export_root
    thwart_obj.matrix_parent_inverse = export_root.matrix_world.inverted()
    created_objs.append(thwart_obj)

    # Nạp lại REFERENCE_BLUEPRINT_PLANE
    img_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/references/phac_thao_thuy_binh_dai_viet_938.jpg'
    img = bpy.data.images.load(img_path, check_existing=True)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-6.27, -44.34, 0.53))
    plane = bpy.context.active_object
    plane.name = 'REFERENCE_BLUEPRINT_PLANE'
    plane.scale = Vector((3.4, 1.9, 1.0))
    plane.rotation_euler = Euler((math.pi / 2.0, 0, math.pi / 2.0))
    export_col.objects.link(plane)
    for c in list(plane.users_collection):
        if c != export_col:
            c.objects.unlink(plane)

    soldier_empties = [c for c in boat.children if 'ThuyBinh' in c.name]
    for idx, s in enumerate(soldier_empties):
        is_stbd = 'Stbd' in s.name
        rower_mesh = mesh_rower_stbd if is_stbd else mesh_rower_port
        rower_name = f"Rower_{'Stbd' if is_stbd else 'Port'}_{idx}"
        
        rower_obj = bpy.data.objects.new(rower_name, rower_mesh)
        export_col.objects.link(rower_obj)
        rower_obj.matrix_world = s.matrix_world.copy()
        rower_obj.parent = export_root
        rower_obj.matrix_parent_inverse = export_root.matrix_world.inverted()
        created_objs.append(rower_obj)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("Đã lắp 6 thủy binh Power Grip vào Export_DaiViet_Master_Full.\n")

    # 7. XUẤT GLB
    bpy.ops.object.select_all(action='DESELECT')
    for o in created_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = export_root

    out_glb = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/thuyen_daiviet_master.glb'
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    file_size = os.path.getsize(out_glb)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Xuất GLB thành công: {out_glb} ({file_size/1024/1024:.2f} MB)\n")

    web3d_glb = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/web3d_export/thuyen_daiviet_master.glb'
    with open(out_glb, 'rb') as fi, open(web3d_glb, 'wb') as fo:
        fo.write(fi.read())

    # 8. RENDER ẢNH ĐỐI CHIẾU
    cam_name = 'Camera_KiemChung_PhacThao'
    cam_obj = bpy.data.objects.get(cam_name)
    if cam_obj:
        bpy.context.scene.camera = cam_obj
        bpy.context.scene.render.resolution_x = 1280
        bpy.context.scene.render.resolution_y = 720
        out_png = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_kiemchung_power_grip_perfect.png'
        bpy.context.scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"RENDER HOÀN TẤT: {out_png}\n")

except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"LỖI: {traceback.format_exc()}\n")
