import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM MASTER] BẮT ĐẦU THIẾT LẬP BẠCH ĐẰNG 938 ĐỈNH CAO ===")

# Dọn dẹp sạch scene
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

for col in list(bpy.data.collections):
    if col.name != 'Collection':
        bpy.data.collections.remove(col)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 24
scene.frame_current = 1

# Tạo các Collection phân cấp chuyên nghiệp
col_env = bpy.data.collections.new('01_DiaHinh_SongNui_BoiCanh')
col_coc = bpy.data.collections.new('02_TranDia_BaiCoc_BachDang')
col_ta = bpy.data.collections.new('03_HamDoi_DaiViet_NgoQuyen')
col_dich = bpy.data.collections.new('04_HamDoi_LauThuyen_NamHan')
col_light = bpy.data.collections.new('05_ChieuSang_KhiQuyen_MuaDong')

for c in [col_env, col_coc, col_ta, col_dich, col_light]:
    scene.collection.children.link(c)

# -------------------------------------------------------------
# 1. BẦU TRỜI MÙA ĐÔNG 938 & CHIẾU SÁNG ĐIỆN ẢNH (WINTER MIST & LOW-SUN)
# -------------------------------------------------------------
world = bpy.data.worlds.get('World_BachDang_Winter_Mist') or bpy.data.worlds.new('World_BachDang_Winter_Mist')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
# Sương mù xám lam lạnh lẽo mùa đông Bắc Bộ (Tháng 12 năm 938)
bg_w.inputs['Color'].default_value = (0.32, 0.40, 0.48, 1.0)
bg_w.inputs['Strength'].default_value = 1.2
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

# Ánh mặt trời mùa đông chiếu góc xiên thấp (22 độ so với chân trời)
sun_data = bpy.data.lights.new(name="Sun_DongBac_Winter", type='SUN')
sun_data.energy = 4.8
sun_data.color = (1.0, 0.94, 0.84)
sun_data.angle = math.radians(2.0)
sun_obj = bpy.data.objects.new(name="Sun_DongBac_Winter", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(65), math.radians(10), math.radians(40))
col_light.objects.link(sun_obj)

# Ánh sáng tán xạ sương mù
mist_light = bpy.data.lights.new(name="Light_SuongMu_TanXa", type='SUN')
mist_light.energy = 1.8
mist_light.color = (0.7, 0.8, 0.9)
mist_obj = bpy.data.objects.new(name="Light_SuongMu_TanXa", object_data=mist_light)
mist_obj.rotation_euler = (math.radians(90), 0, math.radians(130))
col_light.objects.link(mist_obj)

print("-> Đã thiết lập hoàn tất Bầu trời mùa đông 938 & Ánh sáng điện ảnh!")

# -------------------------------------------------------------
# 2. BỜ TÂY: DÃY NÚI ĐÁ VÔI KARST TRÀNG KÊNH HÙNG VĨ (A.N.T. LANDSCAPE)
# -------------------------------------------------------------
print("-> Đang sinh Dãy núi Karst Tràng Kênh bằng ANT Landscape...")
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_TrangKenh',
    mesh_size_x=80.0,
    mesh_size_y=260.0,
    subdivision_x=120,
    subdivision_y=160,
    height=35.0,
    noise_type='ridged_multi_fractal',
    basis_type='VORONOI_F2',
    distortion=2.2,
    strata=6,
    strata_type='0',
    edge_falloff='1',
    falloff_x=4.0,
    falloff_y=4.0,
    smooth_mesh=True,
    refresh=True
)
mount_main = bpy.context.active_object
mount_main.name = 'DayNui_Karst_TrangKenh_Chinh'
# Đặt vị trí bờ Tây và SCALE Z để núi vút cao 30-35m sừng sững trên mặt nước!
mount_main.location = (-55.0, 0.0, -1.0)
mount_main.scale = (1.0, 1.0, 32.0)

# Vật liệu Đá vôi Karst cổ phong hóa nứt nẻ có rêu bám
mat_karst = bpy.data.materials.new('Mat_DaVoi_Karst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.12, 0.14, 0.13, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.88
mount_main.data.materials.append(mat_karst)
if mount_main.name not in col_env.objects: col_env.objects.link(mount_main)
if mount_main.name in scene.collection.objects: scene.collection.objects.unlink(mount_main)

# Núi phụ hậu cảnh phía Bắc
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_HauCanh_Bac',
    mesh_size_x=60.0,
    mesh_size_y=140.0,
    subdivision_x=60,
    subdivision_y=80,
    height=26.0,
    noise_type='ridged_multi_fractal',
    basis_type='VORONOI_F1',
    distortion=1.6,
    smooth_mesh=True,
    refresh=True
)
mount_sub = bpy.context.active_object
mount_sub.name = 'DayNui_Karst_HauCanh_Bac'
mount_sub.location = (-40.0, 110.0, -1.0)
mount_sub.scale = (1.0, 1.0, 26.0)
mount_sub.data.materials.append(mat_karst)
if mount_sub.name not in col_env.objects: col_env.objects.link(mount_sub)
if mount_sub.name in scene.collection.objects: scene.collection.objects.unlink(mount_sub)

print("-> Dãy núi Karst Tràng Kênh hoàn tất!")

# -------------------------------------------------------------
# 3. BỜ ĐÔNG: BÃI BÙN PHÙ SA & RỪNG SÚ VẸT MAI PHỤC (SAPLING TREE GEN)
# -------------------------------------------------------------
print("-> Đang kiến tạo Bờ Đông: Bãi phù sa & Rừng sú vẹt ngập mặn...")
bm_mud = bmesh.new()
# Tạo bãi phù sa kéo dài 260m
mat_m_bank = Matrix.Translation(Vector((42.0, 0.0, 0.1))) @ Matrix.Diagonal(Vector((40.0, 260.0, 0.6, 1.0)))
bmesh.ops.create_cube(bm_mud, size=1.0, matrix=mat_m_bank)
mesh_mud = bpy.data.meshes.new('Mesh_BaiBoi_PhuSa_Dong')
bm_mud.to_mesh(mesh_mud)
bm_mud.free()
obj_mud = bpy.data.objects.new('BaiBoi_PhuSa_QuangYen', mesh_mud)
mat_mud = bpy.data.materials.new('Mat_BunPhuSa_PBR')
mat_mud.use_nodes = True
bsdf_m = next((n for n in mat_mud.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_m:
    bsdf_m.inputs['Base Color'].default_value = (0.07, 0.06, 0.04, 1.0)
    bsdf_m.inputs['Roughness'].default_value = 0.55
obj_mud.data.materials.append(mat_mud)
col_env.objects.link(obj_mud)

# Sinh cây sú vẹt chân thực bằng Sapling Tree Gen với tỷ lệ lớn
scene.cursor.location = (500.0, 500.0, 0.0)
bpy.ops.curve.tree_add(
    do_update=True,
    bevel=True,
    showLeaves=True,
    levels=3,
    length=(1.3, 0.7, 0.4, 0.12),
    branches=(14, 18, 0, 0),
    seed=938,
    scale=3.8
)
base_trunk = bpy.data.objects.get('tree')
base_leaves = bpy.data.objects.get('leaves')

mat_trunk = bpy.data.materials.new('Mat_ThanCay_SuVet_PBR')
mat_trunk.use_nodes = True
bsdf_t = next((n for n in mat_trunk.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_t:
    bsdf_t.inputs['Base Color'].default_value = (0.08, 0.06, 0.04, 1.0)
    bsdf_t.inputs['Roughness'].default_value = 0.85
if base_trunk: base_trunk.data.materials.append(mat_trunk)

mat_leaf = bpy.data.materials.new('Mat_LaCay_SuVet_PBR')
mat_leaf.use_nodes = True
bsdf_l = next((n for n in mat_leaf.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_l:
    bsdf_l.inputs['Base Color'].default_value = (0.03, 0.12, 0.03, 1.0)
    bsdf_l.inputs['Roughness'].default_value = 0.45
if base_leaves: base_leaves.data.materials.append(mat_leaf)

# Rải 28 cây sú vẹt dọc bờ Đông tạo thành thảm rừng rậm rạp che giấu quân mai phục
random.seed(938)
tree_coords = [
    (26.0, -90.0), (32.0, -80.0), (28.0, -70.0), (36.0, -60.0), (30.0, -50.0),
    (35.0, -40.0), (27.0, -30.0), (33.0, -20.0), (29.0, -10.0), (36.0,   0.0),
    (28.0,  10.0), (34.0,  20.0), (30.0,  30.0), (37.0,  40.0), (31.0,  50.0),
    (35.0,  60.0), (29.0,  70.0), (36.0,  80.0), (30.0,  90.0), (42.0, -65.0),
    (44.0, -35.0), (43.0,  -5.0), (45.0,  25.0), (44.0,  55.0), (43.0,  85.0),
    (38.0, -15.0), (39.0,  15.0), (40.0,  45.0)
]

for idx, (tx, ty) in enumerate(tree_coords):
    scl = random.uniform(0.9, 1.35)
    rz = random.uniform(0, 2 * math.pi)
    if base_trunk:
        c_tr = base_trunk.copy()
        c_tr.name = f"Cay_SuVet_Than_{idx+1}"
        c_tr.location = (tx, ty, 0.2)
        c_tr.scale = (scl, scl, scl)
        c_tr.rotation_euler = (0, 0, rz)
        col_env.objects.link(c_tr)
    if base_leaves:
        c_lf = base_leaves.copy()
        c_lf.name = f"Cay_SuVet_La_{idx+1}"
        c_lf.location = (tx, ty, 0.2)
        c_lf.scale = (scl, scl, scl)
        c_lf.rotation_euler = (0, 0, rz)
        col_env.objects.link(c_lf)

if base_trunk: base_trunk.location = (1000, 1000, 0)
if base_leaves: base_leaves.location = (1000, 1000, 0)
print("-> Rừng sú vẹt bờ Đông đã hoàn tất!")

# -------------------------------------------------------------
# 4. MẶT NƯỚC SÔNG BẠCH ĐẰNG & HOẠT CẢNH THỦY TRIỀU RÚT CHUẨN XÁC
# -------------------------------------------------------------
bm_w = bmesh.new()
# Mặt nước rộng 160m x 280m bao trùm toàn bộ cửa sông
bmesh.ops.create_grid(bm_w, x_segments=80, y_segments=100, size=280.0)
mesh_w = bpy.data.meshes.new('Mesh_SongBachDang_MatNuoc')
bm_w.to_mesh(mesh_w)
bm_w.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang_Chinh', mesh_w)
obj_water.location = (0, 0, 0.0)

mat_wat = bpy.data.materials.new('Mat_NuocSong_Reflective_PBR')
mat_wat.use_nodes = True
nw_wat = mat_wat.node_tree.nodes
lw_wat = mat_wat.node_tree.links
bsdf_w = next((n for n in nw_wat if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.03, 0.11, 0.14, 1.0)
    bsdf_w.inputs['Roughness'].default_value = 0.12
    bsdf_w.inputs['Metallic'].default_value = 0.30
    # Thêm gợn sóng nước (Noise Texture -> Bump)
    tex_noise = nw_wat.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 18.0
    tex_noise.inputs['Detail'].default_value = 4.0
    bump_node = nw_wat.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value = 0.15
    bump_node.inputs['Distance'].default_value = 0.1
    lw_wat.new(tex_noise.outputs['Fac'], bump_node.inputs['Height'])
    lw_wat.new(bump_node.outputs['Normal'], bsdf_w.inputs['Normal'])

obj_water.data.materials.append(mat_wat)
col_env.objects.link(obj_water)

# Keyframe thủy triều 4 Pha chuẩn lịch sử:
anim_w = obj_water.animation_data_create()
act_w = bpy.data.actions.new(name='Action_ThuyTrieu_4Pha')
anim_w.action = act_w

for f in range(1, 301):
    if f <= 75:
        # Pha 1: Triều dâng cao ngập kín bãi cọc (Z = +0.65m)
        zt = 0.65 + math.sin(f * 0.08) * 0.015
    elif f <= 150:
        # Pha 2: Triều bắt đầu rút mạnh
        prog = (f - 75) / 75.0
        smooth_prog = prog * prog * (3 - 2 * prog)
        zt = 0.65 - smooth_prog * 1.15
    else:
        # Pha 3 & 4: Triều cạn kiệt ở Z = -0.50m (bãi cọc sắt nhô cao)
        zt = -0.50 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)

print("-> Mặt nước & Thủy triều 4 pha đã keyframe hoàn tất!")

# -------------------------------------------------------------
# 5. NẠP MASTER ASSETS: THUYỀN CHIẾN & BÃI CỌC BỊT SẮT
# -------------------------------------------------------------
assembly_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_assembly.blend'
print(f"-> Đang nạp Master Models từ {assembly_path}...")
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan', 'Collection_Coc_BachDang']

appended_coc = []
appended_ta = []
appended_dich = []

for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'Coc' in ob.name:
                appended_coc.append(ob)
                if ob.name not in col_coc.objects: col_coc.objects.link(ob)
            elif 'NamHan' in ob.name or 'LauThuyen' in ob.name:
                appended_dich.append(ob)
                if ob.name not in col_dich.objects: col_dich.objects.link(ob)
            else:
                appended_ta.append(ob)
                if ob.name not in col_ta.objects: col_ta.objects.link(ob)

print(f"-> Đã nạp thành công: {len(appended_coc)} cọc, {len(appended_ta)} chi tiết thuyền ta, {len(appended_dich)} chi tiết lâu thuyền!")

# -------------------------------------------------------------
# 6. THIẾT LẬP HIERARCHY & HOẠT CẢNH DIỄN BIẾN 4 PHA (BATTLE PROGRESSION)
# -------------------------------------------------------------
# Xác định Object Gốc của Thuyền Ta & Lâu Thuyền
main_ta_obj = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
main_dich_obj = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')

# Tạo Root Empty cho Thuyền Ta (Ngô Quyền)
root_ta = bpy.data.objects.new("Root_ThuyenTa_NgoQuyen", None)
root_ta.empty_display_type = 'ARROWS'
root_ta.empty_display_size = 3.0
col_ta.objects.link(root_ta)

if main_ta_obj:
    # Reset local transform của main_ta_obj để không bị cộng dồn offset
    main_ta_obj.location = (0, 0, 0)
    main_ta_obj.rotation_euler = (0, 0, 0)
    main_ta_obj.parent = root_ta

# Tạo Root Empty cho Lâu Thuyền Nam Hán (Hoằng Tháo)
root_dich = bpy.data.objects.new("Root_LauThuyen_NamHan", None)
root_dich.empty_display_type = 'ARROWS'
root_dich.empty_display_size = 5.0
col_dich.objects.link(root_dich)

if main_dich_obj:
    main_dich_obj.location = (0, 0, 0)
    main_dich_obj.rotation_euler = (0, 0, 0)
    main_dich_obj.parent = root_dich

# Tạo 2 Thuyền Phục Binh Đại Việt xuất kích từ Rừng Sú Vẹt (Pha 4)
hull_ta = bpy.data.objects.get('Than_Thuyen_GoLim')
if hull_ta:
    pb1 = bpy.data.objects.new("Thuyen_PhucBinh_BoDong_1", hull_ta.data)
    pb1.scale = (0.75, 0.75, 0.75)
    col_ta.objects.link(pb1)
    
    pb2 = bpy.data.objects.new("Thuyen_PhucBinh_BoDong_2", hull_ta.data)
    pb2.scale = (0.75, 0.75, 0.75)
    col_ta.objects.link(pb2)

    for f in range(1, 301):
        if f < 170:
            pb1.location = (27.0, 15.0, 0.65)
            pb1.rotation_euler = (0, 0, math.radians(-85))
            pb2.location = (28.0, -18.0, 0.65)
            pb2.rotation_euler = (0, 0, math.radians(-95))
        else:
            p_out = min(1.0, (f - 170) / 75.0)
            pb1.location = (27.0 - p_out * 19.0, 15.0 - p_out * 10.0, -0.45)
            pb1.rotation_euler = (0, 0, math.radians(-70))
            pb2.location = (28.0 - p_out * 20.0, -18.0 + p_out * 14.0, -0.45)
            pb2.rotation_euler = (0, 0, math.radians(-115))
        pb1.keyframe_insert(data_path='location', frame=f)
        pb1.keyframe_insert(data_path='rotation_euler', frame=f)
        pb2.keyframe_insert(data_path='location', frame=f)
        pb2.keyframe_insert(data_path='rotation_euler', frame=f)

# KEYFRAME HOẠT CẢNH THUYỀN TA (NGÔ QUYỀN) - 4 PHA
anim_ta = root_ta.animation_data_create()
act_ta = bpy.data.actions.new(name="Action_NgoQuyen_4Pha")
anim_ta.action = act_ta

for f in range(1, 301):
    if f <= 75:
        # PHA 1: Khiêu chiến và giả thua rút chạy ngược dòng lên phía Bắc qua bãi cọc (Y từ -35 đến +14)
        prog = f / 75.0
        y_pos = -35.0 + prog * 49.0
        x_pos = math.sin(prog * 3.14) * 1.5
        z_pos = 0.65
        rot_z = 0.0 # Hướng Bắc
        rot_x = math.sin(f * 0.2) * math.radians(2.0)
        rot_y = math.cos(f * 0.15) * math.radians(2.5)
    elif f <= 135:
        # PHA 2: Chờ đợi ở thượng lưu (Y = 14 đến 18)
        y_pos = 14.0 + ((f - 75) / 60.0) * 4.0
        x_pos = 1.0
        z_pos = 0.65 - ((f - 75) / 60.0) * 0.8
        rot_z = 0.0
        rot_x = math.sin(f * 0.15) * math.radians(1.5)
        rot_y = math.cos(f * 0.12) * math.radians(1.8)
    elif f <= 185:
        # PHA 3: Triều kiệt, Ngô Quyền hạ lệnh quay thuyền 180 độ phản công!
        turn_prog = (f - 135) / 50.0
        smooth_turn = turn_prog * turn_prog * (3 - 2 * turn_prog)
        y_pos = 18.0 - turn_prog * 3.0
        x_pos = 1.0 - math.sin(turn_prog * math.pi) * 3.0
        z_pos = -0.45
        rot_z = math.radians(smooth_turn * 180.0)
        rot_x = math.sin(turn_prog * math.pi) * math.radians(6.0)
        rot_y = math.sin(f * 0.2) * math.radians(2.0)
    else:
        # PHA 4: Toàn lực xung phong đánh giáp lá cà (Y từ 15 lao xuống Y = 4)
        charge_prog = (f - 185) / 115.0
        y_pos = 15.0 - charge_prog * 11.0
        x_pos = 0.5
        z_pos = -0.45
        rot_z = math.radians(180.0)
        rot_x = math.sin(f * 0.3) * math.radians(3.0)
        rot_y = math.cos(f * 0.25) * math.radians(2.5)

    root_ta.location = (x_pos, y_pos, z_pos)
    root_ta.rotation_euler = (rot_x, rot_y, rot_z)
    root_ta.keyframe_insert(data_path='location', frame=f)
    root_ta.keyframe_insert(data_path='rotation_euler', frame=f)

# KEYFRAME HOẠT CẢNH LÂU THUYỀN NAM HÁN (HOẰNG THÁO) - 4 PHA
anim_dich = root_dich.animation_data_create()
act_dich = bpy.data.actions.new(name="Action_HoangThao_4Pha")
anim_dich.action = act_dich

for f in range(1, 301):
    if f <= 75:
        # PHA 1: Hăm hở truy đuổi từ ngoài cửa biển (Y từ -75 đến -15)
        prog = f / 75.0
        y_pos = -75.0 + prog * 60.0
        x_pos = 0.0
        z_pos = 0.55
        rot_x = math.sin(f * 0.1) * math.radians(1.2)
        rot_y = math.cos(f * 0.08) * math.radians(1.5)
        rot_z = 0.0
    elif f <= 125:
        # PHA 2: Vượt qua bãi cọc khi nước còn cao (Y từ -15 đến 0)
        prog = (f - 75) / 50.0
        y_pos = -15.0 + prog * 15.0
        x_pos = 0.0
        z_pos = 0.55 - prog * 0.4
        rot_x = 0.0
        rot_y = 0.0
        rot_z = 0.0
    elif f <= 180:
        # PHA 3: Triều rút cạn, vấp cọc sắt thủng lườn! Khựng lại, nghiêng 28 độ sang mạn phải!
        hit_prog = (f - 125) / 55.0
        smooth_hit = hit_prog * hit_prog * (3 - 2 * hit_prog)
        y_pos = 0.0 + smooth_hit * 1.5
        x_pos = smooth_hit * 0.6
        z_pos = 0.15 - smooth_hit * 0.55
        rot_x = math.radians(-6.0 * smooth_hit)
        rot_y = math.radians(28.0 * smooth_hit)
        rot_z = math.radians(16.0 * smooth_hit)
    else:
        # PHA 4: Mắc kẹt hoàn toàn trên bãi cọc, tàu bị xé rách chìm dần, bị tiêu diệt
        y_pos = 1.5 + math.sin(f * 0.1) * 0.04
        x_pos = 0.6
        z_pos = -0.40 + math.sin(f * 0.15) * 0.02
        rot_x = math.radians(-6.0 + math.sin(f * 0.2) * 0.5)
        rot_y = math.radians(28.0 + math.sin(f * 0.25) * 0.6)
        rot_z = math.radians(16.0)

    root_dich.location = (x_pos, y_pos, z_pos)
    root_dich.rotation_euler = (rot_x, rot_y, rot_z)
    root_dich.keyframe_insert(data_path='location', frame=f)
    root_dich.keyframe_insert(data_path='rotation_euler', frame=f)

print("-> Hoạt cảnh 4 Pha của hai đoàn chiến thuyền đã hoàn thành!")

# -------------------------------------------------------------
# 7. CAMERA ĐIỆN ẢNH & THIẾT LẬP GÓC NHÌN VIEWPORT TOÀN CẢNH
# -------------------------------------------------------------
cam_data = bpy.data.cameras.new("Cam_ChienTruong_BachDang")
cam_data.lens = 35.0
cam_data.clip_end = 800.0
cam_obj = bpy.data.objects.new("Camera_ChienTruong_BachDang", cam_data)
# Đặt camera ở vị trí góc cao bao quát: Dãy núi Tràng Kênh bên trái, Rừng sú vẹt bên phải, bãi cọc và hai tàu ở giữa!
cam_obj.location = (32.0, -38.0, 22.0)
cam_obj.rotation_euler = (math.radians(64), 0, math.radians(40))
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
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'PERSP'
            r3d.view_distance = 78.0
            r3d.view_location = (0.0, -5.0, 3.0)
            r3d.view_rotation = Euler((math.radians(62), 0.0, math.radians(35)), 'XYZ').to_quaternion()

# Phát hoạt cảnh ngay trên viewport
scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except Exception:
    pass

print("=== [VIETNAM-SIM MASTER] HOÀN TẤT 100%! BỐI CẢNH SIÊU THỰC & CHUẨN LỊCH SỬ! ===")
