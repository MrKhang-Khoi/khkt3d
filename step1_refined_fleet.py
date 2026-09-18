import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM] BƯỚC 1 TINH CHỈNH: ĐỘI HÌNH ĐỈNH CAO CHUẨN XÁC CHÍNH SỬ ===")

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

col_env = bpy.data.collections.new('B1_01_DiaHinh_SongNui')
col_coc = bpy.data.collections.new('B1_02_BaiCoc_NgamSau')
col_ta = bpy.data.collections.new('B1_03_HamDoi_TienPhong_DaiViet')
col_dich = bpy.data.collections.new('B1_04_HamDoi_VienChinh_NamHan')
col_light = bpy.data.collections.new('B1_05_ChieuSang_KhiQuyen')

for c in [col_env, col_coc, col_ta, col_dich, col_light]:
    scene.collection.children.link(c)

# 1. BẦU TRỜI MÙA ĐÔNG 938 & ÁNH SÁNG
world = bpy.data.worlds.get('World_BachDang_B1') or bpy.data.worlds.new('World_BachDang_B1')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
bg_w.inputs['Color'].default_value = (0.35, 0.42, 0.50, 1.0)
bg_w.inputs['Strength'].default_value = 1.25
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

sun_data = bpy.data.lights.new(name="Sun_Winter_LowAngle", type='SUN')
sun_data.energy = 5.2
sun_data.color = (1.0, 0.94, 0.84)
sun_obj = bpy.data.objects.new(name="Sun_Winter_LowAngle", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(66), math.radians(10), math.radians(35))
col_light.objects.link(sun_obj)

mist_light = bpy.data.lights.new(name="Light_SuongMu", type='SUN')
mist_light.energy = 2.0
mist_light.color = (0.7, 0.8, 0.92)
mist_obj = bpy.data.objects.new(name="Light_SuongMu", object_data=mist_light)
mist_obj.rotation_euler = (math.radians(88), 0, math.radians(125))
col_light.objects.link(mist_obj)

# 2. DÃY NÚI KARST TRÀNG KÊNH BỜ TÂY
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_TrangKenh',
    mesh_size_x=70.0,
    mesh_size_y=260.0,
    subdivision_x=120,
    subdivision_y=160,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=0.9,
    noise_depth=8,
    offset=0.88,
    gain=3.8,
    height=0.45,
    height_invert=False,
    edge_falloff='3',
    falloff_x=5.0,
    falloff_y=5.0,
    smooth_mesh=True,
    refresh=True
)
mount_main = bpy.context.active_object
mount_main.name = 'DayNui_Karst_TrangKenh_BoTay'
mount_main.location = (-55.0, 0.0, 0.0)
mount_main.scale = (1.0, 1.0, 30.0)

mat_karst = bpy.data.materials.new('Mat_DaKarst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.13, 0.15, 0.14, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.88
mount_main.data.materials.append(mat_karst)
if mount_main.name not in col_env.objects: col_env.objects.link(mount_main)
if mount_main.name in scene.collection.objects: scene.collection.objects.unlink(mount_main)

# 3. BÃI BÙN PHÙ SA & RỪNG SÚ VẸT BỜ ĐÔNG
bm_mud = bmesh.new()
mat_m_bank = Matrix.Translation(Vector((42.0, 0.0, 0.05))) @ Matrix.Diagonal(Vector((45.0, 260.0, 0.5, 1.0)))
bmesh.ops.create_cube(bm_mud, size=1.0, matrix=mat_m_bank)
mesh_mud = bpy.data.meshes.new('Mesh_BaiBoi_PhuSa')
bm_mud.to_mesh(mesh_mud)
bm_mud.free()
obj_mud = bpy.data.objects.new('BaiBoi_PhuSa_QuangYen', mesh_mud)
mat_mud = bpy.data.materials.new('Mat_BunPhuSa_PBR')
mat_mud.use_nodes = True
bsdf_m = next((n for n in mat_mud.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_m:
    bsdf_m.inputs['Base Color'].default_value = (0.08, 0.07, 0.05, 1.0)
    bsdf_m.inputs['Roughness'].default_value = 0.55
obj_mud.data.materials.append(mat_mud)
col_env.objects.link(obj_mud)

# Sapling tree
scene.cursor.location = (500.0, 500.0, 0.0)
bpy.ops.curve.tree_add(
    do_update=True,
    bevel=True,
    showLeaves=True,
    leafShape='rect',
    leafScale=0.55,
    levels=3,
    length=(1.5, 0.8, 0.45, 0.15),
    branches=(16, 20, 0, 0),
    seed=938,
    scale=4.5
)
base_trunk = bpy.data.objects.get('tree')
base_leaves = bpy.data.objects.get('leaves')

mat_trunk = bpy.data.materials.new('Mat_ThanCay_SuVet_PBR')
mat_trunk.use_nodes = True
bsdf_t = next((n for n in mat_trunk.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_t:
    bsdf_t.inputs['Base Color'].default_value = (0.07, 0.05, 0.04, 1.0)
    bsdf_t.inputs['Roughness'].default_value = 0.85
if base_trunk: base_trunk.data.materials.append(mat_trunk)

mat_leaf = bpy.data.materials.new('Mat_LaCay_SuVet_PBR')
mat_leaf.use_nodes = True
bsdf_l = next((n for n in mat_leaf.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_l:
    bsdf_l.inputs['Base Color'].default_value = (0.04, 0.16, 0.05, 1.0)
    bsdf_l.inputs['Roughness'].default_value = 0.40
if base_leaves: base_leaves.data.materials.append(mat_leaf)

random.seed(938)
tree_coords = [
    (26.0, -95.0), (32.0, -85.0), (28.0, -75.0), (35.0, -65.0), (30.0, -55.0),
    (36.0, -45.0), (27.0, -35.0), (33.0, -25.0), (29.0, -15.0), (36.0,  -5.0),
    (28.0,   5.0), (34.0,  15.0), (30.0,  25.0), (37.0,  35.0), (31.0,  45.0),
    (35.0,  55.0), (29.0,  65.0), (36.0,  75.0), (30.0,  85.0), (35.0,  95.0),
    (42.0, -70.0), (44.0, -40.0), (43.0, -10.0), (45.0,  20.0), (44.0,  50.0),
    (43.0,  80.0), (39.0, -20.0), (40.0,  10.0)
]

for idx, (tx, ty) in enumerate(tree_coords):
    scl = random.uniform(0.9, 1.35)
    rz = random.uniform(0, 2 * math.pi)
    if base_trunk:
        c_tr = base_trunk.copy()
        c_tr.name = f"Cay_SuVet_Than_{idx+1}"
        c_tr.location = (tx, ty, 0.15)
        c_tr.scale = (scl, scl, scl)
        c_tr.rotation_euler = (0, 0, rz)
        col_env.objects.link(c_tr)
    if base_leaves:
        c_lf = base_leaves.copy()
        c_lf.name = f"Cay_SuVet_La_{idx+1}"
        c_lf.location = (tx, ty, 0.15)
        c_lf.scale = (scl, scl, scl)
        c_lf.rotation_euler = (0, 0, rz)
        col_env.objects.link(c_lf)

if base_trunk: base_trunk.location = (1000, 1000, 0)
if base_leaves: base_leaves.location = (1000, 1000, 0)

# 4. MẶT NƯỚC TRIỀU CƯỜNG DÂNG CAO (+0.85m)
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=80, y_segments=100, size=280.0)
mesh_w = bpy.data.meshes.new('Mesh_SongBachDang_MatNuoc')
bm_w.to_mesh(mesh_w)
bm_w.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang_TrieuDang', mesh_w)

mat_wat = bpy.data.materials.new('Mat_NuocSong_Reflective_PBR')
mat_wat.use_nodes = True
nw_wat = mat_wat.node_tree.nodes
lw_wat = mat_wat.node_tree.links
bsdf_w = next((n for n in nw_wat if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.03, 0.11, 0.14, 1.0)
    bsdf_w.inputs['Roughness'].default_value = 0.12
    bsdf_w.inputs['Metallic'].default_value = 0.30
    tex_noise = nw_wat.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 16.0
    tex_noise.inputs['Detail'].default_value = 4.0
    bump_node = nw_wat.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value = 0.14
    bump_node.inputs['Distance'].default_value = 0.1
    lw_wat.new(tex_noise.outputs['Fac'], bump_node.inputs['Height'])
    lw_wat.new(bump_node.outputs['Normal'], bsdf_w.inputs['Normal'])

obj_water.data.materials.append(mat_wat)
col_env.objects.link(obj_water)

anim_w = obj_water.animation_data_create()
act_w = bpy.data.actions.new(name='Action_ThuyTrieu_B1')
anim_w.action = act_w
for f in range(1, 81):
    zt = 0.85 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)

# 5. 25 CỌC BẠCH ĐẰNG NGẬP SÂU VÔ HÌNH DƯỚI NƯỚC
assembly_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_assembly.blend'
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Coc_BachDang']

for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'Coc' in ob.name and ob.name not in col_coc.objects:
                col_coc.objects.link(ob)

# 6. NẠP MASTER SHIPS VÀ NHÂN BẢN HẠM ĐỘI
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan']

ta_objs_imported = []
dich_objs_imported = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'NamHan' in ob.name or 'LauThuyen' in ob.name:
                dich_objs_imported.append(ob)
            elif 'Coc' not in ob.name:
                ta_objs_imported.append(ob)

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
master_dich_root = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')

def clone_ship_hierarchy(source_root, prefix_name, target_collection):
    objs_to_copy = [source_root] + list(source_root.children_recursive)
    mapping = {}
    for o in objs_to_copy:
        new_o = o.copy()
        if o.data:
            new_o.data = o.data.copy()
        new_o.name = f"{prefix_name}_{o.name}"
        mapping[o] = new_o
        target_collection.objects.link(new_o)

    for o in objs_to_copy:
        new_o = mapping[o]
        if o.parent and o.parent in mapping:
            new_o.parent = mapping[o.parent]
            new_o.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        else:
            new_o.parent = None
            
    return mapping[source_root]

# --- A. HẠM ĐỘI TIÊN PHONG ĐẠI VIỆT (3 CHIẾN THUYỀN NHẸ) ---
master_ta_root.location = (0, 0, 0)
master_ta_root.rotation_euler = (0, 0, math.radians(90))
for ob in ta_objs_imported:
    if ob.name not in col_ta.objects: col_ta.objects.link(ob)

ta_ship_2 = clone_ship_hierarchy(master_ta_root, "DaiViet_TaDuc", col_ta)
ta_ship_3 = clone_ship_hierarchy(master_ta_root, "DaiViet_HuuDuc", col_ta)

# Đội hình thoi rút lui:
# Thuyền 1 (Soái tiên phong): X = 0, Y = 10
# Thuyền 2 (Tả dực sườn Tây): X = -6, Y = 20
# Thuyền 3 (Hữu dực sườn Đông): X = +6, Y = 18
viet_fleet = [
    {"name": "Root_DaiViet_1_Soai", "obj": master_ta_root, "offset_x": 0.0, "offset_y": 10.0, "scale": 1.0},
    {"name": "Root_DaiViet_2_TaDuc", "obj": ta_ship_2, "offset_x": -6.0, "offset_y": 20.0, "scale": 0.9},
    {"name": "Root_DaiViet_3_HuuDuc", "obj": ta_ship_3, "offset_x": +6.0, "offset_y": 18.0, "scale": 0.9}
]

for item in viet_fleet:
    root_e = bpy.data.objects.new(item["name"], None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_ta.objects.link(root_e)
    
    ship_obj = item["obj"]
    ship_obj.scale = (item["scale"], item["scale"], item["scale"])
    ship_obj.parent = root_e
    
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Action_{item['name']}")
    anim.action = act
    
    start_y = item["offset_y"]
    start_x = item["offset_x"]
    
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = start_y + prog * 36.0
        cur_x = start_x + math.sin(prog * 2.5) * 0.8
        cur_z = 0.85 + math.sin((f + start_x) * 0.12) * 0.02
        
        pitch = math.sin(f * 0.2) * math.radians(0.5)
        roll = 0.0  # CÂN BẰNG HOÀN TOÀN
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

# --- B. HẠM ĐỘI VIỄN CHINH NAM HÁN (1 SOÁI HẠM LÂU THUYỀN + 2 CHIẾN THUYỀN HỘ VỆ) ---
master_dich_root.location = (0, 0, 0)
master_dich_root.rotation_euler = (0, 0, math.radians(90))
for ob in dich_objs_imported:
    if ob.name not in col_dich.objects: col_dich.objects.link(ob)

han_escort_1 = clone_ship_hierarchy(master_dich_root, "NamHan_HoVe_Tay", col_dich)
han_escort_2 = clone_ship_hierarchy(master_dich_root, "NamHan_HoVe_Dong", col_dich)

# Đội hình tam giác thọc sâu (Trident assault):
# Soái hạm Hoằng Tháo ở trung tâm lòng sông: X = 0, Y = -42
# Thuyền hộ vệ Tả dực sườn Tây: X = -10, Y = -34 (nằm hoàn toàn trong luồng sông thông thoáng)
# Thuyền hộ vệ Hữu dực sườn Đông: X = +10, Y = -34
han_fleet = [
    {"name": "Root_NamHan_1_SoaiHam", "obj": master_dich_root, "offset_x": 0.0, "offset_y": -42.0, "scale": 1.0},
    {"name": "Root_NamHan_2_HoVe_Tay", "obj": han_escort_1, "offset_x": -10.0, "offset_y": -34.0, "scale": 0.65},
    {"name": "Root_NamHan_3_HoVe_Dong", "obj": han_escort_2, "offset_x": +10.0, "offset_y": -34.0, "scale": 0.65}
]

for item in han_fleet:
    root_e = bpy.data.objects.new(item["name"], None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_dich.objects.link(root_e)
    
    ship_obj = item["obj"]
    ship_obj.scale = (item["scale"], item["scale"], item["scale"])
    ship_obj.parent = root_e
    
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Action_{item['name']}")
    anim.action = act
    
    start_y = item["offset_y"]
    start_x = item["offset_x"]
    
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = start_y + prog * 44.0
        cur_x = start_x
        cur_z = 0.85 + math.sin((f + start_x) * 0.08) * 0.015
        
        pitch = math.sin(f * 0.12) * math.radians(0.35)
        roll = 0.0  # CÂN BẰNG HOÀN TOÀN
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

# 7. CAMERA ĐIỆN ẢNH & VIEWPORT
cam_data = bpy.data.cameras.new("Cam_B1_QuanSat")
cam_data.lens = 35.0
cam_data.clip_end = 800.0
cam_obj = bpy.data.objects.new("Camera_B1_QuanSat", cam_data)
# Đặt góc máy cao bao quát toàn diện:
cam_obj.location = (25.0, -52.0, 22.0)
cam_obj.rotation_euler = (math.radians(66), 0, math.radians(30))
col_light.objects.link(cam_obj)
scene.camera = cam_obj

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
            r3d.view_distance = 80.0
            r3d.view_location = (0.0, -12.0, 5.0)
            r3d.view_rotation = Euler((math.radians(65), 0.0, math.radians(28)), 'XYZ').to_quaternion()

scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except Exception:
    pass

print("=== [VIETNAM-SIM] BƯỚC 1 TINH CHỈNH HOÀN TẤT 100%! ===")
