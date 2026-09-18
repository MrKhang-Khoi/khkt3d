import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler, Matrix

engine_dir = os.path.dirname(os.path.abspath(__file__))
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from procedural_asian_architecture import (
    generate_tile_roof,
    generate_dougong_brackets,
    generate_timber_wall_with_lattice_windows,
    generate_balustrade,
    generate_rippling_cloth_flag
)

def create_southern_han_materials():
    mats = {}

    # 1. Gỗ thân tàu phương Bắc sẫm màu tẩm hắc ín chống hà biển
    m_hull = bpy.data.materials.new('Mat_NamHan_GoThanTau')
    m_hull.diffuse_color = (0.16, 0.11, 0.08, 1.0)
    m_hull.use_nodes = True
    nodes = m_hull.node_tree.nodes
    links = m_hull.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tc = nodes.new('ShaderNodeTexCoord')
    mp = nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0, 15.0, 1.0)
    links.new(tc.outputs['Object'], mp.inputs['Vector'])
    n1 = nodes.new('ShaderNodeTexNoise')
    n1.inputs['Scale'].default_value = 40.0
    n1.inputs['Detail'].default_value = 10.0
    links.new(mp.outputs['Vector'], n1.inputs['Vector'])
    cr = nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].position = 0.35
    cr.color_ramp.elements[0].color = (0.10, 0.07, 0.05, 1.0)
    cr.color_ramp.elements[1].position = 0.70
    cr.color_ramp.elements[1].color = (0.22, 0.15, 0.10, 1.0)
    links.new(n1.outputs['Fac'], cr.inputs['Fac'])
    links.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.02
    links.new(n1.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mats['wood_hull'] = m_hull

    # 2. Gỗ Lâu Đài & Khung cột sơn son then đỏ sẫm phương Bắc
    m_castle = bpy.data.materials.new('Mat_NamHan_SonSonLauDai')
    m_castle.diffuse_color = (0.48, 0.12, 0.08, 1.0)
    m_castle.use_nodes = True
    bsdf_c = m_castle.node_tree.nodes.get('Principled BSDF')
    if bsdf_c:
        bsdf_c.inputs['Base Color'].default_value = (0.42, 0.10, 0.06, 1.0)
        bsdf_c.inputs['Roughness'].default_value = 0.42
    mats['wood_castle'] = m_castle

    # 3. Mái ngói âm dương cổ (Ngói đất nung xám đen tráng men mờ thời Đường/Ngũ Đại)
    m_roof = bpy.data.materials.new('Mat_NamHan_NgoiAmDuong')
    m_roof.diffuse_color = (0.18, 0.18, 0.20, 1.0)
    m_roof.use_nodes = True
    nodes_r = m_roof.node_tree.nodes
    links_r = m_roof.node_tree.links
    nodes_r.clear()
    out_r = nodes_r.new('ShaderNodeOutputMaterial')
    bsdf_r = nodes_r.new('ShaderNodeBsdfPrincipled')
    bsdf_r.inputs['Roughness'].default_value = 0.65
    links_r.new(bsdf_r.outputs['BSDF'], out_r.inputs['Surface'])
    tc_r = nodes_r.new('ShaderNodeTexCoord')
    n_r = nodes_r.new('ShaderNodeTexNoise')
    n_r.inputs['Scale'].default_value = 45.0
    n_r.inputs['Detail'].default_value = 6.0
    links_r.new(tc_r.outputs['Object'], n_r.inputs['Vector'])
    cr_r = nodes_r.new('ShaderNodeValToRGB')
    cr_r.color_ramp.elements[0].position = 0.3
    cr_r.color_ramp.elements[0].color = (0.12, 0.12, 0.14, 1.0)
    cr_r.color_ramp.elements[1].position = 0.7
    cr_r.color_ramp.elements[1].color = (0.24, 0.24, 0.26, 1.0)
    links_r.new(n_r.outputs['Fac'], cr_r.inputs['Fac'])
    links_r.new(cr_r.outputs['Color'], bsdf_r.inputs['Base Color'])
    mats['roof'] = m_roof

    # 4. Vải buồm nan hình chữ nhật màu vàng thổ hoàng
    m_sail = bpy.data.materials.new('Mat_NamHan_BuomNan_ThoHoang')
    m_sail.diffuse_color = (0.72, 0.62, 0.42, 1.0)
    m_sail.use_nodes = True
    ns = m_sail.node_tree.nodes
    ls = m_sail.node_tree.links
    ns.clear()
    out_s = ns.new('ShaderNodeOutputMaterial')
    bsdf_s = ns.new('ShaderNodeBsdfPrincipled')
    bsdf_s.inputs['Roughness'].default_value = 0.82
    ls.new(bsdf_s.outputs['BSDF'], out_s.inputs['Surface'])
    tc_s = ns.new('ShaderNodeTexCoord')
    n_s = ns.new('ShaderNodeTexNoise')
    n_s.inputs['Scale'].default_value = 50.0
    n_s.inputs['Detail'].default_value = 8.0
    ls.new(tc_s.outputs['Object'], n_s.inputs['Vector'])
    cr_s = ns.new('ShaderNodeValToRGB')
    cr_s.color_ramp.elements[0].position = 0.3
    cr_s.color_ramp.elements[0].color = (0.62, 0.52, 0.35, 1.0)
    cr_s.color_ramp.elements[1].position = 0.75
    cr_s.color_ramp.elements[1].color = (0.78, 0.68, 0.48, 1.0)
    ls.new(n_s.outputs['Fac'], cr_s.inputs['Fac'])
    ls.new(cr_s.outputs['Color'], bsdf_s.inputs['Base Color'])
    mats['sail'] = m_sail

    # 5. Khiên da trâu bọc sắt hình chữ nhật
    m_shield = bpy.data.materials.new('Mat_NamHan_KhienDaTrau')
    m_shield.diffuse_color = (0.35, 0.25, 0.18, 1.0)
    m_shield.use_nodes = True
    bsdf_sh = m_shield.node_tree.nodes.get('Principled BSDF')
    if bsdf_sh:
        bsdf_sh.inputs['Base Color'].default_value = (0.28, 0.20, 0.14, 1.0)
        bsdf_sh.inputs['Roughness'].default_value = 0.60
    mats['shield'] = m_shield

    # 6. Sắt đen vũ khí / Nỏ máy / Đinh tán
    m_iron = bpy.data.materials.new('Mat_NamHan_SatDen_VuKhi')
    m_iron.diffuse_color = (0.12, 0.12, 0.14, 1.0)
    m_iron.use_nodes = True
    bsdf_i = m_iron.node_tree.nodes.get('Principled BSDF')
    if bsdf_i:
        bsdf_i.inputs['Base Color'].default_value = (0.10, 0.10, 0.12, 1.0)
        bsdf_i.inputs['Metallic'].default_value = 0.94
        bsdf_i.inputs['Roughness'].default_value = 0.38
    mats['iron'] = m_iron

    # 7. Cờ soái Nam Hán thêu đại tự đỏ son
    m_flag = bpy.data.materials.new('Mat_NamHan_CoSoai')
    m_flag.diffuse_color = (0.85, 0.15, 0.10, 1.0)
    m_flag.use_nodes = True
    bsdf_f = m_flag.node_tree.nodes.get('Principled BSDF')
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.78, 0.12, 0.08, 1.0)
        bsdf_f.inputs['Roughness'].default_value = 0.70
    mats['flag'] = m_flag

    # 8. Vàng đồng / Hoa văn
    m_gold = bpy.data.materials.new('Mat_NamHan_DongHoangKim')
    m_gold.diffuse_color = (0.85, 0.68, 0.18, 1.0)
    m_gold.use_nodes = True
    bsdf_g = m_gold.node_tree.nodes.get('Principled BSDF')
    if bsdf_g:
        bsdf_g.inputs['Base Color'].default_value = (0.82, 0.65, 0.15, 1.0)
        bsdf_g.inputs['Metallic'].default_value = 0.85
        bsdf_g.inputs['Roughness'].default_value = 0.32
    mats['gold'] = m_gold

    return mats

def add_smooth_modifiers(obj, solidify_thickness=0.10, bevel_width=0.02, subsurf_levels=1):
    if solidify_thickness > 0:
        sol = obj.modifiers.new("Solidify", 'SOLIDIFY')
        sol.thickness = solidify_thickness
        sol.offset = 0.0
    if bevel_width > 0:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(40)
    if subsurf_levels > 0:
        sub = obj.modifiers.new("Subsurf", 'SUBSURF')
        sub.levels = subsurf_levels
        sub.render_levels = subsurf_levels + 1

def build_southern_han_tower_warship(mats, location=Vector((0, 0, 0)), rotation_z=0.0):
    '''
    DỰNG LÂU THUYỀN CHIẾN HẠM NAM HÁN SIÊU THỰC VỚI KỸ NGHỆ KIẾN TRÚC CỔ:
    - Thân tàu ván mạn dày, có gờ nẹp dọc (Rubbing strakes) và đinh tán sắt.
    - Lâu đài 2 tầng có hệ thống cột gỗ tròn, dầm xà, vách rãnh và cửa sổ chấn song.
    - Hệ thống Đẩu Củng (Dou-gong) chạm khắc nâng đỡ mái.
    - Mái ngói âm dương 3D với hàng trăm ngói ống úp và diềm trích thủy thật.
    - Lan can bao lơn có hàng con tiện gỗ tinh xảo quanh tầng 2.
    - Lá cờ soái Nam Hán lượn sóng vải mềm mại phất phới theo gió.
    '''
    root = bpy.data.objects.new("LauThuyen_NamHan_HoangThao_Master", None)
    root.location = location
    root.rotation_euler = Euler((0, 0, rotation_z))
    bpy.context.collection.objects.link(root)

    # 1. THÂN TÀU ĐÁY CHỮ V SÂU (24M x 5.6M x 3.6M)
    mesh_hull = bpy.data.meshes.new("NamHan_Hull_Mesh")
    bm_hull = bmesh.new()

    stations_x = [-12.0, -10.0, -7.5, -4.5, -1.5,  1.5,  4.5,  7.5, 10.0, 11.5, 12.0]
    beam_w     = [  1.2,   2.1,  2.6,  2.8,  2.8,  2.7,  2.6,  2.3,  1.8,  1.3,  0.8]
    sheer_z    = [  2.8,   2.3,  1.9,  1.7,  1.6,  1.6,  1.7,  1.9,  2.2,  2.6,  2.9]
    keel_z     = [ -0.8,  -1.5, -2.1, -2.3, -2.4, -2.4, -2.3, -2.0, -1.5, -0.9, -0.2]

    rings = []
    for i in range(len(stations_x)):
        x = stations_x[i]
        bw = beam_w[i]
        sz = sheer_z[i]
        kz = keel_z[i]

        pts = [
            Vector((x, -bw, sz)),
            Vector((x, -bw * 0.96, kz + (sz-kz)*0.65)),
            Vector((x, -bw * 0.75, kz + (sz-kz)*0.30)),
            Vector((x, -bw * 0.25, kz + (sz-kz)*0.08)),
            Vector((x,  0.0,       kz)),
            Vector((x,  bw * 0.25, kz + (sz-kz)*0.08)),
            Vector((x,  bw * 0.75, kz + (sz-kz)*0.30)),
            Vector((x,  bw * 0.96, kz + (sz-kz)*0.65)),
            Vector((x,  bw, sz))
        ]
        ring_verts = [bm_hull.verts.new(p) for p in pts]
        rings.append(ring_verts)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for j in range(len(r1) - 1):
            bm_hull.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])

    bm_hull.faces.new(rings[-1])
    bm_hull.faces.new(rings[0])

    bm_hull.to_mesh(mesh_hull)
    bm_hull.free()

    obj_hull = bpy.data.objects.new("NamHan_Hull", mesh_hull)
    obj_hull.parent = root
    obj_hull.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_hull)
    for p in obj_hull.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_hull, solidify_thickness=0.12, bevel_width=0.025, subsurf_levels=1)

    # ĐƯỜNG GỜ NẸP VÁN MẠN DỌC & ĐINH TÁN SẮT (RUBBING STRAKES & RIVETS)
    mesh_strakes = bpy.data.meshes.new("NamHan_Strakes_Mesh")
    bm_str = bmesh.new()
    for side in [-1, 1]:
        for h_ratio in [0.35, 0.65, 0.92]:
            strake_pts = []
            for i in range(len(stations_x)):
                x = stations_x[i]
                bw = beam_w[i] + 0.04
                sz = sheer_z[i]
                kz = keel_z[i]
                cur_z = kz + (sz - kz) * h_ratio
                strake_pts.append(Vector((x, side * bw, cur_z)))

            for k in range(len(strake_pts) - 1):
                p_a = strake_pts[k]
                p_b = strake_pts[k+1]
                mid_pt = (p_a + p_b) * 0.5
                d_vec = p_b - p_a
                length = d_vec.length
                up_v = Vector((0, 0, 1))
                ax = up_v.cross(d_vec.normalized())
                if ax.length > 1e-4:
                    ang = math.acos(max(-1.0, min(1.0, up_v.dot(d_vec.normalized()))))
                    rmat = Matrix.Rotation(ang, 4, ax.normalized())
                else:
                    rmat = Matrix.Identity(4)

                # Nẹp ván gỗ nổi gờ
                bmesh.ops.create_cube(
                    bm_str, size=1.0,
                    matrix=Matrix.Translation(mid_pt) @ rmat @ Matrix.Diagonal(Vector((0.08, 0.08, length, 1.0)))
                )
                # Đinh tán sắt tròn
                bmesh.ops.create_cone(
                    bm_str, cap_ends=True, segments=6,
                    radius1=0.03, radius2=0.03, depth=0.04,
                    matrix=Matrix.Translation(mid_pt + Vector((0, side * 0.05, 0)))
                )

    bm_str.to_mesh(mesh_strakes)
    bm_str.free()
    obj_str = bpy.data.objects.new("NamHan_GờNep_VanMan", mesh_strakes)
    obj_str.parent = root
    obj_str.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_str)
    for p in obj_str.data.polygons:
        p.use_smooth = True

    # 2. SÀN BOONG CHÍNH
    mesh_deck = bpy.data.meshes.new("NamHan_Deck_Mesh")
    bm_deck = bmesh.new()
    deck_rings = []
    for i in range(len(stations_x)):
        x = stations_x[i]
        bw = beam_w[i] * 0.92
        dz = sheer_z[i] * 0.85
        v_l = bm_deck.verts.new(Vector((x, -bw, dz)))
        v_r = bm_deck.verts.new(Vector((x,  bw, dz)))
        deck_rings.append((v_l, v_r))

    for i in range(len(deck_rings) - 1):
        l1, r1 = deck_rings[i]
        l2, r2 = deck_rings[i+1]
        bm_deck.faces.new([l1, r1, r2, l2])

    bm_deck.to_mesh(mesh_deck)
    bm_deck.free()
    obj_deck = bpy.data.objects.new("NamHan_MainDeck", mesh_deck)
    obj_deck.parent = root
    obj_deck.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_deck)
    add_smooth_modifiers(obj_deck, solidify_thickness=0.06, bevel_width=0.015, subsurf_levels=0)

    # 3. LÂU ĐÀI 2 TẦNG NGUY NGA VỚI KIẾN TRÚC CỔ ĐIỂN THỰC THỤ
    c1_x_min, c1_x_max = -6.5, 1.5
    c1_x_mid = (c1_x_min + c1_x_max) * 0.5
    c1_len = c1_x_max - c1_x_min # 8.0m
    c1_w = 3.8
    c1_z_bot = 1.6
    c1_z_height = 2.0 # Lên đến z = 3.6m

    c2_x_min, c2_x_max = -4.8, 0.2
    c2_x_mid = (c2_x_min + c2_x_max) * 0.5
    c2_len = c2_x_max - c2_x_min # 5.0m
    c2_w = 2.8
    c2_z_bot = 3.6
    c2_z_height = 1.6 # Lên đến z = 5.2m

    # --- A. KHUNG CỘT GỖ VÀ CỬA CHẤN SONG TẦNG 1 & TẦNG 2 ---
    mesh_timber = bpy.data.meshes.new("NamHan_TimberFramework_Mesh")
    bm_tim = bmesh.new()

    # Vách & Cửa chấn song Tầng 1 (Lư)
    generate_timber_wall_with_lattice_windows(bm_tim, c1_x_mid, 0.0, c1_z_bot, c1_z_height, c1_len, c1_w)
    # Hệ Đẩu Củng đỡ sàn Tầng 2
    generate_dougong_brackets(bm_tim, c1_x_mid, 0.0, c1_z_bot + c1_z_height, c1_len, c1_w)

    # Lan can bao lơn có con tiện chạy quanh sàn Tầng 2 (Phi Lư)
    generate_balustrade(bm_tim, c1_x_mid, 0.0, c1_z_bot + c1_z_height, c1_len + 0.3, c1_w + 0.3, rail_height=0.75)

    # Vách & Cửa chấn song Tầng 2 (Phi Lư - Đài chỉ huy)
    generate_timber_wall_with_lattice_windows(bm_tim, c2_x_mid, 0.0, c2_z_bot, c2_z_height, c2_len, c2_w)
    # Hệ Đẩu Củng đỡ mái ngói Tầng 2
    generate_dougong_brackets(bm_tim, c2_x_mid, 0.0, c2_z_bot + c2_z_height, c2_len, c2_w)

    bm_tim.to_mesh(mesh_timber)
    bm_tim.free()
    obj_tim = bpy.data.objects.new("NamHan_KienTruc_ViKeo_CuaSong", mesh_timber)
    obj_tim.parent = root
    obj_tim.data.materials.append(mats['wood_castle'])
    bpy.context.collection.objects.link(obj_tim)
    for p in obj_tim.data.polygons:
        p.use_smooth = True

    # --- B. MÁI NGÓI ÂM DƯƠNG 3D VỚI HÀNG TRĂM VIÊN NGÓI VÀ DIỀM TRÍCH THỦY ---
    mesh_roof_tiles = bpy.data.meshes.new("NamHan_RoofTiles_3D_Mesh")
    bm_rf = bmesh.new()

    # Mái chính Tầng 2
    generate_tile_roof(
        bm_rf,
        x_center=c2_x_mid, y_center=0.0,
        z_base=c2_z_bot + c2_z_height,
        length_x=c2_len, width_y=c2_w,
        roof_height=1.15, overhang=0.55
    )

    bm_rf.to_mesh(mesh_roof_tiles)
    bm_rf.free()
    obj_rf = bpy.data.objects.new("NamHan_MaiNgoi_AmDuong_3D", mesh_roof_tiles)
    obj_rf.parent = root
    obj_rf.data.materials.append(mats['roof'])
    bpy.context.collection.objects.link(obj_rf)
    for p in obj_rf.data.polygons:
        p.use_smooth = True

    # --- C. LÁ CỜ SOÁI NAM HÁN VẢI LƯỢN SÓNG KHÍ ĐỘNG HỌC ---
    mesh_flag_cloth = bpy.data.meshes.new("NamHan_Flag_Cloth_Mesh")
    bm_fl = bmesh.new()

    pole_z_top = c2_z_bot + c2_z_height + 1.15 + 2.8
    # Cột cờ gỗ
    bmesh.ops.create_cone(
        bm_fl, cap_ends=True, segments=10,
        radius1=0.05, radius2=0.02, depth=3.2,
        matrix=Matrix.Translation(Vector((c2_x_mid, 0, pole_z_top - 1.6)))
    )
    # Lá cờ lượn sóng
    generate_rippling_cloth_flag(
        bm_fl,
        pole_pos=Vector((c2_x_mid, 0.05, pole_z_top - 0.2)),
        flag_w=2.8, flag_h=1.8,
        segs_x=24, segs_z=14
    )

    bm_fl.to_mesh(mesh_flag_cloth)
    bm_fl.free()
    obj_fl = bpy.data.objects.new("NamHan_CoSoai_VaiSong", mesh_flag_cloth)
    obj_fl.parent = root
    obj_fl.data.materials.append(mats['flag'])
    bpy.context.collection.objects.link(obj_fl)
    for p in obj_fl.data.polygons:
        p.use_smooth = True

    sol_fl = obj_fl.modifiers.new("Solidify", 'SOLIDIFY')
    sol_fl.thickness = 0.008
    sub_fl = obj_fl.modifiers.new("Subsurf", 'SUBSURF')
    sub_fl.levels = 1

    # 4. HÀNG KHIÊN DA TRÂU BỌC SẮT NẸP CHỮ THẬP
    mesh_shields = bpy.data.meshes.new("NamHan_Shields_Mesh")
    bm_shields = bmesh.new()

    for side in [-1, 1]:
        for kx in [-10.5, -9.0, -7.5, -3.5, -1.5, 0.5, 2.5, 4.5, 6.5, 8.5, 10.0]:
            bw = 2.7 if abs(kx) < 6.0 else 1.9
            sz = 1.9 + (abs(kx) / 12.0) ** 1.5 * 0.8
            pos = Vector((kx, side * (bw + 0.08), sz + 0.4))
            mat_sh = Matrix.Translation(pos) @ Matrix.Diagonal(Vector((0.70, 0.06, 0.95, 1.0)))
            bmesh.ops.create_cube(bm_shields, size=1.0, matrix=mat_sh)
            mat_cross = Matrix.Translation(pos + Vector((0, side * 0.04, 0))) @ Matrix.Diagonal(Vector((0.72, 0.03, 0.12, 1.0)))
            bmesh.ops.create_cube(bm_shields, size=1.0, matrix=mat_cross)

    bm_shields.to_mesh(mesh_shields)
    bm_shields.free()
    obj_shields = bpy.data.objects.new("NamHan_HangKhien_DaTrau", mesh_shields)
    obj_shields.parent = root
    obj_shields.data.materials.append(mats['shield'])
    bpy.context.collection.objects.link(obj_shields)
    add_smooth_modifiers(obj_shields, solidify_thickness=0, bevel_width=0.015, subsurf_levels=0)

    # 5. SÀNG NỎ (CHUANG NU)
    mesh_ballista = bpy.data.meshes.new("NamHan_ChuangNu_Mesh")
    bm_bal = bmesh.new()

    for b_pos in [Vector((9.5, 0, 2.3)), Vector((1.0, 0, 3.8))]:
        bmesh.ops.create_cone(bm_bal, cap_ends=True, segments=12, radius1=0.6, radius2=0.6, depth=0.35, matrix=Matrix.Translation(b_pos))
        bmesh.ops.create_cube(bm_bal, size=1.0, matrix=Matrix.Translation(b_pos + Vector((0, 0, 0.35))) @ Matrix.Diagonal(Vector((2.2, 0.25, 0.20, 1.0))))
        rot_bow = Matrix.Rotation(math.radians(90), 4, 'X')
        mat_bow = Matrix.Translation(b_pos + Vector((0.8, 0, 0.35))) @ Matrix.Diagonal(Vector((0.15, 2.4, 0.15, 1.0)))
        bmesh.ops.create_cube(bm_bal, size=1.0, matrix=mat_bow)
        bmesh.ops.create_cone(bm_bal, cap_ends=True, segments=8, radius1=0.03, radius2=0.005, depth=1.8,
                              matrix=Matrix.Translation(b_pos + Vector((0.6, 0, 0.48))) @ Matrix.Rotation(math.radians(90), 4, 'Y'))

    bm_bal.to_mesh(mesh_ballista)
    bm_bal.free()
    obj_bal = bpy.data.objects.new("NamHan_SangNo_ChuangNu", mesh_ballista)
    obj_bal.parent = root
    obj_bal.data.materials.append(mats['iron'])
    bpy.context.collection.objects.link(obj_bal)

    # 6. CỘT BUỒM & CÁNH BUỒM NAN CHỮ NHẬT
    masts_config = [
        ("Cot_Chinh", 4.2, 10.5, 4.8, 7.5, 3.2, 18.0),
        ("Cot_Mui",   8.5,  8.2, 3.8, 5.8, 2.8, 15.0),
    ]

    for m_name, mx, mh, sw, sh, sz_bot, s_ang in masts_config:
        mesh_m = bpy.data.meshes.new(f"NamHan_{m_name}_Mesh")
        bm_m = bmesh.new()
        bmesh.ops.create_cone(
            bm_m, cap_ends=True, segments=16,
            radius1=0.22, radius2=0.12, depth=mh,
            matrix=Matrix.Translation(Vector((mx, 0, mh*0.5 + 1.2)))
        )
        bm_m.to_mesh(mesh_m)
        bm_m.free()
        obj_m = bpy.data.objects.new(f"NamHan_{m_name}", mesh_m)
        obj_m.parent = root
        obj_m.data.materials.append(mats['wood_hull'])
        bpy.context.collection.objects.link(obj_m)
        for p in obj_m.data.polygons:
            p.use_smooth = True

        mesh_s = bpy.data.meshes.new(f"NamHan_BuomNan_{m_name}_Mesh")
        bm_s = bmesh.new()

        rot_s = Matrix.Rotation(math.radians(s_ang), 4, 'Z')
        wind_n = (rot_s @ Vector((0, 1, 0))).normalized()
        pivot = Vector((mx, 0.20, 0))

        num_battens = 6
        for bi in range(num_battens):
            tz = bi / (num_battens - 1)
            bz = sz_bot + tz * sh
            p_s = pivot + rot_s @ Vector((-0.2, 0, bz))
            p_e = pivot + rot_s @ Vector((-0.2 - sw, 0, bz))
            mid = (p_s + p_e) * 0.5
            l_b = (p_e - p_s).length
            dir_b = (p_e - p_s).normalized()
            up = Vector((0, 0, 1))
            ax = up.cross(dir_b).normalized()
            ang = math.acos(max(-1.0, min(1.0, up.dot(dir_b))))
            mat_b = Matrix.Translation(mid) @ Matrix.Rotation(ang, 4, ax)
            bmesh.ops.create_cone(bm_s, cap_ends=True, segments=10, radius1=0.04, radius2=0.035, depth=l_b, matrix=mat_b)

        u_segs, v_segs = 12, 4
        for bi in range(num_battens - 1):
            bz0 = sz_bot + (bi / (num_battens - 1)) * sh
            bz1 = sz_bot + ((bi+1) / (num_battens - 1)) * sh
            grid = []
            for vi in range(v_segs + 1):
                tv = vi / v_segs
                curr_z = bz0 + tv * (bz1 - bz0)
                row = []
                for ui in range(u_segs + 1):
                    tu = ui / u_segs
                    cur_rel_x = -0.2 - tu * sw
                    base_p = pivot + rot_s @ Vector((cur_rel_x, 0, curr_z))
                    c_disp = math.sin(tu * math.pi) * math.sin(tv * math.pi) * 0.22
                    disp_p = base_p + wind_n * c_disp
                    row.append(bm_s.verts.new(disp_p))
                grid.append(row)

            for vi in range(v_segs):
                for ui in range(u_segs):
                    bm_s.faces.new([grid[vi][ui], grid[vi][ui+1], grid[vi+1][ui+1], grid[vi+1][ui]])

        bm_s.to_mesh(mesh_s)
        bm_s.free()
        obj_s = bpy.data.objects.new(f"NamHan_BuomNan_{m_name}", mesh_s)
        obj_s.parent = root
        obj_s.data.materials.append(mats['sail'])
        bpy.context.collection.objects.link(obj_s)
        for p in obj_s.data.polygons:
            p.use_smooth = True
        add_smooth_modifiers(obj_s, solidify_thickness=0.015, bevel_width=0, subsurf_levels=1)

    # 7. 24 MÁI CHÈO HẠNG NẶNG
    mesh_oars = bpy.data.meshes.new("NamHan_HeavyOars_Mesh")
    bm_oars = bmesh.new()

    for side in [-1, 1]:
        for kx in [-9.5, -8.0, -6.5, -5.0, -3.5, -2.0, -0.5, 1.0, 2.5, 4.0, 5.5, 7.0]:
            bw = 2.6 if abs(kx) < 5.0 else 2.1
            oz = 0.6
            pos_port = Vector((kx, side * bw, oz))
            rot_oar = Matrix.Rotation(math.radians(-35 * side), 4, 'X') @ Matrix.Rotation(math.radians(10), 4, 'Z')
            mat_shaft = Matrix.Translation(pos_port + Vector((0, side * 1.5, -0.8))) @ rot_oar @ Matrix.Diagonal(Vector((0.07, 0.07, 4.2, 1.0)))
            bmesh.ops.create_cone(bm_oars, cap_ends=True, segments=10, radius1=0.5, radius2=0.5, depth=1.0, matrix=mat_shaft)
            mat_blade = Matrix.Translation(pos_port + Vector((0, side * 3.0, -1.8))) @ rot_oar @ Matrix.Diagonal(Vector((0.03, 0.28, 1.4, 1.0)))
            bmesh.ops.create_cube(bm_oars, size=1.0, matrix=mat_blade)

    bm_oars.to_mesh(mesh_oars)
    bm_oars.free()
    obj_oars = bpy.data.objects.new("NamHan_24MaiCheo_HangNang", mesh_oars)
    obj_oars.parent = root
    obj_oars.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_oars)
    for p in obj_oars.data.polygons:
        p.use_smooth = True

    return root
