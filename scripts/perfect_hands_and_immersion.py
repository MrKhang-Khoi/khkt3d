import bpy, bmesh, math, os, traceback
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/perfect_hands_and_immersion_log.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== CÂN CHỈNH HOÀN HẢO: CÁN CHÈO NẰM TRỌN 2 BÀN TAY & CHÌM NƯỚC SÂU >= 28CM ===\n")

try:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    soldier_base = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
    giap_base = bpy.data.objects.get('Giap_HoTam_DongSon_ThuyBinh_DaiViet_Master')
    dai_base = bpy.data.objects.get('Dai_That_Lung_ThuyBinh_DaiViet_Master')
    boat = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
    water = bpy.data.objects.get('MatNuoc_SongBachDang_Chinh')

    water_z = water.matrix_world.translation.z if water else -0.135

    # 1. Đổi màu vật liệu đai thắt lưng từ cam phao bơi thành da bò nâu sẫm cổ kính
    mat_belt = bpy.data.materials.get('Mat_DaiThatLung') or (dai_base.data.materials[0] if dai_base.data.materials else None)
    if mat_belt and mat_belt.use_nodes:
        bsdf = mat_belt.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.12, 0.05, 0.02, 1.0) # Nâu sẫm
            bsdf.inputs['Roughness'].default_value = 0.75

    # 2. HÀM TẠO LÍNH VỚI CÁN CHÈO CHUẨN XÁC NẰM TRỌN 2 LÒNG BÀN TAY (Z = 0.88m)
    def build_flawless_rower(is_stbd=False):
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
        
        # Scale đai thắt lưng gọn gàng ôm sát eo (giảm 15% độ phồng)
        o_dai.scale = Vector((0.88, 0.88, 0.88))
        
        rot_facing = Euler((0, 0, math.pi / 2.0)).to_matrix().to_4x4()
        for o in [o_soldier, o_giap, o_dai]:
            o.matrix_world = rot_facing @ o.matrix_world
            
        # Vị trí hai lòng bàn tay lính sau khi xoay rot_facing:
        # Bàn tay trong: (X = 0.40m, Y = -0.32m * side_sign, Z = 0.88m)
        # Bàn tay ngoài: (X = 0.40m, Y = +0.32m * side_sign, Z = 0.88m)
        # Điểm tì cọc chèo mạn thuyền: (X = 0.40m, Y = +1.02m * side_sign, Z = 0.82m)
        # Điểm đầu lưỡi chèo cắm sâu dưới nước:
        # Muốn ngập sâu 30cm: Z_water = -0.135, Z_soldier = 0.996 => Z_tip = -0.135 - 0.30 - 0.996 = -1.43m (cho Tả) và -1.48m (cho Hữu)
        p_handle = Vector((0.40, -0.36 * side_sign, 0.90))
        z_water_target = -1.55 if not is_stbd else -1.50
        p_water = Vector((0.40, 2.60 * side_sign, z_water_target))
        
        dir_oar = p_water - p_handle
        oar_len = dir_oar.length
        dir_norm = dir_oar.normalized()
        
        bm = bmesh.new()
        rot_diff = Vector((0, 0, 1)).rotation_difference(dir_norm)
        
        blade_len = 1.15
        loom_len = oar_len - blade_len
        p_loom_center = p_handle + dir_norm * (loom_len * 0.5)
        mat_loom = Matrix.Translation(p_loom_center) @ rot_diff.to_matrix().to_4x4()
        
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            radius1=0.034,
            radius2=0.030,
            depth=loom_len,
            matrix=mat_loom,
            segments=12
        )
        
        blade_width = 0.23
        blade_thick = 0.026
        p_blade_center = p_water - dir_norm * (blade_len * 0.5)
        mat_blade = Matrix.Translation(p_blade_center) @ rot_diff.to_matrix().to_4x4() @ Matrix.Scale(blade_width, 4, Vector((1,0,0))) @ Matrix.Scale(blade_thick, 4, Vector((0,1,0))) @ Matrix.Scale(blade_len, 4, Vector((0,0,1)))
        
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=mat_blade
        )
        
        # Vòng đệm da/chão tì lên cọc chèo mạn thuyền
        p_fulcrum = Vector((0.40, 1.02 * side_sign, 0.76))
        mat_ring = Matrix.Translation(p_fulcrum) @ rot_diff.to_matrix().to_4x4()
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            radius1=0.046,
            radius2=0.046,
            depth=0.12,
            matrix=mat_ring,
            segments=12
        )
        
        m_oar = bpy.data.meshes.new(f"TMP_Oar_{'Stbd' if is_stbd else 'Port'}")
        bm.to_mesh(m_oar)
        bm.free()
        
        mat_wood = bpy.data.materials.get('Mat_GoLim_ThuyenTa') or bpy.data.materials.get('Mat_GoLim')
        if mat_wood:
            m_oar.materials.append(mat_wood)
            
        o_oar = bpy.data.objects.new(f"TMP_Oar_{'Stbd' if is_stbd else 'Port'}", m_oar)
        bpy.context.scene.collection.objects.link(o_oar)
        
        bpy.ops.object.select_all(action='DESELECT')
        for p in [o_soldier, o_giap, o_dai, o_oar]:
            p.select_set(True)
        bpy.context.view_layer.objects.active = o_soldier
        bpy.ops.object.join()
        
        final_rower = bpy.context.active_object
        dec = final_rower.modifiers.new(name="DecimateWeb", type='DECIMATE')
        dec.ratio = 0.65
        bpy.ops.object.modifier_apply(modifier="DecimateWeb")
        
        final_mesh = final_rower.data.copy()
        bpy.data.objects.remove(final_rower, do_unlink=True)
        return final_mesh

    mesh_rower_port = build_flawless_rower(is_stbd=False)
    mesh_rower_stbd = build_flawless_rower(is_stbd=True)

    # 3. BỤC VÁN NGỒI & CỌC CHÈO
    bm_thwarts = bmesh.new()
    thwart_xs = [-1.92, -0.12, 1.68]
    for tx in thwart_xs:
        # Ván ngồi bắc ngang từ Y = -1.18 đến Y = +1.18 tại Z = 0.36
        mat_thwart = Matrix.Translation(Vector((tx, 0.0, 0.36))) @ Matrix.Scale(0.28, 4, Vector((1,0,0))) @ Matrix.Scale(2.36, 4, Vector((0,1,0))) @ Matrix.Scale(0.045, 4, Vector((0,0,1)))
        bmesh.ops.create_cube(bm_thwarts, size=1.0, matrix=mat_thwart)
        
        # Cọc chèo Thole pin tại X = tx + 0.40, Y = +-1.02, Z = 0.82
        for ssign in [1.0, -1.0]:
            p_pin = Vector((tx + 0.40, 1.02 * ssign, 0.82))
            mat_pin = Matrix.Translation(p_pin)
            bmesh.ops.create_cone(
                bm_thwarts,
                cap_ends=True,
                radius1=0.024,
                radius2=0.020,
                depth=0.25,
                matrix=mat_pin,
                segments=8
            )

    m_thwarts = bpy.data.meshes.new("Mesh_Thwarts_TholePins_Flawless")
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

    for o in created_objs:
        if 'Rower' in o.name:
            bb = [o.matrix_world @ Vector(b) for b in o.bound_box]
            z_min = min(b.z for b in bb)
            z_max = max(b.z for b in bb)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f" - {o.name}: World Z=[{z_min:.3f}, {z_max:.3f}] (Mặt nước: {water_z:.3f}, Độ chìm: {water_z - z_min:.3f}m)\n")

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

    # 6. RENDER CHỤP ẢNH ĐỐI CHIẾU
    cam_name = 'Camera_KiemChung_PhacThao'
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)

    cam_obj.location = Vector((-3.8, -39.5, 2.0))
    look_dir = Vector((-6.27, -44.34, 0.4)) - cam_obj.location
    rot_quat = look_dir.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = 45.0

    bpy.context.scene.camera = cam_obj
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720

    out_png = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_blender_doichieu_phacthao_perfect.png'
    bpy.context.scene.render.filepath = out_png
    bpy.ops.render.render(write_still=True)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"RENDER HOÀN TẤT: {out_png}\n")

except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"LỖI: {traceback.format_exc()}\n")
