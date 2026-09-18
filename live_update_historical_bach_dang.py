# SCRIPT TÁI TẠO ĐỊA HÌNH SỬ HỌC BẠCH ĐẰNG 938 CHÍNH XÁC TRÊN BLENDER
import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Euler, Matrix

print('=== BẮT ĐẦU CẬP NHẬT ĐỊA HÌNH CHÍNH SỬ BẠCH ĐẰNG 938 ===')

# 1. XÓA CÁC ĐỐI TƯỢNG ĐỊA HÌNH SAI CŨ
for name in ['DayNui_DaVoi_TrangKenh', 'BoSong_PhuSa_HaiBen', 'MatNuoc_SongBachDang']:
    ob = bpy.data.objects.get(name)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)

scene = bpy.context.scene

# 2. VÒM TRỜI MÙA ĐÔNG THÁNG CHẠP 938 (OVERCAST WINTER MIST)
world = scene.world or bpy.data.worlds.new('World_Winter_938')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()

out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
# Tone xám lam sương mù gió bấc mùa đông
bg_w.inputs['Color'].default_value = (0.32, 0.40, 0.48, 1.0)
bg_w.inputs['Strength'].default_value = 1.1
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

col_env = bpy.data.collections.get('Collection_BoiCanh_TrangKenh')
if not col_env:
    col_env = bpy.data.collections.new('Collection_BoiCanh_TrangKenh')
    scene.collection.children.link(col_env)

# 3. MẶT NƯỚC CỬA SÔNG BẠCH ĐẰNG RỘNG MÊNH MÔNG (150m x 200m)
bm_water = bmesh.new()
bmesh.ops.create_grid(bm_water, x_segments=64, y_segments=64, size=180.0)
mesh_water = bpy.data.meshes.new('Mesh_CuaSong_BachDang_Rong')
bm_water.to_mesh(mesh_water)
bm_water.free()

obj_water = bpy.data.objects.new('MatNuoc_CuaBien_BachDang', mesh_water)
obj_water.location = (0, 0, 0.0)

mat_water = bpy.data.materials.new('Mat_Nuoc_Song_LichSu')
mat_water.use_nodes = True
bsdf_wat = next((n for n in mat_water.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_wat:
    # Nước cửa sông pha mặn xanh rêu thẫm có sóng
    bsdf_wat.inputs['Base Color'].default_value = (0.04, 0.13, 0.16, 1.0)
    bsdf_wat.inputs['Roughness'].default_value = 0.14
    bsdf_wat.inputs['Metallic'].default_value = 0.25
obj_water.data.materials.append(mat_water)
col_env.objects.link(obj_water)

# 4. BỜ TÂY (HỮU NGẠN): DÃY NÚI ĐÁ VÔI TRÀNG KÊNH LÙI XA VÀO ĐẤT LIỀN (X = -28m đến -75m)
bm_trangkenh = bmesh.new()
# Núi đá vôi karst dạng tháp (tower karst) nhấp nhô lùi sâu bờ hữu
random.seed(938)
for i in range(22):
    kx = -26.0 - random.uniform(2.0, 42.0)
    ky = -55.0 + i * 5.2 + random.uniform(-2.0, 2.0)
    peak_h = random.uniform(8.0, 18.0)
    base_r = random.uniform(5.5, 11.0)
    
    # Karst peak
    mat_k = Matrix.Translation(Vector((kx, ky, peak_h / 2.0 - 0.5))) @ Matrix.Diagonal(Vector((base_r, base_r * 1.2, peak_h, 1.0)))
    bmesh.ops.create_cone(bm_trangkenh, cap_ends=True, segments=8, radius1=1.0, radius2=0.12, depth=1.0, matrix=mat_k)

# Dải chân núi & bãi lầy bờ hữu (Hải Phòng)
mat_bank_west = Matrix.Translation(Vector((-24.0, 0, 0.15))) @ Matrix.Diagonal(Vector((18.0, 140.0, 0.5, 1.0)))
bmesh.ops.create_cube(bm_trangkenh, size=1.0, matrix=mat_bank_west)

mesh_trangkenh = bpy.data.meshes.new('Mesh_TrangKenh_Karst')
bm_trangkenh.to_mesh(mesh_trangkenh)
bm_trangkenh.free()

obj_trangkenh = bpy.data.objects.new('DayNui_TrangKenh_BoHuu', mesh_trangkenh)
mat_karst = bpy.data.materials.new('Mat_DaKarst_TrangKenh')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.13, 0.15, 0.14, 1.0) # Đá vôi xám rêu
    bsdf_k.inputs['Roughness'].default_value = 0.88
obj_trangkenh.data.materials.append(mat_karst)
col_env.objects.link(obj_trangkenh)

# 5. BỜ ĐÔNG (TẢ NGẠN - QUẢNG YÊN): BÃI PHÙ SA NGẬP TRIỀU & RỪNG SÚ VẸT MAI PHỤC (X = +22m đến +75m)
bm_mangrove = bmesh.new()
# Bãi bùn lầy bằng phẳng ngập mặn
mat_bank_east = Matrix.Translation(Vector((36.0, 0, 0.1))) @ Matrix.Diagonal(Vector((30.0, 140.0, 0.4, 1.0)))
bmesh.ops.create_cube(bm_mangrove, size=1.0, matrix=mat_bank_east)

# Rừng ngập mặn sú vẹt (hàng trăm bụi cây sú vẹt đước xanh thẫm)
for j in range(45):
    mx = 24.0 + random.uniform(1.0, 32.0)
    my = -50.0 + j * 2.4 + random.uniform(-1.5, 1.5)
    tree_h = random.uniform(1.4, 2.6)
    tree_r = random.uniform(1.2, 2.2)
    mat_tree = Matrix.Translation(Vector((mx, my, tree_h / 2.0 + 0.1))) @ Matrix.Diagonal(Vector((tree_r, tree_r, tree_h, 1.0)))
    bmesh.ops.create_icosphere(bm_mangrove, subdivisions=1, radius=1.0, matrix=mat_tree)

mesh_mangrove = bpy.data.meshes.new('Mesh_Rung_NgapMan_QuangYen')
bm_mangrove.to_mesh(mesh_mangrove)
bm_mangrove.free()

obj_mangrove = bpy.data.objects.new('Rung_SuVet_BoTa_MaiPhuc', mesh_mangrove)
mat_mangrove = bpy.data.materials.new('Mat_Rung_SuVet_DeepGreen')
mat_mangrove.use_nodes = True
bsdf_m = next((n for n in mat_mangrove.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_m:
    bsdf_m.inputs['Base Color'].default_value = (0.04, 0.08, 0.03, 1.0) # Lá sú vẹt xanh thẫm ngập mặn
    bsdf_m.inputs['Roughness'].default_value = 0.75
obj_mangrove.data.materials.append(mat_mangrove)
col_env.objects.link(obj_mangrove)

# 6. PHÂN BỐ LẠI BÃI CỌC THÀNH DẢI HÌNH CHỮ V CHẶN LUỒNG LẠCH (X = -12m đến +12m, Y = -2m đến +4m)
col_coc = bpy.data.collections.get('Collection_Coc_BachDang')
if col_coc:
    # Trải bãi cọc thành luồng phục kích chữ V
    coords = [
        ('Coc_Chinh_BitSat', Vector((0.0, 0.5, 0.0)), (math.radians(16), 0, 0)),
        ('Coc_Nghieng_GoLim', Vector((-3.5, 2.0, 0.0)), (math.radians(20), math.radians(-10), 0)),
        ('Coc_Gay_MuiSat', Vector((4.0, 2.2, 0.0)), (math.radians(18), math.radians(12), 0))
    ]
    for cname, cloc, crot in coords:
        cobj = bpy.data.objects.get(cname)
        if cobj:
            cobj.location = cloc
            cobj.rotation_euler = crot

# 7. CHIẾN THUYỀN VẬN HÀNH TRÊN MẶT SÔNG RỘNG LỚN
ship_ta = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
if ship_ta:
    ship_ta.location = (2.0, -18.0, 0.0) # Hạ lưu xa
    ship_ta.rotation_euler = (0, 0, math.radians(-8))

ship_han = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
if ship_han:
    # Thuyền giặc lao từ thượng lưu Y = 20m xuống đâm cọc ở Y = 3.5m
    anim_data = ship_han.animation_data
    if anim_data and anim_data.action:
        act = anim_data.action
        for f in range(1, 301):
            t = f / 24.0
            if f < 110:
                prog = f / 110.0
                y_pos = 20.0 - prog * 16.5
                x_pos = -0.5
                z_pos = math.sin(t * 2.0) * 0.05
                pitch = math.sin(t * 1.8) * math.radians(1.5)
                roll = math.cos(t * 1.5) * math.radians(1.2)
                yaw = math.radians(180)
            elif f < 145:
                crash_t = (f - 110) / 35.0
                y_pos = 3.5 - crash_t * 0.4
                x_pos = -0.5
                z_pos = math.sin(crash_t * math.pi) * 0.20 - crash_t * 0.40
                pitch = -math.sin(crash_t * math.pi) * math.radians(3.5) + crash_t * math.radians(5.5)
                roll = crash_t * math.radians(24.0)
                yaw = math.radians(180) + crash_t * math.radians(10.0)
            else:
                settle_t = (f - 145) / 155.0
                y_pos = 3.1
                x_pos = -0.5
                z_pos = -0.40 - settle_t * 0.45
                pitch = math.radians(5.5)
                roll = math.radians(24.0) + settle_t * math.radians(3.5)
                yaw = math.radians(190)
            ship_han.location = (x_pos, y_pos, z_pos)
            ship_han.rotation_euler = Euler((pitch, roll, yaw))
            ship_han.keyframe_insert(data_path='location', frame=f)
            ship_han.keyframe_insert(data_path='rotation_euler', frame=f)

# 8. CẬP NHẬT CAMERA VÀ VIEWPORT
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

print('=== CẬP NHẬT ĐỊA HÌNH SỬ HỌC THÀNH CÔNG 100%! ===')
