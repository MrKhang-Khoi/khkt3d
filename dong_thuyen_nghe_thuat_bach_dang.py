import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ==============================================================================
# 1. BẢNG VẬT LIỆU CHUẨN LỊCH SỬ THẾ KỶ 10 (PBR + SOLID VIEWPORT)
# ==============================================================================

def create_pbr_mat(name, rgba, roughness=0.5, metallic=0.0, wave_scale=4.0, bump_strength=0.25):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    # Vân thớ gỗ / vải tự nhiên
    tex = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.5, 0.1, 4.0)
    links.new(tex.outputs['Object'], mapping.inputs['Vector'])

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = wave_scale
    wave.inputs['Distortion'].default_value = 1.4
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = 0.04
    links.new(wave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_river_mat():
    mat = bpy.data.materials.new("Mat_BachDang_River")
    mat.diffuse_color = (0.05, 0.20, 0.20, 0.85)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.03, 0.16, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.05
        bsdf.inputs['Metallic'].default_value = 0.12
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.82
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.82
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
# 2. KỸ NGHỆ ĐÓNG TÀU THỰC TẾ: THUẬT TOÁN LOFTING QUA CÁC MẶT CẮT SƯỜN THUYỀN
# ==============================================================================

def build_lofted_viet_warship(mat_wood, mat_deck, mat_sail, mat_shield, mat_red, mat_gold):
    """
    THUẬT TOÁN ĐÓNG TÀU CHUYÊN NGHIỆP (NAVAL CROSS-SECTION LOFTING):
    Không nặn từ khối hộp primitive, mà định nghĩa 9 mặt cắt sườn thuyền (Frame Stations)
    từ mũi đến đuôi, sau đó kết nối (Bridge Edge Loops) tạo nên thân thuyền uốn cong hoàn hảo!
    """
    root = bpy.data.objects.new("Thuyen_NgoQuyen_Lofted_Master", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 2.0
    bpy.context.collection.objects.link(root)

    # 1. THÂN THUYỀN LOFTING
    hull_mesh = bpy.data.meshes.new("Lofted_Hull_Mesh")
    hull_obj = bpy.data.objects.new("Lofted_Hull", hull_mesh)
    bpy.context.collection.objects.link(hull_obj)
    hull_obj.parent = root

    bm = bmesh.new()

    # 9 Mặt cắt sườn từ Đuôi (-7m) tới Mũi (+7.5m):
    # Mỗi mặt cắt gồm: (y, half_width, flare_height, keel_drop, sheer_lift)
    stations = [
        (-7.0, 0.15, 0.70, -0.15, 0.75),  # Đuôi én nhọn ngửa cao
        (-5.5, 0.75, 0.85, -0.35, 0.45),  # Sườn đuôi
        (-3.5, 1.02, 0.95, -0.50, 0.25),  # Thân sau
        (-1.5, 1.15, 1.00, -0.55, 0.15),  # Giữa lườn sau
        ( 0.0, 1.18, 1.00, -0.55, 0.10),  # Giữa lườn trung tâm (nở rộng nhất)
        ( 1.5, 1.15, 1.00, -0.55, 0.15),  # Giữa lườn trước
        ( 3.5, 1.00, 0.95, -0.50, 0.28),  # Thân trước
        ( 5.5, 0.65, 0.85, -0.35, 0.65),  # Sườn mũi
        ( 7.5, 0.08, 0.60, -0.10, 1.25),  # Mũi nhọn vút cao kiêu hãnh
    ]

    loops = []
    points_per_ring = 14 # Số điểm trên mỗi vành mặt cắt chữ U

    for y, w, h, keel_z, sheer_z in stations:
        ring_verts = []
        for i in range(points_per_ring):
            t = i / (points_per_ring - 1) # 0.0 (mạn trái) -> 0.5 (đáy) -> 1.0 (mạn phải)
            ang = (t - 0.5) * math.pi # -pi/2 đến +pi/2
            
            # X: Từ -w đến +w theo hình elip
            x = math.sin(ang) * w
            
            # Z: Đáy nông uốn hình chữ U phẳng (shallow arc), mạn vươn lên sheer_z
            # Tại t = 0 và t = 1 (mép be thuyền): z = sheer_z
            # Tại t = 0.5 (sống đáy thuyền): z = keel_z
            u_depth = math.cos(ang) # 0 ở mép, 1 ở đáy
            z = sheer_z - u_depth * (sheer_z - keel_z)

            v = bm.verts.new((x, y, z))
            ring_verts.append(v)
        loops.append(ring_verts)

    bm.verts.ensure_lookup_table()

    # Nối các mặt cắt sườn thuyền (Bridge Loops)
    for s_idx in range(len(stations) - 1):
        r1 = loops[s_idx]
        r2 = loops[s_idx + 1]
        for p_idx in range(points_per_ring - 1):
            v1 = r1[p_idx]
            v2 = r1[p_idx + 1]
            v3 = r2[p_idx + 1]
            v4 = r2[p_idx]
            bm.faces.new((v1, v2, v3, v4))

    # Đùn dầy vỏ gỗ ván mạn thành thuyền 8cm
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.08)

    hull_mesh.materials.append(mat_wood)
    bm.to_mesh(hull_mesh)
    bm.free()
    apply_smooth(hull_obj)

    # Thêm Subdivision Surface để thân thuyền lượn sóng tự nhiên
    sub = hull_obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # 2. MŨI THUYỀN CHẠM KHẮC HÌNH ĐẦU CHIM LẠC / HOA VĂN ĐÔNG SƠN
    prow_mesh = bpy.data.meshes.new("NgoQuyen_Prow_Mesh")
    prow_obj = bpy.data.objects.new("Prow_Sculpt", prow_mesh)
    bpy.context.collection.objects.link(prow_obj)
    prow_obj.parent = root
    prow_obj.location = (0, 7.5, 1.25)
    prow_obj.rotation_euler = Euler((math.radians(-35), 0, 0))

    bm = bmesh.new()
    # Đầu chim Lạc vươn cao rẽ sóng
    make_cone(bm, 0.12, 0.03, 1.6, segments=12)
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.14, 
                             matrix=Matrix.Translation((0, 0, 1.6)))
    prow_mesh.materials.append(mat_gold)
    prow_mesh.materials.append(mat_wood)
    bm.to_mesh(prow_mesh)
    bm.free()
    apply_smooth(prow_obj)

    # 3. NỘI THẤT: CÁC XÀ NGANG SƯỜN THUYỀN (RIBS & THWARTS)
    ribs_mesh = bpy.data.meshes.new("Internal_Ribs_Mesh")
    ribs_obj = bpy.data.objects.new("Internal_Ribs", ribs_mesh)
    bpy.context.collection.objects.link(ribs_obj)
    ribs_obj.parent = root

    bm = bmesh.new()
    for y_rib in [-5.0, -3.8, -2.6, -1.4, -0.2, 1.0, 2.2, 3.4, 4.6]:
        w = 1.15 * math.cos((y_rib / 7.25) * math.pi * 0.45)
        if w > 0.3:
            # Xà ngang ngồi chèo
            bmesh.ops.create_cube(bm, size=1.0, 
                                  matrix=Matrix.Translation((0, y_rib, 0.05)) @ 
                                         Matrix.Scale(w * 1.9, 4, Vector((1,0,0))) @ 
                                         Matrix.Scale(0.24, 4, Vector((0,1,0))) @ 
                                         Matrix.Scale(0.06, 4, Vector((0,0,1))))
    ribs_mesh.materials.append(mat_deck)
    bm.to_mesh(ribs_mesh)
    bm.free()
    apply_smooth(ribs_obj)

    # 4. HỆ THỐNG 16 MÁI CHÈO & CỌC CHÈO (OARS & ROWING PINS)
    oar_mesh = bpy.data.meshes.new("Rowing_Oars_Mesh")
    oar_obj = bpy.data.objects.new("Rowing_Oars", oar_mesh)
    bpy.context.collection.objects.link(oar_obj)
    oar_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-4, 5):
            y_pos = idx * 1.15
            w = 1.15 * math.cos((y_pos / 7.25) * math.pi * 0.45)
            x_g = side * (w + 0.04)
            z_g = 0.22 + 0.32 * ((y_pos / 7.25) ** 2)

            # Cọc chèo gỗ
            make_cylinder(bm, 0.025, 0.22, segments=8, 
                          matrix=Matrix.Translation((x_g, y_pos, z_g + 0.1)))

            # Cán chèo nghiêng xuống nước
            rot_oar = Euler((math.radians(side * 28), 0, math.radians(side * 76))).to_matrix().to_4x4()
            trans_oar = Matrix.Translation((x_g, y_pos, z_g + 0.08))
            make_cylinder(bm, 0.035, 2.5, segments=10, matrix=trans_oar @ rot_oar)

            # Bản chèo dẹt hình lá sen
            blade_m = trans_oar @ rot_oar @ Matrix.Translation((0, 0, 1.15)) @ Matrix.Scale(0.20, 4, Vector((1,0,0))) @ Matrix.Scale(0.02, 4, Vector((0,1,0))) @ Matrix.Scale(0.70, 4, Vector((0,0,1)))
            bmesh.ops.create_cube(bm, size=1.0, matrix=blade_m)

    oar_mesh.materials.append(mat_wood)
    bm.to_mesh(oar_mesh)
    bm.free()
    apply_smooth(oar_obj)

    # 5. CỘT BUỒM TRE & BUỒM NAN TRE CÁNH DƠI (BATTEN SAIL)
    mast_mesh = bpy.data.meshes.new("Batten_Mast_Mesh")
    mast_obj = bpy.data.objects.new("Batten_Mast", mast_mesh)
    bpy.context.collection.objects.link(mast_obj)
    mast_obj.parent = root
    mast_obj.location = (0, 1.2, 0.0)

    bm = bmesh.new()
    make_cone(bm, 0.12, 0.065, 6.4, segments=16, matrix=Matrix.Translation((0, 0, 3.2)))

    # Cánh buồm nan uốn cong 3D đón gió
    rot_sail = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=2.2, 
                          matrix=Matrix.Translation((0, 0.28, 3.2)) @ rot_sail)
    for v in bm.verts[-169:]:
        v.co.x *= 0.92
        v.co.z = v.co.z * 0.96 + 3.2
        v.co.y += math.sin((v.co.z - 1.2) / 2.2 * math.pi) * 0.45

    # 5 Thanh nẹp tre ngang giữ buồm (Battens)
    for b_idx in range(5):
        z_b = 1.5 + b_idx * 0.8
        y_b = 0.28 + math.sin((z_b - 1.2) / 2.2 * math.pi) * 0.45
        make_cylinder(bm, 0.03, 2.0, segments=8, 
                      matrix=Matrix.Translation((0, y_b, z_b)) @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4())

    mast_mesh.materials.append(mat_wood)
    mast_mesh.materials.append(mat_sail)
    for p in mast_mesh.polygons:
        if p.index >= 32 and p.index < 200:
            p.material_index = 1
    bm.to_mesh(mast_mesh)
    bm.free()
    apply_smooth(mast_obj)

    # 6. DÂY CHẰNG BUỒM (RIGGING)
    curve_data = bpy.data.curves.new("Cords_Curve", 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.015
    curve_data.bevel_resolution = 2
    curve_obj = bpy.data.objects.new("Rigging_Cords", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.parent = root

    for side in [0.95, -0.95]:
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(1)
        spline.bezier_points[0].co = Vector((0, 1.2, 6.0))
        spline.bezier_points[0].handle_left_type = 'AUTO'
        spline.bezier_points[0].handle_right_type = 'AUTO'
        spline.bezier_points[1].co = Vector((side, 0.0, 0.35))
        spline.bezier_points[1].handle_left_type = 'AUTO'
        spline.bezier_points[1].handle_right_type = 'AUTO'
    curve_data.materials.append(mat_wood)

    # 7. KHIÊN MÂY ĐAN TRÒN VỒNG 3D HỌA TIẾT ĐỎ SON
    shield_mesh = bpy.data.meshes.new("Shields_Mesh")
    shield_obj = bpy.data.objects.new("Convex_Shields", shield_mesh)
    bpy.context.collection.objects.link(shield_obj)
    shield_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-3, 4):
            y_pos = idx * 1.45
            w = 1.15 * math.cos((y_pos / 7.25) * math.pi * 0.45)
            x_pos = side * (w + 0.06)
            z_pos = 0.32 + 0.32 * ((y_pos / 7.25) ** 2)

            rot_s = Euler((0, math.radians(side * 90), 0)).to_matrix().to_4x4()
            trans_s = Matrix.Translation((x_pos, y_pos, z_pos))
            # Khiên hình vồng mặt trời
            bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.32, 
                                     matrix=trans_s @ rot_s @ Matrix.Scale(0.25, 4, Vector((0,0,1))))

    shield_mesh.materials.append(mat_shield)
    bm.to_mesh(shield_mesh)
    bm.free()
    apply_smooth(shield_obj)

    # 8. CHÈO CẬY LÁI ĐUÔI BẢN LỚN (STEERING OAR)
    rudder_mesh = bpy.data.meshes.new("Steering_Oar_Mesh")
    rudder_obj = bpy.data.objects.new("Steering_Oar", rudder_mesh)
    bpy.context.collection.objects.link(rudder_obj)
    rudder_obj.parent = root
    rudder_obj.location = (0.28, -7.0, 0.5)
    rudder_obj.rotation_euler = Euler((math.radians(-32), math.radians(12), 0))

    bm = bmesh.new()
    make_cylinder(bm, 0.05, 4.4, segments=12)
    blade_mat = Matrix.Translation((0, 0, -1.8)) @ Matrix.Scale(0.35, 4, Vector((1,0,0))) @ Matrix.Scale(0.04, 4, Vector((0,1,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=blade_mat)
    rudder_mesh.materials.append(mat_wood)
    bm.to_mesh(rudder_mesh)
    bm.free()
    apply_smooth(rudder_obj)

    # 9. CỜ NGŨ HÀNH ĐUÔI NHEO PHẤP PHỚI
    flag_mesh = bpy.data.meshes.new("War_Banner_Mesh")
    flag_obj = bpy.data.objects.new("War_Banner", flag_mesh)
    bpy.context.collection.objects.link(flag_obj)
    flag_obj.parent = root
    flag_obj.location = (0, -6.8, 1.2)

    bm = bmesh.new()
    make_cylinder(bm, 0.03, 3.2, segments=8, matrix=Matrix.Translation((0, 0, 1.6)))
    bmesh.ops.create_grid(bm, x_segments=8, y_segments=8, size=1.1, 
                          matrix=Matrix.Translation((0, -0.65, 2.6)) @ Euler((math.radians(90), 0, math.radians(90))).to_matrix().to_4x4())
    for v in bm.verts[-81:]:
        v.co.y += math.sin(v.co.x * 4.5) * 0.15
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
# 3. KHỞI TẠO BỐI CẢNH SÔNG BẠCH ĐẰNG, BÃI CỌC & LÂU THUYỀN
# ==============================================================================

def build_battle_environment(mat_wood, mat_iron, mat_river):
    # Sông
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

    # Cọc
    stake_mesh = bpy.data.meshes.new("Stakes_Mesh")
    stake_obj = bpy.data.objects.new("BaiCoc_BachDang", stake_mesh)
    bpy.context.collection.objects.link(stake_obj)
    bm = bmesh.new()
    stake_coords = [
        (-3.0, 2.0, -1.8, 48), (0.0, 3.0, -1.8, 52), (3.5, 1.5, -1.8, 50),
        (-2.0, -2.0, -1.8, 54), (1.5, -1.0, -1.8, 49), (4.5, -3.0, -1.8, 51),
        (-4.0, -6.0, -1.8, 50), (-0.5, -5.5, -1.8, 53), (2.5, -7.0, -1.8, 48),
        (-2.5, -10.0, -1.8, 52), (1.0, -11.0, -1.8, 50), (3.8, -12.0, -1.8, 55),
        (-1.2, 7.0, -1.8, 47), (2.0, 8.0, -1.8, 50)
    ]
    for x, y, z, pitch in stake_coords:
        full_m = Matrix.Translation((x, y, z)) @ Euler((math.radians(pitch), 0, math.radians(-10))).to_matrix().to_4x4()
        make_cone(bm, 0.16, 0.12, 3.2, segments=12, matrix=full_m @ Matrix.Translation((0, 0, 1.6)))
        make_cone(bm, 0.125, 0.01, 0.55, segments=10, matrix=full_m @ Matrix.Translation((0, 0, 3.45)))
    stake_mesh.materials.append(mat_wood)
    stake_mesh.materials.append(mat_iron)
    for p in stake_mesh.polygons:
        p.material_index = 1 if p.center.z > 0.0 else 0
    bm.to_mesh(stake_mesh)
    bm.free()
    apply_smooth(stake_obj)

    return river

def setup_cinema(vn_ship):
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Battle_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.55, 0.65, 0.78, 1.0)
        bg.inputs['Strength'].default_value = 1.4

    sun_data = bpy.data.lights.new("Hero_Sun", 'SUN')
    sun_data.energy = 6.5
    sun_data.color = (1.0, 0.94, 0.82)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(45), math.radians(20), math.radians(-35)))

    cam_data = bpy.data.cameras.new("Hero_Cam")
    cam_data.lens = 40 # Ống kính tiêu cự 40mm nghệ thuật
    cam_obj = bpy.data.objects.new("Camera_Lofted_Hero", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam_target = bpy.data.objects.new("Cam_Aim_Hero", None)
    bpy.context.collection.objects.link(cam_target)
    cam_target.parent = vn_ship
    cam_target.location = (0, 0, 1.2)

    track = cam_obj.constraints.new('TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    cam_obj.parent = vn_ship
    cam_obj.location = (11.0, -11.0, 4.5)

def embed_script_in_blend():
    """
    NẠP TRỰC TIẾP MÃ NGUỒN VÀO TAB SCRIPTING TRONG BLENDER!
    Để khi người dùng mở tab Scripting (như ảnh chụp của họ),
    đoạn mã này hiển thị ngay trên Text Editor!
    """
    this_script_path = os.path.abspath(__file__) if '__file__' in locals() else ""
    if this_script_path and os.path.exists(this_script_path):
        with open(this_script_path, 'r', encoding='utf-8') as f:
            code_str = f.read()
        text_block = bpy.data.texts.new("dong_thuyen_nghe_thuat_bach_dang.py")
        text_block.write(code_str)

def main():
    print("=== DỰNG THUYỀN THEO THUẬT TOÁN ĐÓNG TÀU LOFTING QUỐC TẾ ===")
    reset_scene()

    mat_vn_wood = create_pbr_mat("Mat_GoLim_ThuyenTa", (0.24, 0.13, 0.05, 1.0), roughness=0.55, bump_strength=0.35)
    mat_deck = create_pbr_mat("Mat_VanGo_Boong", (0.42, 0.25, 0.12, 1.0), roughness=0.6)
    mat_sail = create_pbr_mat("Mat_BuomNanTre", (0.84, 0.74, 0.48, 1.0), roughness=0.85, wave_scale=6.0)
    mat_iron = create_pbr_mat("Mat_SatRen_Coc", (0.12, 0.12, 0.14, 1.0), roughness=0.35, metallic=0.92)
    mat_shield = create_pbr_mat("Mat_KhienMay_SonSon", (0.72, 0.16, 0.10, 1.0), roughness=0.45)
    mat_red = create_pbr_mat("Mat_CoDo_TuyenSon", (0.88, 0.12, 0.08, 1.0), roughness=0.5)
    mat_gold = create_pbr_mat("Mat_HoaVanDongSon", (0.85, 0.65, 0.15, 1.0), roughness=0.3, metallic=0.85)
    mat_river = create_river_mat()

    vn_ship = build_lofted_viet_warship(mat_vn_wood, mat_deck, mat_sail, mat_shield, mat_red, mat_gold)
    river = build_battle_environment(mat_vn_wood, mat_iron, mat_river)
    setup_cinema(vn_ship)
    embed_script_in_blend()

    # Viewport Material Shading
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

    desktop_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    os.makedirs(desktop_dir, exist_ok=True)
    blend_path = os.path.join(desktop_dir, "thuyen_bach_dang_lofting.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f" ĐÃ LƯU FILE BLENDER LOFTING TẠI: {blend_path}")

    # Render ảnh đặc tả kiểm chứng
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    render_img = os.path.join(desktop_dir, "anh_thuyen_lofting_tinh_xao.png")
    scene.render.filepath = render_img
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH THUYỀN LOFTING TẠI: {render_img}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
