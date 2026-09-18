import bpy
import bmesh
import math
import random
import os
from mathutils import Vector, Euler, Matrix

print("================================================================================")
print("=== [VIETNAM-SIM MASTER] PHÂN CẢNH 3: THỦY TRIỀU RÚT - TỔNG PHẢN CÔNG & ĐẮM TÀU ===")
print("=== CĂN CỨ: ĐẠI VIỆT SỬ KÝ TOÀN THƯ & CHỈ ĐẠO LỊCH SỬ PO-HISTORIAN (240 FRAMES) ===")
print("================================================================================")

WS_DIR = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
SOLDIER_BLEND = os.path.join(WS_DIR, "thuy_binh_dai_viet_master.blend")
SHIP_TA_BLEND = os.path.join(WS_DIR, "assets", "ships", "thuyen_ta_ngoquyen_master.blend")
SHIP_DICH_BLEND = os.path.join(WS_DIR, "assets", "ships", "lau_thuyen_namhan_master.blend")
COC_BLEND = os.path.join(WS_DIR, "assets", "props", "coc_bach_dang_master.blend")
STEP2_CHECKPOINT = os.path.join(WS_DIR, "scenes", "dai_chien_bach_dang_step2_checkpoint.blend")

# 1. TẠO CẢNH MỚI HOÀN TOÀN TRỐNG ĐỂ DỰNG PHÂN CẢNH 3
bpy.ops.wm.read_homefile(use_empty=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 240
scene.render.fps = 24
scene.frame_current = 1

# Cấu hình Render & Viewport AgX
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = 0.15
if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    scene.eevee.shadow_resolution_scale = 2.0

col_env = bpy.data.collections.new('01_DiaHinh_SongNui')
col_coc = bpy.data.collections.new('02_TranDia_BaiCoc')
col_ta = bpy.data.collections.new('03_HamDoi_DaiViet_TienPhong')
col_dich = bpy.data.collections.new('04_HamDoi_NamHan_DaiHamDoi')
col_crew = bpy.data.collections.new('05_ThuyThu_BinhSi_DaiViet')
col_light = bpy.data.collections.new('06_ChieuSang_KhiQuyen')
col_cam = bpy.data.collections.new('07_Cameras_DienAnh')

for c in [col_env, col_coc, col_ta, col_dich, col_crew, col_light, col_cam]:
    scene.collection.children.link(c)

# 2. BẦU TRỜI & ÁNH SÁNG MÙA ĐÔNG CHIỀU GIỜ MÙI (13H-14H)
world = bpy.data.worlds.get('World_Step3_Master') or bpy.data.worlds.new('World_Step3_Master')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
bg_w.inputs['Color'].default_value = (0.24, 0.32, 0.40, 1.0) # Bầu trời lạnh mùa đông
bg_w.inputs['Strength'].default_value = 0.80
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

sun_data = bpy.data.lights.new(name="Sun_Winter_14h", type='SUN')
sun_data.energy = 7.8
sun_data.color = (1.0, 0.95, 0.88)
sun_data.angle = math.radians(0.4)
sun_obj = bpy.data.objects.new(name="Sun_Winter_14h", object_data=sun_data)
# Hướng nắng chếch Tây Nam rọi bóng xiên dữ dội
sun_obj.rotation_euler = (math.radians(52), math.radians(16), math.radians(45))
col_light.objects.link(sun_obj)

# 3. DÃY NÚI ĐÁ VÔI KARST TRÀNG KÊNH (BỜ TÂY) & QUẢNG YÊN (BỜ ĐÔNG)
if os.path.exists(STEP2_CHECKPOINT):
    with bpy.data.libraries.load(STEP2_CHECKPOINT, link=False) as (data_from, data_to):
        data_to.objects = [o for o in data_from.objects if 'DayNui_Karst' in o]
    for o in data_to.objects:
        if o:
            col_env.objects.link(o)
else:
    for name, pos_x in [('DayNui_Karst_TrangKenh_BoTay', -135.0), ('DayNui_Karst_QuangYen_BoDong', 135.0)]:
        bpy.ops.mesh.landscape_add(
            ant_terrain_name=name,
            mesh_size_x=110.0, mesh_size_y=600.0,
            subdivision_x=100, subdivision_y=160,
            noise_type='ridged_multi_fractal',
            distortion=0.85, height=0.55, smooth_mesh=True
        )
        mount = bpy.context.active_object
        mount.name = name
        mount.location = (pos_x, 15.0, 0.0)
        mount.scale = (1.0, 1.0, 50.0)
        col_env.objects.link(mount)

# 4. MẶT NƯỚC SÔNG BẠCH ĐẰNG - DIỄN HOẠT THỦY TRIỀU RÚT TỪ Z = +0.85m XUỐNG Z = -1.45m
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=140, y_segments=200, size=650.0)
mesh_w = bpy.data.meshes.new('Mesh_SongBachDang_MatNuoc')
bm_w.to_mesh(mesh_w)
bm_w.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang_Chinh', mesh_w)
col_env.objects.link(obj_water)

mat_wat = bpy.data.materials.new('Mat_NuocSong_TrieuRut_PBR')
mat_wat.use_nodes = True
nw_wat = mat_wat.node_tree.nodes
lw_wat = mat_wat.node_tree.links
bsdf_w = next((n for n in nw_wat if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.015, 0.075, 0.095, 1.0)
    bsdf_w.inputs['Roughness'].default_value = 0.08
    bsdf_w.inputs['Metallic'].default_value = 0.20
    tex_noise = nw_wat.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 28.0
    tex_noise.inputs['Detail'].default_value = 5.0
    bump_node = nw_wat.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value = 0.15
    bump_node.inputs['Distance'].default_value = 0.09
    lw_wat.new(tex_noise.outputs['Fac'], bump_node.inputs['Height'])
    lw_wat.new(bump_node.outputs['Normal'], bsdf_w.inputs['Normal'])
obj_water.data.materials.append(mat_wat)

anim_w = obj_water.animation_data_create()
act_w = bpy.data.actions.new(name='Action_ThuyTrieu_Rut_938')
anim_w.action = act_w

for f in range(1, 241):
    if f <= 50:
        prog = (f - 1) / 49.0
        z_tide = 0.85 - prog * 0.40
    elif f <= 180:
        prog = (f - 50) / 130.0
        z_tide = 0.45 - (prog ** 1.1) * 1.65
    else:
        prog = (f - 180) / 60.0
        z_tide = -1.20 - prog * 0.25
    
    wave = math.sin(f * 0.08) * 0.018
    obj_water.location = (0, 0, z_tide + wave)
    obj_water.keyframe_insert(data_path='location', frame=f)

print("-> Mặt nước sông Bạch Đằng & Động học triều rút (Z: +0.85m -> -1.45m) hoàn tất!")

# 5. TRẬN ĐỊA BÃI CỌC BẠCH ĐẰNG (GỖ LIM BỊT SẮT - CẮM NGHIÊNG 45°-55° XUÔI THEO NƯỚC RÚT)
with bpy.data.libraries.load(COC_BLEND, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Coc_BachDang']

hero_stakes = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'Coc' in ob.name:
                hero_stakes.append(ob)
                col_coc.objects.link(ob)

random.seed(938)
if hero_stakes:
    master_coc = hero_stakes[0]
    master_coc.location = (0, 0, -1.8)
    master_coc.rotation_euler = (math.radians(-50.0), 0, 0)
    
    for idx in range(120):
        cx = random.uniform(-85.0, 85.0)
        cy = random.uniform(-20.0, 22.0)
        cz = random.uniform(-2.2, -1.7)
        slant_x = random.uniform(-6.0, 6.0)
        slant_y = random.uniform(-46.0, -56.0)
        
        c_inst = master_coc.copy()
        c_inst.name = f"Coc_TranDia_{idx+1}"
        c_inst.location = (cx, cy, cz)
        c_inst.rotation_euler = (math.radians(slant_y), math.radians(slant_x), 0)
        col_coc.objects.link(c_inst)

print(f"-> Trận địa bãi cọc ({len(col_coc.objects)} cọc lim bịt sắt nghiêng 45°-55°) hoàn tất!")

# 6. NẠP MASTER THUYỀN CHIẾN HAI BÊN
with bpy.data.libraries.load(SHIP_TA_BLEND, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta']
ta_col = data_to.collections[0] if data_to.collections else None

with bpy.data.libraries.load(SHIP_DICH_BLEND, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Lau_Thuyen_NamHan']
dich_col = data_to.collections[0] if data_to.collections else None

ta_master_objs = [ob for ob in ta_col.objects if ob] if ta_col else []
dich_master_objs = [ob for ob in dich_col.objects if ob] if dich_col else []

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
master_dich_root = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')

def clone_ship_hierarchy(source_root, prefix, target_col):
    family = [source_root] + list(source_root.children_recursive)
    mapping = {}
    for o in family:
        new_o = o.copy()
        new_o.name = f"{prefix}_{o.name}"
        new_o.animation_data_clear()
        mapping[o] = new_o
        target_col.objects.link(new_o)
    for o in family:
        new_o = mapping[o]
        if o.parent and o.parent in mapping:
            new_o.parent = mapping[o.parent]
            new_o.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        else:
            new_o.parent = None
    return mapping[source_root]

# Nạp nguyên mẫu Thủy Binh Đại Việt 9.8/10
with bpy.data.libraries.load(SOLDIER_BLEND, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_ThuyBinh_DaiViet_Master']

soldier_collection = data_to.collections[0] if data_to.collections else bpy.data.collections.get('Collection_ThuyBinh_DaiViet_Master')
print("-> Nạp thành công Collection_ThuyBinh_DaiViet_Master:", soldier_collection.name if soldier_collection else "None")

# 7. DÀN DỰNG HẠM ĐỘI ĐẠI VIỆT (8 THUYỀN) - QUAY ĐẦU 180° & TỔNG PHẢN CÔNG
viet_fleet_data = [
    ("DV_01_SoaiTienPhong_Ta",    -8.0,  -42.0, 1.15),
    ("DV_02_SoaiTienPhong_Huu",   +8.0,  -42.0, 1.15),
    ("DV_Ta_01_TienDac",        -26.0,  -55.0, 1.05),
    ("DV_Ta_02_TrungQuan",      -46.0,  -68.0, 1.00),
    ("DV_Ta_03_KhoaHau",        -66.0,  -82.0, 0.95),
    ("DV_Huu_01_TienDac",       +26.0,  -55.0, 1.05),
    ("DV_Huu_02_TrungQuan",     +46.0,  -68.0, 1.00),
    ("DV_Huu_03_KhoaHau",       +66.0,  -82.0, 0.95)
]

for idx, (s_name, px, py, scl) in enumerate(viet_fleet_data):
    if idx == 0:
        s_root = master_ta_root
        if s_root.name not in col_ta.objects:
            col_ta.objects.link(s_root)
        for c in s_root.children_recursive:
            if c.name not in col_ta.objects:
                col_ta.objects.link(c)
        
        row_x_positions = [-1.8, 0.0, 1.8]
        for r_i, rx in enumerate(row_x_positions):
            inst_l = bpy.data.objects.new(f"ThuyBinh_9_8_Port_{r_i}", None)
            inst_l.instance_type = 'COLLECTION'
            inst_l.instance_collection = soldier_collection
            inst_l.location = (rx, 0.65, 0.45)
            inst_l.rotation_euler = (0, 0, math.radians(0))
            inst_l.scale = (0.78, 0.78, 0.78)
            inst_l.parent = s_root
            col_crew.objects.link(inst_l)
            
            inst_r = bpy.data.objects.new(f"ThuyBinh_9_8_Stbd_{r_i}", None)
            inst_r.instance_type = 'COLLECTION'
            inst_r.instance_collection = soldier_collection
            inst_r.location = (rx, -0.65, 0.45)
            inst_r.rotation_euler = (0, 0, math.radians(0))
            inst_r.scale = (0.78, 0.78, 0.78)
            inst_r.parent = s_root
            col_crew.objects.link(inst_r)

        mat_flag = bpy.data.materials.new("Mat_CoLenh_NguHanh_PBR")
        mat_flag.use_nodes = True
        bsdf_f = next((n for n in mat_flag.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf_f:
            bsdf_f.inputs['Base Color'].default_value = (0.85, 0.12, 0.08, 1.0)
            bsdf_f.inputs['Roughness'].default_value = 0.40
        
        bm_flag = bmesh.new()
        bmesh.ops.create_cube(bm_flag, size=1.0)
        mesh_f = bpy.data.meshes.new("Mesh_CoLenh_NguHanh")
        bm_flag.to_mesh(mesh_f)
        bm_flag.free()
        obj_f = bpy.data.objects.new("CoLenh_NguHanh_Master", mesh_f)
        obj_f.scale = (0.05, 0.9, 0.6)
        obj_f.location = (-3.2, 0.0, 2.2)
        obj_f.rotation_euler = (0, math.radians(-15), 0)
        obj_f.data.materials.append(mat_flag)
        obj_f.parent = s_root
        col_ta.objects.link(obj_f)

    else:
        s_root = clone_ship_hierarchy(master_ta_root, f"Ta_{idx}", col_ta)
        inst_crew = bpy.data.objects.new(f"Crew_Instance_Fleet_{idx}", None)
        inst_crew.instance_type = 'COLLECTION'
        inst_crew.instance_collection = soldier_collection
        inst_crew.location = (0, 0, 0.45)
        inst_crew.scale = (0.75, 0.75, 0.75)
        inst_crew.parent = s_root
        col_crew.objects.link(inst_crew)

    s_root.scale = (scl, scl, scl)
    s_root.rotation_euler = (0, 0, math.radians(90))

    root_ta = bpy.data.objects.new(f"Root_{s_name}", None)
    root_ta.empty_display_type = 'PLAIN_AXES'
    root_ta.empty_display_size = 0.3
    col_ta.objects.link(root_ta)
    s_root.parent = root_ta

    anim_ta = root_ta.animation_data_create()
    act_ta = bpy.data.actions.new(name=f"Act_PhanCong_{s_name}")
    anim_ta.action = act_ta

    turn_dir = 1.0 if px <= 0 else -1.0
    for f in range(1, 241):
        if f <= 50:
            prog_w = (f - 1) / 49.0
            z_water = 0.85 - prog_w * 0.40
        elif f <= 180:
            prog_w = (f - 50) / 130.0
            z_water = 0.45 - (prog_w ** 1.1) * 1.65
        else:
            prog_w = (f - 180) / 60.0
            z_water = -1.20 - prog_w * 0.25

        if f <= 50:
            prog1 = (f - 1) / 49.0
            cur_y = py - prog1 * 6.0
            cur_x = px
            yaw = 0.0
            roll = 0.0
        elif f <= 95:
            prog2 = (f - 50) / 45.0
            cur_y = py - 6.0 + math.sin(prog2 * math.pi) * 3.0
            cur_x = px + math.sin(prog2 * math.pi) * 4.0 * turn_dir
            yaw = turn_dir * prog2 * math.pi
            roll = turn_dir * math.sin(prog2 * math.pi) * math.radians(3.5)
        else:
            prog3 = (f - 95) / 145.0
            cur_y = (py - 6.0) + (prog3 ** 0.95) * 65.0
            cur_x = px + turn_dir * 1.5 + math.sin(prog3 * 4.0) * 1.2
            yaw = turn_dir * math.pi
            roll = 0.0

        cur_z = z_water + 0.12 + math.sin((f + idx * 3) * 0.16) * 0.025
        pitch = math.sin((f + idx * 4) * 0.20) * math.radians(0.45)

        root_ta.location = (cur_x, cur_y, cur_z)
        root_ta.rotation_euler = (pitch, roll, yaw)
        root_ta.keyframe_insert(data_path='location', frame=f)
        root_ta.keyframe_insert(data_path='rotation_euler', frame=f)

    for c in s_root.children_recursive:
        if 'Mai_Cheo' in c.name or 'Cheo' in c.name:
            anim_o = c.animation_data_create()
            act_o = bpy.data.actions.new(name=f"Act_Oar_Fast_{s_name}")
            anim_o.action = act_o
            for f in range(1, 241):
                freq = 0.35 if f <= 50 else (0.55 if f <= 95 else 0.80)
                rz = math.sin(f * freq + idx) * math.radians(16.0)
                ry = math.cos(f * freq + idx) * math.radians(6.5)
                c.rotation_euler = (0, ry, rz)
                c.keyframe_insert(data_path='rotation_euler', frame=f)
            break

print("-> Đội thuyền Đại Việt (8 thuyền - ĐẦY ĐỦ THỦY BINH 9.8/10, QUAY ĐẦU 180° PHẢN CÔNG) hoàn tất!")

# 8. DÀN DỰNG ĐẠI HẠM ĐỘI NAM HÁN (26 CHIẾN HẠM) - ĐÂM CỌC, THỦNG ĐÁY & NGHIÊNG ĐẮM
han_fleet_data = [
    ("NH_W1_01", -70.0, 16.0, 0.78, True,  -28.0, 110),
    ("NH_W1_02", -48.0, 12.0, 0.82, True,  -32.0, 115),
    ("NH_W1_03", -28.0,  8.0, 0.86, True,  -35.0, 118),
    ("NH_W1_04", -10.0,  6.0, 0.92, True,  -38.0, 120),
    ("NH_W1_05", +10.0,  6.0, 0.92, True,  +38.0, 120),
    ("NH_W1_06", +28.0,  8.0, 0.86, True,  +35.0, 118),
    ("NH_W1_07", +48.0, 12.0, 0.82, True,  +32.0, 115),
    ("NH_W1_08", +70.0, 16.0, 0.78, True,  +28.0, 110),

    ("NH_W2_01", -80.0, 52.0, 0.82, True,  -26.0, 135),
    ("NH_W2_02", -56.0, 44.0, 0.86, True,  -30.0, 138),
    ("NH_W2_03", -28.0, 38.0, 0.92, True,  -34.0, 142),
    ("NH_W2_SoaiHam_LauThuyen_HoangThao", 0.0, 34.0, 1.40, True, +32.0, 140),
    ("NH_W2_05", +28.0, 38.0, 0.92, True,  +34.0, 142),
    ("NH_W2_06", +56.0, 44.0, 0.86, True,  +30.0, 138),
    ("NH_W2_07", +80.0, 52.0, 0.82, True,  +26.0, 135),
    ("NH_W2_08", -42.0, 62.0, 0.82, False, -18.0, 150),
    ("NH_W2_09", +42.0, 62.0, 0.82, False, +18.0, 150),

    ("NH_W3_01", -68.0, 90.0, 0.82, False, -15.0, 160),
    ("NH_W3_02", -34.0, 85.0, 0.88, False, -20.0, 162),
    ("NH_W3_03",   0.0, 82.0, 0.92, False, +18.0, 165),
    ("NH_W3_04", +34.0, 85.0, 0.88, False, +20.0, 162),
    ("NH_W3_05", +68.0, 90.0, 0.82, False, +15.0, 160),
    ("NH_W3_06", -50.0, 108.0, 0.80, False, -12.0, 170),
    ("NH_W3_07", +18.0, 104.0, 0.80, False, +14.0, 170),
    ("NH_W3_08", -22.0, 124.0, 0.78, False, -10.0, 175),
    ("NH_W3_09", +46.0, 120.0, 0.78, False, +10.0, 175),
]

for idx, (h_name, px, py, scl, is_wrecked, wreck_roll, crash_frame) in enumerate(han_fleet_data):
    if idx == 11:
        h_root = master_dich_root
        if h_root.name not in col_dich.objects:
            col_dich.objects.link(h_root)
        for c in h_root.children_recursive:
            if c.name not in col_dich.objects:
                col_dich.objects.link(c)
    else:
        h_root = clone_ship_hierarchy(master_dich_root, f"Dich_{idx}", col_dich)

    h_root.scale = (scl, scl, scl)
    h_root.rotation_euler = (0, 0, math.radians(-90))

    root_h = bpy.data.objects.new(f"Root_{h_name}", None)
    root_h.empty_display_type = 'PLAIN_AXES'
    root_h.empty_display_size = 0.3
    col_dich.objects.link(root_h)
    h_root.parent = root_h

    anim_h = root_h.animation_data_create()
    act_h = bpy.data.actions.new(name=f"Act_Wreck_{h_name}")
    anim_h.action = act_h

    for f in range(1, 241):
        if f <= 50:
            prog_w = (f - 1) / 49.0
            z_water = 0.85 - prog_w * 0.40
        elif f <= 180:
            prog_w = (f - 50) / 130.0
            z_water = 0.45 - (prog_w ** 1.1) * 1.65
        else:
            prog_w = (f - 180) / 60.0
            z_water = -1.20 - prog_w * 0.25

        if f < crash_frame:
            if f <= 65:
                p1 = (f - 1) / 64.0
                cur_y = py - p1 * 12.0
            else:
                p2 = (f - 65) / float(crash_frame - 65)
                cur_y = (py - 12.0) - (p2 ** 1.2) * 18.0
            
            cur_x = px
            cur_z = z_water - 0.45 + math.sin(f * 0.12 + idx) * 0.02
            pitch = math.sin(f * 0.14 + idx) * math.radians(0.35)
            roll = 0.0
            yaw = 0.0
        else:
            p_crash = (f - crash_frame) / float(240 - crash_frame)
            if is_wrecked:
                cur_y = (py - 12.0) - 18.0 - math.sin(p_crash * math.pi * 0.5) * 1.5
                cur_x = px + math.sin(p_crash * math.pi * 0.5) * 1.0 * (1.0 if wreck_roll > 0 else -1.0)
                roll = math.radians(wreck_roll) * min(1.0, p_crash * 2.5)
                pitch = math.radians(-5.5) * min(1.0, p_crash * 2.0)
                yaw = math.radians(8.0) * min(1.0, p_crash * 1.5)
                cur_z = (z_water - 0.45) - p_crash * 0.55
            else:
                cur_y = (py - 12.0) - 18.0 - p_crash * 4.0
                cur_x = px + p_crash * 2.5
                roll = math.radians(wreck_roll) * min(1.0, p_crash * 1.8)
                pitch = math.radians(2.0)
                yaw = math.radians(14.0) * min(1.0, p_crash)
                cur_z = z_water - 0.40 - p_crash * 0.35

        root_h.location = (cur_x, cur_y, cur_z)
        root_h.rotation_euler = (pitch, roll, yaw)
        root_h.keyframe_insert(data_path='location', frame=f)
        root_h.keyframe_insert(data_path='rotation_euler', frame=f)

print(f"-> Đại hạm đội Nam Hán ({len(han_fleet_data)} chiến hạm - ĐÂM CỌC THỦNG LƯỜN & NGHIÊNG ĐẮM) hoàn tất!")

# 9. THIẾT LẬP 03 CAMERA ĐIỆN ẢNH CHUẨN MỰC
cam1_data = bpy.data.cameras.new("Cam1_ToanCanh_BaoQuat")
cam1_data.lens = 28.0
cam1_data.clip_end = 2000.0
cam1_obj = bpy.data.objects.new("Camera_ToanCanh_ChienTruong", cam1_data)
cam1_obj.location = (0.0, -135.0, 68.0)
cam1_obj.rotation_euler = (math.radians(65), 0, 0)
col_cam.objects.link(cam1_obj)

cam2_data = bpy.data.cameras.new("Cam2_CanCanh_DamTau_NamHan")
cam2_data.lens = 50.0
cam2_data.clip_end = 1000.0
cam2_obj = bpy.data.objects.new("Camera_CanCanh_DamTau", cam2_data)
cam2_obj.location = (-16.0, -15.0, 10.5)
cam2_obj.rotation_euler = (math.radians(72), 0, math.radians(-35))
col_cam.objects.link(cam2_obj)

cam3_data = bpy.data.cameras.new("Cam3_CanCanh_SoaiThuyen_DV01")
cam3_data.lens = 45.0
cam3_data.clip_end = 1000.0
cam3_obj = bpy.data.objects.new("Camera_CanCanh_SoaiThuyen_DV01", cam3_data)
cam3_obj.location = (-15.0, -48.0, 4.5)
cam3_obj.rotation_euler = (math.radians(78), 0, math.radians(-65))
col_cam.objects.link(cam3_obj)

scene.camera = cam1_obj

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
            r3d.view_location = (0.0, 0.0, 0.0)
            r3d.view_rotation = Euler((math.radians(65), 0.0, 0.0), 'XYZ').to_quaternion()

out_blend = os.path.join(WS_DIR, "scenes", "dai_chien_bach_dang_step3_counter_offensive.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
print(f"=== [VIETNAM-SIM MASTER] ĐÃ LƯU THÀNH CÔNG PHÂN CẢNH 3: {out_blend} ===")
