import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Matrix

engine_dir = os.path.dirname(os.path.abspath(__file__))
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from pbr_materials import get_vietnam_naval_materials
from batten_sail import create_vietnamese_batwing_sail

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

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

def build_vietnamese_warship(mats):
    root = bpy.data.objects.new("Thuyen_Chien_NgoQuyen_938", None)
    bpy.context.collection.objects.link(root)

    # 1. THÂN THUYỀN LOFTING
    mesh_hull = bpy.data.meshes.new("Hull_Loft_Mesh")
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

    obj_hull = bpy.data.objects.new("Than_Thuyen_GoLim", mesh_hull)
    obj_hull.parent = root
    obj_hull.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_hull)
    for p in obj_hull.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_hull, solidify_thickness=0.07, bevel_width=0.015, subsurf_levels=1)

    # 2. SÀN BOONG THUYỀN
    mesh_deck = bpy.data.meshes.new("Deck_Mesh")
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
    obj_deck = bpy.data.objects.new("San_Boong_Thuyen", mesh_deck)
    obj_deck.parent = root
    obj_deck.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_deck)
    add_smooth_modifiers(obj_deck, solidify_thickness=0.04, bevel_width=0.01, subsurf_levels=0)

    # 3. KHUNG SƯỜN & XÀ NGANG
    mesh_ribs = bpy.data.meshes.new("Ribs_Mesh")
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
    obj_ribs = bpy.data.objects.new("Khung_Suon_ChiuLuc", mesh_ribs)
    obj_ribs.parent = root
    obj_ribs.data.materials.append(mats['wood_lim'])
    bpy.context.collection.objects.link(obj_ribs)

    # 4. CÁNH BUỒM CÁNH DƠI (BAT-WING SAIL ENGINE)
    sail_rig = create_vietnamese_batwing_sail(mats, parent_obj=root, mast_pos=Vector((0.8, 0, 0)), mast_height=5.6, sail_angle_deg=28.0)

    # 5. 16 MÁI CHÈO
    mesh_oars = bpy.data.meshes.new("Oars_Mesh")
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
    obj_oars = bpy.data.objects.new("Mai_Cheo_Thuyen", mesh_oars)
    obj_oars.parent = root
    obj_oars.data.materials.append(mats['wood_hull'])
    bpy.context.collection.objects.link(obj_oars)
    for p in obj_oars.data.polygons:
        p.use_smooth = True

    # 6. KHIÊN MÂY SƠN THEN
    mesh_shields = bpy.data.meshes.new("Shields_Mesh")
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
    obj_shields = bpy.data.objects.new("Khien_May_SonThen", mesh_shields)
    obj_shields.parent = root
    obj_shields.data.materials.append(mats['shield'])
    bpy.context.collection.objects.link(obj_shields)
    for p in obj_shields.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_shields, solidify_thickness=0, bevel_width=0.015, subsurf_levels=1)

    # 7. MŨI CHIM LẠC ĐỒNG
    mesh_prow = bpy.data.meshes.new("Prow_LacBird_Mesh")
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
    obj_prow = bpy.data.objects.new("Mui_ChimLac_DongSon", mesh_prow)
    obj_prow.parent = root
    obj_prow.data.materials.append(mats['bronze'])
    bpy.context.collection.objects.link(obj_prow)
    for p in obj_prow.data.polygons:
        p.use_smooth = True
    add_smooth_modifiers(obj_prow, solidify_thickness=0, bevel_width=0.01, subsurf_levels=1)

    return root

def build_historic_stakes(mat_wood, mat_iron):
    mesh_stake = bpy.data.meshes.new("BaiCoc_BachDang_Mesh")
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
    mesh = bpy.data.meshes.new("Song_BachDang_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=32, y_segments=32, size=35.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Song_BachDang_Nuoc", mesh)
    obj.location = (0, 0, -0.05)
    obj.data.materials.append(mat_river)
    bpy.context.collection.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def setup_cinema_view(target_obj):
    # Chiếu sáng chính rực rỡ từ phía trước-trái chiếu thẳng vào mặt buồm cánh dơi
    sun_data = bpy.data.lights.new(name="Sun_BạchĐằng_Dawn", type='SUN')
    sun_data.energy = 5.5
    sun_data.color = (1.0, 0.95, 0.88)
    sun_data.angle = math.radians(2.5)
    sun_obj = bpy.data.objects.new(name="Sun_BạchĐằng_Dawn", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(35), math.radians(15), math.radians(65))
    bpy.context.collection.objects.link(sun_obj)

    # Ánh sáng bầu trời dịu nhẹ
    fill_data = bpy.data.lights.new(name="Sky_Fill_Light", type='SUN')
    fill_data.energy = 2.5
    fill_data.color = (0.78, 0.88, 0.98)
    fill_obj = bpy.data.objects.new(name="Sky_Fill_Light", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-40), math.radians(-20), math.radians(-30))
    bpy.context.collection.objects.link(fill_obj)

    # Camera toàn cảnh góc 3/4 điện ảnh lùi xa và nâng cao để thấy trọn vẹn cánh buồm cánh dơi vươn cao
    cam_data = bpy.data.cameras.new("CinemaCamera")
    cam_data.lens = 42.0
    cam_obj = bpy.data.objects.new("CinemaCamera", cam_data)
    cam_obj.location = (14.0, -12.5, 6.2)
    cam_obj.rotation_euler = (math.radians(68), math.radians(0), math.radians(48))
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

def build_scene():
    reset_scene()
    mats = get_vietnam_naval_materials()
    ship = build_vietnamese_warship(mats)
    stakes = build_historic_stakes(mats['wood_lim'], mats['iron'])
    river = build_river_plane(mats['river'])
    setup_cinema_view(ship)

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

if __name__ == "__main__":
    build_scene()
    out_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    blend_path = os.path.join(out_dir, "thuyen_buom_canh_doi_bach_dang.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f" ĐÃ LƯU FILE BUỒM CÁNH DƠI CHUẨN XÁC TẠI: {blend_path}")

    render_path = os.path.join(out_dir, "anh_buom_canh_doi_chuan_xac.png")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = render_path
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH BUỒM CÁNH DƠI TẠI: {render_path}")
    except Exception as e:
        print(f" Lỗi render: {e}")
