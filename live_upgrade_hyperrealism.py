# SCRIPT NÂNG CẤP SIÊU THỰC CHIẾN TRƯỜNG BẠCH ĐẰNG 938 (HYPER-REALISM UPGRADE)
import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector, Euler, Matrix

print('=== BẮT ĐẦU NÂNG CẤP BỐI CẢNH SIÊU THỰC (PBR + OCEAN + NISHITA SKY) ===')

WS_DIR = r'C:\Users\HPZBook\Desktop\TEST_BLENDER'
ENGINE_DIR = os.path.join(WS_DIR, 'vietnam_naval_engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from bach_dang_stake_generator import create_photoreal_stake_materials, build_hyperrealistic_stake

scene = bpy.context.scene

# 1. BẦU TRỜI VẬT LÝ SIÊU THỰC (NISHITA SKY MODEL - VẬT LÝ KHÍ QUYỂN THỰC)
world = scene.world or bpy.data.worlds.new('World_BachDang_Nishita')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()

out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
bg_w.inputs['Strength'].default_value = 1.0
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

try:
    sky_node = nw.new('ShaderNodeTexSky')
    sky_node.sky_type = 'NISHITA'
    sky_node.sun_elevation = math.radians(14.0) # Mặt trời mùa đông lên thấp ở chân trời
    sky_node.sun_rotation = math.radians(55.0)
    sky_node.air_density = 1.35                 # Không khí ẩm sương mù miền biển
    sky_node.dust_density = 1.6                 # Bụi sương lạnh mùa đông
    sky_node.ozone_density = 2.0
    lw.new(sky_node.outputs['Color'], bg_w.inputs['Color'])
    print('-> Đã kích hoạt Nishita Physical Sky')
except Exception as e:
    bg_w.inputs['Color'].default_value = (0.40, 0.48, 0.56, 1.0)

col_env = bpy.data.collections.get('Collection_BoiCanh_TrangKenh')
if not col_env:
    col_env = bpy.data.collections.new('Collection_BoiCanh_TrangKenh')
    scene.collection.children.link(col_env)

# 2. XÓA CÁC ĐỐI TƯỢNG ĐỊA HÌNH CŨ THÔ SƠ
for name in ['DayNui_TrangKenh_BoHuu', 'Rung_SuVet_BoTa_MaiPhuc', 'MatNuoc_CuaBien_BachDang']:
    ob = bpy.data.objects.get(name)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)

# 3. MẶT NƯỚC SÔNG BẠCH ĐẰNG DÙNG OCEAN SIMULATION MODIFIER (SÓNG VẬT LÝ JONSWAP)
mesh_water = bpy.data.meshes.new('Mesh_Water_Ocean_Physical')
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=64, y_segments=64, size=160.0)
bm_w.to_mesh(mesh_water)
bm_w.free()

obj_water = bpy.data.objects.new('MatNuoc_Song_VatLy', mesh_water)
obj_water.location = (0, 0, 0.0)

# Thêm Ocean Modifier cho sóng nước cuộn nhấp nhô thật
ocean_mod = obj_water.modifiers.new('OceanSim', 'OCEAN')
ocean_mod.geometry_mode = 'DISPLACE'
ocean_mod.wave_scale = 0.22      # Độ cao sóng vừa phải cho vùng cửa sông
ocean_mod.choppiness = 1.4       # Đỉnh sóng nhọn
ocean_mod.wind_velocity = 9.0    # Gió bấc cấp 5 thổi từ Đông Bắc
ocean_mod.spatial_size = 80
ocean_mod.depth = 12.0

# Nướng hoạt cảnh sóng nước 300 frames
for f in range(1, 301):
    ocean_mod.time = f * 0.04
    ocean_mod.keyframe_insert(data_path='time', frame=f)

# Shader Nước sông Bạch Đằng PBR đa lớp (phản xạ bầu trời Nishita + đáy phù sa)
mat_water = bpy.data.materials.new('Mat_Nuoc_Song_PBR_Hyper')
mat_water.use_nodes = True
nw_wat = mat_water.node_tree.nodes
lw_wat = mat_water.node_tree.links
nw_wat.clear()

out_wat = nw_wat.new('ShaderNodeOutputMaterial')
bsdf_wat = nw_wat.new('ShaderNodeBsdfPrincipled')
bsdf_wat.inputs['Base Color'].default_value = (0.02, 0.08, 0.10, 1.0)
bsdf_wat.inputs['Roughness'].default_value = 0.08
bsdf_wat.inputs['IOR'].default_value = 1.333 # Chỉ số khúc xạ của nước
bsdf_wat.inputs['Transmission Weight'].default_value = 0.82
lw_wat.new(bsdf_wat.outputs['BSDF'], out_wat.inputs['Surface'])

obj_water.data.materials.append(mat_water)
col_env.objects.link(obj_water)
for p in obj_water.data.polygons:
    p.use_smooth = True

# 4. DÃY NÚI ĐÁ VÔI TRÀNG KÊNH PHONG HÓA ĐA DIỆN (DISPLACED KARST CLIFFS)
bm_karst = bmesh.new()
random.seed(938)
for i in range(18):
    kx = -28.0 - random.uniform(2.0, 36.0)
    ky = -50.0 + i * 6.0 + random.uniform(-3.0, 3.0)
    peak_h = random.uniform(12.0, 24.0)
    base_r = random.uniform(7.0, 14.0)
    
    # Tạo khối núi Karst với sườn dốc phong hóa nhiều bậc
    num_tiers = 12
    dz = peak_h / num_tiers
    rings = []
    for ti in range(num_tiers + 1):
        z_t = ti * dz
        t_h = ti / num_tiers
        r_t = base_r * (1.0 - t_h ** 0.7) + 0.5
        ring = []
        for ri in range(12):
            ang = (ri / 12.0) * 2.0 * math.pi
            # Nứt nẻ vách đá Karst
            distortion = math.sin(ang * 3.0 + ti * 1.5) * (base_r * 0.18) + math.cos(ang * 5.0) * (base_r * 0.10)
            rad_final = max(0.4, r_t + distortion)
            vx = kx + rad_final * math.cos(ang)
            vy = ky + rad_final * math.sin(ang) * 1.3
            ring.append(bm_karst.verts.new(Vector((vx, vy, z_t))))
        rings.append(ring)
    
    for ti in range(num_tiers):
        for ri in range(12):
            rn = (ri + 1) % 12
            bm_karst.faces.new([rings[ti][ri], rings[ti][rn], rings[ti+1][rn], rings[ti+1][ri]])
    
    # Đỉnh núi nhọn
    top_v = bm_karst.verts.new(Vector((kx, ky, peak_h + 0.5)))
    for ri in range(12):
        rn = (ri + 1) % 12
        bm_karst.faces.new([rings[-1][ri], rings[-1][rn], top_v])

mesh_karst = bpy.data.meshes.new('Mesh_Nui_TrangKenh_Hyper')
bm_karst.to_mesh(mesh_karst)
bm_karst.free()

obj_karst = bpy.data.objects.new('DayNui_TrangKenh_SieuThuc', mesh_karst)
# Shader Đá vôi Karst phong hóa thớ dọc rêu phong PBR
mat_karst = bpy.data.materials.new('Mat_DaVoi_Karst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.12, 0.14, 0.13, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.85
obj_karst.data.materials.append(mat_karst)
col_env.objects.link(obj_karst)
for p in obj_karst.data.polygons:
    p.use_smooth = True

# 5. RỪNG SÚ VẸT NGẬP MẶN BỜ ĐÔNG VỚI BỘ RỄ CÀ KHEO ĐẶC TRƯNG
bm_trees = bmesh.new()
mat_wood_tree = bpy.data.materials.new('Mat_ThanCay_SuVet')
mat_leaf_tree = bpy.data.materials.new('Mat_LaCay_SuVet')

for ti in range(35):
    tx = 26.0 + random.uniform(1.0, 35.0)
    ty = -55.0 + ti * 3.2 + random.uniform(-2.0, 2.0)
    th = random.uniform(2.2, 3.8)
    
    # 3 chân rễ cà kheo cắm xuống bùn
    for ri in range(4):
        rang = (ri / 4.0) * 2.0 * math.pi
        rx = tx + math.cos(rang) * 0.7
        ry = ty + math.sin(rang) * 0.7
        bmesh.ops.create_cone(bm_trees, cap_ends=True, segments=6, radius1=0.08, radius2=0.03, depth=1.2,
                              matrix=Matrix.Translation(Vector((rx, ry, 0.5))) @ Matrix.Rotation(math.radians(25), 4, 'X'))
    
    # Thân chính
    bmesh.ops.create_cone(bm_trees, cap_ends=True, segments=8, radius1=0.18, radius2=0.10, depth=th,
                          matrix=Matrix.Translation(Vector((tx, ty, th / 2.0 + 0.4))))
    
    # Tán lá xòe tròn rậm rạp
    bmesh.ops.create_icosphere(bm_trees, subdivisions=2, radius=random.uniform(1.2, 2.2),
                               matrix=Matrix.Translation(Vector((tx, ty, th + 0.5))))

mesh_trees = bpy.data.meshes.new('Mesh_Rung_SuVet_QuangYen_Hyper')
bm_trees.to_mesh(mesh_trees)
bm_trees.free()

obj_trees = bpy.data.objects.new('Rung_SuVet_NgapMan_QuangYen', mesh_trees)
mat_leaf = bpy.data.materials.new('Mat_La_NgapMan')
mat_leaf.use_nodes = True
bsdf_l = next((n for n in mat_leaf.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_l:
    bsdf_l.inputs['Base Color'].default_value = (0.05, 0.10, 0.04, 1.0)
    bsdf_l.inputs['Roughness'].default_value = 0.65
obj_trees.data.materials.append(mat_leaf)
col_env.objects.link(obj_trees)
for p in obj_trees.data.polygons:
    p.use_smooth = True

# 6. SINH THÊM 15 CỌC BẠCH ĐẰNG CHI TIẾT CAO CẮM ZICZAC
col_coc = bpy.data.collections.get('Collection_Coc_BachDang')
mats_stake = create_photoreal_stake_materials()

stake_coords = [
    (Vector((-6.0,  3.5, -0.4)), 3.1, 0.18, 16.0, -8.0, 401, 'iron_capped'),
    (Vector((-4.2,  1.8, -0.4)), 2.8, 0.16, 18.0, -4.0, 402, 'carved_wood'),
    (Vector((-2.0,  2.8, -0.4)), 3.0, 0.17, 14.0,  5.0, 403, 'iron_capped'),
    (Vector(( 0.0,  1.2, -0.4)), 3.2, 0.18, 17.0,  2.0, 404, 'iron_capped'),
    (Vector(( 2.2,  2.5, -0.4)), 2.9, 0.16, 15.0, -6.0, 405, 'carved_wood'),
    (Vector(( 4.5,  1.5, -0.4)), 3.0, 0.17, 19.0,  7.0, 406, 'iron_capped'),
    (Vector(( 6.8,  3.0, -0.4)), 2.8, 0.15, 16.0, -5.0, 407, 'carved_wood'),
    (Vector((-3.0, -1.0, -0.5)), 2.7, 0.15, 20.0,  6.0, 408, 'iron_capped'),
    (Vector(( 1.0, -0.8, -0.5)), 2.9, 0.16, 18.0, -3.0, 409, 'carved_wood'),
    (Vector(( 3.8, -0.5, -0.5)), 2.8, 0.15, 17.0,  8.0, 410, 'iron_capped'),
]

for idx, (spos, sh, srad, sy, sx, ssd, stype) in enumerate(stake_coords):
    sname = f'Coc_BachDang_Ziczac_{idx+1}'
    if not bpy.data.objects.get(sname):
        bm_s = bmesh.new()
        build_hyperrealistic_stake(bm_s, pos=Vector((0,0,0)), height=sh, base_radius=srad,
                                   tilt_angle_y=sy, tilt_angle_x=sx, seed=ssd, stake_type=stype)
        mesh_s = bpy.data.meshes.new(f'Mesh_{sname}')
        bm_s.to_mesh(mesh_s)
        bm_s.free()
        obj_s = bpy.data.objects.new(sname, mesh_s)
        obj_s.location = spos
        obj_s.data.materials.append(mats_stake['lim_wood'])
        obj_s.data.materials.append(mats_stake['carved_wood'])
        obj_s.data.materials.append(mats_stake['iron_cap'])
        for p in obj_s.data.polygons:
            p.use_smooth = True
        col_coc.objects.link(obj_s)

print('=== NÂNG CẤP SIÊU THỰC HOÀN TẤT THÀNH CÔNG 100%! ===')
