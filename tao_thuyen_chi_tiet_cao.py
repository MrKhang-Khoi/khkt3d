import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ==============================================================================
# 1. BẢNG VẬT LIỆU CHUẨN LỊCH SỬ THẾ KỶ 10 (RICH PBR & VIEWPORT SHADING)
# ==============================================================================

def create_rich_pbr_material(name, diffuse_rgba, roughness=0.55, metallic=0.0, wave_scale=3.0, bump_strength=0.25):
    """Tạo vật liệu PBR cao cấp có màu Viewport rực rỡ và Shader Nodes chân thực."""
    mat = bpy.data.materials.new(name=name)
    mat.diffuse_color = diffuse_rgba
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = diffuse_rgba
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Thêm vân gỗ / thớ sợi tự nhiên
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.2, 0.12, 3.5)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = wave_scale
    wave.inputs['Distortion'].default_value = 1.6
    wave.inputs['Detail'].default_value = 2.0
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = 0.05
    links.new(wave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_river_pbr():
    """Mặt nước lợ sông Bạch Đằng."""
    mat = bpy.data.materials.new("Mat_BachDang_River")
    mat.diffuse_color = (0.06, 0.22, 0.22, 0.85)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.18, 0.17, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['Metallic'].default_value = 0.12
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.8
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.8
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = 1.333
    return mat

def make_cylinder(bm, r, depth, segments=16, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r, radius2=r, depth=depth, matrix=mat
    )

def make_cone(bm, r1, r2, depth, segments=16, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r1, radius2=r2, depth=depth, matrix=mat
    )

def apply_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True

# ==============================================================================
# 2. DỰNG CHI TIẾT THUYỀN CHIẾN NGÔ QUYỀN (VIETNAMESE HERO WARSHIP)
# ==============================================================================

def build_refined_ngo_quyen_warship(mat_wood, mat_deck, mat_sail, mat_shield, mat_red):
    """
    Dựng Thuyền Thoi / Thuyền Đuôi Én Ngô Quyền chuẩn mực:
    - Thân thuyền độc mộc ghép ván cong mềm mại, lòng thuyền có xà ngang chịu lực.
    - Mũi thuyền nhọn vút cao chạm hoa văn sóng nước Đông Sơn.
    - Đuôi thuyền én cách điệu.
    - 16 Mái chèo tay có cọc chèo gắn be thuyền.
    - Cột buồm tre, buồm nan tre cánh dơi có nẹp ngang và dây chằng.
    - Khiên mây sơn son đỏ thắm gài dọc hai bên mạn.
    - Chèo cậy lái đuôi bản lớn.
    - Cờ thần đuôi nheo phấp phới.
    """
    root = bpy.data.objects.new("Thuyen_NgoQuyen_Master", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 2.0
    bpy.context.collection.objects.link(root)

    # --------------------------------------------------------------------------
    # A. VỎ THUYỀN (HULL) - MỀM MẠI, KHÍ ĐỘNG HỌC, ĐÁY NÔNG
    # --------------------------------------------------------------------------
    hull_mesh = bpy.data.meshes.new("NgoQuyen_Curved_Hull_Mesh")
    hull_obj = bpy.data.objects.new("NgoQuyen_Curved_Hull", hull_mesh)
    bpy.context.collection.objects.link(hull_obj)
    hull_obj.parent = root

    bm = bmesh.new()
    # Dựng thân thuyền từ lưới nhiều phân đoạn để uốn cong mượt
    bmesh.ops.create_grid(bm, x_segments=16, y_segments=32, size=1.0)
    for v in bm.verts:
        # Tọa độ gốc: X từ -0.5 đến +0.5, Y từ -0.5 đến +0.5
        u_x = v.co.x * 2.0  # -1.0 đến +1.0 (chiều ngang)
        u_y = v.co.y * 2.0  # -1.0 đến +1.0 (chiều dọc thân)

        # Kích thước thực tế: Dài 14.5m, Rộng 2.2m, Mạn cao 1.1m
        y = u_y * 7.25
        
        # Độ rộng mạn thuyền: nở rộng ở giữa (u_y = 0), thu nhọn dần về mũi và đuôi
        clamped_uy = max(-1.0, min(1.0, u_y))
        cos_val = max(0.01, math.cos(clamped_uy * math.pi * 0.46))
        width_curve = cos_val ** 0.8
        x = u_x * (1.1 * width_curve)

        # Độ cong lượn của đáy thuyền & mạn thuyền
        flare = 1.0 - (u_x ** 2)
        
        sheer = 0.35 * (clamped_uy ** 2)
        if clamped_uy > 0:
            sheer += (abs(clamped_uy) ** 1.6) * 0.65
        else:
            sheer += (abs(clamped_uy) ** 1.6) * 0.45

        z = sheer - (flare * 0.65)

        v.co.x = x
        v.co.y = y
        v.co.z = z

    # Đùn dầy vỏ gỗ thành thuyền 6cm
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.08)
    
    hull_mesh.materials.append(mat_wood)
    bm.to_mesh(hull_mesh)
    bm.free()
    apply_smooth(hull_obj)

    # Thêm Subdivision Surface để thân thuyền lượn sóng cực kỳ mượt mà
    sub = hull_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # --------------------------------------------------------------------------
    # B. XÀ NGANG VÀ CHỖ NGỒI TAY CHÈO (THWARTS & INTERNAL RIBS)
    # --------------------------------------------------------------------------
    thwart_mesh = bpy.data.meshes.new("NgoQuyen_Thwarts_Mesh")
    thwart_obj = bpy.data.objects.new("NgoQuyen_Thwarts", thwart_mesh)
    bpy.context.collection.objects.link(thwart_obj)
    thwart_obj.parent = root

    bm = bmesh.new()
    for i in range(-5, 6):
        y_pos = i * 1.1
        w_factor = max(0.01, math.cos((y_pos / 7.25) * math.pi * 0.46)) ** 0.8
        w_span = 2.0 * w_factor
        if w_span > 0.5:
            # Thanh gỗ ngang cho binh sĩ ngồi chèo
            bmesh.ops.create_cube(bm, size=1.0, 
                                  matrix=Matrix.Translation((0, y_pos, 0.15)) @ 
                                         Matrix.Scale(w_span, 4, Vector((1,0,0))) @ 
                                         Matrix.Scale(0.22, 4, Vector((0,1,0))) @ 
                                         Matrix.Scale(0.06, 4, Vector((0,0,1))))
    thwart_mesh.materials.append(mat_deck)
    bm.to_mesh(thwart_mesh)
    bm.free()
    apply_smooth(thwart_obj)

    # --------------------------------------------------------------------------
    # C. HỆ THỐNG 16 MÁI CHÈO & CỌC CHÈO (OARS & ROWING PINS)
    # --------------------------------------------------------------------------
    oar_mesh = bpy.data.meshes.new("NgoQuyen_Detailed_Oars_Mesh")
    oar_obj = bpy.data.objects.new("NgoQuyen_Detailed_Oars", oar_mesh)
    bpy.context.collection.objects.link(oar_obj)
    oar_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-4, 5):
            y_pos = idx * 1.15
            w_factor = max(0.01, math.cos((y_pos / 7.25) * math.pi * 0.46)) ** 0.8
            x_gunwale = side * (1.08 * w_factor)
            z_gunwale = 0.28 + 0.35 * ((y_pos / 7.25) ** 2)

            # Cọc chèo gỗ (Rowing pin) gắn trên be thuyền
            make_cylinder(bm, 0.025, 0.22, segments=8, 
                          matrix=Matrix.Translation((x_gunwale, y_pos, z_gunwale + 0.1)))

            # Cán chèo gỗ tròn dài 2.4m nghiêng xuống mặt nước
            rot_oar = Euler((math.radians(side * 26), 0, math.radians(side * 78))).to_matrix().to_4x4()
            trans_oar = Matrix.Translation((x_gunwale, y_pos, z_gunwale + 0.08))
            make_cylinder(bm, 0.032, 2.4, segments=10, matrix=trans_oar @ rot_oar)

            # Lưỡi bản chèo dẹt hình lá bao lồi
            blade_m = trans_oar @ rot_oar @ Matrix.Translation((0, 0, 1.1)) @ Matrix.Scale(0.18, 4, Vector((1,0,0))) @ Matrix.Scale(0.02, 4, Vector((0,1,0))) @ Matrix.Scale(0.65, 4, Vector((0,0,1)))
            bmesh.ops.create_cube(bm, size=1.0, matrix=blade_m)

    oar_mesh.materials.append(mat_wood)
    bm.to_mesh(oar_mesh)
    bm.free()
    apply_smooth(oar_obj)

    # --------------------------------------------------------------------------
    # D. CỘT BUỒM TRE & CÁNH BUỒM NAN CÓ NẸP NGANG (BATTEN SAIL ASSEMBLY)
    # --------------------------------------------------------------------------
    mast_mesh = bpy.data.meshes.new("NgoQuyen_Batten_Mast_Mesh")
    mast_obj = bpy.data.objects.new("NgoQuyen_Batten_Mast", mast_mesh)
    bpy.context.collection.objects.link(mast_obj)
    mast_obj.parent = root
    mast_obj.location = (0, 1.2, 0.1)

    bm = bmesh.new()
    # Cột buồm tre cao 6.2m, có các đốt tre
    make_cone(bm, 0.11, 0.065, 6.2, segments=16, matrix=Matrix.Translation((0, 0, 3.1)))

    # Cánh buồm nan tre cánh dơi có độ phồng đón gió
    rot_sail = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=2.2, 
                          matrix=Matrix.Translation((0, 0.25, 3.2)) @ rot_sail)
    for v in bm.verts[-169:]:
        v.co.x *= 0.9
        v.co.z = v.co.z * 0.95 + 3.2
        # Độ phồng căng gió 3D
        v.co.y += math.sin((v.co.z - 1.2) / 2.2 * math.pi) * 0.42

    # 5 Thanh nẹp tre ngang giữ buồm (Battens)
    for b_idx in range(5):
        z_batten = 1.6 + b_idx * 0.75
        y_batten = 0.25 + math.sin((z_batten - 1.2) / 2.2 * math.pi) * 0.42
        make_cylinder(bm, 0.03, 1.95, segments=8, 
                      matrix=Matrix.Translation((0, y_batten, z_batten)) @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4())

    mast_mesh.materials.append(mat_wood)
    mast_mesh.materials.append(mat_sail)
    for p in mast_mesh.polygons:
        if p.index >= 32 and p.index < 200:
            p.material_index = 1
    bm.to_mesh(mast_mesh)
    bm.free()
    apply_smooth(mast_obj)

    # --------------------------------------------------------------------------
    # E. DÂY CHẰNG BUỒM & DÂY LÈO (RIGGING CORDS)
    # --------------------------------------------------------------------------
    curve_data = bpy.data.curves.new("NgoQuyen_Cords_Curve", 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.015
    curve_data.bevel_resolution = 2
    curve_obj = bpy.data.objects.new("NgoQuyen_Cords", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.parent = root

    for side in [0.95, -0.95]:
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(1)
        spline.bezier_points[0].co = Vector((0, 1.2, 5.8))
        spline.bezier_points[0].handle_left_type = 'AUTO'
        spline.bezier_points[0].handle_right_type = 'AUTO'
        spline.bezier_points[1].co = Vector((side, 0.0, 0.35))
        spline.bezier_points[1].handle_left_type = 'AUTO'
        spline.bezier_points[1].handle_right_type = 'AUTO'
    curve_data.materials.append(mat_wood)

    # --------------------------------------------------------------------------
    # F. HÀNG KHIÊN MÂY SƠN SON HÌNH TRÒN CÓ ĐỘ VỒNG 3D (SHIELDS)
    # --------------------------------------------------------------------------
    shield_mesh = bpy.data.meshes.new("NgoQuyen_3D_Shields_Mesh")
    shield_obj = bpy.data.objects.new("NgoQuyen_3D_Shields", shield_mesh)
    bpy.context.collection.objects.link(shield_obj)
    shield_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-3, 4):
            y_pos = idx * 1.45
            w_factor = max(0.01, math.cos((y_pos / 7.25) * math.pi * 0.46)) ** 0.8
            x_pos = side * (1.12 * w_factor)
            z_pos = 0.35 + 0.35 * ((y_pos / 7.25) ** 2)

            rot_s = Euler((0, math.radians(side * 90), 0)).to_matrix().to_4x4()
            trans_s = Matrix.Translation((x_pos, y_pos, z_pos))

            # Khiên đan mây có độ vồng nhô ở tâm (Convex Shield)
            bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.32, matrix=trans_s @ rot_s @ Matrix.Scale(0.2, 4, Vector((0,0,1))))

    shield_mesh.materials.append(mat_shield)
    bm.to_mesh(shield_mesh)
    bm.free()
    apply_smooth(shield_obj)

    # --------------------------------------------------------------------------
    # G. CHÈO CẬY LÁI ĐUÔI BẢN LỚN (STEERING OAR)
    # --------------------------------------------------------------------------
    rudder_mesh = bpy.data.meshes.new("NgoQuyen_Steering_Rudder_Mesh")
    rudder_obj = bpy.data.objects.new("NgoQuyen_Steering_Rudder", rudder_mesh)
    bpy.context.collection.objects.link(rudder_obj)
    rudder_obj.parent = root
    rudder_obj.location = (0.28, -7.0, 0.45)
    rudder_obj.rotation_euler = Euler((math.radians(-32), math.radians(12), 0))

    bm = bmesh.new()
    make_cylinder(bm, 0.05, 4.4, segments=12)
    # Bản lái dẹt lớn uốn lượn
    blade_mat = Matrix.Translation((0, 0, -1.8)) @ Matrix.Scale(0.35, 4, Vector((1,0,0))) @ Matrix.Scale(0.04, 4, Vector((0,1,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=blade_mat)
    rudder_mesh.materials.append(mat_wood)
    bm.to_mesh(rudder_mesh)
    bm.free()
    apply_smooth(rudder_obj)

    # --------------------------------------------------------------------------
    # H. CỜ THẦN ĐUÔI NHEO PHẤP PHỚI (WAR BANNER)
    # --------------------------------------------------------------------------
    flag_mesh = bpy.data.meshes.new("NgoQuyen_Banner_Mesh")
    flag_obj = bpy.data.objects.new("NgoQuyen_Banner", flag_mesh)
    bpy.context.collection.objects.link(flag_obj)
    flag_obj.parent = root
    flag_obj.location = (0, -6.8, 1.2)

    bm = bmesh.new()
    make_cylinder(bm, 0.03, 3.2, segments=8, matrix=Matrix.Translation((0, 0, 1.6)))
    # Lá cờ đuôi nheo tam giác lượn sóng
    bmesh.ops.create_grid(bm, x_segments=6, y_segments=6, size=1.0, 
                          matrix=Matrix.Translation((0, -0.6, 2.6)) @ Euler((math.radians(90), 0, math.radians(90))).to_matrix().to_4x4())
    for v in bm.verts[-49:]:
        v.co.y += math.sin(v.co.x * 4.0) * 0.12 # Sóng lượn của cờ
    flag_mesh.materials.append(mat_wood)
    flag_mesh.materials.append(mat_red)
    for p in flag_mesh.polygons:
        if p.index >= 16:
            p.material_index = 1
    bm.to_mesh(flag_mesh)
    bm.free()
    apply_smooth(flag_obj)

    return root

# ==============================================================================
# 3. DỰNG LÂU THUYỀN NAM HÁN (ENEMY TOWER SHIP) - ĐỒ SỘ, ĐÁY CHỮ V
# ==============================================================================

def build_refined_nam_han_ship(mat_wood, mat_sail):
    root = bpy.data.objects.new("LauThuyen_NamHan_Master", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 2.5
    bpy.context.collection.objects.link(root)

    # Thân đại hạm đáy V sâu
    mesh = bpy.data.meshes.new("NamHan_Refined_Hull_Mesh")
    obj = bpy.data.objects.new("NamHan_Refined_Hull", mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = root

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 28.0
        v.co.x *= 6.8
        v.co.z *= 4.4
        u = v.co.y / 14.0
        v.co.x *= max(0.18, 1.0 - (abs(u) ** 2) * 0.65)
        v.co.z += (u ** 2) * 0.85
        # Đáy chữ V sâu hoắm ăn nước 2.6m
        if v.co.z < 0:
            v.co.x *= max(0.08, (v.co.z + 2.2) / 2.2)
    mesh.materials.append(mat_wood)
    bm.to_mesh(mesh)
    bm.free()
    apply_smooth(obj)
    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # Lầu chỉ huy 2 tầng có mái dốc
    tower_mesh = bpy.data.meshes.new("NamHan_Refined_Tower_Mesh")
    tower_obj = bpy.data.objects.new("NamHan_Refined_Tower", tower_mesh)
    bpy.context.collection.objects.link(tower_obj)
    tower_obj.parent = root
    tower_obj.location = (0, -2.0, 2.8)

    bm = bmesh.new()
    # Tầng 1
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 1.2)) @ Matrix.Scale(4.8, 4, Vector((1,0,0))) @ Matrix.Scale(6.0, 4, Vector((0,1,0))) @ Matrix.Scale(2.4, 4, Vector((0,0,1))))
    # Tầng 2
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 3.2)) @ Matrix.Scale(3.2, 4, Vector((1,0,0))) @ Matrix.Scale(3.8, 4, Vector((0,1,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1))))
    # Mái ngói cong dốc 4 góc
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.8, radius2=0.2, depth=1.1,
                          matrix=Matrix.Translation((0, 0, 4.6)) @ Euler((0,0,math.radians(45))).to_matrix().to_4x4())
    tower_mesh.materials.append(mat_wood)
    bm.to_mesh(tower_mesh)
    bm.free()
    apply_smooth(tower_obj)

    # 2 Cột buồm lớn nan cứng
    mast_mesh = bpy.data.meshes.new("NamHan_TwinMasts_Mesh")
    mast_obj = bpy.data.objects.new("NamHan_TwinMasts", mast_mesh)
    bpy.context.collection.objects.link(mast_obj)
    mast_obj.parent = root

    bm = bmesh.new()
    for y_m, h_m in [(4.5, 11.5), (-6.2, 15.5)]:
        make_cone(bm, 0.30, 0.14, h_m, segments=16, matrix=Matrix.Translation((0, y_m, 1.6 + h_m / 2.0)))
        make_cylinder(bm, 0.10, 6.2, segments=10, matrix=Matrix.Translation((0, y_m, 1.6 + h_m * 0.75)) @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4())
        rot_s = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
        bmesh.ops.create_grid(bm, x_segments=10, y_segments=10, size=2.6, 
                              matrix=Matrix.Translation((0, y_m + 0.3, 1.6 + h_m * 0.5)) @ rot_s @ Matrix.Scale(1.3, 4, Vector((1,0,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1))))

    mast_mesh.materials.append(mat_wood)
    mast_mesh.materials.append(mat_sail)
    for p in mast_mesh.polygons:
        if p.index >= 80:
            p.material_index = 1
    bm.to_mesh(mast_mesh)
    bm.free()
    apply_smooth(mast_obj)

    return root

# ==============================================================================
# 4. BÃI CỌC BẠCH ĐẰNG (IRON-TIPPED STAKES)
# ==============================================================================

def build_stakes(mat_wood, mat_iron):
    mesh = bpy.data.meshes.new("Stakes_Field_Mesh")
    obj = bpy.data.objects.new("BaiCoc_BachDang", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    stake_coords = [
        (-3.0, 2.0, -1.8, 48), (0.0, 3.0, -1.8, 52), (3.5, 1.5, -1.8, 50),
        (-2.0, -2.0, -1.8, 54), (1.5, -1.0, -1.8, 49), (4.5, -3.0, -1.8, 51),
        (-4.0, -6.0, -1.8, 50), (-0.5, -5.5, -1.8, 53), (2.5, -7.0, -1.8, 48),
        (-2.5, -10.0, -1.8, 52), (1.0, -11.0, -1.8, 50), (3.8, -12.0, -1.8, 55),
        (-1.2, 7.0, -1.8, 47), (2.0, 8.0, -1.8, 50)
    ]
    for x, y, z, pitch in stake_coords:
        rot_s = Euler((math.radians(pitch), 0, math.radians(-10))).to_matrix().to_4x4()
        full_m = Matrix.Translation((x, y, z)) @ rot_s
        make_cone(bm, 0.16, 0.12, 3.2, segments=12, matrix=full_m @ Matrix.Translation((0, 0, 1.6)))
        make_cone(bm, 0.125, 0.01, 0.55, segments=10, matrix=full_m @ Matrix.Translation((0, 0, 3.45)))

    mesh.materials.append(mat_wood)
    mesh.materials.append(mat_iron)
    for p in mesh.polygons:
        if p.center.z > 0.0:
            p.material_index = 1
        else:
            p.material_index = 0
    bm.to_mesh(mesh)
    bm.free()
    apply_smooth(obj)
    return obj

# ==============================================================================
# 5. MẶT SÔNG & HOẠT ẢNH THỦY TRIỀU
# ==============================================================================

def build_river(mat_river):
    bpy.ops.mesh.primitive_plane_add(size=160.0, location=(0, 0, 0.0))
    river = bpy.context.active_object
    river.name = "BachDang_River"
    river.data.materials.append(mat_river)
    ocean_mod = river.modifiers.new("Waves", 'OCEAN')
    ocean_mod.geometry_mode = 'GENERATE'
    ocean_mod.repeat_x = 2
    ocean_mod.repeat_y = 2
    ocean_mod.spatial_size = 80
    ocean_mod.resolution = 12
    ocean_mod.wave_scale = 0.7
    ocean_mod.choppiness = 1.1
    return river

def animate_scene(river_obj, vn_ship, enemy_ship, total_frames=180):
    bpy.context.scene.render.fps = 30
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames

    # Triều rút
    river_obj.animation_data_create()
    act_r = bpy.data.actions.new("Tide_Action")
    river_obj.animation_data.action = act_r
    for f in range(1, total_frames + 1):
        tide_z = 0.5 - (f / total_frames) * 2.1
        river_obj.location.z = tide_z
        river_obj.keyframe_insert("location", frame=f)

    # Thuyền Ngô Quyền
    vn_ship.animation_data_create()
    act_vn = bpy.data.actions.new("VN_Action")
    vn_ship.animation_data.action = act_vn
    for f in range(1, total_frames + 1):
        t = f / total_frames
        tide_z = 0.5 - t * 2.1
        if f <= 60:
            y_pos = 18.0 + (f / 60.0) * 8.0
            x_pos = -6.0 + math.sin(f * 0.1) * 0.5
            yaw = 0
        elif f <= 90:
            sub_t = (f - 60) / 30.0
            y_pos = 26.0 - sub_t * 4.0
            x_pos = -6.0 + sub_t * 3.0
            yaw = math.radians(sub_t * 180)
        else:
            sub_t = (f - 90) / 90.0
            y_pos = 22.0 - sub_t * 12.0
            x_pos = -3.0 - sub_t * 2.0
            yaw = math.radians(180)
        z_pos = tide_z + 0.15 + math.sin(f * 0.3) * 0.08
        vn_ship.location = Vector((x_pos, y_pos, z_pos))
        vn_ship.rotation_euler = Euler((math.sin(f * 0.25) * 0.05, math.cos(f * 0.2) * 0.06, yaw))
        vn_ship.keyframe_insert("location", frame=f)
        vn_ship.keyframe_insert("rotation_euler", frame=f)

    # Lâu thuyền Nam Hán đâm cọc
    enemy_ship.animation_data_create()
    act_en = bpy.data.actions.new("Enemy_Action")
    enemy_ship.animation_data.action = act_en
    for f in range(1, total_frames + 1):
        tide_z = 0.5 - (f / total_frames) * 2.1
        if f < 70:
            y_pos = -25.0 + (f / 70.0) * 18.0
            x_pos = 1.0
            z_pos = tide_z - 0.8
            pitch = -0.05
            roll = math.sin(f * 0.15) * 0.04
        elif f < 100:
            sub_t = (f - 70) / 30.0
            y_pos = -7.0 + sub_t * 1.5
            x_pos = 1.0 + sub_t * 0.8
            z_pos = -0.4 - sub_t * 0.3
            pitch = -0.05 - sub_t * 0.15
            roll = sub_t * 0.35
        else:
            y_pos = -5.5
            x_pos = 1.8
            z_pos = -0.7
            pitch = -0.22
            roll = 0.42 + math.sin(f * 0.1) * 0.02
        enemy_ship.location = Vector((x_pos, y_pos, z_pos))
        enemy_ship.rotation_euler = Euler((pitch, roll, 0.05))
        enemy_ship.keyframe_insert("location", frame=f)
        enemy_ship.keyframe_insert("rotation_euler", frame=f)

# ==============================================================================
# 6. CAMERA & ÁNH SÁNG ĐẶC TẢ CON THUYỀN (HERO SHIP SHOWCASE)
# ==============================================================================

def setup_cinema_lighting_and_cam(vn_ship):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Battle_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.55, 0.65, 0.78, 1.0)
        bg.inputs['Strength'].default_value = 1.5

    # Mặt trời rực rỡ chiếu sáng toàn bộ chi tiết thuyền
    sun_data = bpy.data.lights.new("Hero_Sun", 'SUN')
    sun_data.energy = 6.5
    sun_data.color = (1.0, 0.94, 0.82)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(45), math.radians(20), math.radians(-35)))

    # Đèn phụ chiếu sáng mạn đối diện
    fill_data = bpy.data.lights.new("Hero_Fill", 'SUN')
    fill_data.energy = 2.0
    fill_data.color = (0.6, 0.8, 1.0)
    fill_obj = bpy.data.objects.new("FillSun", fill_data)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = Euler((math.radians(-50), 0, math.radians(140)))

    # Camera đặc tả góc nhìn 3/4 mạn thuyền Ngô Quyền
    cam_data = bpy.data.cameras.new("Hero_Ship_Cam")
    cam_data.lens = 35
    cam_obj = bpy.data.objects.new("Camera_Hero", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Khóa mục tiêu ngắm thẳng vào giữa thuyền Ngô Quyền
    cam_target = bpy.data.objects.new("Cam_Aim_Hero", None)
    bpy.context.collection.objects.link(cam_target)
    cam_target.parent = vn_ship
    cam_target.location = (0, 0, 1.8)

    track = cam_obj.constraints.new('TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Camera đặt ở khoảng cách 16m để bắt trọn từng mái chèo, khiên đỏ, buồm nan và thân thuyền uốn lượn
    cam_obj.parent = vn_ship
    cam_obj.location = (11.5, -12.0, 5.2)

def set_material_preview():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

def main():
    print("=== DỰNG LẠI MÔ HÌNH THUYỀN CHI TIẾT CAO & CHUẨN LỊCH SỬ ===")
    reset_scene()

    # Bảng vật liệu lịch sử
    mat_vn_wood = create_rich_pbr_material("Mat_GoLim_ThuyenTa", (0.22, 0.12, 0.05, 1.0), roughness=0.55, bump_strength=0.35)
    mat_deck = create_rich_pbr_material("Mat_VanGo_Boong", (0.38, 0.22, 0.10, 1.0), roughness=0.6)
    mat_enemy_wood = create_rich_pbr_material("Mat_GoThong_NamHan", (0.42, 0.28, 0.16, 1.0), roughness=0.7)
    mat_sail = create_rich_pbr_material("Mat_BuomNanTre", (0.84, 0.74, 0.48, 1.0), roughness=0.85, wave_scale=6.0, bump_strength=0.15)
    mat_iron = create_rich_pbr_material("Mat_SatRen_Coc", (0.12, 0.12, 0.14, 1.0), roughness=0.35, metallic=0.92)
    mat_shield = create_rich_pbr_material("Mat_KhienMay_SonSon", (0.68, 0.16, 0.10, 1.0), roughness=0.45)
    mat_red = create_rich_pbr_material("Mat_CoDo_TuyenSon", (0.85, 0.12, 0.08, 1.0), roughness=0.5)
    mat_river = create_river_pbr()

    # Dựng các đối tượng chi tiết cao
    vn_ship = build_refined_ngo_quyen_warship(mat_vn_wood, mat_deck, mat_sail, mat_shield, mat_red)
    enemy_ship = build_refined_nam_han_ship(mat_enemy_wood, mat_sail)
    stakes = build_stakes(mat_vn_wood, mat_iron)
    river = build_river(mat_river)

    animate_scene(river, vn_ship, enemy_ship, total_frames=180)
    setup_cinema_lighting_and_cam(vn_ship)
    set_material_preview()

    desktop_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    os.makedirs(desktop_dir, exist_ok=True)
    blend_path = os.path.join(desktop_dir, "bach_dang_thuyen_tinh_xao.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f" ĐÃ LƯU FILE BLENDER MÔ HÌNH TINH XẢO TẠI: {blend_path}")

    # Render ảnh đặc tả kiểm chứng chất lượng cao tại Frame 80
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.frame_set(80)

    render_img = os.path.join(desktop_dir, "anh_kiem_chung_thuyen_tinh_xao.png")
    scene.render.filepath = render_img
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH ĐẶC TẢ TẠI: {render_img}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
