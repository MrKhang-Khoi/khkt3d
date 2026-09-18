# MASTER SCRIPT: PHOTOREAL BẠCH ĐẰNG 938 VỚI ANT LANDSCAPE & SAPLING TREE GEN
import bpy
import bmesh
import math
import os
import random
import sys
from mathutils import Vector, Euler, Matrix

print('=== BẮT ĐẦU DỰNG BỐI CẢNH SIÊU THỰC VỚI ANT LANDSCAPE & SAPLING TREE GEN ===')

WS_DIR = r'C:\Users\HPZBook\Desktop\TEST_BLENDER'
ENGINE_DIR = os.path.join(WS_DIR, 'vietnam_naval_engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from bach_dang_stake_generator import create_photoreal_stake_materials, build_hyperrealistic_stake

# 1. XÓA CÁC ĐỐI TƯỢNG HÌNH KHỐI SƠ SÀI CŨ
for ob in list(bpy.context.scene.objects):
    if any(k in ob.name for k in ['DayNui', 'Nui', 'Rung', 'MatNuoc', 'Tree', 'tree', 'leaves', 'SuVet', 'Landscape']):
        bpy.data.objects.remove(ob, do_unlink=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 24

col_env = bpy.data.collections.get('Collection_BoiCanh_LichSu') or bpy.data.collections.new('Collection_BoiCanh_LichSu')
if col_env.name not in scene.collection.children:
    scene.collection.children.link(col_env)

# 2. DÃY NÚI TRÀNG KÊNH: DÙNG ANT LANDSCAPE CHUYÊN NGHIỆP (KHẮC PHỤC HOÀN TOÀN LOW-POLY)
print('-> Đang sinh dãy núi Tràng Kênh bằng A.N.T. Landscape...')
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_TrangKenh_Landscape',
    mesh_size_x=55.0,
    mesh_size_y=160.0,
    subdivision_x=80,
    subdivision_y=110,
    height=22.0,
    noise_type='ridged_multi_fractal',
    basis_type='VORONOI_F2',
    distortion=1.8,
    strata=5,
    strata_type='0',
    edge_falloff='X_AXIS',
    falloff_x='POSITIVE',
    smooth_mesh=True,
    refresh=True
)
obj_mount = bpy.context.active_object
obj_mount.name = 'DayNui_TrangKenh_Landscape_ANT'
obj_mount.location = (-45.0, 0.0, -1.5)

# Gán vật liệu Đá vôi Karst PBR phong hóa nứt nẻ
mat_karst = bpy.data.materials.new('Mat_DaKarst_PBR_Hyper')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.12, 0.14, 0.13, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.88
obj_mount.data.materials.append(mat_karst)
if obj_mount.name not in col_env.objects:
    col_env.objects.link(obj_mount)
if obj_mount.name in scene.collection.objects:
    scene.collection.objects.unlink(obj_mount)

# 3. RỪNG SÚ VẸT NGẬP MẶN: DÙNG SAPLING TREE GEN SINH CÂY THẬT VỚI CÀNH & LÁ
print('-> Đang sinh cây sú vẹt chân thực bằng Sapling Tree Gen...')
# Đặt 3D cursor ở vị trí tạm
scene.cursor.location = (100.0, 100.0, 0.0)
bpy.ops.curve.tree_add(
    do_update=True,
    bevel=True,
    showLeaves=True,
    levels=3,
    length=(1.0, 0.5, 0.3, 0.1),
    branches=(10, 14, 0, 0),
    seed=938,
    scale=2.2
)

# Tìm tree và leaves vừa sinh
tree_trunk = bpy.data.objects.get('tree')
tree_leaves = bpy.data.objects.get('leaves')

mat_trunk = bpy.data.materials.new('Mat_ThanCay_PBR')
mat_trunk.use_nodes = True
bsdf_tr = next((n for n in mat_trunk.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_tr:
    bsdf_tr.inputs['Base Color'].default_value = (0.08, 0.06, 0.04, 1.0)
    bsdf_tr.inputs['Roughness'].default_value = 0.8

mat_leaves = bpy.data.materials.new('Mat_LaCay_PBR')
mat_leaves.use_nodes = True
bsdf_lf = next((n for n in mat_leaves.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_lf:
    bsdf_lf.inputs['Base Color'].default_value = (0.04, 0.09, 0.03, 1.0)
    bsdf_lf.inputs['Roughness'].default_value = 0.6

if tree_trunk:
    tree_trunk.data.materials.append(mat_trunk)
if tree_leaves:
    tree_leaves.data.materials.append(mat_leaves)

# Gom cụm cây sú vẹt thành Group và Scatter dọc bờ Đông (X = 25m đến 45m)
random.seed(938)
tree_positions = [
    (26.0, -55.0), (32.0, -48.0), (28.0, -40.0), (35.0, -32.0), (27.0, -25.0),
    (33.0, -18.0), (29.0, -10.0), (36.0,  -2.0), (28.0,   6.0), (34.0,  14.0),
    (27.0,  22.0), (35.0,  30.0), (30.0,  38.0), (33.0,  46.0), (28.0,  54.0),
    (38.0, -42.0), (40.0, -20.0), (39.0,   5.0), (41.0,  28.0), (42.0,  45.0)
]

for idx, (px, py) in enumerate(tree_positions):
    scl = random.uniform(0.75, 1.25)
    rot_z = random.uniform(0, 2.0 * math.pi)
    
    # Nhân bản thân cây
    if tree_trunk:
        new_trunk = tree_trunk.copy()
        new_trunk.name = f'Cay_SuVet_Trunk_{idx+1}'
        new_trunk.location = (px, py, 0.1)
        new_trunk.scale = (scl, scl, scl)
        new_trunk.rotation_euler = (0, 0, rot_z)
        col_env.objects.link(new_trunk)
    
    # Nhân bản lá cây
    if tree_leaves:
        new_leaf = tree_leaves.copy()
        new_leaf.name = f'Cay_SuVet_Leaves_{idx+1}'
        new_leaf.location = (px, py, 0.1)
        new_leaf.scale = (scl, scl, scl)
        new_leaf.rotation_euler = (0, 0, rot_z)
        col_env.objects.link(new_leaf)

# Ẩn cây gốc mẫu
if tree_trunk:
    tree_trunk.location = (500, 500, 0)
if tree_leaves:
    tree_leaves.location = (500, 500, 0)

# Bãi bùn phù sa ngập mặn bờ Đông
bm_mud = bmesh.new()
mat_m_bank = Matrix.Translation(Vector((36.0, 0, 0.05))) @ Matrix.Diagonal(Vector((28.0, 160.0, 0.3, 1.0)))
bmesh.ops.create_cube(bm_mud, size=1.0, matrix=mat_m_bank)
mesh_mud = bpy.data.meshes.new('Mesh_BoPhuSa_QuangYen')
bm_mud.to_mesh(mesh_mud)
bm_mud.free()
obj_mud = bpy.data.objects.new('BoPhuSa_RungNgapMan', mesh_mud)
mat_mud_pbr = bpy.data.materials.new('Mat_BunPhuSa_PBR')
mat_mud_pbr.use_nodes = True
bsdf_mp = next((n for n in mat_mud_pbr.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_mp:
    bsdf_mp.inputs['Base Color'].default_value = (0.07, 0.06, 0.04, 1.0)
    bsdf_mp.inputs['Roughness'].default_value = 0.75
obj_mud.data.materials.append(mat_mud_pbr)
col_env.objects.link(obj_mud)

# 4. MẶT NƯỚC SÔNG BẠCH ĐẰNG RỘNG LỚN & THỦY TRIỀU RÚT THEO THỜI GIAN
bm_wat = bmesh.new()
bmesh.ops.create_grid(bm_wat, x_segments=64, y_segments=64, size=180.0)
mesh_wat = bpy.data.meshes.new('Mesh_SongBachDang_Rong')
bm_wat.to_mesh(mesh_wat)
bm_wat.free()
obj_wat = bpy.data.objects.new('MatNuoc_Song_BachDang_Hyper', mesh_wat)
obj_wat.location = (0, 0, 0.0)

mat_w_pbr = bpy.data.materials.new('Mat_NuocSong_Reflective')
mat_w_pbr.use_nodes = True
bsdf_wp = next((n for n in mat_w_pbr.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_wp:
    bsdf_wp.inputs['Base Color'].default_value = (0.03, 0.11, 0.14, 1.0)
    bsdf_wp.inputs['Roughness'].default_value = 0.12
    bsdf_wp.inputs['Metallic'].default_value = 0.25
obj_wat.data.materials.append(mat_w_pbr)
col_env.objects.link(obj_wat)

# Hoạt cảnh thủy triều rút
anim_wat = obj_wat.animation_data_create()
act_wat = bpy.data.actions.new(name='Action_ThuyTrieu_Rut_Chuan')
anim_wat.action = act_wat
for f in range(1, 301):
    if f < 75:
        z_tide = 0.65 + math.sin(f * 0.1) * 0.02
    elif f < 155:
        t_drop = (f - 75) / 80.0
        z_tide = 0.65 - t_drop * 1.15
    else:
        z_tide = -0.50 + math.sin(f * 0.08) * 0.02
    obj_wat.location = (0, 0, z_tide)
    obj_wat.keyframe_insert(data_path='location', frame=f)

# 5. CẬP NHẬT GÓC VIEWPORT 3D PERSPECTIVE TOÀN DIỆN
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'PERSP'
            r3d.view_distance = 65.0
            r3d.view_location = (0.0, 2.0, 2.0)
            r3d.view_rotation = Euler((math.radians(58), 0.0, math.radians(18)), 'XYZ').to_quaternion()

try:
    bpy.ops.screen.animation_play()
except Exception:
    pass

print('=== DỰNG BỐI CẢNH SIÊU THỰC VỚI ANT LANDSCAPE & SAPLING TREE HOÀN TẤT 100%! ===')
