# SCRIPT TỰ ĐỘNG DỰNG TOÀN DIỆN BỐI CẢNH ĐẠI CHIẾN BẠCH ĐẰNG TRỰC TIẾP TRÊN BLENDER
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler, Matrix

print('=== BẮT ĐẦU DỰNG TOÀN DIỆN BỐI CẢNH TRÊN BLENDER VIEWPORT ===')

WS_DIR = r'C:\Users\HPZBook\Desktop\TEST_BLENDER'

# 1. XÓA CÁC ĐỐI TƯỢNG MẶC ĐỊNH
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 24

# 2. BẦU TRỜI MÙA ĐÔNG 938 (WORLD SKY SHADER)
world = bpy.data.worlds.get('World_BachDang_Live') or bpy.data.worlds.new('World_BachDang_Live')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()

out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
bg_w.inputs['Color'].default_value = (0.35, 0.45, 0.55, 1.0) # Sương mù đông lam nhạt
bg_w.inputs['Strength'].default_value = 1.2
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

# 3. DÃY NÚI ĐÁ VÔI TRÀNG KÊNH & BỜ SÔNG (TERRAIN & MOUNTAINS)
col_env = bpy.data.collections.new('Collection_BoiCanh_TrangKenh')
scene.collection.children.link(col_env)

# Dãy núi Tràng Kênh hậu cảnh phía Tây và Bắc
bm_mount = bmesh.new()
for side in [-1, 1]:
    for i in range(16):
        x = side * (16.0 + (i % 3) * 3.0)
        y = -25.0 + i * 4.0
        peak_h = 6.0 + math.sin(i * 1.3) * 3.5 + math.cos(i * 0.7) * 2.0
        base_r = 5.0 + (i % 4) * 1.2
        # Tạo ngọn núi đá vôi dốc đứng karst
        mat_m = Matrix.Translation(Vector((x, y, peak_h / 2.0))) @ Matrix.Diagonal(Vector((base_r, base_r * 1.3, peak_h, 1.0)))
        bmesh.ops.create_cone(bm_mount, cap_ends=True, segments=7, radius1=1.0, radius2=0.08, depth=1.0, matrix=mat_m)

mesh_mount = bpy.data.meshes.new('Mesh_Nui_TrangKenh')
bm_mount.to_mesh(mesh_mount)
bm_mount.free()
obj_mount = bpy.data.objects.new('DayNui_DaVoi_TrangKenh', mesh_mount)

mat_rock = bpy.data.materials.new('Mat_DaVoi_TrangKenh')
mat_rock.use_nodes = True
bsdf_rock = next((n for n in mat_rock.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_rock:
    bsdf_rock.inputs['Base Color'].default_value = (0.14, 0.16, 0.15, 1.0) # Xám đá vôi rêu phong
    bsdf_rock.inputs['Roughness'].default_value = 0.85
obj_mount.data.materials.append(mat_rock)
col_env.objects.link(obj_mount)

# Bờ sông phù sa hai bên (Riverbanks)
bm_bank = bmesh.new()
for side in [-1, 1]:
    mat_b = Matrix.Translation(Vector((side * 14.0, 0, 0.2))) @ Matrix.Diagonal(Vector((10.0, 70.0, 0.6, 1.0)))
    bmesh.ops.create_cube(bm_bank, size=1.0, matrix=mat_b)
mesh_bank = bpy.data.meshes.new('Mesh_BoSong_PhuSa')
bm_bank.to_mesh(mesh_bank)
bm_bank.free()
obj_bank = bpy.data.objects.new('BoSong_PhuSa_HaiBen', mesh_bank)

mat_mud = bpy.data.materials.new('Mat_PhuSa_BoSong')
mat_mud.use_nodes = True
bsdf_mud = next((n for n in mat_mud.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_mud:
    bsdf_mud.inputs['Base Color'].default_value = (0.10, 0.08, 0.05, 1.0) # Đất bùn phù sa sẫm
    bsdf_mud.inputs['Roughness'].default_value = 0.7
obj_bank.data.materials.append(mat_mud)
col_env.objects.link(obj_bank)

# 4. MẶT NƯỚC SÔNG BẠCH ĐẰNG CUỘN SÓNG (Z = 0.0)
bm_water = bmesh.new()
bmesh.ops.create_grid(bm_water, x_segments=48, y_segments=48, size=80.0)
mesh_water = bpy.data.meshes.new('Mesh_Nuoc_SongBachDang')
bm_water.to_mesh(mesh_water)
bm_water.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang', mesh_water)
obj_water.location = (0, 0, 0.0)

mat_water = bpy.data.materials.new('Mat_Nuoc_Song_PBR')
mat_water.use_nodes = True
bsdf_wat = next((n for n in mat_water.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_wat:
    bsdf_wat.inputs['Base Color'].default_value = (0.05, 0.15, 0.16, 1.0) # Nước sông Bạch Đằng xanh thẫm
    bsdf_wat.inputs['Roughness'].default_value = 0.12
    bsdf_wat.inputs['Metallic'].default_value = 0.3
obj_water.data.materials.append(mat_water)
col_env.objects.link(obj_water)

# 5. LINK BÃI CỌC BẠCH ĐẰNG (COLLECTION_COC_BACHDANG)
coc_path = os.path.join(WS_DIR, 'assets', 'props', 'coc_bach_dang_master.blend')
with bpy.data.libraries.load(coc_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Coc_BachDang']
col_coc = data_to.collections[0]
scene.collection.children.link(col_coc)

# 6. LINK THUYỀN CHIẾN ĐẠI VIỆT (NGÔ QUYỀN - HẠ LƯU Y = -10m)
thuyen_path = os.path.join(WS_DIR, 'assets', 'ships', 'thuyen_ta_ngoquyen_master.blend')
with bpy.data.libraries.load(thuyen_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta']
col_thuyen = data_to.collections[0]
scene.collection.children.link(col_thuyen)

ship_ta = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
if ship_ta:
    ship_ta.location = (1.8, -10.5, 0.0)
    ship_ta.rotation_euler = (0, 0, math.radians(-12))
    # Gán animation bập bềnh sóng
    act_ta = bpy.data.actions.get('Action_Thuyen_Ta_WaveMotion')
    if act_ta:
        if not ship_ta.animation_data:
            ship_ta.animation_data_create()
        ship_ta.animation_data.action = act_ta

# 7. LINK LÂU THUYỀN NAM HÁN (THƯỢNG LƯU Y = 13m LAO XUỐNG ĐÂM CỌC)
lau_path = os.path.join(WS_DIR, 'assets', 'ships', 'lau_thuyen_namhan_master.blend')
with bpy.data.libraries.load(lau_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Lau_Thuyen_NamHan']
col_lau = data_to.collections[0]
scene.collection.children.link(col_lau)

ship_han = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
if ship_han:
    ship_han.location = (-0.8, 12.5, 0.0)
    ship_han.rotation_euler = (0, 0, math.radians(180))
    # Nướng animation đâm cọc
    anim_data = ship_han.animation_data_create()
    action = bpy.data.actions.new(name='Action_LauThuyen_DaiChien')
    anim_data.action = action
    for f in range(1, 301):
        t = f / 24.0
        if f < 110:
            prog = f / 110.0
            y_pos = 12.5 - prog * 9.0 # từ 12.5m xuống 3.5m
            x_pos = -0.8
            z_pos = math.sin(t * 2.0) * 0.05
            pitch = math.sin(t * 1.8) * math.radians(1.5)
            roll = math.cos(t * 1.5) * math.radians(1.2)
            yaw = math.radians(180)
        elif f < 145:
            crash_t = (f - 110) / 35.0
            y_pos = 3.5 - crash_t * 0.4
            x_pos = -0.8
            z_pos = math.sin(crash_t * math.pi) * 0.20 - crash_t * 0.40
            pitch = -math.sin(crash_t * math.pi) * math.radians(3.5) + crash_t * math.radians(5.5)
            roll = crash_t * math.radians(24.0) # Nghiêng mạn đâm cọc
            yaw = math.radians(180) + crash_t * math.radians(10.0)
        else:
            settle_t = (f - 145) / 155.0
            y_pos = 3.1
            x_pos = -0.8
            z_pos = -0.40 - settle_t * 0.45
            pitch = math.radians(5.5)
            roll = math.radians(24.0) + settle_t * math.radians(3.5)
            yaw = math.radians(190)
        ship_han.location = (x_pos, y_pos, z_pos)
        ship_han.rotation_euler = Euler((pitch, roll, yaw))
        ship_han.keyframe_insert(data_path='location', frame=f)
        ship_han.keyframe_insert(data_path='rotation_euler', frame=f)

# 8. HỆ THỐNG CHIẾU SÁNG TOÀN CẢNH
sun_data = bpy.data.lights.new('Sun_Dawn_Winter', 'SUN')
sun_data.energy = 5.2
sun_data.color = (1.0, 0.95, 0.88) # Nắng sớm vàng ấm
sun_obj = bpy.data.objects.new('Sun_Dawn_Winter', sun_data)
sun_obj.rotation_euler = (math.radians(48), math.radians(14), math.radians(45))
scene.collection.objects.link(sun_obj)

fill_data = bpy.data.lights.new('Sky_Fill_Light', 'SUN')
fill_data.energy = 2.8
fill_data.color = (0.75, 0.85, 1.0)
fill_obj = bpy.data.objects.new('Sky_Fill_Light', fill_data)
fill_obj.rotation_euler = (math.radians(-30), math.radians(-15), math.radians(-130))
scene.collection.objects.link(fill_obj)

# 9. CAMERA ĐIỆN ẢNH TOÀN CẢNH
cam_data = bpy.data.cameras.new('Cinema_Battle_Cam')
cam_data.lens = 35.0
cam_obj = bpy.data.objects.new('Cinema_Battle_Cam', cam_data)
cam_obj.location = (22.0, -22.0, 14.0)
dir_cam = Vector((0, 0, 1.5)) - cam_obj.location
cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# 10. CHUYỂN TẤT CẢ VIEWPORT SANG MATERIAL PREVIEW
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

print('=== DỰNG TOÀN DIỆN BỐI CẢNH THÀNH CÔNG 100%! ===')
