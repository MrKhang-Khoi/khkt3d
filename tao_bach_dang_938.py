import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    """Làm sạch scene trước khi dựng mới."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ==============================================================================
# 1. HỆ THỐNG VẬT LIỆU CHUẨN LỊCH SỬ THẾ KỶ 10 (HISTORICAL PBR SHADERS)
# ==============================================================================

def create_wood_material(name, dark_color, light_color, roughness=0.7, scale_u=2.0):
    """Vật liệu gỗ lim / gỗ sao bản địa có vân thớ."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (scale_u, 0.2, 3.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 1.5
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = dark_color
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = light_color
    links.new(wave.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.25
    links.new(wave.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_bamboo_sail_material():
    """Vật liệu buồm đan nan tre / cói (Batten sail) phương Đông cổ đại."""
    mat = bpy.data.materials.new(name="Mat_Bamboo_Batten_Sail")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.85
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 12.0) # Các nan tre ngang
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    wave = nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = 'Z'
    wave.inputs['Scale'].default_value = 4.0
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.45, 0.38, 0.22, 1.0) # Nâu rơm rạ đậm
    ramp.color_ramp.elements[1].color = (0.75, 0.65, 0.42, 1.0) # Vàng cói sáng
    links.new(wave.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    return mat

def create_iron_stake_material():
    """Vật liệu mũi sắt rèn bọc đầu cọc nhọn Bạch Đằng."""
    mat = bpy.data.materials.new(name="Mat_Forged_Iron")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.95
        bsdf.inputs['Roughness'].default_value = 0.4
    return mat

def create_river_water_material():
    """Vật liệu nước lợ sông Bạch Đằng (nhiều phù sa pha nước biển cửa sông)."""
    mat = bpy.data.materials.new(name="Mat_BachDang_River")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        # Nước màu lục đục pha ánh nâu phù sa cửa sông
        bsdf.inputs['Base Color'].default_value = (0.04, 0.16, 0.15, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.08
        bsdf.inputs['Metallic'].default_value = 0.1
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.75
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.75
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = 1.333
    return mat

def apply_bevel(obj, width=0.04, segments=2):
    for p in obj.data.polygons:
        p.use_smooth = True
    b = obj.modifiers.new("Bevel", 'BEVEL')
    b.width = width
    b.segments = segments
    b.limit_method = 'ANGLE'
    b.angle_limit = math.radians(35)

def make_cylinder(bm, r, depth, segments=12, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r, radius2=r, depth=depth, matrix=mat
    )

def make_cone(bm, r1, r2, depth, segments=12, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r1, radius2=r2, depth=depth, matrix=mat
    )

# ==============================================================================
# 2. DỰNG THUYỀN TA: THUYỀN CHIẾN NGÔ QUYỀN (KHINH CHU / THUYỀN THOI ĐÁY NÔNG)
# ==============================================================================

def build_ngo_quyen_warship(mat_wood, mat_sail):
    """
    Thuyền thoi / thuyền đuôi én Ngô Quyền:
    - Kích thước: Dài 14m, Rộng 2.0m, Mạn cao 0.95m.
    - Mớn nước: Cực nông (0.55m) lướt trên bãi cọc.
    - Đáy phẳng uốn nhẹ (Shallow arc).
    - Có hàng mái chèo tay, chèo lái đuôi, buồm nan gập mở, khiên mây bảo vệ.
    """
    root = bpy.data.objects.new("Thuyen_NgoQuyen_Root", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 1.5
    bpy.context.collection.objects.link(root)

    # 1. Thân thuyền thoi (Hull)
    mesh = bpy.data.meshes.new("NgoQuyen_Hull_Mesh")
    obj = bpy.data.objects.new("NgoQuyen_Hull", mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = root

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 14.0 # Dài 14m
        v.co.x *= 2.0  # Rộng 2.0m
        v.co.z *= 0.95 # Cao 0.95m

        u = v.co.y / 7.0 # -1 đến +1
        # Thon nhọn hai đầu thuyền thoi
        v.co.x *= max(0.08, 1.0 - (abs(u) ** 1.8) * 0.85)
        
        # Mũi nhọn vút cong, đuôi én hơi ngửa
        if v.co.y > 0:
            v.co.z += (u ** 1.4) * 0.7
        else:
            v.co.z += (abs(u) ** 1.4) * 0.5

        # Đáy phẳng nông (Đặc trưng lướt trên bãi cọc)
        if v.co.z < 0:
            v.co.x *= 0.85 # Không vát nhọn chữ V, giữ đáy phẳng
            v.co.z *= 0.65 # Giảm độ sâu ăn nước

    mesh.materials.append(mat_wood)
    bm.to_mesh(mesh)
    bm.free()
    apply_bevel(obj, width=0.03, segments=2)

    # 2. Hàng Mái Chèo Tay (8 mái chèo mỗi bên mạn = 16 mái chèo)
    oar_mesh = bpy.data.meshes.new("NgoQuyen_Oars_Mesh")
    oar_obj = bpy.data.objects.new("NgoQuyen_Oars", oar_mesh)
    bpy.context.collection.objects.link(oar_obj)
    oar_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-4, 5):
            y_pos = idx * 1.1
            x_base = side * (0.95 * max(0.2, 1.0 - (abs(y_pos) / 7.0) ** 2))
            # Cán chèo gỗ
            rot_m = Euler((math.radians(side * 28), 0, math.radians(side * 75))).to_matrix().to_4x4()
            trans_m = Matrix.Translation((x_base, y_pos, 0.35))
            make_cylinder(bm, 0.03, 2.2, segments=8, matrix=trans_m @ rot_m)
            # Bản chèo dẹt ở đầu
            bmesh.ops.create_cube(bm, size=0.25, 
                                  matrix=trans_m @ rot_m @ Matrix.Translation((0, 0, 1.0)) @ Matrix.Scale(0.15, 4, Vector((1,0,0))))
    oar_mesh.materials.append(mat_wood)
    bm.to_mesh(oar_mesh)
    bm.free()

    # 3. Chèo Cậy Lái Đuôi (Steering Oar - Thay thế hoàn toàn bánh lái phương Tây)
    rudder_mesh = bpy.data.meshes.new("Steering_Oar_Mesh")
    rudder_obj = bpy.data.objects.new("NgoQuyen_Steering_Oar", rudder_mesh)
    bpy.context.collection.objects.link(rudder_obj)
    rudder_obj.parent = root
    rudder_obj.location = (0.25, -6.8, 0.4)
    rudder_obj.rotation_euler = Euler((math.radians(-35), math.radians(10), 0))

    bm = bmesh.new()
    make_cylinder(bm, 0.05, 4.2, segments=10)
    bmesh.ops.create_cube(bm, size=0.5, matrix=Matrix.Translation((0, 0, -1.8)) @ Matrix.Scale(0.1, 4, Vector((1,0,0))))
    rudder_mesh.materials.append(mat_wood)
    bm.to_mesh(rudder_mesh)
    bm.free()

    # 4. Cột Buồm & Cánh Buồm Nan Tre (Batten Sail)
    mast_mesh = bpy.data.meshes.new("NgoQuyen_Mast_Mesh")
    mast_obj = bpy.data.objects.new("NgoQuyen_Mast", mast_mesh)
    bpy.context.collection.objects.link(mast_obj)
    mast_obj.parent = root
    mast_obj.location = (0, 1.2, 0.2)

    bm = bmesh.new()
    # Cột buồm tre cao 5.5m
    make_cone(bm, 0.10, 0.06, 5.5, segments=12, matrix=Matrix.Translation((0, 0, 2.75)))
    # Buồm nan hình thang cánh dơi
    rot_sail = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    bmesh.ops.create_grid(bm, x_segments=8, y_segments=8, size=1.8, 
                          matrix=Matrix.Translation((0, 0.2, 2.8)) @ rot_sail)
    for v in bm.verts[-81:]:
        v.co.x *= 0.85
        v.co.z = v.co.z * 0.9 + 2.8
        v.co.y += math.sin((v.co.z - 1.2) / 2.0 * math.pi) * 0.35

    mast_mesh.materials.append(mat_wood)
    mast_mesh.materials.append(mat_sail)
    for p in mast_mesh.polygons:
        if p.index >= 30:
            p.material_index = 1
    bm.to_mesh(mast_mesh)
    bm.free()

    # 5. Hàng Khiên Mây Bảo Vệ Dọc Mạn (Rattan Shields)
    shield_mat = bpy.data.materials.new("Mat_Rattan_Shield")
    shield_mat.use_nodes = True
    shield_mat.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value = (0.6, 0.45, 0.22, 1.0)
    
    shield_mesh = bpy.data.meshes.new("Shields_Mesh")
    shield_obj = bpy.data.objects.new("NgoQuyen_Shields", shield_mesh)
    bpy.context.collection.objects.link(shield_obj)
    shield_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for idx in range(-3, 4):
            y_pos = idx * 1.4
            x_pos = side * (1.0 * max(0.2, 1.0 - (abs(y_pos) / 7.0) ** 2))
            rot_s = Euler((0, math.radians(side * 90), 0)).to_matrix().to_4x4()
            trans_s = Matrix.Translation((x_pos, y_pos, 0.55))
            make_cylinder(bm, 0.28, 0.04, segments=12, matrix=trans_s @ rot_s)
    shield_mesh.materials.append(shield_mat)
    bm.to_mesh(shield_mesh)
    bm.free()

    return root

# ==============================================================================
# 3. DỰNG THUYỀN ĐỊCH: LÂU THUYỀN NAM HÁN (ĐẠI HẠM ĐÁY CHỮ V - LƯU HOẰNG THÁO)
# ==============================================================================

def build_nam_han_tower_ship(mat_wood, mat_sail):
    """
    Lâu thuyền Nam Hán:
    - Kích thước: Dài 28m, Rộng 6.5m, Cao thân 4.2m.
    - Mớn nước: Rất sâu (2.4m - 2.8m).
    - Đáy nhọn chữ V sâu (Deep-V Keel) - TỬ HUYỆT KHI TRIỀU RÚT.
    - Lầu chỉ huy 2 tầng trên boong có mái ngói dốc, 2 cột buồm lớn nan cứng.
    """
    root = bpy.data.objects.new("LauThuyen_NamHan_Root", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 2.5
    bpy.context.collection.objects.link(root)

    # 1. Thân Lâu Thuyền Đáy Chữ V (Deep-V Keel)
    mesh = bpy.data.meshes.new("NamHan_Hull_Mesh")
    obj = bpy.data.objects.new("NamHan_Hull", mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = root

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 28.0 # Dài 28m
        v.co.x *= 6.5  # Rộng 6.5m
        v.co.z *= 4.2  # Cao thân 4.2m

        u = v.co.y / 14.0 # -1 đến +1
        v.co.x *= max(0.18, 1.0 - (abs(u) ** 2) * 0.65)
        
        # Mũi và đuôi nâng cao thành hộp chiến đấu
        v.co.z += (u ** 2) * 0.8

        # ĐÁY CHỮ V SÂU (ĂN NƯỚC SÂU ĐỤNG CỌC)
        if v.co.z < 0:
            # Đáy vát chéo nhọn hoắt xuống sống trâu chính giữa
            v.co.x *= max(0.08, (v.co.z + 2.1) / 2.1)

    mesh.materials.append(mat_wood)
    bm.to_mesh(mesh)
    bm.free()
    apply_bevel(obj, width=0.08, segments=3)

    # 2. Lầu Chỉ Huy 2 Tầng (Command Towers)
    tower_mesh = bpy.data.meshes.new("NamHan_Tower_Mesh")
    tower_obj = bpy.data.objects.new("NamHan_Tower", tower_mesh)
    bpy.context.collection.objects.link(tower_obj)
    tower_obj.parent = root
    tower_obj.location = (0, -2.0, 2.6)

    bm = bmesh.new()
    # Tầng 1: Nhà gỗ boong lầu
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 1.2)) @ Matrix.Scale(4.5, 4, Vector((1,0,0))) @ Matrix.Scale(5.5, 4, Vector((0,1,0))) @ Matrix.Scale(2.2, 4, Vector((0,0,1))))
    # Tầng 2: Chòi vọng gác chỉ huy
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 3.0)) @ Matrix.Scale(3.0, 4, Vector((1,0,0))) @ Matrix.Scale(3.5, 4, Vector((0,1,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1))))
    # Mái dốc che lầu
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.5, radius2=0.2, depth=1.0,
                          matrix=Matrix.Translation((0, 0, 4.4)) @ Euler((0,0,math.radians(45))).to_matrix().to_4x4())
    
    tower_mesh.materials.append(mat_wood)
    bm.to_mesh(tower_mesh)
    bm.free()
    apply_bevel(tower_obj, width=0.05, segments=2)

    # 3. Hai Cột Buồm Lớn Nan Cứng (Twin Masts)
    masts_mesh = bpy.data.meshes.new("NamHan_Masts_Mesh")
    masts_obj = bpy.data.objects.new("NamHan_Masts", masts_mesh)
    bpy.context.collection.objects.link(masts_obj)
    masts_obj.parent = root

    bm = bmesh.new()
    # Cột buồm mũi (cao 11m) & Cột buồm chính (cao 15m)
    for y_mast, h_mast in [(4.5, 11.0), (-6.0, 15.0)]:
        make_cone(bm, 0.28, 0.14, h_mast, segments=16, 
                  matrix=Matrix.Translation((0, y_mast, 1.5 + h_mast / 2.0)))
        # Xà buồm
        make_cylinder(bm, 0.10, 6.0, segments=10, 
                      matrix=Matrix.Translation((0, y_mast, 1.5 + h_mast * 0.75)) @ Euler((0, math.radians(90), 0)).to_matrix().to_4x4())
        # Cánh buồm nan lớn
        rot_s = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
        bmesh.ops.create_grid(bm, x_segments=10, y_segments=10, size=2.4, 
                              matrix=Matrix.Translation((0, y_mast + 0.3, 1.5 + h_mast * 0.5)) @ rot_s @ Matrix.Scale(1.3, 4, Vector((1,0,0))) @ Matrix.Scale(1.8, 4, Vector((0,0,1))))

    masts_mesh.materials.append(mat_wood)
    masts_mesh.materials.append(mat_sail)
    for p in masts_mesh.polygons:
        if p.index >= 80:
            p.material_index = 1
    bm.to_mesh(masts_mesh)
    bm.free()

    # 4. Bánh Lái Trục Đứng Đuôi Thuyền (Axial Sternpost Rudder)
    rudder_mesh = bpy.data.meshes.new("NamHan_Rudder_Mesh")
    rudder_obj = bpy.data.objects.new("NamHan_Rudder", rudder_mesh)
    bpy.context.collection.objects.link(rudder_obj)
    rudder_obj.parent = root
    rudder_obj.location = (0, -14.2, -0.5)

    bm = bmesh.new()
    make_cylinder(bm, 0.12, 4.5, segments=10) # Trục đứng
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, -0.6, -1.0)) @ Matrix.Scale(0.12, 4, Vector((1,0,0))) @ Matrix.Scale(1.2, 4, Vector((0,1,0))) @ Matrix.Scale(2.5, 4, Vector((0,0,1))))
    rudder_mesh.materials.append(mat_wood)
    bm.to_mesh(rudder_mesh)
    bm.free()

    return root

# ==============================================================================
# 4. DỰNG BÃI CỌC NGẦM BẠCH ĐẰNG (IRON-TIPPED WOODEN STAKES)
# ==============================================================================

def build_bach_dang_stakes(mat_wood, mat_iron):
    """
    Bãi cọc Bạch Đằng:
    - Thân gỗ lim đốn từ rừng Yên Hưng.
    - Đầu vót nhọn, bọc chóp sắt rèn cố định bằng đinh.
    - Cắm nghiêng 50 độ đón đầu dòng nước chảy ra biển.
    """
    stake_mesh = bpy.data.meshes.new("Stakes_Field_Mesh")
    stake_obj = bpy.data.objects.new("Bai_Coc_BachDang", stake_mesh)
    bpy.context.collection.objects.link(stake_obj)

    bm = bmesh.new()

    # Trận địa cọc cắm so le hình chữ chi
    stake_coords = [
        # (x, y, z_base, nghieng_deg)
        (-3.0, 2.0, -1.8, 48), (0.0, 3.0, -1.8, 52), (3.5, 1.5, -1.8, 50),
        (-2.0, -2.0, -1.8, 54), (1.5, -1.0, -1.8, 49), (4.5, -3.0, -1.8, 51),
        (-4.0, -6.0, -1.8, 50), (-0.5, -5.5, -1.8, 53), (2.5, -7.0, -1.8, 48),
        (-2.5, -10.0, -1.8, 52), (1.0, -11.0, -1.8, 50), (3.8, -12.0, -1.8, 55),
        (-1.2, 7.0, -1.8, 47), (2.0, 8.0, -1.8, 50)
    ]

    for x, y, z, pitch in stake_coords:
        rot_stake = Euler((math.radians(pitch), 0, math.radians(-10))).to_matrix().to_4x4()
        trans_stake = Matrix.Translation((x, y, z))
        full_mat = trans_stake @ rot_stake

        # Thân cọc gỗ lim dài 3.2m
        make_cone(bm, 0.16, 0.12, 3.2, segments=12, 
                  matrix=full_mat @ Matrix.Translation((0, 0, 1.6)))
        
        # Chóp nhọn bọc sắt rèn ở đầu cọc
        make_cone(bm, 0.125, 0.01, 0.55, segments=10, 
                  matrix=full_mat @ Matrix.Translation((0, 0, 3.45)))

    stake_mesh.materials.append(mat_wood)
    stake_mesh.materials.append(mat_iron)
    # Gán vật liệu sắt cho các chóp cọc nhọn
    for p in stake_mesh.polygons:
        # Mặt chóp sắt nằm ở đỉnh
        center_z = p.center.z
        if center_z > 0.0:
            p.material_index = 1
        else:
            p.material_index = 0

    bm.to_mesh(stake_mesh)
    bm.free()
    apply_bevel(stake_obj, width=0.015, segments=2)
    return stake_obj

# ==============================================================================
# 5. DỰNG MẶT NƯỚC SÔNG BẠCH ĐẰNG VÀ MÔ PHỎNG THỦY TRIỀU RÚT (TIDAL ANIMATION)
# ==============================================================================

def build_river_water(mat_river):
    """Mặt nước sông rộng lớn có Ocean Modifier dập dềnh."""
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
    ocean_mod.wave_scale = 0.7  # Sóng sông lừng cửa biển, không quá cuộn như biển khơi
    ocean_mod.choppiness = 1.1
    ocean_mod.wind_velocity = 12.0

    return river

def animate_tidal_battle(river_obj, vn_ship, enemy_ship, total_frames=180):
    """
    KỊCH BẢN THỦY CHIẾN BẠCH ĐẰNG 938 CHUẨN XÁC:
    1. Triều bắt đầu rút: Mực nước sông hạ từ Z = +0.6m xuống Z = -1.6m.
    2. Thuyền Ngô Quyền (mớn nước nông 0.55m): Lướt an toàn bên trên bãi cọc, quay mũi 180 độ vây đánh.
    3. Lâu thuyền Nam Hán (đáy chữ V ăn sâu 2.6m): Tiến vào, đâm trúng cọc sắt lúc triều rút, thủng đáy, khựng lại và nghiêng đổ đắm chìm!
    """
    bpy.context.scene.render.fps = 30
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames

    # A. Hoạt ảnh Mực Nước Triều Rút (River Water Heave)
    river_obj.animation_data_create()
    act_river = bpy.data.actions.new("Tide_Receding_Action")
    river_obj.animation_data.action = act_river

    for f in range(1, total_frames + 1):
        t = f / total_frames # 0.0 đến 1.0
        # Nước rút sâu dần: Frame 1 (+0.5m ngập cọc) -> Frame 180 (-1.6m cọc nhô cao 1m)
        tide_z = 0.5 - t * 2.1
        river_obj.location.z = tide_z
        river_obj.keyframe_insert("location", frame=f)

    # B. Hoạt ảnh Thuyền Ngô Quyền (Ta)
    vn_ship.animation_data_create()
    act_vn = bpy.data.actions.new("NgoQuyen_Tactical_Action")
    vn_ship.animation_data.action = act_vn

    for f in range(1, total_frames + 1):
        t = f / total_frames
        tide_z = 0.5 - t * 2.1
        
        # Giai đoạn 1 (Frame 1-60): Nhử địch rút lui về phía thượng lưu (+Y)
        # Giai đoạn 2 (Frame 61-100): Triều rút lộ cọc, quay ngoắt 180 độ phản công
        # Giai đoạn 3 (Frame 101-180): Áp sát vây khốn thuyền giặc
        if f <= 60:
            y_pos = 18.0 + (f / 60.0) * 8.0
            x_pos = -6.0 + math.sin(f * 0.1) * 0.5
            yaw = math.radians(0) # Đang chạy xuôi
        elif f <= 90:
            sub_t = (f - 60) / 30.0
            y_pos = 26.0 - sub_t * 4.0
            x_pos = -6.0 + sub_t * 3.0
            yaw = math.radians(sub_t * 180) # Quay mũi 180 độ
        else:
            sub_t = (f - 90) / 90.0
            y_pos = 22.0 - sub_t * 12.0 # Lao vào áp sát hạm đội địch
            x_pos = -3.0 - sub_t * 2.0
            yaw = math.radians(180)

        # Thuyền nổi an toàn trên mặt nước rút
        z_pos = tide_z + 0.15 + math.sin(f * 0.3) * 0.08
        pitch = math.sin(f * 0.25) * 0.05
        roll = math.cos(f * 0.2) * 0.06

        vn_ship.location = Vector((x_pos, y_pos, z_pos))
        vn_ship.rotation_mode = 'XYZ'
        vn_ship.rotation_euler = Euler((pitch, roll, yaw), 'XYZ')
        vn_ship.keyframe_insert("location", frame=f)
        vn_ship.keyframe_insert("rotation_euler", frame=f)

    # C. Hoạt ảnh Lâu Thuyền Nam Hán (Địch - Mắc cọc & Đắm)
    enemy_ship.animation_data_create()
    act_enemy = bpy.data.actions.new("NamHan_Wreck_Action")
    enemy_ship.animation_data.action = act_enemy

    for f in range(1, total_frames + 1):
        t = f / total_frames
        tide_z = 0.5 - t * 2.1

        if f < 70:
            # Lao vào cửa sông đuổi theo thuyền ta (+Y)
            y_pos = -25.0 + (f / 70.0) * 18.0 # Tiến tới y = -7.0 (vào đúng bãi cọc)
            x_pos = 1.0
            z_pos = tide_z - 0.8 # Mớn nước sâu 2.5m
            pitch = -0.05
            roll = math.sin(f * 0.15) * 0.04
        elif f < 100:
            # ĐÂM CỌC TẠI FRAME 70: Khựng lại đột ngột, cọc xé toạc đáy thuyền
            sub_t = (f - 70) / 30.0
            y_pos = -7.0 + sub_t * 1.5 # Trôi dạt chậm lại do cọc giữ
            x_pos = 1.0 + sub_t * 0.8
            # Tàu bị cọc nhấc đáy lên trong khi triều tiếp tục rút -> Tàu bắt đầu nghiêng lật
            z_pos = -0.4 - sub_t * 0.3
            pitch = -0.05 - sub_t * 0.15 # Mũi chúi xuống nước
            roll = sub_t * 0.35          # Nghiêng mạn 20 độ vì đáy V mắc cọc
        else:
            # BỊ CỌC CẮM CHẶT, NGHIÊNG ĐẮM HOÀN TOÀN
            sub_t = (f - 100) / 80.0
            y_pos = -5.5
            x_pos = 1.8
            z_pos = -0.7 # Kẹt cứng trên cọc
            pitch = -0.22 # Chúi mũi sâu
            roll = 0.42 + math.sin(f * 0.1) * 0.02 # Nghiêng gục 25 độ, hoàn toàn bất lực!

        enemy_ship.location = Vector((x_pos, y_pos, z_pos))
        enemy_ship.rotation_mode = 'XYZ'
        enemy_ship.rotation_euler = Euler((pitch, roll, 0.05), 'XYZ')
        enemy_ship.keyframe_insert("location", frame=f)
        enemy_ship.keyframe_insert("rotation_euler", frame=f)

def setup_battle_camera_and_sun():
    """Thiết lập ánh sáng chiến trường và góc máy kịch tính."""
    # 1. Bầu trời mây mù lịch sử (Overcast Estuary Sky)
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Battle_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Màu trời xám lạnh pha ánh sáng mờ ảo cửa biển mùa đông
        bg.inputs['Color'].default_value = (0.50, 0.58, 0.65, 1.0)
        bg.inputs['Strength'].default_value = 1.3

    # 2. Ánh nắng xuyên mây
    sun_data = bpy.data.lights.new("Sun_Historical", type='SUN')
    sun_data.energy = 5.5
    sun_data.color = (1.0, 0.92, 0.80)
    sun_obj = bpy.data.objects.new("Sun_Historical", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(55), math.radians(20), math.radians(-35)))

    # 3. Camera Góc Nhìn Chiến Dịch Toàn Cảnh (Master Epic Cam)
    cam_data = bpy.data.cameras.new("Epic_Battle_Cam")
    cam_data.lens = 28 # Góc rộng để thấy cả bãi cọc nhô lên, thuyền giặc đắm và thuyền ta vây hãm
    cam_obj = bpy.data.objects.new("Camera_Historical", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Đặt camera chếch bên sườn bãi cọc nhìn bao quát
    cam_obj.location = (20.0, -14.0, 9.5)
    
    # Target ngắm vào trung tâm bãi cọc và Lâu thuyền địch
    target = bpy.data.objects.new("Cam_Aim_Battle", None)
    bpy.context.collection.objects.link(target)
    target.location = (0.0, -4.0, 0.5)

    track = cam_obj.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

def main():
    print("=== ĐANG TÁI HIỆN CHIẾN DỊCH SÔNG BẠCH ĐẰNG 938 (NGÔ QUYỀN) ===")
    reset_scene()

    # 1. Khởi tạo vật liệu lịch sử
    mat_viet_wood = create_wood_material("Mat_Viet_LimWood", (0.16, 0.09, 0.04, 1.0), (0.35, 0.22, 0.12, 1.0), roughness=0.65)
    mat_enemy_wood = create_wood_material("Mat_NamHan_PineWood", (0.28, 0.18, 0.10, 1.0), (0.45, 0.30, 0.16, 1.0), roughness=0.7)
    mat_sail = create_bamboo_sail_material()
    mat_iron = create_iron_stake_material()
    mat_river = create_river_water_material()

    # 2. Dựng các đối tượng lịch sử
    vn_ship = build_ngo_quyen_warship(mat_viet_wood, mat_sail)
    enemy_ship = build_nam_han_tower_ship(mat_enemy_wood, mat_sail)
    stakes = build_bach_dang_stakes(mat_viet_wood, mat_iron)
    river = build_river_water(mat_river)

    # 3. Mô phỏng thủy triều rút & kịch bản tác chiến
    animate_tidal_battle(river, vn_ship, enemy_ship, total_frames=180)

    # 4. Ánh sáng & Camera
    setup_battle_camera_and_sun()

    # 5. Lưu file .blend vào thư mục TEST_BLENDER trên Desktop
    desktop_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    os.makedirs(desktop_dir, exist_ok=True)

    blend_file = os.path.join(desktop_dir, "bach_dang_938_simulation.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f" ĐÃ LƯU SCENE LỊCH SỬ TẠI: {blend_file}")

    # 6. Render ảnh kiểm chứng kịch tính tại Frame 115 (lúc triều rút kiệt, cọc nhô lên đâm thủng Lâu thuyền)
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.frame_set(115)

    render_img = os.path.join(desktop_dir, "anh_kiem_chung_bach_dang.png")
    scene.render.filepath = render_img
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH BẰNG CHỨNG TẠI: {render_img}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
