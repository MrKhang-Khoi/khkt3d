import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ==============================================================================
# 1. HỆ THỐNG VẬT LIỆU LỊCH SỬ VIỆT NAM THẾ KỶ 10 (PBR + VIEWPORT COLOR)
# ==============================================================================

def create_historical_material(name, diffuse_rgba, roughness=0.6, metallic=0.0, wave_scale=2.0, bump_str=0.25):
    """
    Tạo vật liệu cao cấp:
    1. Viewport Color (diffuse_color): Đảm bảo hiển thị rực rỡ NGAY CẢ TRONG CHẾ ĐỘ SOLID/CLAY!
    2. Node Tree Procedural: Vân thớ, gờ nổi, nẹp nan khi chuyển sang Material Preview / Rendered.
    """
    mat = bpy.data.materials.new(name=name)
    # Cài đặt màu hiển thị ngay trong chế độ Solid (Viewport Shading)
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

    # Thêm vân thớ Procedural
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.5, 0.15, 4.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = wave_scale
    wave.inputs['Distortion'].default_value = 1.2
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = bump_str
    bump.inputs['Distance'].default_value = 0.04
    links.new(wave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_river_material():
    """Mặt nước sông Bạch Đằng phù sa pha nước biển."""
    mat = bpy.data.materials.new(name="Mat_BachDang_River")
    mat.diffuse_color = (0.05, 0.22, 0.20, 0.8) # Xanh rêu phù sa trong Solid mode
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.18, 0.16, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.06
        bsdf.inputs['Metallic'].default_value = 0.15
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.82
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.82
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = 1.333
    return mat

def make_cone(bm, r1, r2, depth, segments=12, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r1, radius2=r2, depth=depth, matrix=mat
    )

def make_cylinder(bm, r, depth, segments=12, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r, radius2=r, depth=depth, matrix=mat
    )

def apply_smooth_bevel(obj, width=0.03):
    for p in obj.data.polygons:
        p.use_smooth = True
    b = obj.modifiers.new("Bevel", 'BEVEL')
    b.width = width
    b.segments = 2
    b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(35)

# ==============================================================================
# 2. DỰNG MÔ HÌNH LỊCH SỬ NÂNG CAO ĐẦY ĐỦ MÀU SẮC
# ==============================================================================

def build_scene():
    # 1. BẢNG MÀU CHÍNH XÁC LỊCH SỬ THẾ KỶ 10
    # Gỗ Lim / Sao Đại Việt (quét nhựa chai chống thấm): Nâu sẫm ấm áp
    mat_vn_wood = create_historical_material("Mat_GoLim_DaiViet", (0.24, 0.13, 0.06, 1.0), roughness=0.6, bump_str=0.3)
    # Gỗ Thông Bắc (thuyền Nam Hán): Nâu sáng ngả xám khói
    mat_enemy_wood = create_historical_material("Mat_GoThong_NamHan", (0.42, 0.28, 0.16, 1.0), roughness=0.7, bump_str=0.25)
    # Buồm nan tre / cói: Vàng rơm tươi tắn có nẹp nan
    mat_sail = create_historical_material("Mat_BuomNanTre", (0.82, 0.72, 0.48, 1.0), roughness=0.85, wave_scale=6.0, bump_str=0.15)
    # Mũi sắt rèn cọc Bạch Đằng: Đen xỉn ánh kim loại
    mat_iron = create_historical_material("Mat_SatRen_Coc", (0.12, 0.12, 0.14, 1.0), roughness=0.35, metallic=0.92, bump_str=0.1)
    # Cọc gỗ lim ngâm bùn: Nâu đen sẫm rêu phong
    mat_stake_wood = create_historical_material("Mat_CocGoLim_YenHung", (0.15, 0.09, 0.05, 1.0), roughness=0.85, bump_str=0.4)
    # Khiên mây sơn son (sơn ta Phú Thọ cổ truyền): Đỏ cánh gián son
    mat_shield = create_historical_material("Mat_KhienMay_SonTa", (0.65, 0.18, 0.12, 1.0), roughness=0.5, bump_str=0.2)
    # Mặt nước sông Bạch Đằng
    mat_river = create_river_material()

    # 2. THUYỀN CHIẾN NGÔ QUYỀN (THUYỀN THOI ĐÁY NÔNG)
    vn_root = bpy.data.objects.new("Thuyen_NgoQuyen_Root", None)
    vn_root.empty_display_type = 'ARROWS'
    bpy.context.collection.objects.link(vn_root)

    # Thân thuyền thoi
    vn_mesh = bpy.data.meshes.new("VN_Hull_Mesh")
    vn_obj = bpy.data.objects.new("VN_ThuyenThoi", vn_mesh)
    bpy.context.collection.objects.link(vn_obj)
    vn_obj.parent = vn_root

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 14.0
        v.co.x *= 2.1
        v.co.z *= 0.95
        u = v.co.y / 7.0
        v.co.x *= max(0.08, 1.0 - (abs(u) ** 1.8) * 0.85)
        if v.co.y > 0:
            v.co.z += (u ** 1.4) * 0.7
        else:
            v.co.z += (abs(u) ** 1.4) * 0.5
        if v.co.z < 0:
            v.co.x *= 0.85 # Đáy phẳng nông
            v.co.z *= 0.65
    vn_mesh.materials.append(mat_vn_wood)
    bm.to_mesh(vn_mesh)
    bm.free()
    apply_smooth_bevel(vn_obj, width=0.03)

    # 16 Mái chèo tay
    oar_mesh = bpy.data.meshes.new("VN_Oars_Mesh")
    oar_obj = bpy.data.objects.new("VN_MaiCheo", oar_mesh)
    bpy.context.collection.objects.link(oar_obj)
    oar_obj.parent = vn_root
    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-4, 5):
            y_pos = idx * 1.1
            x_base = side * (1.0 * max(0.2, 1.0 - (abs(y_pos) / 7.0) ** 2))
            rot_m = Euler((math.radians(side * 28), 0, math.radians(side * 75))).to_matrix().to_4x4()
            trans_m = Matrix.Translation((x_base, y_pos, 0.35))
            make_cylinder(bm, 0.03, 2.2, segments=8, matrix=trans_m @ rot_m)
            bmesh.ops.create_cube(bm, size=0.25, 
                                  matrix=trans_m @ rot_m @ Matrix.Translation((0, 0, 1.0)) @ Matrix.Scale(0.15, 4, Vector((1,0,0))))
    oar_mesh.materials.append(mat_vn_wood)
    bm.to_mesh(oar_mesh)
    bm.free()

    # Cột buồm & Buồm nan tre
    mast_mesh = bpy.data.meshes.new("VN_Mast_Mesh")
    mast_obj = bpy.data.objects.new("VN_CotBuom", mast_mesh)
    bpy.context.collection.objects.link(mast_obj)
    mast_obj.parent = vn_root
    mast_obj.location = (0, 1.2, 0.2)
    bm = bmesh.new()
    make_cone(bm, 0.10, 0.06, 5.5, segments=12, matrix=Matrix.Translation((0, 0, 2.75)))
    rot_sail = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    bmesh.ops.create_grid(bm, x_segments=8, y_segments=8, size=1.8, 
                          matrix=Matrix.Translation((0, 0.2, 2.8)) @ rot_sail)
    for v in bm.verts[-81:]:
        v.co.x *= 0.85
        v.co.z = v.co.z * 0.9 + 2.8
        v.co.y += math.sin((v.co.z - 1.2) / 2.0 * math.pi) * 0.35
    mast_mesh.materials.append(mat_vn_wood)
    mast_mesh.materials.append(mat_sail)
    for p in mast_mesh.polygons:
        if p.index >= 30:
            p.material_index = 1
    bm.to_mesh(mast_mesh)
    bm.free()

    # Khiên mây sơn đỏ truyền thống
    shield_mesh = bpy.data.meshes.new("VN_Shields_Mesh")
    shield_obj = bpy.data.objects.new("VN_KhienMay", shield_mesh)
    bpy.context.collection.objects.link(shield_obj)
    shield_obj.parent = vn_root
    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-3, 4):
            y_pos = idx * 1.4
            x_pos = side * (1.05 * max(0.2, 1.0 - (abs(y_pos) / 7.0) ** 2))
            rot_s = Euler((0, math.radians(side * 90), 0)).to_matrix().to_4x4()
            trans_s = Matrix.Translation((x_pos, y_pos, 0.55))
            make_cylinder(bm, 0.28, 0.05, segments=12, matrix=trans_s @ rot_s)
    shield_mesh.materials.append(mat_shield)
    bm.to_mesh(shield_mesh)
    bm.free()

    # 3. THUYỀN ĐỊCH: LÂU THUYỀN NAM HÁN (ĐÁY CHỮ V SÂU)
    enemy_root = bpy.data.objects.new("LauThuyen_NamHan_Root", None)
    enemy_root.empty_display_type = 'ARROWS'
    bpy.context.collection.objects.link(enemy_root)

    en_mesh = bpy.data.meshes.new("Enemy_Hull_Mesh")
    en_obj = bpy.data.objects.new("Enemy_LauThuyen", en_mesh)
    bpy.context.collection.objects.link(en_obj)
    en_obj.parent = enemy_root

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 28.0
        v.co.x *= 6.5
        v.co.z *= 4.2
        u = v.co.y / 14.0
        v.co.x *= max(0.18, 1.0 - (abs(u) ** 2) * 0.65)
        v.co.z += (u ** 2) * 0.8
        # ĐÁY CHỮ V SÂU ĂN NƯỚC (ĐÂM CỌC)
        if v.co.z < 0:
            v.co.x *= max(0.08, (v.co.z + 2.1) / 2.1)
    en_mesh.materials.append(mat_enemy_wood)
    bm.to_mesh(en_mesh)
    bm.free()
    apply_smooth_bevel(en_obj, width=0.06)

    # Lầu chỉ huy 2 tầng có mái ngói
    tower_mesh = bpy.data.meshes.new("Enemy_Tower_Mesh")
    tower_obj = bpy.data.objects.new("Enemy_LauChiHuy", tower_mesh)
    bpy.context.collection.objects.link(tower_obj)
    tower_obj.parent = enemy_root
    tower_obj.location = (0, -2.0, 2.6)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 1.2)) @ Matrix.Scale(4.5, 4, Vector((1,0,0))) @ Matrix.Scale(5.5, 4, Vector((0,1,0))) @ Matrix.Scale(2.2, 4, Vector((0,0,1))))
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 3.0)) @ Matrix.Scale(3.0, 4, Vector((1,0,0))) @ Matrix.Scale(3.5, 4, Vector((0,1,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1))))
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.6, radius2=0.2, depth=1.0,
                          matrix=Matrix.Translation((0, 0, 4.4)) @ Euler((0,0,math.radians(45))).to_matrix().to_4x4())
    tower_mesh.materials.append(mat_enemy_wood)
    bm.to_mesh(tower_mesh)
    bm.free()
    apply_smooth_bevel(tower_obj, width=0.04)

    # 2 Cột buồm lớn
    en_mast_mesh = bpy.data.meshes.new("Enemy_Masts_Mesh")
    en_mast_obj = bpy.data.objects.new("Enemy_CotBuom", en_mast_mesh)
    bpy.context.collection.objects.link(en_mast_obj)
    en_mast_obj.parent = enemy_root
    bm = bmesh.new()
    for y_m, h_m in [(4.5, 11.0), (-6.0, 15.0)]:
        make_cone(bm, 0.28, 0.14, h_m, segments=16, matrix=Matrix.Translation((0, y_m, 1.5 + h_m / 2.0)))
        make_cylinder(bm, 0.10, 6.0, segments=10, matrix=Matrix.Translation((0, y_m, 1.5 + h_m * 0.75)) @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4())
        rot_s = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
        bmesh.ops.create_grid(bm, x_segments=10, y_segments=10, size=2.4, 
                              matrix=Matrix.Translation((0, y_m + 0.3, 1.5 + h_m * 0.5)) @ rot_s @ Matrix.Scale(1.3, 4, Vector((1,0,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1))))
    en_mast_mesh.materials.append(mat_enemy_wood)
    en_mast_mesh.materials.append(mat_sail)
    for p in en_mast_mesh.polygons:
        if p.index >= 80:
            p.material_index = 1
    bm.to_mesh(en_mast_mesh)
    bm.free()

    # 4. TRẬN ĐỊA CỌC NGẦM BẠCH ĐẰNG (ĐẦU BỌC SẮT RÈN)
    stake_mesh = bpy.data.meshes.new("Coc_BachDang_Mesh")
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
        rot_s = Euler((math.radians(pitch), 0, math.radians(-10))).to_matrix().to_4x4()
        full_m = Matrix.Translation((x, y, z)) @ rot_s
        # Thân cọc gỗ lim
        make_cone(bm, 0.16, 0.12, 3.2, segments=12, matrix=full_m @ Matrix.Translation((0, 0, 1.6)))
        # Chóp sắt nhọn
        make_cone(bm, 0.125, 0.01, 0.55, segments=10, matrix=full_m @ Matrix.Translation((0, 0, 3.45)))
    stake_mesh.materials.append(mat_stake_wood)
    stake_mesh.materials.append(mat_iron)
    for p in stake_mesh.polygons:
        if p.center.z > 0.0:
            p.material_index = 1
        else:
            p.material_index = 0
    bm.to_mesh(stake_mesh)
    bm.free()

    # 5. MẶT NƯỚC SÔNG BẠCH ĐẰNG
    bpy.ops.mesh.primitive_plane_add(size=160.0, location=(0, 0, 0.0))
    river = bpy.context.active_object
    river.name = "BachDang_River_Surface"
    river.data.materials.append(mat_river)
    ocean_mod = river.modifiers.new("RiverWaves", 'OCEAN')
    ocean_mod.geometry_mode = 'GENERATE'
    ocean_mod.repeat_x = 2
    ocean_mod.repeat_y = 2
    ocean_mod.spatial_size = 80
    ocean_mod.resolution = 12
    ocean_mod.wave_scale = 0.7
    ocean_mod.choppiness = 1.1

    return vn_root, enemy_root, river

def animate_tidal_battle(river_obj, vn_ship, enemy_ship, total_frames=180):
    """Mô phỏng thủy triều rút & kịch bản tác chiến 180 frame."""
    bpy.context.scene.render.fps = 30
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames

    # Triều rút
    river_obj.animation_data_create()
    river_act = bpy.data.actions.new("Tide_Action")
    river_obj.animation_data.action = river_act
    for f in range(1, total_frames + 1):
        tide_z = 0.5 - (f / total_frames) * 2.1
        river_obj.location.z = tide_z
        river_obj.keyframe_insert("location", frame=f)

    # Thuyền Ngô Quyền
    vn_ship.animation_data_create()
    vn_act = bpy.data.actions.new("VN_Action")
    vn_ship.animation_data.action = vn_act
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
    en_act = bpy.data.actions.new("Enemy_Action")
    enemy_ship.animation_data.action = en_act
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

def setup_lighting_and_camera():
    """Chiếu sáng tự nhiên và góc máy điện ảnh."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Battle_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.55, 0.65, 0.75, 1.0)
        bg.inputs['Strength'].default_value = 1.4

    sun_data = bpy.data.lights.new("Sun_Light", 'SUN')
    sun_data.energy = 6.0
    sun_data.color = (1.0, 0.94, 0.82)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(52), math.radians(18), math.radians(-42)))

    cam_data = bpy.data.cameras.new("Cinema_Cam")
    cam_data.lens = 28
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_obj.location = (20.0, -14.0, 9.5)

    target = bpy.data.objects.new("Cam_Target", None)
    bpy.context.collection.objects.link(target)
    target.location = (0.0, -4.0, 0.5)

    track = cam_obj.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

def set_viewport_display_to_material():
    """
    CỰC KỲ QUAN TRỌNG:
    Tự động cấu hình 3D Viewport sang chế độ MATERIAL PREVIEW!
    Khi người dùng mở file .blend lên, màn hình sẽ hiển thị FULL MÀU SẮC NGAY LẬP TỨC
    thay vì màn hình xám trắng Solid!
    """
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        # Chuyển sang Material Preview (hiển thị shader + texture)
                        space.shading.type = 'MATERIAL'

def main():
    print("=== NÂNG CẤP MÀU SẮC & TEXTURE LỊCH SỬ BẠCH ĐẰNG 938 ===")
    reset_scene()
    vn_ship, enemy_ship, river = build_scene()
    animate_tidal_battle(river, vn_ship, enemy_ship, total_frames=180)
    setup_lighting_and_camera()
    set_viewport_display_to_material()

    desktop_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    os.makedirs(desktop_dir, exist_ok=True)
    blend_file = os.path.join(desktop_dir, "bach_dang_938_simulation.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f" ĐÃ CẬP NHẬT FILE BLENDER FULL MÀU SẮC: {blend_file}")

    # Render lại ảnh kiểm chứng với đầy đủ vật liệu PBR tại Frame 115
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.frame_set(115)
    render_img = os.path.join(desktop_dir, "anh_kiem_chung_mau_sac.png")
    scene.render.filepath = render_img
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH MÀU SẮC KIỂM CHỨNG TẠI: {render_img}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
