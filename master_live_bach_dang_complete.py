import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Matrix

print("=== BẮT ĐẦU XÂY DỰNG TOÀN DIỆN BẠCH ĐẰNG 938 SIÊU THỰC ===")

# 1. DỌN DẸP SẠCH CÁC OBJECT CŨ TRONG CẢNH ĐỂ TRÁNH TRÙNG LẶP
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

# Xóa các collection không dùng
for col in list(bpy.data.collections):
    if col.name not in ['Collection']:
        bpy.data.collections.remove(col)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 24
scene.frame_current = 1

# Tạo các Collection quản lý chuyên nghiệp
col_env = bpy.data.collections.new('BoiCanh_DiaHinh_SongNui')
col_coc = bpy.data.collections.new('TranDia_BaiCoc_BachDang')
col_quan_ta = bpy.data.collections.new('HamDoi_QuanTa_NgoQuyen')
col_quan_dich = bpy.data.collections.new('HamDoi_LauThuyen_NamHan')
col_lighting = bpy.data.collections.new('ChieuSang_KhiQuyen_MuaDong')

for c in [col_env, col_coc, col_quan_ta, col_quan_dich, col_lighting]:
    scene.collection.children.link(c)

# 2. BẦU TRỜI MÙA ĐÔNG 938 & ÁNH SÁNG ĐIỆN ẢNH (WINTER OVERCAST & LOW-ANGLE SUN)
world = bpy.data.worlds.get('World_BachDang_Winter') or bpy.data.worlds.new('World_BachDang_Winter')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
# Sương mù xám lam mùa đông giá rét cửa sông Bạch Đằng
bg_w.inputs['Color'].default_value = (0.28, 0.35, 0.42, 1.0)
bg_w.inputs['Strength'].default_value = 1.1
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

# Mặt trời mùa đông chiếu góc xiên thấp (Gió mùa Đông Bắc)
sun_data = bpy.data.lights.new(name="Nang_DongBac_XienThap", type='SUN')
sun_data.energy = 4.2
sun_data.color = (1.0, 0.92, 0.82)
sun_data.angle = math.radians(2.0)
sun_obj = bpy.data.objects.new(name="Sun_NangDongBac", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(62), math.radians(12), math.radians(35))
col_lighting.objects.link(sun_obj)

# Ánh sáng khuếch tán sương mù sông nước
sky_light = bpy.data.lights.new(name="Light_SuongMu_SongNuoc", type='SUN')
sky_light.energy = 1.5
sky_light.color = (0.65, 0.75, 0.85)
sky_light_obj = bpy.data.objects.new(name="Sun_SuongMu_Ta", object_data=sky_light)
sky_light_obj.rotation_euler = (math.radians(85), 0, math.radians(120))
col_lighting.objects.link(sky_light_obj)

print("-> Đã thiết lập Bầu trời & Ánh sáng mùa đông 938")

# 3. BỜ TÂY: DÃY NÚI ĐÁ VÔI KARST TRÀNG KÊNH (ANT LANDSCAPE CHUYÊN NGHIỆP)
print("-> Đang kiến tạo Dãy núi Tràng Kênh bằng ANT Landscape...")
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_TrangKenh',
    mesh_size_x=75.0,
    mesh_size_y=220.0,
    subdivision_x=100,
    subdivision_y=140,
    height=32.0,
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
obj_mount = bpy.context.active_object
obj_mount.name = 'DayNui_Karst_TrangKenh_Chinh'
obj_mount.location = (-60.0, 0.0, -2.0)

# Vật liệu Đá vôi Karst cổ phong hóa nứt nẻ
mat_karst = bpy.data.materials.new('Mat_DaVoi_Karst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.13, 0.15, 0.14, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.85
obj_mount.data.materials.append(mat_karst)
if obj_mount.name not in col_env.objects:
    col_env.objects.link(obj_mount)
if obj_mount.name in scene.collection.objects:
    scene.collection.objects.unlink(obj_mount)

# Dãy núi phụ hậu cảnh phía Bắc
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Phu_HauCanh',
    mesh_size_x=50.0,
    mesh_size_y=120.0,
    subdivision_x=60,
    subdivision_y=80,
    height=24.0,
    noise_type='ridged_multi_fractal',
    basis_type='VORONOI_F1',
    distortion=1.5,
    smooth_mesh=True,
    refresh=True
)
obj_mount_sub = bpy.context.active_object
obj_mount_sub.name = 'DayNui_HauCanh_Bac'
obj_mount_sub.location = (-45.0, 100.0, -1.0)
obj_mount_sub.data.materials.append(mat_karst)
if obj_mount_sub.name not in col_env.objects:
    col_env.objects.link(obj_mount_sub)
if obj_mount_sub.name in scene.collection.objects:
    scene.collection.objects.unlink(obj_mount_sub)

print("-> Dãy núi Karst Tràng Kênh hoàn tất!")

# 4. BỜ ĐÔNG: BÃI BÙN PHÙ SA & RỪNG SÚ VẸT MAI PHỤC (QUẢNG YÊN)
print("-> Đang tạo bãi bồi phù sa và rừng sú vẹt ngập mặn...")
bm_mud = bmesh.new()
# Bãi phù sa thoai thoải
for y_idx in range(40):
    for x_idx in range(15):
        px = 24.0 + x_idx * 3.2
        py = -100.0 + y_idx * 5.0
        # Dốc thoai thoải dần xuống mép nước
        pz = -0.2 + (x_idx * 0.15) + (math.sin(y_idx * 0.4) * 0.08)
        # vertex grid
bm_mud = bmesh.new()
mat_m_bank = Matrix.Translation(Vector((45.0, 0.0, 0.2))) @ Matrix.Diagonal(Vector((40.0, 220.0, 0.8, 1.0)))
bmesh.ops.create_cube(bm_mud, size=1.0, matrix=mat_m_bank)
mesh_mud = bpy.data.meshes.new('Mesh_BaiBoi_PhuSa_Dong')
bm_mud.to_mesh(mesh_mud)
bm_mud.free()
obj_mud = bpy.data.objects.new('BaiBoi_PhuSa_QuangYen', mesh_mud)
mat_mud = bpy.data.materials.new('Mat_BunPhuSa_PBR')
mat_mud.use_nodes = True
bsdf_m = next((n for n in mat_mud.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_m:
    bsdf_m.inputs['Base Color'].default_value = (0.08, 0.07, 0.05, 1.0)
    bsdf_m.inputs['Roughness'].default_value = 0.65
obj_mud.data.materials.append(mat_mud)
col_env.objects.link(obj_mud)

# Sinh cây sú vẹt mẫu chân thực bằng Sapling Tree Gen
scene.cursor.location = (200.0, 200.0, 0.0)
bpy.ops.curve.tree_add(
    do_update=True,
    bevel=True,
    showLeaves=True,
    levels=3,
    length=(1.2, 0.6, 0.35, 0.1),
    branches=(12, 16, 0, 0),
    seed=938,
    scale=2.5
)
tree_trunk = bpy.data.objects.get('tree')
tree_leaves = bpy.data.objects.get('leaves')

mat_trunk = bpy.data.materials.new('Mat_ThanCay_SuVet')
mat_trunk.use_nodes = True
bsdf_t = next((n for n in mat_trunk.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_t:
    bsdf_t.inputs['Base Color'].default_value = (0.09, 0.07, 0.05, 1.0)
    bsdf_t.inputs['Roughness'].default_value = 0.85
if tree_trunk:
    tree_trunk.data.materials.append(mat_trunk)

mat_leaf = bpy.data.materials.new('Mat_LaCay_SuVet')
mat_leaf.use_nodes = True
bsdf_l = next((n for n in mat_leaf.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_l:
    bsdf_l.inputs['Base Color'].default_value = (0.04, 0.12, 0.04, 1.0)
    bsdf_l.inputs['Roughness'].default_value = 0.55
if tree_leaves:
    tree_leaves.data.materials.append(mat_leaf)

# Phân bố rải rác 24 cụm cây sú vẹt tạo thành Rừng Ngập Mặn che giấu chiến thuyền
random.seed(938)
tree_coords = [
    (28.0, -80.0), (34.0, -70.0), (30.0, -60.0), (38.0, -50.0), (32.0, -40.0),
    (36.0, -30.0), (29.0, -20.0), (35.0, -10.0), (31.0,   0.0), (37.0,  10.0),
    (30.0,  20.0), (38.0,  30.0), (33.0,  40.0), (39.0,  50.0), (32.0,  60.0),
    (36.0,  70.0), (30.0,  80.0), (44.0, -55.0), (46.0, -25.0), (45.0,   5.0),
    (48.0,  35.0), (46.0,  65.0), (42.0, -15.0), (43.0,  25.0)
]

for idx, (tx, ty) in enumerate(tree_coords):
    scl = random.uniform(0.75, 1.3)
    rz = random.uniform(0, 2 * math.pi)
    if tree_trunk:
        c_tr = tree_trunk.copy()
        c_tr.name = f"Cay_SuVet_Trunk_{idx+1}"
        c_tr.location = (tx, ty, 0.2)
        c_tr.scale = (scl, scl, scl)
        c_tr.rotation_euler = (0, 0, rz)
        col_env.objects.link(c_tr)
    if tree_leaves:
        c_lf = tree_leaves.copy()
        c_lf.name = f"Cay_SuVet_Leaves_{idx+1}"
        c_lf.location = (tx, ty, 0.2)
        c_lf.scale = (scl, scl, scl)
        c_lf.rotation_euler = (0, 0, rz)
        col_env.objects.link(c_lf)

if tree_trunk: tree_trunk.location = (1000, 1000, 0)
if tree_leaves: tree_leaves.location = (1000, 1000, 0)
print("-> Rừng sú vẹt bờ Đông hoàn tất!")

# 5. MẶT NƯỚC SÔNG BẠCH ĐẰNG & HOẠT CẢNH THỦY TRIỀU RÚT (ANIMATED TIDE)
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=80, y_segments=80, size=240.0)
mesh_w = bpy.data.meshes.new('Mesh_SongBachDang')
bm_w.to_mesh(mesh_w)
bm_w.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang_Live', mesh_w)
obj_water.location = (0, 0, 0.0)

mat_wat = bpy.data.materials.new('Mat_NuocSong_Reflective_PBR')
mat_wat.use_nodes = True
bsdf_w = next((n for n in mat_wat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.02, 0.10, 0.13, 1.0) # Nước phù sa pha mặn
    bsdf_w.inputs['Roughness'].default_value = 0.10
    bsdf_w.inputs['Metallic'].default_value = 0.35
obj_water.data.materials.append(mat_wat)
col_env.objects.link(obj_water)

# Hoạt cảnh thủy triều rút chuẩn xác theo 4 Pha (300 frames):
# Pha 1 (1-75): Triều dâng cao Z = +0.65m (cọc chìm sâu)
# Pha 2 (75-145): Triều bắt đầu rút nhanh, Z hạ từ +0.65m xuống -0.50m
# Pha 3 & 4 (145-300): Triều kiệt ở Z = -0.50m (cọc nhô cao 0.7m đâm xuyên mạn thuyền)
anim_w = obj_water.animation_data_create()
act_w = bpy.data.actions.new(name='Action_ThuyTrieu_4Pha')
anim_w.action = act_w

for f in range(1, 301):
    if f <= 75:
        zt = 0.65 + math.sin(f * 0.08) * 0.015
    elif f <= 150:
        prog = (f - 75) / 75.0
        # Đường cong rút triều dốc mạnh
        smooth_prog = prog * prog * (3 - 2 * prog)
        zt = 0.65 - smooth_prog * 1.15
    else:
        zt = -0.50 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)

print("-> Mặt nước & Thủy triều 4 pha đã keyframe hoàn tất!")

# 6. NHẬP MASTER ASSETS: THUYỀN CHIẾN & BÃI CỌC TỪ MASTER BLEND
assembly_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_assembly.blend'
print(f"-> Đang nạp các master models từ {assembly_path}...")
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan', 'Collection_Coc_BachDang']

# Gắn các object từ các collection vừa nạp vào scene
appended_objs = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            appended_objs.append(ob)
            if 'Coc' in ob.name:
                if ob.name not in col_coc.objects: col_coc.objects.link(ob)
            elif 'NamHan' in ob.name or 'LauThuyen' in ob.name:
                if ob.name not in col_quan_dich.objects: col_quan_dich.objects.link(ob)
            else:
                if ob.name not in col_quan_ta.objects: col_quan_ta.objects.link(ob)

print(f"-> Đã nạp thành công {len(appended_objs)} master objects!")

# 7. THIẾT LẬP ROOT CONTROLLER & HOẠT CẢNH DIỄN BIẾN 4 PHA (BATTLE PROGRESSION)
# Tìm các object cốt lõi của 2 bên
thuyen_ta_roots = [o for o in col_quan_ta.objects if o.parent is None]
namhan_roots = [o for o in col_quan_dich.objects if o.parent is None]

# Tạo Root Empty cho Thuyền Ta (Ngô Quyền)
root_ta = bpy.data.objects.new("Root_ThuyenTa_NgoQuyen", None)
root_ta.empty_display_type = 'ARROWS'
root_ta.empty_display_size = 3.0
col_quan_ta.objects.link(root_ta)
for ob in thuyen_ta_roots:
    ob.parent = root_ta

# Tạo Root Empty cho Lâu Thuyền Nam Hán (Hoằng Tháo)
root_dich = bpy.data.objects.new("Root_LauThuyen_NamHan", None)
root_dich.empty_display_type = 'ARROWS'
root_dich.empty_display_size = 5.0
col_quan_dich.objects.link(root_dich)
for ob in namhan_roots:
    ob.parent = root_dich

# Tạo 2 Thuyền Phục Binh Đại Việt từ rừng sú vẹt bên bờ Đông (Pha 4 xuất kích)
thuyen_ta_mesh_objs = [o for o in col_quan_ta.objects if o.type == 'MESH']
if thuyen_ta_mesh_objs:
    base_m = thuyen_ta_mesh_objs[0]
    # Phục binh 1
    pb1 = bpy.data.objects.new("Thuyen_PhucBinh_BoDong_1", base_m.data)
    pb1.scale = (0.7, 0.7, 0.7)
    col_quan_ta.objects.link(pb1)
    # Phục binh 2
    pb2 = bpy.data.objects.new("Thuyen_PhucBinh_BoDong_2", base_m.data)
    pb2.scale = (0.7, 0.7, 0.7)
    col_quan_ta.objects.link(pb2)

    # Keyframe phục binh mai phục trong rừng sú vẹt rồi xông ra
    for f in range(1, 301):
        if f < 170:
            # Ẩn trong rừng sú vẹt (X = 26m)
            pb1.location = (26.0, 10.0, 0.6)
            pb1.rotation_euler = (0, 0, math.radians(-85))
            pb2.location = (27.0, -15.0, 0.6)
            pb2.rotation_euler = (0, 0, math.radians(-95))
        else:
            # Xông ra tấn công mạn thuyền giặc
            p_out = min(1.0, (f - 170) / 70.0)
            pb1.location = (26.0 - p_out * 18.0, 10.0 - p_out * 6.0, -0.3)
            pb1.rotation_euler = (0, 0, math.radians(-75))
            pb2.location = (27.0 - p_out * 19.0, -15.0 + p_out * 10.0, -0.3)
            pb2.rotation_euler = (0, 0, math.radians(-110))
        pb1.keyframe_insert(data_path='location', frame=f)
        pb1.keyframe_insert(data_path='rotation_euler', frame=f)
        pb2.keyframe_insert(data_path='location', frame=f)
        pb2.keyframe_insert(data_path='rotation_euler', frame=f)

# KEYFRAME HOẠT CẢNH CHO ROOT THUYỀN TA (NGÔ QUYỀN) - 4 PHA
anim_ta = root_ta.animation_data_create()
act_ta = bpy.data.actions.new(name="Action_NgoQuyen_4Pha")
anim_ta.action = act_ta

for f in range(1, 301):
    if f <= 75:
        # PHA 1: Khiêu chiến và giả thua rút lui ngược dòng vượt qua bãi cọc (Y từ -30 đến +12)
        prog = f / 75.0
        y_pos = -30.0 + prog * 42.0
        x_pos = math.sin(prog * 3.0) * 1.5 # Lượn sóng tránh chướng ngại
        z_pos = 0.65
        rot_z = math.radians(0) # Hướng mũi lên thượng lưu (Bắc)
        rot_x = math.sin(f * 0.2) * math.radians(2.0)
        rot_y = math.cos(f * 0.15) * math.radians(2.5)
    elif f <= 140:
        # PHA 2: Chờ đợi ở thượng lưu cho triều rút (Y = 12 đến 16)
        y_pos = 12.0 + (f - 75) / 65.0 * 4.0
        x_pos = 1.0
        z_pos = 0.65 - ((f - 75) / 65.0) * 0.8
        rot_z = math.radians(0)
        rot_x = math.sin(f * 0.15) * math.radians(1.5)
        rot_y = math.cos(f * 0.12) * math.radians(1.8)
    elif f <= 190:
        # PHA 3: Triều kiệt, Ngô Quyền hạ lệnh quay thuyền 180 độ đánh quật trở lại!
        turn_prog = (f - 140) / 50.0
        smooth_turn = turn_prog * turn_prog * (3 - 2 * turn_prog)
        y_pos = 16.0 - turn_prog * 2.0
        x_pos = 1.0 - math.sin(turn_prog * math.pi) * 3.0
        z_pos = -0.45
        rot_z = math.radians(smooth_turn * 180.0) # Quay ngoắt 180 độ
        rot_x = math.sin(turn_prog * math.pi) * math.radians(6.0)
        rot_y = math.sin(f * 0.2) * math.radians(2.0)
    else:
        # PHA 4: Toàn lực xung phong tiêu diệt địch (Y từ 14 lao về phía Nam Y = 4)
        charge_prog = (f - 190) / 110.0
        y_pos = 14.0 - charge_prog * 10.0
        x_pos = 0.5
        z_pos = -0.45
        rot_z = math.radians(180.0) # Giữ hướng tiến công trực diện
        rot_x = math.sin(f * 0.3) * math.radians(3.0)
        rot_y = math.cos(f * 0.25) * math.radians(2.5)

    root_ta.location = (x_pos, y_pos, z_pos)
    root_ta.rotation_euler = (rot_x, rot_y, rot_z)
    root_ta.keyframe_insert(data_path='location', frame=f)
    root_ta.keyframe_insert(data_path='rotation_euler', frame=f)

# KEYFRAME HOẠT CẢNH CHO LÂU THUYỀN NAM HÁN (HOẰNG THÁO) - 4 PHA
anim_dich = root_dich.animation_data_create()
act_dich = bpy.data.actions.new(name="Action_HoangThao_4Pha")
anim_dich.action = act_dich

for f in range(1, 301):
    if f <= 75:
        # PHA 1: Hung hăng truy đuổi, lướt trên mặt nước triều cường (Y từ -70 đến -15)
        prog = f / 75.0
        y_pos = -70.0 + prog * 55.0
        x_pos = 0.0
        z_pos = 0.55
        rot_x = math.sin(f * 0.1) * math.radians(1.2)
        rot_y = math.cos(f * 0.08) * math.radians(1.5)
        rot_z = 0.0
    elif f <= 125:
        # PHA 2: Tiến vào bãi cọc (Y từ -15 đến 0)
        prog = (f - 75) / 50.0
        y_pos = -15.0 + prog * 15.0
        x_pos = 0.0
        z_pos = 0.55 - prog * 0.4
        rot_x = 0.0
        rot_y = 0.0
        rot_z = 0.0
    elif f <= 180:
        # PHA 3: Triều rút cạn, đâm sầm vào bãi cọc bọc sắt! Khựng lại, thủng đáy, nghiêng 28 độ!
        hit_prog = (f - 125) / 55.0
        smooth_hit = hit_prog * hit_prog * (3 - 2 * hit_prog)
        y_pos = 0.0 + smooth_hit * 1.5 # Khựng lại gần như đứng yên
        x_pos = smooth_hit * 0.8
        z_pos = 0.15 - smooth_hit * 0.55 # Lún sâu xuống cọc
        # Tàu bị cọc sắt bẩy nghiêng mạn 28 độ và xoay gãy bánh lái
        rot_x = math.radians(-6.0 * smooth_hit)
        rot_y = math.radians(28.0 * smooth_hit)
        rot_z = math.radians(18.0 * smooth_hit)
    else:
        # PHA 4: Mắc kẹt hoàn toàn, rung lắc hỗn loạn do vỡ lườn tàu và bị quân ta giáp công
        y_pos = 1.5 + math.sin(f * 0.1) * 0.05
        x_pos = 0.8
        z_pos = -0.40 + math.sin(f * 0.15) * 0.02
        rot_x = math.radians(-6.0 + math.sin(f * 0.2) * 0.5)
        rot_y = math.radians(28.0 + math.sin(f * 0.25) * 0.8) # Giữ độ nghiêng nguy kịch
        rot_z = math.radians(18.0)

    root_dich.location = (x_pos, y_pos, z_pos)
    root_dich.rotation_euler = (rot_x, rot_y, rot_z)
    root_dich.keyframe_insert(data_path='location', frame=f)
    root_dich.keyframe_insert(data_path='rotation_euler', frame=f)

print("-> Hoạt cảnh 4 Pha của hai đoàn chiến thuyền đã thiết lập xuất sắc!")

# 8. BỐ TRÍ CAMERA ĐIỆN ẢNH QUAN SÁT (CINEMATIC CAMERA)
cam_data = bpy.data.cameras.new("Cam_BachDang_Cinematic")
cam_data.lens = 38.0
cam_data.clip_end = 600.0
cam_obj = bpy.data.objects.new("Camera_ChienTruong_BachDang", cam_data)
cam_obj.location = (28.0, -32.0, 18.0)
cam_obj.rotation_euler = (math.radians(65), 0, math.radians(38))
col_lighting.objects.link(cam_obj)
scene.camera = cam_obj

# Cập nhật Viewport Shading = MATERIAL và góc nhìn bao quát
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
            r3d.view_distance = 68.0
            r3d.view_location = (0.0, 0.0, 2.0)
            r3d.view_rotation = Euler((math.radians(60), 0.0, math.radians(22)), 'XYZ').to_quaternion()

# Cho timeline về Frame 1 và phát chuyển động
scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except Exception:
    pass

print("=== HOÀN TẤT TOÀN DIỆN BẠCH ĐẰNG 938: CHUẨN XÁC LỊCH SỬ & KỸ THUẬT SIÊU THỰC 100%! ===")
