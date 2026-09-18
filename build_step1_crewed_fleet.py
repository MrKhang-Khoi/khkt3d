import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM MASTER] TÍCH HỢP TOÀN BỘ QUÂN LÍNH LÊN 34 CHIẾN THUYỀN ===")

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

scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = 0.1
if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    scene.eevee.shadow_resolution_scale = 2.0

col_env = bpy.data.collections.new('01_DiaHinh_SongNui')
col_coc = bpy.data.collections.new('02_TranDia_BaiCoc')
col_ta = bpy.data.collections.new('03_HamDoi_DaiViet_TienPhong')
col_dich = bpy.data.collections.new('04_HamDoi_NamHan_DaiHamDoi')
col_light = bpy.data.collections.new('05_ChieuSang_KhiQuyen')
col_crew = bpy.data.collections.new('06_ThuyThu_BinhSi_HaiBen')

for c in [col_env, col_coc, col_ta, col_dich, col_light, col_crew]:
    scene.collection.children.link(c)

# 2. BẦU TRỜI & ÁNH SÁNG TƯƠNG PHẢN ĐẸP
world = bpy.data.worlds.get('World_Step1_Master') or bpy.data.worlds.new('World_Step1_Master')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
bg_w.inputs['Color'].default_value = (0.28, 0.36, 0.44, 1.0)
bg_w.inputs['Strength'].default_value = 0.85
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

sun_data = bpy.data.lights.new(name="Sun_Winter", type='SUN')
sun_data.energy = 7.2
sun_data.color = (1.0, 0.97, 0.91)
sun_data.angle = math.radians(0.4)
sun_obj = bpy.data.objects.new(name="Sun_Winter", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(58), math.radians(12), math.radians(35))
col_light.objects.link(sun_obj)

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
    bsdf_k.inputs['Base Color'].default_value = (0.09, 0.11, 0.10, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.85
mount_west.data.materials.append(mat_karst)
if mount_west.name not in col_env.objects: col_env.objects.link(mount_west)
if mount_west.name in scene.collection.objects: scene.collection.objects.unlink(mount_west)

# 4. DÃY NÚI ĐÁ BỜ ĐÔNG (QUẢNG YÊN, X = +135m)
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

# 5. MẶT NƯỚC SÔNG BẠCH ĐẰNG (SẪM MÀU, TRONG VÀ TƯƠNG PHẢN ĐẸP)
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
    bsdf_w.inputs['Base Color'].default_value = (0.02, 0.08, 0.11, 1.0)
    bsdf_w.inputs['Roughness'].default_value = 0.09
    bsdf_w.inputs['Metallic'].default_value = 0.15
    tex_noise = nw_wat.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 24.0
    tex_noise.inputs['Detail'].default_value = 4.0
    bump_node = nw_wat.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value = 0.12
    bump_node.inputs['Distance'].default_value = 0.08
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

# 6. BÃI CỌC BẠCH ĐẰNG (CHÌM SÂU 0.7m DƯỚI NƯỚC TRIỀU CƯỜNG)
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

# CẬP NHẬT VẬT LIỆU BUỒM VÀNG RƠM ĐẶC TRƯNG ĐẠI VIỆT
for mat in bpy.data.materials:
    if 'Buom_CanhDoi' in mat.name:
        if mat.use_nodes:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.86, 0.65, 0.22, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.55
    elif 'NamHan_BuomNan' in mat.name:
        if mat.use_nodes:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                bsdf.inputs['Base Color'].default_value = (0.78, 0.74, 0.65, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.60

# =========================================================================
# TẠO VẬT LIỆU VÀ NGUYÊN MẪU QUÂN LÍNH 3D TỐI ƯU WEBGL
# =========================================================================
def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

mat_da_viet = get_or_create_mat("Mat_DaNguoi_VietCo", (0.72, 0.48, 0.32), 0.0, 0.65)
mat_giap_dong = get_or_create_mat("Mat_GiapHoTam_Dong", (0.55, 0.35, 0.14), 0.7, 0.35)
mat_giap_namhan = get_or_create_mat("Mat_GiapSat_NamHan", (0.22, 0.23, 0.25), 0.8, 0.30)
mat_bao_hoangthao = get_or_create_mat("Mat_CamBao_HoangThao", (0.78, 0.62, 0.15), 0.4, 0.40)
mat_flag = get_or_create_mat("Mat_CoLenh_DaiViet", (0.88, 0.15, 0.08), 0.0, 0.40)
mat_drum = get_or_create_mat("Mat_TrongTran_DongSon", (0.35, 0.25, 0.12), 0.3, 0.50)

# 1. Mesh Tay chèo Đại Việt
bm = bmesh.new()
# Đầu
mat_head = Matrix.Translation(Vector((0.0, 0.0, 0.85))) @ Matrix.Diagonal(Vector((0.14, 0.13, 0.15, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_head)
# Khăn đỏ
mat_band = Matrix.Translation(Vector((0.0, 0.0, 0.92))) @ Matrix.Diagonal(Vector((0.16, 0.15, 0.06, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_band)
# Thân
mat_torso = Matrix.Translation(Vector((0.0, 0.0, 0.52))) @ Matrix.Diagonal(Vector((0.28, 0.18, 0.42, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_torso)
# Khố chàm
mat_loincl = Matrix.Translation(Vector((0.0, 0.0, 0.24))) @ Matrix.Diagonal(Vector((0.30, 0.22, 0.22, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_loincl)
# Hai tay cầm chèo
mat_arm_l = Matrix.Translation(Vector((0.18, -0.16, 0.42))) @ Matrix.Diagonal(Vector((0.30, 0.09, 0.09, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_arm_l)
mat_arm_r = Matrix.Translation(Vector((0.18, 0.16, 0.42))) @ Matrix.Diagonal(Vector((0.30, 0.09, 0.09, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_arm_r)

mesh_rower = bpy.data.meshes.new("Mesh_Archetype_Rower_DaiViet")
bm.to_mesh(mesh_rower)
bm.free()
mesh_rower.materials.append(mat_da_viet)

# 2. Mesh Tướng chỉ huy Đại Việt
bm = bmesh.new()
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.58))) @ Matrix.Diagonal(Vector((0.15, 0.14, 0.16, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.32, 0.22, 0.55, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
mat_mirror = Matrix.Translation(Vector((0.17, 0.0, 1.25))) @ Matrix.Diagonal(Vector((0.04, 0.16, 0.16, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_mirror)
mat_ll = Matrix.Translation(Vector((0.0, -0.12, 0.44))) @ Matrix.Diagonal(Vector((0.15, 0.15, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.12, 0.44))) @ Matrix.Diagonal(Vector((0.15, 0.15, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
mat_arm = Matrix.Translation(Vector((0.32, 0.18, 1.40))) @ Matrix.Diagonal(Vector((0.45, 0.09, 0.09, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_arm)
mat_blade = Matrix.Translation(Vector((0.68, 0.18, 1.55))) @ Matrix.Diagonal(Vector((0.55, 0.04, 0.08, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_blade)

mesh_cmd = bpy.data.meshes.new("Mesh_Archetype_Commander_DaiViet")
bm.to_mesh(mesh_cmd)
bm.free()
mesh_cmd.materials.append(mat_giap_dong)

# 3. Mesh Lính gõ trống
bm = bmesh.new()
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.55))) @ Matrix.Diagonal(Vector((0.14, 0.13, 0.15, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.30, 0.20, 0.50, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
mat_ll = Matrix.Translation(Vector((0.0, -0.11, 0.44))) @ Matrix.Diagonal(Vector((0.14, 0.14, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.11, 0.44))) @ Matrix.Diagonal(Vector((0.14, 0.14, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
mat_d_l = Matrix.Translation(Vector((0.24, -0.15, 1.25))) @ Matrix.Diagonal(Vector((0.25, 0.08, 0.08, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_d_l)
mat_d_r = Matrix.Translation(Vector((0.24, 0.15, 1.25))) @ Matrix.Diagonal(Vector((0.25, 0.08, 0.08, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_d_r)

mesh_drummer = bpy.data.meshes.new("Mesh_Archetype_Drummer_DaiViet")
bm.to_mesh(mesh_drummer)
bm.free()
mesh_drummer.materials.append(mat_da_viet)

# 4. Mesh Lính thủy Nam Hán
bm = bmesh.new()
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.62))) @ Matrix.Diagonal(Vector((0.16, 0.16, 0.17, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_spike = Matrix.Translation(Vector((0.0, 0.0, 1.78))) @ Matrix.Diagonal(Vector((0.04, 0.04, 0.16, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_spike)
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.36, 0.26, 0.58, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
mat_ll = Matrix.Translation(Vector((0.0, -0.13, 0.44))) @ Matrix.Diagonal(Vector((0.16, 0.16, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.13, 0.44))) @ Matrix.Diagonal(Vector((0.16, 0.16, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
mat_spear = Matrix.Translation(Vector((0.26, 0.20, 1.15))) @ Matrix.Diagonal(Vector((0.05, 0.05, 2.30, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_spear)
mat_tip = Matrix.Translation(Vector((0.26, 0.20, 2.35))) @ Matrix.Diagonal(Vector((0.10, 0.02, 0.32, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_tip)

mesh_han_soldier = bpy.data.meshes.new("Mesh_Archetype_Soldier_NamHan")
bm.to_mesh(mesh_han_soldier)
bm.free()
mesh_han_soldier.materials.append(mat_giap_namhan)

# 5. Mesh Tướng quân Lưu Hoằng Tháo
bm = bmesh.new()
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.65))) @ Matrix.Diagonal(Vector((0.18, 0.18, 0.20, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_plume = Matrix.Translation(Vector((-0.06, 0.0, 1.84))) @ Matrix.Diagonal(Vector((0.08, 0.08, 0.20, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_plume)
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.38, 0.28, 0.62, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
mat_cape = Matrix.Translation(Vector((-0.20, 0.0, 0.95))) @ Matrix.Diagonal(Vector((0.06, 0.38, 0.90, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_cape)
mat_ll = Matrix.Translation(Vector((0.0, -0.15, 0.44))) @ Matrix.Diagonal(Vector((0.17, 0.17, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.15, 0.44))) @ Matrix.Diagonal(Vector((0.17, 0.17, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
mat_sword = Matrix.Translation(Vector((0.30, 0.0, 0.65))) @ Matrix.Diagonal(Vector((0.06, 0.06, 1.35, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_sword)

mesh_hoangthao = bpy.data.meshes.new("Mesh_Archetype_LuuHoangThao")
bm.to_mesh(mesh_hoangthao)
bm.free()
mesh_hoangthao.materials.append(mat_bao_hoangthao)

# =========================================================================
# A. ĐỘI THUYỀN ĐẠI VIỆT (8 THUYỀN - PHỄU NHỬ MỒI + ĐẦY ĐỦ QUÂN LÍNH)
# =========================================================================
viet_fleet_data = [
    ("DV_01_SoaiTienPhong_Ta",    -9.0,  -32.0, 1.10),
    ("DV_02_SoaiTienPhong_Huu",   +9.0,  -32.0, 1.10),
    ("DV_Ta_01_TienDac",        -28.0,  -48.0, 1.00),
    ("DV_Ta_02_TrungQuan",      -48.0,  -64.0, 0.95),
    ("DV_Ta_03_KhoaHau",        -68.0,  -80.0, 0.90),
    ("DV_Huu_01_TienDac",       +28.0,  -48.0, 1.00),
    ("DV_Huu_02_TrungQuan",     +48.0,  -64.0, 0.95),
    ("DV_Huu_03_KhoaHau",       +68.0,  -80.0, 0.90)
]

for idx, (s_name, px, py, scl) in enumerate(viet_fleet_data):
    if idx == 0:
        s_root = master_ta_root
        # Cờ Lệnh
        bm_flag = bmesh.new()
        bmesh.ops.create_cube(bm_flag, size=1.0)
        mesh_f = bpy.data.meshes.new("Mesh_CoLenh")
        bm_flag.to_mesh(mesh_f)
        bm_flag.free()
        obj_f = bpy.data.objects.new("CoLenh_NguHanh", mesh_f)
        obj_f.scale = (0.08, 0.8, 0.5)
        obj_f.location = (2.5, 0.0, 2.8)
        obj_f.data.materials.append(mat_flag)
        obj_f.parent = s_root
        col_ta.objects.link(obj_f)

        # Trống Trận
        bm_drum = bmesh.new()
        bmesh.ops.create_cube(bm_drum, size=1.0)
        mesh_d = bpy.data.meshes.new("Mesh_TrongTran")
        bm_drum.to_mesh(mesh_d)
        bm_drum.free()
        obj_d = bpy.data.objects.new("TrongTran_KhieuChien", mesh_d)
        obj_d.scale = (0.5, 0.5, 0.4)
        obj_d.location = (0.5, 0.0, 1.3)
        obj_d.data.materials.append(mat_drum)
        obj_d.parent = s_root
        col_ta.objects.link(obj_d)

        # Lính đánh trống
        obj_drummer = bpy.data.objects.new("Linh_DanhTrong_DV01", mesh_drummer)
        obj_drummer.location = (0.0, 0.0, 0.65)
        obj_drummer.rotation_euler = (0, 0, 0)
        obj_drummer.parent = s_root
        col_crew.objects.link(obj_drummer)
    else:
        s_root = clone_ship_clean(master_ta_root, f"Ta_{idx}", col_ta)
    
    s_root.location = (0, 0, 0)
    s_root.rotation_euler = (0, 0, math.radians(90))
    s_root.scale = (scl, scl, scl)
    
    # 1. BỐ TRÍ TAY CHÈO TRÊN THUYỀN (10 TAY CHÈO MỖI THUYỀN - CHIA 2 HÀNG)
    # Tọa độ X dọc thân thuyền: -2.4, -1.2, 0.0, 1.2, 2.4
    x_coords = [-2.4, -1.2, 0.0, 1.2, 2.4]
    for r_idx, rx in enumerate(x_coords):
        # Tay chèo Mạn Trái (Port, Y = +0.68)
        r_port = bpy.data.objects.new(f"Crew_Rower_Port_{s_name}_{r_idx}", mesh_rower)
        r_port.location = (rx, 0.68, 0.35)
        r_port.rotation_euler = (0, 0, 0)
        r_port.parent = s_root
        col_crew.objects.link(r_port)
        
        # Tay chèo Mạn Phải (Starboard, Y = -0.68)
        r_stbd = bpy.data.objects.new(f"Crew_Rower_Stbd_{s_name}_{r_idx}", mesh_rower)
        r_stbd.location = (rx, -0.68, 0.35)
        r_stbd.rotation_euler = (0, 0, 0)
        r_stbd.parent = s_root
        col_crew.objects.link(r_stbd)
        
        # Hoạt họa người chèo gập ngả theo nhịp chèo
        for r_obj in [r_port, r_stbd]:
            anim_r = r_obj.animation_data_create()
            act_r = bpy.data.actions.new(name=f"Act_{r_obj.name}")
            anim_r.action = act_r
            for f in range(1, 81):
                stroke_phase = (f + idx * 2) * 0.35
                pitch_rower = math.sin(stroke_phase) * math.radians(11.0)
                r_obj.rotation_euler = (0, pitch_rower, 0)
                r_obj.keyframe_insert(data_path='rotation_euler', frame=f)

    # 2. TƯỚNG CHỈ HUY ĐỨNG Ở SÀN ĐUÔI (STERN COMMANDER)
    cmd_obj = bpy.data.objects.new(f"Crew_Cmd_{s_name}", mesh_cmd)
    cmd_obj.location = (-3.6, 0.0, 0.55)
    cmd_obj.rotation_euler = (0, 0, 0)
    cmd_obj.parent = s_root
    col_crew.objects.link(cmd_obj)

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
        cur_y = py + prog * 12.0
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.14) * 0.025
        
        pitch = math.sin((f + idx * 4) * 0.16) * math.radians(0.45)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa mái chèo khua nước
    oar_obj = None
    for c in s_root.children_recursive:
        if 'Mai_Cheo' in c.name or 'Cheo' in c.name:
            oar_obj = c
            break
    if oar_obj:
        oar_anim = oar_obj.animation_data_create()
        oar_act = bpy.data.actions.new(name=f"Act_Oar_{s_name}")
        oar_anim.action = oar_act
        for f in range(1, 81):
            stroke_phase = (f + idx * 2) * 0.35
            rz = math.sin(stroke_phase) * math.radians(12.0)
            ry = math.cos(stroke_phase) * math.radians(5.0)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)

print("-> Đội thuyền Đại Việt (8 thuyền - ĐẦY ĐỦ 80 TAY CHÈO, 8 CHỈ HUY, CỜ TRỐNG) hoàn tất!")

# =========================================================================
# B. ĐẠI HẠM ĐỘI NAM HÁN (26 CHIẾN HẠM + LÍNH GIÁP SẮT & HOẰNG THÁO)
# =========================================================================
han_fleet_data = [
    # ĐỢT 1: THÊ ĐỘI TIÊN PHONG
    ("NH_W1_01", -75.0, 36.0, 0.75),
    ("NH_W1_02", -54.0, 30.0, 0.80),
    ("NH_W1_03", -32.0, 26.0, 0.85),
    ("NH_W1_04", -11.0, 24.0, 0.90),
    ("NH_W1_05", +11.0, 24.0, 0.90),
    ("NH_W1_06", +32.0, 26.0, 0.85),
    ("NH_W1_07", +54.0, 30.0, 0.80),
    ("NH_W1_08", +75.0, 36.0, 0.75),

    # ĐỢT 2: THÊ ĐỘI TRUNG QUÂN
    ("NH_W2_01", -85.0, 74.0, 0.80),
    ("NH_W2_02", -60.0, 64.0, 0.85),
    ("NH_W2_03", -30.0, 60.0, 0.90),
    ("NH_W2_SoaiHam_LauThuyen_HoangThao", 0.0, 56.0, 1.35), # SOÁI HẠM HOẰNG THÁO
    ("NH_W2_05", +30.0, 60.0, 0.90),
    ("NH_W2_06", +60.0, 64.0, 0.85),
    ("NH_W2_07", +85.0, 74.0, 0.80),
    ("NH_W2_08", -45.0, 82.0, 0.80),
    ("NH_W2_09", +45.0, 82.0, 0.80),

    # ĐỢT 3: THÊ ĐỘI HẬU QUÂN & TIẾP VIỆN
    ("NH_W3_01", -72.0, 110.0, 0.80),
    ("NH_W3_02", -36.0, 105.0, 0.85),
    ("NH_W3_03",   0.0, 102.0, 0.90),
    ("NH_W3_04", +36.0, 105.0, 0.85),
    ("NH_W3_05", +72.0, 110.0, 0.80),
    ("NH_W3_06", -54.0, 130.0, 0.80),
    ("NH_W3_07", +20.0, 126.0, 0.80),
    ("NH_W3_08", -24.0, 146.0, 0.75),
    ("NH_W3_09", +50.0, 142.0, 0.75),
]

for idx, (h_name, px, py, scl) in enumerate(han_fleet_data):
    if idx == 11:
        h_root = master_dich_root
        # ĐẶT TƯỚNG QUÂN LƯU HOẰNG THÁO LÊN TẦNG 3 SOÁI HẠM
        ht_obj = bpy.data.objects.new("Tuong_LuuHoangThao_Master", mesh_hoangthao)
        ht_obj.location = (0.5, 0.0, 5.2)
        ht_obj.rotation_euler = (0, 0, 0)
        ht_obj.parent = h_root
        col_crew.objects.link(ht_obj)

        # 6 Lính giáp sắt đứng gác lan can tầng 2 và tầng 3
        for g_idx, (gx, gy, gz) in enumerate([
            (2.2, 1.6, 2.3), (2.2, -1.6, 2.3),
            (-2.2, 1.6, 2.3), (-2.2, -1.6, 2.3),
            (0.0, 1.4, 4.2), (0.0, -1.4, 4.2)
        ]):
            g_obj = bpy.data.objects.new(f"Crew_Guard_SoaiHam_{g_idx}", mesh_han_soldier)
            g_obj.location = (gx, gy, gz)
            g_obj.rotation_euler = (0, 0, 0)
            g_obj.parent = h_root
            col_crew.objects.link(g_obj)
    else:
        h_root = clone_ship_clean(master_dich_root, f"Dich_{idx}", col_dich)
        # Mỗi tàu Nam Hán bố trí 4 lính giáp sắt đứng lan can
        for g_idx, (gx, gy, gz) in enumerate([(1.8, 1.5, 2.3), (1.8, -1.5, 2.3), (-1.8, 1.5, 2.3), (-1.8, -1.5, 2.3)]):
            g_obj = bpy.data.objects.new(f"Crew_Guard_{h_name}_{g_idx}", mesh_han_soldier)
            g_obj.location = (gx, gy, gz)
            g_obj.rotation_euler = (0, 0, 0)
            g_obj.parent = h_root
            col_crew.objects.link(g_obj)
        
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
        cur_y = py - prog * 15.0
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.10) * 0.018
        
        pitch = math.sin((f + idx * 2) * 0.12) * math.radians(0.3)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa 24 mái chèo Nam Hán quạt nước
    oar_obj = None
    for c in h_root.children_recursive:
        if 'MaiCheo' in c.name or 'Cheo' in c.name:
            oar_obj = c
            break
    if oar_obj:
        oar_anim = oar_obj.animation_data_create()
        oar_act = bpy.data.actions.new(name=f"Act_Oar_{h_name}")
        oar_anim.action = oar_act
        for f in range(1, 81):
            stroke_phase = (f + idx * 2) * 0.30
            rz = math.sin(stroke_phase) * math.radians(9.0)
            ry = math.cos(stroke_phase) * math.radians(3.5)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)

print(f"-> Đại Hạm đội Nam Hán ({len(han_fleet_data)} chiến hạm + 108 lính giáp sắt + Lưu Hoằng Tháo) hoàn tất!")

# 8. CAMERA ĐIỆN ẢNH TOÀN CẢNH SẮC NÉT
cam_data = bpy.data.cameras.new("Cam_Headon_Master")
cam_data.lens = 26.0
cam_data.clip_end = 1800.0
cam_obj = bpy.data.objects.new("Camera_ChienTruong_Headon", cam_data)

cam_obj.location = (0.0, -135.0, 68.0)
cam_obj.rotation_euler = (math.radians(63), 0, 0)
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
            r3d.view_distance = 160.0
            r3d.view_location = (0.0, 15.0, 5.0)
            r3d.view_rotation = Euler((math.radians(63), 0.0, 0.0), 'XYZ').to_quaternion()

for ob in bpy.context.selected_objects:
    ob.select_set(False)

scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except:
    pass

print("=== [VIETNAM-SIM MASTER] TÍCH HỢP QUÂN LÍNH 100% HOÀN THÀNH XUẤT SẮC! ===")