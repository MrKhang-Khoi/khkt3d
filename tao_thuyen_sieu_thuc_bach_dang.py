import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ==============================================================================
# 1. BỘ TẠO VẬT LIỆU PBR SIÊU THỰC ĐA TẦNG (PROCEDURAL PBR SHADER ENGINE)
# ==============================================================================

def create_photoreal_wood_mat(name, base_rgb=(0.22, 0.12, 0.05), rough=0.55, bump_scale=35.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*base_rgb, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = 0.0
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (1.0, 18.0, 1.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    noise1 = nodes.new('ShaderNodeTexNoise')
    noise1.inputs['Scale'].default_value = bump_scale
    noise1.inputs['Detail'].default_value = 10.0
    noise1.inputs['Roughness'].default_value = 0.65
    noise1.inputs['Distortion'].default_value = 1.8
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (base_rgb[0] * 0.6, base_rgb[1] * 0.6, base_rgb[2] * 0.6, 1.0)
    ramp.color_ramp.elements[1].position = 0.70
    ramp.color_ramp.elements[1].color = (min(1.0, base_rgb[0] * 1.3), min(1.0, base_rgb[1] * 1.3), min(1.0, base_rgb[2] * 1.3), 1.0)
    links.new(noise1.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.02
    links.new(noise1.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_sail_cloth_mat(name):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.78, 0.70, 0.52, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.76, 0.68, 0.50, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 60.0
    noise.inputs['Detail'].default_value = 8.0
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.01
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

def create_ancient_bronze_mat(name):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.75, 0.55, 0.22, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.70, 0.50, 0.20, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.88
        bsdf.inputs['Roughness'].default_value = 0.35
    return mat

def create_iron_mat(name):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.15, 0.15, 0.17, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.14, 0.14, 0.16, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.92
        bsdf.inputs['Roughness'].default_value = 0.40
    return mat

def create_shield_lacquer_mat(name):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.68, 0.14, 0.10, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.65, 0.13, 0.09, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.38
        bsdf.inputs['Metallic'].default_value = 0.05
    return mat

def create_water_mat(name):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (0.08, 0.22, 0.22, 0.8)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.05, 0.18, 0.18, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Metallic'].default_value = 0.1
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.85
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.85
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = 1.333
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    tex_coord = nodes.new('ShaderNodeTexCoord')
    wave_noise = nodes.new('ShaderNodeTexNoise')
    wave_noise.inputs['Scale'].default_value = 15.0
    wave_noise.inputs['Detail'].default_value = 4.0
    links.new(tex_coord.outputs['Object'], wave_noise.inputs['Vector'])

    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.05
    links.new(wave_noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return mat

# ==============================================================================
# 2. HÌNH HỌC VÀ THUẬT TOÁN ĐÓNG TÀU CHUYÊN NGHIỆP
# ==============================================================================

def add_smooth_modifiers(obj, solidify_thickness=0.08, bevel_width=0.015, subsurf_levels=1):
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

def build_hyperrealistic_viet_warship(mats):
    parent = bpy.data.objects.new("Thuyen_Viet_NgoQuyen_Master", None)
    bpy.context.collection.objects.link(parent)

    # A. THÂN THUYỀN LOFTING
    mesh_hull = bpy.data.meshes.new("Thuyen_Hull_Loft")
    bm_hull = bmesh.new()

    stations_x = [-6.0, -5.0, -3.8, -2.4, -0.8,  0.8,  2.4,  3.8,  5.0,  5.8,  6.3]
    beam_w     = [ 0.15, 0.70, 1.05, 1.18, 1.22, 1.20, 1.14, 0.95, 0.65, 0.35, 0.10]
    sheer_z    = [ 1.10, 0.72, 0.50, 0.40, 0.36, 0.38, 0.44, 0.56, 0.78, 1.05, 1.35]
    keel_z     = [-0.30,-0.60,-0.75,-0.80,-0.82,-0.80,-0.75,-0.62,-0.42,-0.15, 0.10]

    rings = []
    for i in range(len(stations_x)):
        x = stations_x[i]
        bw = beam_w[i]
        sz = sheer_z[i]
        kz = keel_z[i]

        pts = [
            Vector((x, -bw, sz)),
            Vector((x, -bw * 0.92, kz + (sz-kz)*0.45)),
            Vector((x, -bw * 0.55, kz + (sz-kz)*0.12)),
            Vector((x,  0.0,       kz)),
            Vector((x,  bw * 0.55, kz + (sz-kz)*0.12)),
            Vector((x,  bw * 0.92, kz + (sz-kz)*0.45)),
            Vector((x,  bw, sz))
        ]
        ring_verts = [bm_hull.verts.new(p) for p in pts]
        rings.append(ring_verts)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for j in range(len(r1) - 1):
            bm_hull.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])

    bm_hull.to_mesh(mesh_hull)
    bm_hull.free()

    obj_hull = bpy.data.objects.new("Thuyen_Hull", mesh_hull)
    obj_hull.parent = parent
    obj_hull.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_hull)
    for p in obj_hull.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_hull, solidify_thickness=0.07, bevel_width=0.015, subsurf_levels=1)

    # B. SÀN BOONG THUYỀN
    mesh_deck = bpy.data.meshes.new("Thuyen_Deck")
    bm_deck = bmesh.new()
    deck_rings = []
    for i in range(1, len(stations_x) - 1):
        x = stations_x[i]
        bw = beam_w[i] * 0.88
        dz = keel_z[i] + (sheer_z[i] - keel_z[i]) * 0.58
        v_l = bm_deck.verts.new(Vector((x, -bw, dz)))
        v_r = bm_deck.verts.new(Vector((x,  bw, dz)))
        deck_rings.append((v_l, v_r))

    for i in range(len(deck_rings) - 1):
        l1, r1 = deck_rings[i]
        l2, r2 = deck_rings[i+1]
        bm_deck.faces.new([l1, r1, r2, l2])

    bm_deck.to_mesh(mesh_deck)
    bm_deck.free()
    obj_deck = bpy.data.objects.new("Thuyen_Deck", mesh_deck)
    obj_deck.parent = parent
    obj_deck.data.materials.append(mats['wood_deck'])
    bpy.context.collection.objects.link(obj_deck)
    add_smooth_modifiers(obj_deck, solidify_thickness=0.04, bevel_width=0.01, subsurf_levels=0)

    # C. HỆ THỐNG KHUNG SƯỜN
    mesh_ribs = bpy.data.meshes.new("Thuyen_Ribs")
    bm_ribs = bmesh.new()
    for i in range(1, len(stations_x) - 1):
        x = stations_x[i]
        bw = beam_w[i] * 0.94
        sz = sheer_z[i] * 0.98
        bmesh.ops.create_cube(bm_ribs, size=1.0, matrix=Matrix.Translation(Vector((x, 0, sz))) @ Matrix.Diagonal(Vector((0.08, bw * 2.0, 0.07, 1.0))))
        kz = keel_z[i] + 0.05
        bmesh.ops.create_cube(bm_ribs, size=1.0, matrix=Matrix.Translation(Vector((x, 0, (sz+kz)/2))) @ Matrix.Diagonal(Vector((0.08, 0.08, (sz-kz), 1.0))))

    bm_ribs.to_mesh(mesh_ribs)
    bm_ribs.free()
    obj_ribs = bpy.data.objects.new("Thuyen_Ribs", mesh_ribs)
    obj_ribs.parent = parent
    obj_ribs.data.materials.append(mats['wood_lim'])
    bpy.context.collection.objects.link(obj_ribs)

    # D. CỘT BUỒM VÀ CÁNH BUỒM CÁNH ÉN
    mesh_rig = bpy.data.meshes.new("Thuyen_Rigging")
    bm_rig = bmesh.new()
    bmesh.ops.create_cone(bm_rig, cap_ends=True, segments=16, radius1=0.10, radius2=0.06, depth=5.8, matrix=Matrix.Translation(Vector((0.5, 0, 2.7))))
    bmesh.ops.create_cone(bm_rig, cap_ends=True, segments=12, radius1=0.04, radius2=0.03, depth=3.2, matrix=Matrix.Translation(Vector((0.4, 0, 4.8))) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    bmesh.ops.create_cone(bm_rig, cap_ends=True, segments=12, radius1=0.04, radius2=0.03, depth=3.0, matrix=Matrix.Translation(Vector((0.4, 0, 1.2))) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    bm_rig.to_mesh(mesh_rig)
    bm_rig.free()
    obj_rig = bpy.data.objects.new("Thuyen_Mast_Spars", mesh_rig)
    obj_rig.parent = parent
    obj_rig.data.materials.append(mats['wood_lim'])
    bpy.context.collection.objects.link(obj_rig)
    for p in obj_rig.data.polygons:
        p.use_smooth = True

    mesh_sail = bpy.data.meshes.new("Thuyen_Sail_Cloth")
    bm_sail = bmesh.new()
    sail_u = 8
    sail_v = 12
    sail_grid = []
    for vi in range(sail_v + 1):
        t_v = vi / sail_v
        row = []
        z_curr = 1.2 + t_v * 3.6
        y_span = (1.4 - t_v * 0.3)
        for ui in range(sail_u + 1):
            t_u = (ui / sail_u) * 2.0 - 1.0
            y_curr = t_u * y_span
            x_belly = 0.4 + math.sin(t_v * math.pi) * math.cos(t_u * math.pi * 0.5) * 0.42
            v = bm_sail.verts.new(Vector((x_belly, y_curr, z_curr)))
            row.append(v)
        sail_grid.append(row)

    for vi in range(sail_v):
        for ui in range(sail_u):
            bm_sail.faces.new([sail_grid[vi][ui], sail_grid[vi][ui+1], sail_grid[vi+1][ui+1], sail_grid[vi+1][ui]])

    bm_sail.to_mesh(mesh_sail)
    bm_sail.free()
    obj_sail = bpy.data.objects.new("Thuyen_Sail", mesh_sail)
    obj_sail.parent = parent
    obj_sail.data.materials.append(mats['sail_cloth'])
    bpy.context.collection.objects.link(obj_sail)
    for p in obj_sail.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_sail, solidify_thickness=0.015, bevel_width=0, subsurf_levels=1)

    # E. 16 MÁI CHÈO
    mesh_oars = bpy.data.meshes.new("Thuyen_Oars")
    bm_oars = bmesh.new()
    for side in [-1, 1]:
        for idx, kx in enumerate([-4.2, -3.1, -2.0, -0.9, 0.2, 1.3, 2.4, 3.5]):
            bw = 1.15 if abs(kx) < 3.0 else 0.85
            sz = 0.45 + (abs(kx) / 6.0) ** 1.8 * 0.5
            pos_pin = Vector((kx, side * bw, sz))
            bmesh.ops.create_cone(bm_oars, cap_ends=True, segments=8, radius1=0.025, radius2=0.02, depth=0.22,
                                  matrix=Matrix.Translation(pos_pin + Vector((0, 0, 0.1))))
            rot_mat = Matrix.Rotation(math.radians(-25 * side), 4, 'X') @ Matrix.Rotation(math.radians(12), 4, 'Z')
            mat_shaft = Matrix.Translation(pos_pin + Vector((0, side * 0.9, -0.4))) @ rot_mat @ Matrix.Diagonal(Vector((0.04, 0.04, 2.6, 1.0)))
            bmesh.ops.create_cone(bm_oars, cap_ends=True, segments=10, radius1=0.5, radius2=0.5, depth=1.0, matrix=mat_shaft)
            mat_blade = Matrix.Translation(pos_pin + Vector((0, side * 1.8, -0.85))) @ rot_mat @ Matrix.Diagonal(Vector((0.02, 0.16, 0.9, 1.0)))
            bmesh.ops.create_cube(bm_oars, size=1.0, matrix=mat_blade)

    bm_oars.to_mesh(mesh_oars)
    bm_oars.free()
    obj_oars = bpy.data.objects.new("Thuyen_Oars", mesh_oars)
    obj_oars.parent = parent
    obj_oars.data.materials.append(mats['wood_oar'])
    bpy.context.collection.objects.link(obj_oars)
    for p in obj_oars.data.polygons:
        p.use_smooth = True

    # F. HÀNG KHIÊN MÂY SƠN THẾN
    mesh_shields = bpy.data.meshes.new("Thuyen_Shields")
    bm_shields = bmesh.new()
    for side in [-1, 1]:
        for kx in [-3.8, -2.6, -1.4, -0.2, 1.0, 2.2, 3.4]:
            bw = 1.16 if abs(kx) < 2.5 else 0.92
            sz = 0.48 + (abs(kx) / 6.0) ** 1.8 * 0.48
            pos = Vector((kx, side * (bw + 0.05), sz))
            rot = Matrix.Rotation(math.radians(90 * side), 4, 'X')
            mat_sh = Matrix.Translation(pos) @ rot @ Matrix.Diagonal(Vector((0.26, 0.26, 0.06, 1.0)))
            bmesh.ops.create_cone(bm_shields, cap_ends=True, segments=16, radius1=1.0, radius2=0.9, depth=1.0, matrix=mat_sh)

    bm_shields.to_mesh(mesh_shields)
    bm_shields.free()
    obj_shields = bpy.data.objects.new("Thuyen_Shields", mesh_shields)
    obj_shields.parent = parent
    obj_shields.data.materials.append(mats['shield'])
    bpy.context.collection.objects.link(obj_shields)
    for p in obj_shields.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_shields, solidify_thickness=0, bevel_width=0.015, subsurf_levels=1)

    # G. MŨI THUYỀN CHIM LẠC ĐỒNG
    mesh_prow = bpy.data.meshes.new("Thuyen_Prow_LacBird")
    bm_prow = bmesh.new()
    prow_pts = [
        Vector((5.8, 0, 1.0)),
        Vector((6.3, 0, 1.35)),
        Vector((6.7, 0, 1.85)),
        Vector((7.0, 0, 2.25)),
        Vector((6.8, 0, 2.05)),
        Vector((6.5, 0, 1.65)),
        Vector((6.2, 0, 1.25))
    ]
    for pt in prow_pts:
        bmesh.ops.create_icosphere(bm_prow, subdivisions=2, radius=0.10, matrix=Matrix.Translation(pt))

    bmesh.ops.create_cone(bm_prow, cap_ends=True, segments=12, radius1=0.12, radius2=0.01, depth=0.7,
                          matrix=Matrix.Translation(Vector((6.85, 0, 2.1))) @ Matrix.Rotation(math.radians(-65), 4, 'Y'))

    bm_prow.to_mesh(mesh_prow)
    bm_prow.free()
    obj_prow = bpy.data.objects.new("Thuyen_Prow_Figurehead", mesh_prow)
    obj_prow.parent = parent
    obj_prow.data.materials.append(mats['bronze'])
    bpy.context.collection.objects.link(obj_prow)
    for p in obj_prow.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_prow, solidify_thickness=0, bevel_width=0.01, subsurf_levels=1)

    return parent

# ==============================================================================
# 3. MÔ PHỎNG BÃI CỌC BẠCH ĐẰNG VÀ MẶT NƯỚC
# ==============================================================================

def build_historic_stakes(mat_wood, mat_iron):
    mesh_stake = bpy.data.meshes.new("BaiCoc_Mesh")
    bm = bmesh.new()

    coords = [
        (3.5, -2.8, -0.6, 22, -15),
        (5.0, -3.2, -0.5, 28,  10),
        (6.5, -2.2, -0.4, 25,  -5),
        (4.2,  3.0, -0.6, 24,  18),
        (5.8,  2.8, -0.4, 26, -12),
        (7.2,  2.2, -0.3, 20,   8),
        (8.5,  0.5, -0.2, 30,  -8),
        (8.8, -1.0, -0.2, 28,  14),
    ]

    for x, y, z, rot_y, rot_x in coords:
        rot = Matrix.Rotation(math.radians(rot_y), 4, 'Y') @ Matrix.Rotation(math.radians(rot_x), 4, 'X')
        m_body = Matrix.Translation(Vector((x, y, z))) @ rot @ Matrix.Diagonal(Vector((0.28, 0.28, 2.8, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.5, radius2=0.42, depth=1.0, matrix=m_body)
        m_tip = Matrix.Translation(Vector((x, y, z)) + rot @ Vector((0, 0, 1.4))) @ rot @ Matrix.Diagonal(Vector((0.24, 0.24, 0.8, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.5, radius2=0.01, depth=1.0, matrix=m_tip)

    bm.to_mesh(mesh_stake)
    bm.free()
    obj_stake = bpy.data.objects.new("BaiCoc_BachDang", mesh_stake)
    obj_stake.data.materials.append(mat_wood)
    obj_stake.data.materials.append(mat_iron)
    bpy.context.collection.objects.link(obj_stake)
    for p in obj_stake.data.polygons:
        p.use_smooth = True
    return obj_stake

def build_river_plane(mat_river):
    mesh = bpy.data.meshes.new("Song_BachDang_Surface")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=32, y_segments=32, size=35.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Song_BachDang_MatNuoc", mesh)
    obj.location = (0, 0, -0.05)
    obj.data.materials.append(mat_river)
    bpy.context.collection.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

# ==============================================================================
# 4. ÁNH SÁNG ĐIỆN ẢNH VÀ CAMERA
# ==============================================================================

def setup_studio_lighting(target_obj):
    sun_data = bpy.data.lights.new(name="Sun_BạchĐằng_Dawn", type='SUN')
    sun_data.energy = 4.5
    sun_data.color = (1.0, 0.94, 0.85)
    sun_data.angle = math.radians(2.0)
    sun_obj = bpy.data.objects.new(name="Sun_BạchĐằng_Dawn", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(130))
    bpy.context.collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new(name="Sky_Fill_Light", type='SUN')
    fill_data.energy = 1.8
    fill_data.color = (0.75, 0.85, 0.95)
    fill_obj = bpy.data.objects.new(name="Sky_Fill_Light", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-50), math.radians(-30), math.radians(-40))
    bpy.context.collection.objects.link(fill_obj)

    cam_data = bpy.data.cameras.new("CinemaCamera")
    cam_data.lens = 45.0
    cam_obj = bpy.data.objects.new("CinemaCamera", cam_data)
    cam_obj.location = (11.5, -9.5, 4.8)
    cam_obj.rotation_euler = (math.radians(72), math.radians(0), math.radians(50))
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

# ==============================================================================
# 5. TÍCH HỢP CODE TRỰC TIẾP VÀO TAB SCRIPTING CỦA BLENDER
# ==============================================================================

def embed_into_blender_scripting_editor():
    this_file = os.path.abspath(__file__) if '__file__' in globals() else ""
    if this_file and os.path.exists(this_file):
        with open(this_file, 'r', encoding='utf-8') as f:
            full_code = f.read()
    else:
        full_code = "# Script tạo thuyền chiến Bạch Đằng siêu thực (Ngô Quyền 938)\n"

    txt = bpy.data.texts.new("tao_thuyen_sieu_thuc_bach_dang.py")
    txt.write(full_code)

    # Chuyển 3D View sang Material Preview
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

def main():
    print("=== KHỞI CHẠY HỆ THỐNG DỰNG HÌNH THUYỀN CHIẾN SIÊU THỰC ===")
    reset_scene()

    mats = {
        'wood_hull': create_photoreal_wood_mat("Mat_GoLim_ThuyenTa", (0.22, 0.12, 0.05), rough=0.52, bump_scale=32.0),
        'wood_deck': create_photoreal_wood_mat("Mat_VanGo_Boong", (0.35, 0.22, 0.10), rough=0.60, bump_scale=40.0),
        'wood_lim':  create_photoreal_wood_mat("Mat_GoLim_KhungSuon", (0.18, 0.10, 0.04), rough=0.48, bump_scale=25.0),
        'wood_oar':  create_photoreal_wood_mat("Mat_GoLim_MaiCheo", (0.38, 0.25, 0.12), rough=0.55, bump_scale=35.0),
        'sail_cloth': create_sail_cloth_mat("Mat_Buom_NanTreCoi"),
        'bronze':    create_ancient_bronze_mat("Mat_DongCo_DongSon"),
        'iron':      create_iron_mat("Mat_SatRen_MuiCoc"),
        'shield':    create_shield_lacquer_mat("Mat_KhienMay_SonThen"),
        'river':     create_water_mat("Mat_SongBachDang_Nuoc")
    }

    warship = build_hyperrealistic_viet_warship(mats)
    stakes = build_historic_stakes(mats['wood_lim'], mats['iron'])
    river = build_river_plane(mats['river'])

    setup_studio_lighting(warship)
    embed_into_blender_scripting_editor()

    out_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    os.makedirs(out_dir, exist_ok=True)
    blend_file = os.path.join(out_dir, "thuyen_bach_dang_sieu_thuc.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f" ĐÃ LƯU FILE BLENDER SIÊU THỰC TẠI: {blend_file}")

    render_file = os.path.join(out_dir, "anh_thuyen_sieu_thuc.png")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = render_file
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH KIỂM CHỨNG TẠI: {render_file}")
    except Exception as err:
        print(f" Lỗi render: {err}")

if __name__ == "__main__":
    main()
