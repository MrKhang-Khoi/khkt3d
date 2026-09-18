# SCRIPT LẮP RÁP ĐẠI CHIẾN BẠCH ĐẰNG CHUẨN TỌA ĐỘ CHIẾN THUẬT LỊCH SỬ
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler

WS_DIR = r'C:\Users\HPZBook\Desktop\TEST_BLENDER'
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300
scene.render.fps = 24

# 1. LINK & SPAWN BÃI CỌC (TRUNG TÂM CHIẾN TRƯỜNG Y = -2m đến +4m)
coc_blend = os.path.join(WS_DIR, 'assets', 'props', 'coc_bach_dang_master.blend')
with bpy.data.libraries.load(coc_blend, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Coc_BachDang']

col_coc = data_to.collections[0]
scene.collection.children.link(col_coc)

# 2. LINK & SPAWN THUYỀN ĐẠI VIỆT (HẠ LƯU Y = -8.5m)
thuyen_blend = os.path.join(WS_DIR, 'assets', 'ships', 'thuyen_ta_ngoquyen_master.blend')
with bpy.data.libraries.load(thuyen_blend, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta']

col_thuyen = data_to.collections[0]
scene.collection.children.link(col_thuyen)

ship_ta = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
if ship_ta:
    # Đặt thuyền ta ở vị trí rút lui nhử địch qua bãi cọc
    ship_ta.location = (1.5, -9.5, 0.0)
    ship_ta.rotation_euler = (0, 0, math.radians(-10))

# 3. LINK & SPAWN LÂU THUYỀN NAM HÁN (THƯỢNG LƯU Y = 14m LAO XUỐNG ĐÂM CỌC)
lau_blend = os.path.join(WS_DIR, 'assets', 'ships', 'lau_thuyen_namhan_master.blend')
with bpy.data.libraries.load(lau_blend, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Lau_Thuyen_NamHan']

col_lau = data_to.collections[0]
scene.collection.children.link(col_lau)

ship_han = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
if ship_han:
    # Animation hành động chiến đấu lịch sử:
    anim_data = ship_han.animation_data_create()
    action = bpy.data.actions.new(name='Action_Lau_Thuyen_Battle')
    anim_data.action = action
    
    for f in range(1, 301):
        t = f / 24.0
        if f < 110:
            # Giai đoạn 1: Đuổi theo thuyền Đại Việt
            prog = f / 110.0
            y_pos = 14.0 - prog * 10.5 # từ 14m xuống 3.5m
            x_pos = -0.5
            z_pos = math.sin(t * 2.2) * 0.05
            pitch = math.sin(t * 1.8) * math.radians(1.5)
            roll = math.cos(t * 1.5) * math.radians(1.2)
            yaw = math.radians(180)
        elif f < 145:
            # Giai đoạn 2: Đâm trúng cọc ngầm ở frame 110! Khựng lại, vỡ mạn, nghiêng mạnh
            crash_t = (f - 110) / 35.0
            y_pos = 3.5 - crash_t * 0.5
            x_pos = -0.5
            z_pos = math.sin(crash_t * math.pi) * 0.25 - crash_t * 0.40
            pitch = -math.sin(crash_t * math.pi) * math.radians(4.0) + crash_t * math.radians(6.0)
            roll = crash_t * math.radians(24.0) # Nghiêng mạn
            yaw = math.radians(180) + crash_t * math.radians(10.0)
        else:
            # Giai đoạn 3: Mắc cạn vỡ lườn, chìm dần
            settle_t = (f - 145) / 155.0
            y_pos = 3.0
            x_pos = -0.5
            z_pos = -0.40 - settle_t * 0.50
            pitch = math.radians(6.0)
            roll = math.radians(24.0) + settle_t * math.radians(4.0)
            yaw = math.radians(190)

        ship_han.location = (x_pos, y_pos, z_pos)
        ship_han.rotation_euler = Euler((pitch, roll, yaw))
        ship_han.keyframe_insert(data_path='location', frame=f)
        ship_han.keyframe_insert(data_path='rotation_euler', frame=f)

# 4. MẶT NƯỚC SÔNG BẠCH ĐẰNG RỘNG LỚN (ĐÁY THUYỀN CHẠM MẶT NƯỚC Z = 0)
bm_water = bmesh.new()
bmesh.ops.create_grid(bm_water, x_segments=32, y_segments=32, size=50.0)
mesh_water = bpy.data.meshes.new('Mesh_Song_BachDang_Nuoc')
bm_water.to_mesh(mesh_water)
bm_water.free()

obj_water = bpy.data.objects.new('Song_BachDang_Nuoc', mesh_water)
obj_water.location = (0, 0, 0.0)

mat_water = bpy.data.materials.new('Mat_Nuoc_SongBachDang')
mat_water.use_nodes = True
bsdf_wat = next((n for n in mat_water.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_wat:
    bsdf_wat.inputs['Base Color'].default_value = (0.04, 0.12, 0.14, 1.0)
    bsdf_wat.inputs['Roughness'].default_value = 0.15
    bsdf_wat.inputs['Metallic'].default_value = 0.2
obj_water.data.materials.append(mat_water)
scene.collection.objects.link(obj_water)

# 5. CHIẾU SÁNG & CAMERA TOÀN CẢNH ĐIỆN ẢNH
sun_data = bpy.data.lights.new('Sun_Dawn', 'SUN')
sun_data.energy = 5.0
sun_data.color = (1.0, 0.94, 0.85)
sun_obj = bpy.data.objects.new('Sun_Dawn', sun_data)
sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(45))
scene.collection.objects.link(sun_obj)

sky_data = bpy.data.lights.new('Sky_Fill', 'SUN')
sky_data.energy = 2.5
sky_data.color = (0.75, 0.88, 1.0)
sky_obj = bpy.data.objects.new('Sky_Fill', sky_data)
sky_obj.rotation_euler = (math.radians(-35), math.radians(-15), math.radians(-130))
scene.collection.objects.link(sky_obj)

cam_data = bpy.data.cameras.new('BattleCamera')
cam_data.lens = 38.0
cam_obj = bpy.data.objects.new('BattleCamera', cam_data)
cam_obj.location = (20.0, -18.0, 12.0)
dir_cam = Vector((0, 2.0, 1.5)) - cam_obj.location
cam_obj.rotation_euler = dir_cam.to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Lưu scene assembly
assembly_path = os.path.join(WS_DIR, 'scenes', 'dai_chien_bach_dang_assembly.blend')
bpy.ops.wm.save_as_mainfile(filepath=assembly_path)
print('Saved assembly:', assembly_path)

# Xuất GLB nướng animation
output_glb = os.path.join(WS_DIR, 'web3d_export', 'bach_dang_battle_optimized.glb')
bpy.ops.export_scene.gltf(
    filepath=output_glb,
    export_format='GLB',
    export_image_format='AUTO',
    export_animations=True,
    export_bake_animation=True,
    export_animation_mode='ACTIVE_ACTIONS',
    export_materials='EXPORT',
    export_cameras=True
)
print('Exported GLB:', output_glb)
