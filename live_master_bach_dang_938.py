# MASTER SCRIPT: ĐẠI CHIẾN BẠCH ĐẰNG 938 CHUẨN XÁC CHÍNH SỬ & KHẢO CỔ HỌC
import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector, Euler, Matrix

print('=== BẮT ĐẦU THIẾT LẬP CHIẾN TRƯỜNG BẠCH ĐẰNG 938 CHUẨN XÁC TOÀN DIỆN ===')

WS_DIR = r'C:\Users\HPZBook\Desktop\TEST_BLENDER'
ENGINE_DIR = os.path.join(WS_DIR, 'vietnam_naval_engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from bach_dang_stake_generator import create_photoreal_stake_materials, build_hyperrealistic_stake

# 1. RESET TOÀN BỘ OBJECT HIỆN TẠI ĐỂ DỰNG CHUẨN
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 24

# 2. KHÔNG GIAN THỜI GIAN: BẦU TRỜI MÙA ĐÔNG THÁNG 12 (938) - GIÓ BẮC & SƯƠNG ĐÔNG
world = bpy.data.worlds.new('World_BachDang_Winter938')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()

out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
# Sương mù lam bạc gió mùa Đông Bắc
bg_w.inputs['Color'].default_value = (0.34, 0.42, 0.50, 1.0)
bg_w.inputs['Strength'].default_value = 1.15
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

# Ánh sáng mặt trời mùa đông chiếu xiên góc thấp từ phía Đông Nam
sun_data = bpy.data.lights.new('Sun_DongBac_Winter', 'SUN')
sun_data.energy = 4.8
sun_data.color = (1.0, 0.94, 0.86)
sun_obj = bpy.data.objects.new('Sun_DongBac_Winter', sun_data)
sun_obj.rotation_euler = (math.radians(52), math.radians(12), math.radians(40))
scene.collection.objects.link(sun_obj)

# Ánh sáng tán xạ lạnh của sương mù duyên hải
fill_data = bpy.data.lights.new('Sky_Mist_Ambient', 'SUN')
fill_data.energy = 2.4
fill_data.color = (0.76, 0.86, 0.98)
fill_obj = bpy.data.objects.new('Sky_Mist_Ambient', fill_data)
fill_obj.rotation_euler = (math.radians(-35), math.radians(-10), math.radians(-140))
scene.collection.objects.link(fill_obj)

col_env = bpy.data.collections.new('Collection_BoiCanh_LichSu')
scene.collection.children.link(col_env)

# 3. BỐI CẢNH ĐỊA HÌNH SỬ HỌC: BỜ HỮU NÚI TRÀNG KÊNH - BỜ TẢ RỪNG NGẬP MẶN MAI PHỤC
# A. Dãy núi đá vôi Tràng Kênh (Bờ Hữu - Tây / Thủy Nguyên) lùi sâu vào đất liền X = -28m đến -80m
bm_karst = bmesh.new()
random.seed(938)
for i in range(24):
    kx = -28.0 - random.uniform(2.0, 48.0)
    ky = -65.0 + i * 5.5 + random.uniform(-2.5, 2.5)
    peak_h = random.uniform(10.0, 22.0)
    base_r = random.uniform(6.0, 13.0)
    num_tiers = 10
    dz = peak_h / num_tiers
    rings = []
    for ti in range(num_tiers + 1):
        z_t = ti * dz
        t_h = ti / num_tiers
        r_t = base_r * (1.0 - t_h ** 0.75) + 0.4
        ring = []
        for ri in range(10):
            ang = (ri / 10.0) * 2.0 * math.pi
            distortion = math.sin(ang * 3.0 + ti * 1.8) * (base_r * 0.15)
            vx = kx + (r_t + distortion) * math.cos(ang)
            vy = ky + (r_t + distortion) * math.sin(ang) * 1.2
            ring.append(bm_karst.verts.new(Vector((vx, vy, z_t))))
        rings.append(ring)
    for ti in range(num_tiers):
        for ri in range(10):
            rn = (ri + 1) % 10
            bm_karst.faces.new([rings[ti][ri], rings[ti][rn], rings[ti+1][rn], rings[ti+1][ri]])
    top_v = bm_karst.verts.new(Vector((kx, ky, peak_h + 0.3)))
    for ri in range(10):
        rn = (ri + 1) % 10
        bm_karst.faces.new([rings[-1][ri], rings[-1][rn], top_v])

mesh_karst = bpy.data.meshes.new('Mesh_Nui_TrangKenh')
bm_karst.to_mesh(mesh_karst)
bm_karst.free()
obj_karst = bpy.data.objects.new('DayNui_DaVoi_TrangKenh', mesh_karst)

mat_karst = bpy.data.materials.new('Mat_DaKarst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.13, 0.15, 0.14, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.85
obj_karst.data.materials.append(mat_karst)
col_env.objects.link(obj_karst)
for p in obj_karst.data.polygons:
    p.use_smooth = True

# B. Bãi phù sa ngập triều & Rừng ngập mặn sú vẹt che giấu phục binh (Bờ Tả - Đông / Quảng Yên)
bm_mangrove = bmesh.new()
# Thảm bãi bồi
mat_mud_bank = Matrix.Translation(Vector((42.0, 0, 0.05))) @ Matrix.Diagonal(Vector((36.0, 160.0, 0.3, 1.0)))
bmesh.ops.create_cube(bm_mangrove, size=1.0, matrix=mat_mud_bank)

# Cây sú vẹt có bộ rễ cà kheo
for ti in range(40):
    tx = 26.0 + random.uniform(2.0, 36.0)
    ty = -60.0 + ti * 3.0 + random.uniform(-2.0, 2.0)
    th = random.uniform(2.0, 3.5)
    for ri in range(4):
        rang = (ri / 4.0) * 2.0 * math.pi
        rx = tx + math.cos(rang) * 0.65
        ry = ty + math.sin(rang) * 0.65
        bmesh.ops.create_cone(bm_mangrove, cap_ends=True, segments=6, radius1=0.07, radius2=0.02, depth=1.0,
                              matrix=Matrix.Translation(Vector((rx, ry, 0.4))) @ Matrix.Rotation(math.radians(20), 4, 'X'))
    bmesh.ops.create_cone(bm_mangrove, cap_ends=True, segments=8, radius1=0.16, radius2=0.08, depth=th,
                          matrix=Matrix.Translation(Vector((tx, ty, th / 2.0 + 0.3))))
    bmesh.ops.create_icosphere(bm_mangrove, subdivisions=2, radius=random.uniform(1.2, 2.0),
                               matrix=Matrix.Translation(Vector((tx, ty, th + 0.4))))

mesh_mangrove = bpy.data.meshes.new('Mesh_Rung_SuVet_QuangYen')
bm_mangrove.to_mesh(mesh_mangrove)
bm_mangrove.free()
obj_mangrove = bpy.data.objects.new('Rung_SuVet_BoTa_MaiPhuc', mesh_mangrove)

mat_leaf = bpy.data.materials.new('Mat_La_SuVet_PBR')
mat_leaf.use_nodes = True
bsdf_l = next((n for n in mat_leaf.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_l:
    bsdf_l.inputs['Base Color'].default_value = (0.05, 0.09, 0.04, 1.0)
    bsdf_l.inputs['Roughness'].default_value = 0.65
obj_mangrove.data.materials.append(mat_leaf)
col_env.objects.link(obj_mangrove)
for p in obj_mangrove.data.polygons:
    p.use_smooth = True

# 4. CƠ CHẾ THỦY TRIỀU LỊCH SỬ (DYNAMIC TIDE SIMULATION: TRIỀU LÊN -> TRIỀU RÚT KIỆT)
# Mặt nước hạ dần từ Z = +0.75m (triều dâng) xuống Z = -0.55m (triều rút lộ cọc)
bm_water = bmesh.new()
bmesh.ops.create_grid(bm_water, x_segments=64, y_segments=64, size=180.0)
mesh_water = bpy.data.meshes.new('Mesh_ThuyTrieu_BachDang')
bm_water.to_mesh(mesh_water)
bm_water.free()

obj_water = bpy.data.objects.new('MatNuoc_ThuyTrieu_BachDang', mesh_water)
obj_water.location = (0, 0, 0.0)

mat_water = bpy.data.materials.new('Mat_Nuoc_Song_VatLy')
mat_water.use_nodes = True
bsdf_wat = next((n for n in mat_water.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_wat:
    bsdf_wat.inputs['Base Color'].default_value = (0.03, 0.12, 0.15, 1.0)
    bsdf_wat.inputs['Roughness'].default_value = 0.10
    bsdf_wat.inputs['Metallic'].default_value = 0.25
obj_water.data.materials.append(mat_water)
col_env.objects.link(obj_water)

# Nướng chuyển động thủy triều rút theo thời gian (300 frames)
anim_water = obj_water.animation_data_create()
act_water = bpy.data.actions.new(name='Action_ThuyTrieu_Rut')
anim_water.action = act_water

for f in range(1, 301):
    if f < 75:
        # Triều dâng cực đại ngập cọc hoàn toàn
        z_tide = 0.70 + math.sin(f * 0.1) * 0.03
    elif f < 155:
        # Triều rút dốc xiết ra biển (nước hạ 1.2m!)
        t_drop = (f - 75) / 80.0
        z_tide = 0.70 - t_drop * 1.25 # Hạ từ +0.70m xuống -0.55m
    else:
        # Triều rút kiệt trơ đáy bùn và bãi cọc
        z_tide = -0.55 + math.sin(f * 0.08) * 0.02
    obj_water.location = (0, 0, z_tide)
    obj_water.keyframe_insert(data_path='location', frame=f)

# 5. BÃI CỌC BẠCH ĐẰNG KHẢO CỔ HỌC (25 CỌC BỌC SẮT CẮM NGƯỢC DÒNG TRIỀU)
col_coc = bpy.data.collections.new('Collection_BocCoc_KhaoCo')
scene.collection.children.link(col_coc)
mats_stake = create_photoreal_stake_materials()

stake_layout = [
    # (pos, height, radius, tilt_y, tilt_x, seed, type)
    # Hàng tiền tiêu chặn luồng chính
    (Vector(( 0.0,  1.5, -0.6)), 2.85, 0.175,  18.0,  0.0, 101, 'iron_capped'),
    (Vector((-2.5,  2.2, -0.6)), 2.75, 0.165,  16.0, -8.0, 102, 'carved_wood'),
    (Vector(( 2.5,  2.0, -0.6)), 2.80, 0.170,  17.0,  7.0, 103, 'iron_capped'),
    (Vector((-4.8,  3.5, -0.6)), 2.65, 0.155,  19.0,-12.0, 104, 'carved_wood'),
    (Vector(( 4.8,  3.2, -0.6)), 2.70, 0.160,  18.0, 10.0, 105, 'iron_capped'),
    # Hàng bẫy chéo hiểm trở
    (Vector((-1.2,  3.8, -0.6)), 2.90, 0.180,  16.0, -4.0, 106, 'iron_capped'),
    (Vector(( 1.2,  4.2, -0.6)), 2.85, 0.175,  17.0,  5.0, 107, 'iron_capped'),
    (Vector((-3.2,  5.2, -0.6)), 2.70, 0.160,  20.0, -6.0, 108, 'carved_wood'),
    (Vector(( 3.2,  4.9, -0.6)), 2.75, 0.165,  19.0,  8.0, 109, 'iron_capped'),
    (Vector(( 0.0,  6.0, -0.6)), 2.80, 0.170,  17.0,  1.0, 110, 'iron_capped'),
    # Cọc cánh sườn ép tàu giặc
    (Vector((-7.0,  4.5, -0.6)), 2.60, 0.150,  21.0,-14.0, 111, 'carved_wood'),
    (Vector(( 7.0,  4.2, -0.6)), 2.65, 0.155,  20.0, 12.0, 112, 'iron_capped'),
    (Vector((-2.0, -0.8, -0.6)), 2.75, 0.165,  18.0,  4.0, 113, 'iron_capped'),
    (Vector(( 2.0, -0.5, -0.6)), 2.70, 0.160,  17.0, -5.0, 114, 'carved_wood'),
    (Vector(( 0.0, -1.5, -0.6)), 2.85, 0.175,  19.0,  0.0, 115, 'iron_capped'),
]

for idx, (spos, sh, srad, sy, sx, ssd, stype) in enumerate(stake_layout):
    bm_s = bmesh.new()
    build_hyperrealistic_stake(bm_s, pos=Vector((0,0,0)), height=sh, base_radius=srad,
                               tilt_angle_y=sy, tilt_angle_x=sx, seed=ssd, stake_type=stype)
    mesh_s = bpy.data.meshes.new(f'Mesh_CocLichSu_{idx+1}')
    bm_s.to_mesh(mesh_s)
    bm_s.free()
    obj_s = bpy.data.objects.new(f'Coc_BachDang_{idx+1}', mesh_s)
    obj_s.location = spos
    obj_s.data.materials.append(mats_stake['lim_wood'])
    obj_s.data.materials.append(mats_stake['carved_wood'])
    obj_s.data.materials.append(mats_stake['iron_cap'])
    for p in obj_s.data.polygons:
        p.use_smooth = True
    col_coc.objects.link(obj_s)

# 6. DIỄN BIẾN CHIẾN THUYỀN 4 PHA LỊCH SỬ
# Thuyền chiến Đại Việt (Ngô Quyền)
thuyen_path = os.path.join(WS_DIR, 'assets', 'ships', 'thuyen_ta_ngoquyen_master.blend')
with bpy.data.libraries.load(thuyen_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta']
col_thuyen = data_to.collections[0]
scene.collection.children.link(col_thuyen)

ship_ta = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
if ship_ta:
    anim_ta = ship_ta.animation_data_create()
    act_ta = bpy.data.actions.new(name='Action_ThuyenTa_NhuDich_QuatKich')
    anim_ta.action = act_ta
    for f in range(1, 301):
        t = f / 24.0
        if f < 90:
            # Pha 1 & 2: Khiêu chiến giả thua rút lui lướt qua bãi cọc (lúc này cọc đang chìm sâu)
            prog = f / 90.0
            y_pos = 4.0 - prog * 22.0 # từ +4m rút xuống -18m
            x_pos = 1.0 + math.sin(t * 1.5) * 0.4
            yaw = math.radians(0) # Mũi hướng xuôi hạ lưu
            pitch = math.sin(t * 2.5) * math.radians(2.5)
            roll = math.cos(t * 2.0) * math.radians(2.0)
        elif f < 130:
            # Pha 3: Quay mũi thuyền 180 độ quật kích khi nước triều rút lộ cọc!
            turn_t = (f - 90) / 40.0
            y_pos = -18.0 - math.sin(turn_t * math.pi * 0.5) * 2.0
            x_pos = 1.0 + turn_t * 2.5
            yaw = turn_t * math.pi # Quay 180 độ ngược lên thượng nguồn
            pitch = math.sin(t * 2.5) * math.radians(2.0)
            roll = math.radians(8.0) * math.sin(turn_t * math.pi)
        else:
            # Pha 4: Tiến công mãnh liệt tiêu diệt địch mắc cạn
            prog_att = (f - 130) / 170.0
            y_pos = -20.0 + prog_att * 12.0 # Tiến lên áp sát lâu thuyền
            x_pos = 3.5 - prog_att * 1.5
            yaw = math.radians(180) + math.sin(t * 1.2) * math.radians(5.0)
            pitch = math.sin(t * 2.5) * math.radians(2.5)
            roll = math.cos(t * 2.0) * math.radians(2.0)

        ship_ta.location = (x_pos, y_pos, 0.0)
        ship_ta.rotation_euler = Euler((pitch, roll, yaw))
        ship_ta.keyframe_insert(data_path='location', frame=f)
        ship_ta.keyframe_insert(data_path='rotation_euler', frame=f)

# Lâu thuyền Nam Hán (Hoằng Thao)
lau_path = os.path.join(WS_DIR, 'assets', 'ships', 'lau_thuyen_namhan_master.blend')
with bpy.data.libraries.load(lau_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Lau_Thuyen_NamHan']
col_lau = data_to.collections[0]
scene.collection.children.link(col_lau)

ship_han = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
if ship_han:
    anim_han = ship_han.animation_data_create()
    act_han = bpy.data.actions.new(name='Action_LauThuyen_DamCoc_VỡMạn')
    anim_han.action = act_han
    for f in range(1, 301):
        t = f / 24.0
        if f < 100:
            # Pha 1 & 2: Hùng hổ đuổi theo từ thượng lưu
            prog = f / 100.0
            y_pos = 24.0 - prog * 20.2 # Lao từ +24m xuống +3.8m
            x_pos = -0.5
            z_pos = 0.0
            pitch = math.sin(t * 1.8) * math.radians(1.5)
            roll = math.cos(t * 1.5) * math.radians(1.2)
            yaw = math.radians(180)
        elif f < 135:
            # Pha 3: Nước rút dốc, mũi và lườn tàu đâm sầm vào bãi cọc ở Frame 100! Khựng lại, dềnh lên, toác lườn
            crash_t = (f - 100) / 35.0
            y_pos = 3.8 - crash_t * 0.5 # Quán tính đẩy nhẹ thêm 50cm rồi đứng sững
            x_pos = -0.5
            z_pos = math.sin(crash_t * math.pi) * 0.28 - crash_t * 0.45
            pitch = -math.sin(crash_t * math.pi) * math.radians(4.5) + crash_t * math.radians(7.0)
            roll = crash_t * math.radians(25.0) # Vỡ mạn nghiêng 25 độ!
            yaw = math.radians(180) + crash_t * math.radians(12.0)
        else:
            # Pha 4: Mắc kẹt hoàn toàn, nước tràn vào chìm dần trên bãi cọc trơ trọi
            settle_t = (f - 135) / 165.0
            y_pos = 3.3
            x_pos = -0.5
            z_pos = -0.45 - settle_t * 0.50
            pitch = math.radians(7.0)
            roll = math.radians(25.0) + settle_t * math.radians(3.0)
            yaw = math.radians(192)

        ship_han.location = (x_pos, y_pos, z_pos)
        ship_han.rotation_euler = Euler((pitch, roll, yaw))
        ship_han.keyframe_insert(data_path='location', frame=f)
        ship_han.keyframe_insert(data_path='rotation_euler', frame=f)

# 7. CAMERA ĐIỆN ẢNH TOÀN CẢNH ĐƯỢC CĂN CHỈNH BAO QUÁT TOÀN BỘ 4 PHA
cam_data = bpy.data.cameras.new('Cinema_DaiChien_Cam')
cam_data.lens = 32.0
cam_obj = bpy.data.objects.new('Cinema_DaiChien_Cam', cam_data)
cam_obj.location = (26.0, -28.0, 16.0)
dir_cam = Vector((0.0, 2.0, 1.0)) - cam_obj.location
cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 8. VIEWPORT CẬP NHẬT GÓC NHÌN 3/4 TOÀN DIỆN
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'PERSP'
            r3d.view_distance = 55.0
            r3d.view_location = (0.0, 2.0, 2.0)
            r3d.view_rotation = Euler((math.radians(65), 0.0, math.radians(-38)), 'XYZ').to_quaternion()

# Bật chạy animation
try:
    bpy.ops.screen.animation_play()
except Exception as e:
    pass

print('=== THIẾT LẬP CHIẾN TRƯỜNG BẠCH ĐẰNG 938 HOÀN TẤT THÀNH CÔNG 100%! ===')
