import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM MASTER] CHUẨN HÓA BƯỚC 1: ĐỘI HÌNH PHỄU NHỬ MỒI & CỜ LỆNH TRỐNG TRẬN ===")

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

# Cấu hình màu sắc & tương phản cao AgX
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

for c in [col_env, col_coc, col_ta, col_dich, col_light]:
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
# TẠO CỜ LỆNH & TRỐNG TRẬN KHIÊU CHIẾN TRÊN THUYỀN CHỈ HUY ĐẠI VIỆT
# =========================================================================
mat_flag = bpy.data.materials.new("Mat_CoLenh_DaiViet")
mat_flag.use_nodes = True
bsdf_fl = next((n for n in mat_flag.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_fl:
    bsdf_fl.inputs['Base Color'].default_value = (0.88, 0.15, 0.08, 1.0) # Đỏ cờ lệnh Đại Việt
    bsdf_fl.inputs['Roughness'].default_value = 0.40

mat_drum = bpy.data.materials.new("Mat_TrongTran_DongSon")
mat_drum.use_nodes = True
bsdf_dr = next((n for n in mat_drum.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_dr:
    bsdf_dr.inputs['Base Color'].default_value = (0.35, 0.25, 0.12, 1.0) # Gỗ bọc da trâu viền đồng
    bsdf_dr.inputs['Metallic'].default_value = 0.30
    bsdf_dr.inputs['Roughness'].default_value = 0.50

# =========================================================================
# A. ĐỘI THUYỀN ĐẠI VIỆT (8 THUYỀN) - THẾ TRẬN PHỄU NHỬ MỒI KINH ĐIỂN
# 2 Thuyền Tiên tiêu ở chính giữa luồng sông đối mặt Soái hạm Hoằng Tháo
# 6 Thuyền hai bên lùi dần sang hai mạn tạo phễu đón đường tháo chạy
# =========================================================================
viet_fleet_data = [
    # Tên, X, Y, Scale
    # 1. TOÁN TIỀN TIÊU CHÍNH DIỆN (CHỌC TỨC SOÁI HẠM HOẰNG THÁO)
    ("DV_01_SoaiTienPhong_Ta",    -9.0,  -32.0, 1.10), # Thuyền chỉ huy có Cờ & Trống
    ("DV_02_SoaiTienPhong_Huu",   +9.0,  -32.0, 1.10), # Thuyền phó khiêu chiến

    # 2. CÁNH TẢ LÙI DẦN VỀ BỜ TÂY (HÌNH PHỄU THOÁNG ĐÃNG)
    ("DV_Ta_01_TienDac",        -28.0,  -48.0, 1.00),
    ("DV_Ta_02_TrungQuan",      -48.0,  -64.0, 0.95),
    ("DV_Ta_03_KhoaHau",        -68.0,  -80.0, 0.90),

    # 3. CÁNH HỮU LÙI DẦN VỀ BỜ ĐÔNG (HÌNH PHỄU THOÁNG ĐÃNG)
    ("DV_Huu_01_TienDac",       +28.0,  -48.0, 1.00),
    ("DV_Huu_02_TrungQuan",     +48.0,  -64.0, 0.95),
    ("DV_Huu_03_KhoaHau",       +68.0,  -80.0, 0.90)
]

for idx, (s_name, px, py, scl) in enumerate(viet_fleet_data):
    if idx == 0:
        s_root = master_ta_root
        # Thêm Cột Cờ Lệnh & Trống Trận lên thuyền chỉ huy DV_01
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
        cur_y = py + prog * 12.0  # Tiến lướt sóng rõ nét
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.14) * 0.025
        
        pitch = math.sin((f + idx * 4) * 0.16) * math.radians(0.45)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa mái chèo khua nước nhịp nhàng
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

print("-> Đội thuyền Đại Việt (8 thuyền - Phễu Nhử Mồi, Cờ Lệnh & Trống Trận) hoàn tất!")

# =========================================================================
# B. ĐẠI HẠM ĐỘI NAM HÁN (26 CHIẾN HẠM)
# =========================================================================
han_fleet_data = [
    # ĐỢT 1: THÊ ĐỘI TIÊN PHONG (Y = +25 đến +38) - 8 Tàu trải rộng X = -75 đến +75
    ("NH_W1_01", -75.0, 36.0, 0.75),
    ("NH_W1_02", -54.0, 30.0, 0.80),
    ("NH_W1_03", -32.0, 26.0, 0.85),
    ("NH_W1_04", -11.0, 24.0, 0.90),
    ("NH_W1_05", +11.0, 24.0, 0.90),
    ("NH_W1_06", +32.0, 26.0, 0.85),
    ("NH_W1_07", +54.0, 30.0, 0.80),
    ("NH_W1_08", +75.0, 36.0, 0.75),

    # ĐỢT 2: THÊ ĐỘI TRUNG QUÂN (Soái hạm Hoằng Tháo ở giữa, Y = +56 đến +80) - 9 Tàu
    ("NH_W2_01", -85.0, 74.0, 0.80),
    ("NH_W2_02", -60.0, 64.0, 0.85),
    ("NH_W2_03", -30.0, 60.0, 0.90),
    ("NH_W2_SoaiHam_LauThuyen_HoangThao", 0.0, 56.0, 1.35), # SOÁI HẠM 3 TẦNG HOẰNG THÁO
    ("NH_W2_05", +30.0, 60.0, 0.90),
    ("NH_W2_06", +60.0, 64.0, 0.85),
    ("NH_W2_07", +85.0, 74.0, 0.80),
    ("NH_W2_08", -45.0, 82.0, 0.80),
    ("NH_W2_09", +45.0, 82.0, 0.80),

    # ĐỢT 3: THÊ ĐỘI HẬU QUÂN & TIẾP VIỆN (Y = +100 đến +150) - 9 Tàu
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
        cur_y = py - prog * 15.0  # Lao nhanh xuống phía Nam (-Y)
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

print(f"-> Đại Hạm đội Nam Hán ({len(han_fleet_data)} chiến hạm) hoàn tất!")

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

print("=== [VIETNAM-SIM MASTER] NÂNG CẤP ĐỘI HÌNH PHỄU NHỬ MỒI THÀNH CÔNG 100%! ===")