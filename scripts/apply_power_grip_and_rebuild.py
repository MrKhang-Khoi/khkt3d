import bpy, bmesh, math, os, traceback
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/rebuild_power_grip_log.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== BẮT ĐẦU TÁI TẠO POWER GRIP & VẬT LÝ CHÈO THUYỀN CHUẨN 2D ===\n")

try:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    soldier_base = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
    giap_base = bpy.data.objects.get('Giap_HoTam_DongSon_ThuyBinh_DaiViet_Master')
    dai_base = bpy.data.objects.get('Dai_That_Lung_ThuyBinh_DaiViet_Master')
    boat = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
    water = bpy.data.objects.get('MatNuoc_SongBachDang_Chinh')
    water_z = water.matrix_world.translation.z if water else -0.135

    # 1. Hàm nắn bàn tay thành Power Grip ôm khít quanh trục cán chèo
    def apply_power_grip(obj, p_inboard, p_outboard, is_stbd=False):
        # Trục cán chèo
        axis_dir = p_outboard - p_inboard
        axis_norm = axis_dir.normalized()
        grip_radius = 0.038 # Bán kính nắm đấm ôm cán chèo (đường kính cán ~ 6.5cm)
        
        vg_L = obj.vertex_groups.get('hand.L')
        vg_R = obj.vertex_groups.get('hand.R')
        
        # Với mạn Port: tay R ở p_inboard, tay L ở p_outboard
        # Với mạn Stbd: tay L ở p_inboard, tay R ở p_outboard
        vgroups = [vg_L, vg_R]
        for vg in vgroups:
            if not vg:
                continue
            for v in obj.data.vertices:
                w = 0.0
                for g in v.groups:
                    if g.group == vg.index:
                        w = g.weight
                        break
                if w > 0.2:
                    p = v.co
                    rel = p - p_inboard
                    proj_len = rel.dot(axis_norm)
                    p_on_axis = p_inboard + axis_norm * proj_len
                    radial = p - p_on_axis
                    dist = radial.length
                    if dist > 0.001:
                        radial_norm = radial.normalized()
                        # Cuộn tròn các ngón tay quanh trục
                        target_dist = grip_radius + 0.006 * math.sin(p.z * 18.0)
                        v.co = p_on_axis + radial_norm * (dist * (1.0 - w * 0.95) + target_dist * (w * 0.95))

    # 2. Xây dựng lính hoàn chỉnh cho từng mạn
    def build_rower_with_power_grip(is_stbd=False):
        side_sign = -1.0 if is_stbd else 1.0
        
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
            # Apply transform
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            
        # Vị trí hai bàn tay sau khi quay:
        # X = 0.45m (vươn tay ra trước)
        # Tay trong (gần tim thuyền): Y = -0.15m * side_sign, Z = 0.90m
        # Tay ngoài (gần mạn thuyền): Y = +0.28m * side_sign, Z = 0.86m
        # Cọc chèo mạn thuyền: Y = +1.02m * side_sign, Z = 0.78m
        # Đầu lưỡi chèo ngập nước: Y = +2.60m * side_sign, Z = -1.55m
        p_grip_end = Vector((0.45, -0.32 * side_sign, 0.92))
        p_hand_in = Vector((0.45, -0.15 * side_sign, 0.90))
        p_hand_out = Vector((0.45, 0.28 * side_sign, 0.86))
        p_fulcrum = Vector((0.45, 1.02 * side_sign, 0.78))
        z_water_target = -1.55 if not is_stbd else -1.50
        p_water_tip = Vector((0.45, 2.60 * side_sign, z_water_target))
        
        # Nắn tay lính vào cán chèo (Power Grip)
        apply_power_grip(o_soldier, p_hand_in, p_hand_out, is_stbd=is_stbd)
        
        # Dựng mái chèo gỗ lim nguyên khối
        dir_oar = p_water_tip - p_grip_end
        oar_len = dir_oar.length
        dir_norm = dir_oar.normalized()
        rot_diff = Vector((0, 0, 1)).rotation_difference(dir_norm)
        
        bm = bmesh.new()
        blade_len = 1.15
        loom_len = oar_len - blade_len
        p_loom_center = p_grip_end + dir_norm * (loom_len * 0.5)
        mat_loom = Matrix.Translation(p_loom_center) @ rot_diff.to_matrix().to_4x4()
        
        # Cán chèo hình trụ tròn d = 6.5cm
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            radius1=0.034,
            radius2=0.031,
            depth=loom_len,
            matrix=mat_loom,
            segments=16
        )
        
        # Lưỡi chèo bản rộng chìm dưới nước
        blade_width = 0.24
        blade_thick = 0.026
        p_blade_center = p_water_tip - dir_norm * (blade_len * 0.5)
        mat_blade = Matrix.Translation(p_blade_center) @ rot_diff.to_matrix().to_4x4() @ Matrix.Scale(blade_width, 4, Vector((1,0,0))) @ Matrix.Scale(blade_thick, 4, Vector((0,1,0))) @ Matrix.Scale(blade_len, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=mat_blade)
        
        # Vòng chão / da tì khít vào cọc chèo mạn thuyền
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

    mesh_rower_port = build_rower_with_power_grip(is_stbd=False)
    mesh_rower_stbd = build_rower_with_power_grip(is_stbd=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("Đã tạo xong mesh Power Grip cho cả hai mạn Tả/Hữu.\n")

    # 3. TÁI TẠO BỤC NGỒI & CỌC CHÈO
    bm_thwarts = bmesh.new()
    thwart_xs = [-1.92, -0.12, 1.68]
    for tx in thwart_xs:
        # Ván ngồi bắc ngang tại Z = 0.36
        mat_thwart = Matrix.Translation(Vector((tx, 0.0, 0.36))) @ Matrix.Scale(0.28, 4, Vector((1,0,0))) @ Matrix.Scale(2.36, 4, Vector((0,1,0))) @ Matrix.Scale(0.045, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm_thwarts, size=1.0, matrix=mat_thwart)
        
        # Cọc chèo mạn thuyền tại X = tx + 0.45, Y = +-1.02, Z = 0.78
        for ssign in [1.0, -1.0]:
            p_pin = Vector((tx + 0.45, 1.02 * ssign, 0.78))
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

    m_thwarts = bpy.data.meshes.new("Mesh_Thwarts_TholePins_PowerGrip")
    bm_thwarts.to_mesh(m_thwarts)
    bm_thwarts.free()
    mat_wood = bpy.data.materials.get('Mat_GoLim_ThuyenTa') or bpy.data.materials.get('Mat_GoLim')
    if mat_wood:
        m_thwarts.materials.append(mat_wood)

    # 4. TÁI TẠO Export_DaiViet_Master_Full
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

    # Nạp lại REFERENCE_BLUEPRINT_PLANE vào export_col
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
        f.write("Đã gắn xong 6 lính Power Grip vào Export_Ship_Root.\n")

    # 5. XUẤT GLB
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

    # 6. RENDER LẠI ẢNH ĐỐI CHIẾU
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
