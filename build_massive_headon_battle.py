import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM] TÁI THIẾT LẬP: ĐẠI CHIẾN BẠCH ĐẰNG ĐỐI ĐẦU HÙNG HẬU THEO THAM CHIẾU ===")

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

col_env = bpy.data.collections.new('01_DiaHinh_BoiCanh')
col_coc = bpy.data.collections.new('02_TranDia_BaiCoc')
col_ta = bpy.data.collections.new('03_HamDoi_DaiViet_TienPhong')
col_dich = bpy.data.collections.new('04_HamDoi_NamHan_QuanDoan')
col_light = bpy.data.collections.new('05_ChieuSang_KhiQuyen')

for c in [col_env, col_coc, col_ta, col_dich, col_light]:
    scene.collection.children.link(c)

# 2. BẦU TRỜI MÙA ĐÔNG 938 & ÁNH SÁNG
world = bpy.data.worlds.get('World_BachDang_Headon') or bpy.data.worlds.new('World_BachDang_Headon')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
# Sương mù đông lam nhạt
bg_w.inputs['Color'].default_value = (0.35, 0.42, 0.50, 1.0)
bg_w.inputs['Strength'].default_value = 1.25
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

sun_data = bpy.data.lights.new(name="Sun_Winter", type='SUN')
sun_data.energy = 5.2
sun_data.color = (1.0, 0.94, 0.85)
sun_obj = bpy.data.objects.new(name="Sun_Winter", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(65), math.radians(10), math.radians(35))
col_light.objects.link(sun_obj)

mist_light = bpy.data.lights.new(name="Light_SuongMu", type='SUN')
mist_light.energy = 2.0
mist_light.color = (0.7, 0.8, 0.92)
mist_obj = bpy.data.objects.new(name="Light_SuongMu", object_data=mist_light)
mist_obj.rotation_euler = (math.radians(88), 0, math.radians(125))
col_light.objects.link(mist_obj)

# 3. BỜ TÂY: DÃY NÚI ĐÁ VÔI KARST TRÀNG KÊNH
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_TrangKenh',
    mesh_size_x=70.0,
    mesh_size_y=280.0,
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
mount_main.location = (-65.0, 10.0, 0.0)
mount_main.scale = (1.0, 1.0, 32.0)

mat_karst = bpy.data.materials.new('Mat_DaKarst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.13, 0.15, 0.14, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.88
mount_main.data.materials.append(mat_karst)
if mount_main.name not in col_env.objects: col_env.objects.link(mount_main)
if mount_main.name in scene.collection.objects: scene.collection.objects.unlink(mount_main)

# 4. BỜ ĐÔNG: BÃI BÙN PHÙ SA & RỪNG SÚ VẸT
bm_mud = bmesh.new()
mat_m_bank = Matrix.Translation(Vector((55.0, 10.0, 0.05))) @ Matrix.Diagonal(Vector((45.0, 280.0, 0.5, 1.0)))
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

# 5. MẶT NƯỚC SÔNG BẠCH ĐẰNG (TRIỀU CƯỜNG DÂNG CAO +0.85m)
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=80, y_segments=120, size=300.0)
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
act_w = bpy.data.actions.new(name='Action_ThuyTrieu')
anim_w.action = act_w
for f in range(1, 81):
    zt = 0.85 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)

# 6. BÃI CỌC BẠCH ĐẰNG NGẬP SÂU TRẢI RỘNG (45 CỌC NGẦM Ở Y = -2 ĐẾN +4)
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

# Sinh thêm cọc trải rộng toàn bộ lòng sông (từ X = -30 đến +30)
random.seed(938)
if hero_stakes:
    master_coc = hero_stakes[0]
    for idx in range(30):
        cx = random.uniform(-28.0, 28.0)
        cy = random.uniform(-3.0, 5.0)
        cz = random.uniform(-0.6, -0.4) # Đầu cọc ngập sâu dưới nước 0.85m ít nhất 0.8m
        slant_x = random.uniform(-5.0, 5.0)
        slant_y = random.uniform(-40.0, -55.0) # Nghiêng về phía Nam chống lại quân địch
        
        c_inst = master_coc.copy()
        c_inst.name = f"Coc_TranDia_Rong_{idx+1}"
        c_inst.location = (cx, cy, cz)
        c_inst.rotation_euler = (math.radians(slant_y), math.radians(slant_x), 0)
        col_coc.objects.link(c_inst)

print("-> Bãi cọc trải rộng ngầm dưới nước hoàn tất!")

# 7. NẠP MASTER SHIPS VÀ TẠO HẠM ĐỘI ĐỐI ĐẦU HÙNG HẬU
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan']

ta_objs = []
dich_objs = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'NamHan' in ob.name or 'LauThuyen' in ob.name:
                dich_objs.append(ob)
            elif 'Coc' not in ob.name:
                ta_objs.append(ob)

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
master_dich_root = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')

def clone_ship(source_root, prefix_name, target_col):
    objs = [source_root] + list(source_root.children_recursive)
    mapping = {}
    for o in objs:
        new_o = o.copy()
        new_o.name = f"{prefix_name}_{o.name}"
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

# =============================================================
# A. HẠM ĐỘI ĐẠI VIỆT (TIỀN CẢNH - PHÍA DƯỚI)
# Mũi thuyền hướng lên phía Bắc (+Y) - ĐỐI ĐẦU VỚI QUÂN NAM HÁN
# =============================================================
master_ta_root.location = (0, 0, 0)
master_ta_root.rotation_euler = (0, 0, math.radians(90)) # Mũi hướng +Y
for ob in ta_objs:
    if ob.name not in col_ta.objects: col_ta.objects.link(ob)

# Bố trí 8 chiến thuyền Đại Việt theo đội hình mũi tên / cánh cung tiến công
viet_positions = [
    # (Tên, X, Y, Scale)
    ("DaiViet_01_SoaiTienPhong",  0.0,  -8.0, 1.05), # Mũi tiên phong dẫn đầu
    ("DaiViet_02_TienPhongTa",   -5.5, -14.0, 0.95),
    ("DaiViet_03_TienPhongHuu",  +5.5, -14.0, 0.95),
    ("DaiViet_04_TrungQuanTa",  -11.0, -22.0, 0.90),
    ("DaiViet_05_TrungQuanGiua",   0.0, -24.0, 1.00),
    ("DaiViet_06_TrungQuanHuu", +11.0, -22.0, 0.90),
    ("DaiViet_07_HauVeTa",      -17.0, -32.0, 0.85),
    ("DaiViet_08_HauVeHuu",     +17.0, -32.0, 0.85)
]

for idx, (s_name, px, py, scl) in enumerate(viet_positions):
    if idx == 0:
        ship_root = master_ta_root
    else:
        ship_root = clone_ship(master_ta_root, f"DV_{idx}", col_ta)
    
    root_e = bpy.data.objects.new(f"Root_{s_name}", None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_ta.objects.link(root_e)
    
    ship_root.scale = (scl, scl, scl)
    ship_root.parent = root_e
    
    # Keyframe hoạt cảnh lướt sóng thẳng hướng Bắc (+Y)
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Act_{s_name}")
    anim.action = act
    
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        # Tiến nhẹ lướt sóng nhử địch
        cur_y = py + prog * 4.0
        cur_x = px + math.sin((f + idx * 5) * 0.1) * 0.15
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.12) * 0.02
        
        pitch = math.sin((f + idx * 4) * 0.15) * math.radians(0.5)
        roll = 0.0   # TUYỆT ĐỐI KHÔNG NGHIÊNG
        yaw = 0.0    # TIẾN THẲNG HƯỚNG BẮC (+Y)
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

print("-> Hạm đội Đại Việt (8 chiến thuyền) dàn trận hướng Bắc hoàn tất!")

# =============================================================
# B. HẠM ĐỘI NAM HÁN (HẬU CẢNH - PHÍA TRÊN)
# Mũi thuyền hướng xuống phía Nam (-Y) - LAO THẲNG VÀO QUÂN TA
# =============================================================
master_dich_root.location = (0, 0, 0)
master_dich_root.rotation_euler = (0, 0, math.radians(-90)) # Mũi hướng -Y (NGƯỢC HƯỚNG TÀU TA!)
for ob in dich_objs:
    if ob.name not in col_dich.objects: col_dich.objects.link(ob)

# Bố trí 25 chiến hạm Nam Hán thành 3 đợt hùng hậu (Armada Waves):
han_positions = [
    # ĐỢT 1: TIÊN PHONG ÁP SÁT BÃI CỌC (Y = +8 đến +14) - 7 Tàu dàn hàng ngang
    ("NamHan_W1_01", -24.0, 13.0, 0.70),
    ("NamHan_W1_02", -16.0, 10.0, 0.75),
    ("NamHan_W1_03",  -8.0,  8.0, 0.80),
    ("NamHan_W1_04",   0.0,  7.0, 0.85), # Mũi nhọn đợt 1
    ("NamHan_W1_05",  +8.0,  8.0, 0.80),
    ("NamHan_W1_06", +16.0, 10.0, 0.75),
    ("NamHan_W1_07", +24.0, 13.0, 0.70),

    # ĐỢT 2: TRUNG QUÂN HÙNG MẠNH (Y = +22 đến +36) - 9 Tàu
    ("NamHan_W2_SoaiHam_HoangThao", 0.0, 24.0, 1.25), # ĐẠI SOÁI HẠM 3 TẦNG CỦA HOẰNG THÁO
    ("NamHan_W2_02",  -9.0, 26.0, 0.85),
    ("NamHan_W2_03",  +9.0, 26.0, 0.85),
    ("NamHan_W2_04", -18.0, 29.0, 0.80),
    ("NamHan_W2_05", +18.0, 29.0, 0.80),
    ("NamHan_W2_06", -26.0, 32.0, 0.75),
    ("NamHan_W2_07", +26.0, 32.0, 0.75),
    ("NamHan_W2_08", -13.0, 36.0, 0.75),
    ("NamHan_W2_09", +13.0, 36.0, 0.75),

    # ĐỢT 3: HẬU QUÂN & TIẾP VIỆN TRẢI DÀI VỀ PHÍA CỬA BIỂN (Y = +45 đến +75) - 9 Tàu
    ("NamHan_W3_01",   0.0, 46.0, 0.85),
    ("NamHan_W3_02", -11.0, 48.0, 0.80),
    ("NamHan_W3_03", +11.0, 48.0, 0.80),
    ("NamHan_W3_04", -22.0, 52.0, 0.75),
    ("NamHan_W3_05", +22.0, 52.0, 0.75),
    ("NamHan_W3_06",  -7.0, 60.0, 0.75),
    ("NamHan_W3_07",  +7.0, 60.0, 0.75),
    ("NamHan_W3_08", -18.0, 68.0, 0.70),
    ("NamHan_W3_09", +18.0, 68.0, 0.70),
]

for idx, (h_name, px, py, scl) in enumerate(han_positions):
    if idx == 7: # Vị trí Soái hạm Hoằng Tháo
        ship_root = master_dich_root
    else:
        ship_root = clone_ship(master_dich_root, f"NH_{idx}", col_dich)
        
    root_e = bpy.data.objects.new(f"Root_{h_name}", None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_dich.objects.link(root_e)
    
    ship_root.scale = (scl, scl, scl)
    ship_root.parent = root_e
    
    # Keyframe hoạt cảnh lao xuống phía Nam (-Y) hung hãn đuổi theo quân ta
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Act_{h_name}")
    anim.action = act
    
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        # Tiến xuống phía Nam (-Y)
        cur_y = py - prog * 6.0
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.09) * 0.015
        
        pitch = math.sin((f + idx * 2) * 0.12) * math.radians(0.35)
        roll = 0.0   # TUYỆT ĐỐI KHÔNG NGHIÊNG, ĐẦM CHẮC VỮNG CHÃI
        yaw = 0.0    # LAO THẲNG HƯỚNG NAM (-Y)
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

print(f"-> Hạm đội Nam Hán ({len(han_positions)} chiến hạm) dàn trận hướng Nam hoàn tất!")

# 8. CAMERA ĐIỆN ẢNH KHỚP CHÍNH XÁC GÓC NHÌN ẢNH THAM CHIẾU
cam_data = bpy.data.cameras.new("Cam_BachDang_Headon")
cam_data.lens = 32.0 # Ống kính góc rộng bao quát
cam_data.clip_end = 1000.0
cam_obj = bpy.data.objects.new("Camera_ChienTruong_DoiDau", cam_data)

# Đặt camera ở phía Nam nhìn thẳng lên phía Bắc:
# Tiền cảnh: Đội thuyền Đại Việt (hướng lên)
# Trung cảnh: Bãi cọc ngầm
# Hậu cảnh: Toàn bộ đại hạm đội Nam Hán (hướng xuống)
cam_obj.location = (0.0, -56.0, 28.0)
cam_obj.rotation_euler = (math.radians(65), 0, 0)
col_light.objects.link(cam_obj)
scene.camera = cam_obj

# Cập nhật Viewport 3D góc nhìn chuẩn
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
            r3d.view_distance = 75.0
            r3d.view_location = (0.0, 10.0, 5.0)
            r3d.view_rotation = Euler((math.radians(65), 0.0, 0.0), 'XYZ').to_quaternion()

scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except:
    pass

print("=== [VIETNAM-SIM] BẢN TÁI THIẾT LẬP ĐỐI ĐẦU HÙNG HẬU HOÀN TẤT 100%! ===")
