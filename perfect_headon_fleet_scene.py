import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM MASTER] CHUẨN HÓA BƯỚC 1: TỶ LỆ VÀNG ĐIỆN ẢNH & CHIẾN THUẬT HẢI QUÂN ===")

# 1. DỌN DẸP SẠCH CẢNH
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

for col in list(bpy.data.collections):
    if col.name != 'Collection':
        bpy.data.collections.remove(col)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 80
scene.render.fps = 24
scene.frame_current = 1

col_env = bpy.data.collections.new('01_DiaHinh_SongNui')
col_coc = bpy.data.collections.new('02_TranDia_BaiCoc')
col_ta = bpy.data.collections.new('03_HamDoi_DaiViet_TienPhong')
col_dich = bpy.data.collections.new('04_HamDoi_NamHan_DaiHamDoi')
col_light = bpy.data.collections.new('05_ChieuSang_KhiQuyen')

for c in [col_env, col_coc, col_ta, col_dich, col_light]:
    scene.collection.children.link(c)

# 2. BẦU TRỜI & ÁNH SÁNG
world = bpy.data.worlds.get('World_Step1_Master') or bpy.data.worlds.new('World_Step1_Master')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
bg_w.inputs['Color'].default_value = (0.35, 0.44, 0.50, 1.0)
bg_w.inputs['Strength'].default_value = 1.30
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

sun_data = bpy.data.lights.new(name="Sun_Winter", type='SUN')
sun_data.energy = 5.2
sun_data.color = (1.0, 0.96, 0.90)
sun_obj = bpy.data.objects.new(name="Sun_Winter", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(60), math.radians(10), math.radians(35))
col_light.objects.link(sun_obj)

mist_light = bpy.data.lights.new(name="Light_SuongMu", type='SUN')
mist_light.energy = 2.4
mist_light.color = (0.65, 0.78, 0.90)
mist_obj = bpy.data.objects.new(name="Light_SuongMu", object_data=mist_light)
mist_obj.rotation_euler = (math.radians(88), 0, math.radians(125))
col_light.objects.link(mist_obj)

# 3. DÃY NÚI ĐÁ VÔI BỜ TÂY (TRÀNG KÊNH, X = -135m)
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_TrangKenh',
    mesh_size_x=110.0,
    mesh_size_y=600.0,
    subdivision_x=110,
    subdivision_y=180,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=0.85,
    noise_depth=8,
    offset=0.88,
    gain=3.8,
    height=0.55,
    height_invert=False,
    edge_falloff='3',
    falloff_x=7.0,
    falloff_y=7.0,
    smooth_mesh=True,
    refresh=True
)
mount_west = bpy.context.active_object
mount_west.name = 'DayNui_Karst_TrangKenh_BoTay'
mount_west.location = (-135.0, 15.0, 0.0)
mount_west.scale = (1.0, 1.0, 50.0)

mat_karst = bpy.data.materials.new('Mat_DaKarst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.11, 0.14, 0.13, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.85
mount_west.data.materials.append(mat_karst)
if mount_west.name not in col_env.objects: col_env.objects.link(mount_west)
if mount_west.name in scene.collection.objects: scene.collection.objects.unlink(mount_west)

# 4. DÃY NÚI ĐÁ BỜ ĐÔNG (QUẢNG YÊN, X = +135m) -> LÒNG SÔNG RỘNG 270m
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_QuangYen',
    mesh_size_x=110.0,
    mesh_size_y=600.0,
    subdivision_x=110,
    subdivision_y=180,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=0.85,
    noise_depth=8,
    offset=0.85,
    gain=3.6,
    height=0.52,
    height_invert=False,
    edge_falloff='3',
    falloff_x=7.0,
    falloff_y=7.0,
    smooth_mesh=True,
    refresh=True
)
mount_east = bpy.context.active_object
mount_east.name = 'DayNui_Karst_QuangYen_BoDong'
mount_east.location = (135.0, 15.0, 0.0)
mount_east.scale = (1.0, 1.0, 48.0)
mount_east.data.materials.append(mat_karst)
if mount_east.name not in col_env.objects: col_env.objects.link(mount_east)
if mount_east.name in scene.collection.objects: scene.collection.objects.unlink(mount_east)

# 5. MẶT NƯỚC SÔNG BẠCH ĐẰNG (600m x 600m)
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=120, y_segments=180, size=650.0)
mesh_w = bpy.data.meshes.new('Mesh_SongBachDang_MatNuoc')
bm_w.to_mesh(mesh_w)
bm_w.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang_Chinh', mesh_w)
obj_water.location = (0, 0, 0.85)

mat_wat = bpy.data.materials.new('Mat_NuocSong_Reflective_PBR')
mat_wat.use_nodes = True
nw_wat = mat_wat.node_tree.nodes
lw_wat = mat_wat.node_tree.links
bsdf_w = next((n for n in nw_wat if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.05, 0.15, 0.17, 1.0)
    bsdf_w.inputs['Roughness'].default_value = 0.16
    bsdf_w.inputs['Metallic'].default_value = 0.20
    tex_noise = nw_wat.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 24.0
    tex_noise.inputs['Detail'].default_value = 4.0
    bump_node = nw_wat.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value = 0.11
    bump_node.inputs['Distance'].default_value = 0.07
    lw_wat.new(tex_noise.outputs['Fac'], bump_node.inputs['Height'])
    lw_wat.new(bump_node.outputs['Normal'], bsdf_w.inputs['Normal'])

obj_water.data.materials.append(mat_wat)
col_env.objects.link(obj_water)

anim_w = obj_water.animation_data_create()
act_w = bpy.data.actions.new(name='Action_ThuyTrieu')
anim_w.action = act_w
for f in range(1, 81):
    zt = 0.85 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)

# 6. BÃI CỌC BẠCH ĐẰNG (CHÌM SÂU 0.7m)
assembly_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_assembly.blend'
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Coc_BachDang']

hero_stakes = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'Coc' in ob.name:
                hero_stakes.append(ob)
                col_coc.objects.link(ob)

for ob in hero_stakes:
    ob.location.z -= 2.65

random.seed(938)
if hero_stakes:
    master_coc = hero_stakes[0]
    for idx in range(65):
        cx = random.uniform(-90.0, 90.0)
        cy = random.uniform(-8.0, 10.0)
        cz = random.uniform(-3.1, -2.8)
        slant_x = random.uniform(-4.0, 4.0)
        slant_y = random.uniform(-40.0, -55.0)
        
        c_inst = master_coc.copy()
        c_inst.name = f"Coc_NgapSau_{idx+1}"
        c_inst.location = (cx, cy, cz)
        c_inst.rotation_euler = (math.radians(slant_y), math.radians(slant_x), 0)
        col_coc.objects.link(c_inst)

# 7. NẠP MASTER SHIPS
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan']

ta_master_objs = []
dich_master_objs = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'NamHan' in ob.name or 'LauThuyen' in ob.name:
                dich_master_objs.append(ob)
            elif 'Coc' not in ob.name:
                ta_master_objs.append(ob)

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
master_dich_root = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')

def clone_ship_clean(source_root, prefix_name, target_col):
    objs = [source_root] + list(source_root.children_recursive)
    mapping = {}
    for o in objs:
        new_o = o.copy()
        new_o.name = f"{prefix_name}_{o.name}"
        new_o.animation_data_clear()
        mapping[o] = new_o
        target_col.objects.link(new_o)
    for o in objs:
        new_o = mapping[o]
        if o.parent and o.parent in mapping:
            new_o.parent = mapping[o.parent]
            new_o.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        else:
            new_o.parent = None
    return mapping[source_root]

master_ta_root.animation_data_clear()
master_dich_root.animation_data_clear()
for o in ta_master_objs:
    o.animation_data_clear()
    if o.name not in col_ta.objects: col_ta.objects.link(o)
for o in dich_master_objs:
    o.animation_data_clear()
    if o.name not in col_dich.objects: col_dich.objects.link(o)

# =========================================================================
# A. ĐỘI THUYỀN ĐẠI VIỆT (8 THUYỀN TIỀN CẢNH)
# Dàn đội hình mũi tên, bố cục hoàn hảo nằm trọn trong khung hình camera
# =========================================================================
viet_fleet_data = [
    # Tên, X, Y, Scale
    ("DV_01_TienPhong_MuiDau",     0.0,  -10.0, 1.10),
    ("DV_02_TienPhong_Ta",       -18.0,  -24.0, 1.00),
    ("DV_03_TienPhong_Huu",      +18.0,  -24.0, 1.00),
    ("DV_04_TrungQuan_Ta",       -34.0,  -38.0, 0.95),
    ("DV_05_TrungQuan_Giua",       0.0,  -40.0, 1.05),
    ("DV_06_TrungQuan_Huu",      +34.0,  -38.0, 0.95),
    ("DV_07_HauQuan_Ta",         -42.0,  -52.0, 0.90),
    ("DV_08_HauQuan_Huu",        +42.0,  -52.0, 0.90)
]

for idx, (s_name, px, py, scl) in enumerate(viet_fleet_data):
    if idx == 0:
        s_root = master_ta_root
    else:
        s_root = clone_ship_clean(master_ta_root, f"Ta_{idx}", col_ta)
    
    s_root.location = (0, 0, 0)
    s_root.rotation_euler = (0, 0, math.radians(90))
    s_root.scale = (scl, scl, scl)
    
    root_e = bpy.data.objects.new(f"Root_{s_name}", None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_ta.objects.link(root_e)
    s_root.parent = root_e
    
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Act_{s_name}")
    anim.action = act
    
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = py + prog * 4.0
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.12) * 0.02
        
        pitch = math.sin((f + idx * 4) * 0.15) * math.radians(0.4)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

print("-> Đội thuyền Đại Việt (8 thuyền) hoàn tất!")

# =========================================================================
# B. ĐẠI HẠM ĐỘI NAM HÁN (26 CHIẾN HẠM HẬU CẢNH)
# =========================================================================
han_fleet_data = [
    # ĐỢT 1: THÊ ĐỘI TIÊN PHONG (Áp sát tuyến cọc, Y = +20 đến +34) - 8 Tàu trải rộng X = -75 đến +75
    ("NH_W1_01", -75.0, 32.0, 0.75),
    ("NH_W1_02", -54.0, 26.0, 0.80),
    ("NH_W1_03", -32.0, 22.0, 0.85),
    ("NH_W1_04", -11.0, 20.0, 0.90),
    ("NH_W1_05", +11.0, 20.0, 0.90),
    ("NH_W1_06", +32.0, 22.0, 0.85),
    ("NH_W1_07", +54.0, 26.0, 0.80),
    ("NH_W1_08", +75.0, 32.0, 0.75),

    # ĐỢT 2: THÊ ĐỘI TRUNG QUÂN (Soái hạm Hoằng Tháo ở giữa, Y = +52 đến +75) - 9 Tàu trải rộng X = -85 đến +85
    ("NH_W2_01", -85.0, 70.0, 0.80),
    ("NH_W2_02", -60.0, 60.0, 0.85),
    ("NH_W2_03", -30.0, 56.0, 0.90),
    ("NH_W2_SoaiHam_LauThuyen_HoangThao", 0.0, 52.0, 1.35), # SOÁI HẠM HOẰNG THÁO
    ("NH_W2_05", +30.0, 56.0, 0.90),
    ("NH_W2_06", +60.0, 60.0, 0.85),
    ("NH_W2_07", +85.0, 70.0, 0.80),
    ("NH_W2_08", -45.0, 78.0, 0.80),
    ("NH_W2_09", +45.0, 78.0, 0.80),

    # ĐỢT 3: THÊ ĐỘI HẬU QUÂN & TIẾP VIỆN (Y = +95 đến +145) - 9 Tàu
    ("NH_W3_01", -72.0, 105.0, 0.80),
    ("NH_W3_02", -36.0, 100.0, 0.85),
    ("NH_W3_03",   0.0,  98.0, 0.90),
    ("NH_W3_04", +36.0, 100.0, 0.85),
    ("NH_W3_05", +72.0, 105.0, 0.80),
    ("NH_W3_06", -54.0, 125.0, 0.80),
    ("NH_W3_07", +20.0, 122.0, 0.80),
    ("NH_W3_08", -24.0, 142.0, 0.75),
    ("NH_W3_09", +50.0, 138.0, 0.75),
]

for idx, (h_name, px, py, scl) in enumerate(han_fleet_data):
    if idx == 11:
        h_root = master_dich_root
    else:
        h_root = clone_ship_clean(master_dich_root, f"Dich_{idx}", col_dich)
        
    h_root.location = (0, 0, 0)
    h_root.rotation_euler = (0, 0, math.radians(-90))
    h_root.scale = (scl, scl, scl)
    
    root_e = bpy.data.objects.new(f"Root_{h_name}", None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_dich.objects.link(root_e)
    h_root.parent = root_e
    
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Act_{h_name}")
    anim.action = act
    
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = py - prog * 5.5
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.09) * 0.015
        
        pitch = math.sin((f + idx * 2) * 0.12) * math.radians(0.3)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

print(f"-> Đại Hạm đội Nam Hán ({len(han_fleet_data)} chiến hạm) hoàn tất!")

# 8. CAMERA ĐIỆN ẢNH VỪA VẶN BỐ CỤC HOÀN HẢO
cam_data = bpy.data.cameras.new("Cam_Headon_Master")
cam_data.lens = 26.0
cam_data.clip_end = 1800.0
cam_obj = bpy.data.objects.new("Camera_ChienTruong_Headon", cam_data)

# Đặt camera lùi nhẹ và cao hơn chút để bao trọn cả 8 thuyền ta với lề an toàn
cam_obj.location = (0.0, -125.0, 62.0)
cam_obj.rotation_euler = (math.radians(64), 0, 0)
col_light.objects.link(cam_obj)
scene.camera = cam_obj

# Cập nhật Viewport 3D
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True
                    space.overlay.show_relationship_lines = False
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'PERSP'
            r3d.view_distance = 150.0
            r3d.view_location = (0.0, 20.0, 5.0)
            r3d.view_rotation = Euler((math.radians(64), 0.0, 0.0), 'XYZ').to_quaternion()

for ob in bpy.context.selected_objects:
    ob.select_set(False)

scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except Exception:
    pass

print("=== [VIETNAM-SIM MASTER] THIẾT LẬP TỶ LỆ VÀNG HOÀN HẢO 100%! ===")