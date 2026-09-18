"""
DỰNG ĐẶC TẢ BÃI CỌC BẠCH ĐẰNG SIÊU THỰC (THEO CHÍNH SỬ & TRANH SA BÀN BẢO TÀNG) - V4
Cân bằng màu sắc điện ảnh: Nước sông Bạch Đằng xanh rêu thẫm cuộn sóng bọt trắng,
Thân gỗ Lim đen mun sẫm màu, ánh sáng rim-light và lửa chiến rực rỡ.
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler, Matrix

engine_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\vietnam_naval_engine"
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from bach_dang_stake_generator import (
    create_photoreal_stake_materials,
    build_hyperrealistic_stake
)
from enemy_warship import create_southern_han_materials, build_southern_han_tower_warship

def main():
    print("=== BẮT ĐẦU DỰNG BÃI CỌC BẠCH ĐẰNG SIÊU THỰC V4 ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 1. BỘ VẬT LIỆU PBR ĐA TẦNG
    mats_stake = create_photoreal_stake_materials()

    bm_stakes = bmesh.new()

    # 2. BÃI CỌC: 3 CỌC CHỦ ĐẠO TIỀN CẢNH + 12 CỌC TRUNG & HẬU CẢNH
    hero_stakes = [
        # (pos, height, radius, tilt_y, tilt_x, seed, type)
        (Vector(( 0.02, -1.80, -0.65)), 2.88, 0.175,  6.5, -2.0, 101, 'iron_capped'), # Cọc giữa
        (Vector((-1.65, -1.20, -0.75)), 2.70, 0.150, 12.0, -7.0, 202, 'carved_wood'),  # Cọc trái
        (Vector(( 1.75, -1.10, -0.70)), 2.75, 0.165,  5.0,  5.5, 303, 'carved_wood'),  # Cọc phải
    ]

    field_stakes = [
        (Vector((-2.7,  0.9, -0.85)), 2.50, 0.13,  15.0, -9.0, 404, 'carved_wood'),
        (Vector((-1.0,  1.7, -0.80)), 2.65, 0.14,  13.0,  4.0, 505, 'iron_capped'),
        (Vector(( 1.0,  1.9, -0.80)), 2.55, 0.14,  17.0, -3.0, 606, 'carved_wood'),
        (Vector(( 2.6,  1.2, -0.85)), 2.45, 0.13,  14.0,  8.0, 707, 'iron_capped'),
        (Vector((-3.6,  2.9, -0.90)), 2.40, 0.12,  19.0,-12.0, 808, 'carved_wood'),
        (Vector((-2.0,  3.6, -0.85)), 2.60, 0.13,  11.0,  7.0, 909, 'iron_capped'),
        (Vector((-0.1,  3.9, -0.85)), 2.50, 0.13,  16.0, -5.0, 111, 'carved_wood'),
        (Vector(( 1.9,  3.5, -0.85)), 2.55, 0.14,  14.0,  6.0, 222, 'carved_wood'),
        (Vector(( 3.4,  3.0, -0.90)), 2.40, 0.12,  18.0, 11.0, 333, 'iron_capped'),
        (Vector((-1.4,  5.9, -0.95)), 2.35, 0.12,  21.0, -4.0, 444, 'carved_wood'),
        (Vector(( 0.6,  6.3, -0.95)), 2.40, 0.12,  17.0,  7.0, 555, 'iron_capped'),
        (Vector(( 2.3,  5.7, -0.95)), 2.30, 0.11,  19.0, -8.0, 666, 'carved_wood'),
    ]

    all_stakes = hero_stakes + field_stakes

    print(f"-> Đang dựng {len(all_stakes)} cọc Bạch Đằng siêu thực...")
    for pos, h, rad, ry, rx, sd, stype in all_stakes:
        build_hyperrealistic_stake(
            bm_stakes,
            pos=pos, height=h, base_radius=rad,
            tilt_angle_y=ry, tilt_angle_x=rx,
            seed=sd, stake_type=stype
        )

    mesh_stakes = bpy.data.meshes.new("BaiCoc_BachDang_Mesh")
    bm_stakes.to_mesh(mesh_stakes)
    bm_stakes.free()

    obj_stakes = bpy.data.objects.new("BaiCoc_BachDang_SieuThuc", mesh_stakes)
    obj_stakes.data.materials.append(mats_stake['lim_wood'])    # Index 0
    obj_stakes.data.materials.append(mats_stake['carved_wood']) # Index 1
    obj_stakes.data.materials.append(mats_stake['iron_cap'])    # Index 2
    bpy.context.collection.objects.link(obj_stakes)
    for p in obj_stakes.data.polygons: p.use_smooth = True

    # 3. MẶT NƯỚC SÔNG BẠCH ĐẰNG (ĐẬM MÀU XANH RÊU PHÙ SA + BỌT TRẮNG)
    print("-> Đang tạo mặt nước sông Bạch Đằng xanh rêu thẫm...")
    m_water = bpy.data.materials.new('Mat_Nuoc_SongBachDang_Realistic')
    m_water.diffuse_color = (0.015, 0.06, 0.065, 0.95)
    m_water.use_nodes = True
    nw_w = m_water.node_tree.nodes
    lw_w = m_water.node_tree.links
    nw_w.clear()

    out_wat = nw_w.new('ShaderNodeOutputMaterial')
    bsdf_wat = nw_w.new('ShaderNodeBsdfPrincipled')
    lw_w.new(bsdf_wat.outputs['BSDF'], out_wat.inputs['Surface'])

    # Sóng nước và bọt sóng cuộn
    tc_wat = nw_w.new('ShaderNodeTexCoord')
    noise_wave = nw_w.new('ShaderNodeTexNoise')
    noise_wave.inputs['Scale'].default_value = 7.0
    noise_wave.inputs['Detail'].default_value = 8.0
    noise_wave.inputs['Roughness'].default_value = 0.50
    lw_w.new(tc_wat.outputs['Object'], noise_wave.inputs['Vector'])

    cr_foam = nw_w.new('ShaderNodeValToRGB')
    cr_foam.color_ramp.elements[0].position = 0.58
    cr_foam.color_ramp.elements[0].color = (0.012, 0.050, 0.055, 1.0) # Sông Bạch Đằng xanh rêu sâu thẫm
    cr_foam.color_ramp.elements[1].position = 0.70
    cr_foam.color_ramp.elements[1].color = (0.90, 0.94, 0.95, 1.0) # Bọt trắng xóa
    lw_w.new(noise_wave.outputs['Fac'], cr_foam.inputs['Fac'])
    lw_w.new(cr_foam.outputs['Color'], bsdf_wat.inputs['Base Color'])

    bsdf_wat.inputs['Roughness'].default_value = 0.08
    bsdf_wat.inputs['Metallic'].default_value = 0.04
    if 'Transmission Weight' in bsdf_wat.inputs:
        bsdf_wat.inputs['Transmission Weight'].default_value = 0.40
    elif 'Transmission' in bsdf_wat.inputs:
        bsdf_wat.inputs['Transmission'].default_value = 0.40

    bump_wat = nw_w.new('ShaderNodeBump')
    bump_wat.inputs['Strength'].default_value = 0.35
    bump_wat.inputs['Distance'].default_value = 0.05
    lw_w.new(noise_wave.outputs['Fac'], bump_wat.inputs['Height'])
    lw_w.new(bump_wat.outputs['Normal'], bsdf_wat.inputs['Normal'])

    mesh_water = bpy.data.meshes.new("Water_Surface_Mesh")
    bm_wat = bmesh.new()
    bmesh.ops.create_grid(bm_wat, x_segments=64, y_segments=64, size=40.0)

    for v in bm_wat.verts:
        v.co.z = math.sin(v.co.x * 0.7 + v.co.y * 1.1) * 0.035 + math.cos(v.co.x * 1.3) * 0.02

    bm_wat.to_mesh(mesh_water)
    bm_wat.free()
    obj_wat = bpy.data.objects.new("MatNuoc_SongBachDang", mesh_water)
    obj_wat.location = (0, 0, 0.0)
    obj_wat.data.materials.append(m_water)
    bpy.context.collection.objects.link(obj_wat)
    for p in obj_wat.data.polygons: p.use_smooth = True

    # 4. HẬU CẢNH: THUYỀN CHIẾN NAM HÁN VỠ MẠN BỐC CHÁY
    print("-> Đang dựng thuyền giặc Nam Hán bốc cháy ở hậu cảnh...")
    mats_enemy = create_southern_han_materials()
    enemy_ship = build_southern_han_tower_warship(
        mats_enemy,
        location=Vector((-5.2, 9.8, -0.45)),
        rotation_z=math.radians(18)
    )
    enemy_ship.rotation_euler = Euler((math.radians(12), math.radians(-18), math.radians(26)))

    # 5. BẦU TRỜI & ÁNH SÁNG ĐIỆN ẢNH (TƯƠNG PHẢN CAO)
    print("-> Đang thiết lập bầu trời và ánh sáng...")
    if bpy.context.scene.world is None:
        world = bpy.data.worlds.new("World_BachDang")
        bpy.context.scene.world = world
    else:
        world = bpy.context.scene.world
    world.use_nodes = True
    nw_sky = world.node_tree.nodes
    lw_sky = world.node_tree.links
    nw_sky.clear()

    out_sky = nw_sky.new('ShaderNodeOutputWorld')
    bg_sky = nw_sky.new('ShaderNodeBackground')
    # Bầu trời khói lửa u tối, điểm sắc cam vàng mờ
    bg_sky.inputs['Color'].default_value = (0.10, 0.08, 0.09, 1.0)
    bg_sky.inputs['Strength'].default_value = 0.75
    lw_sky.new(bg_sky.outputs['Background'], out_sky.inputs['Surface'])

    # Mặt trời tà chiếu xiên (Rim Light) làm nổi bật thớ nứt nẻ
    sun_data = bpy.data.lights.new(name="Sun_Sunset_Rim", type='SUN')
    sun_data.energy = 5.2
    sun_data.color = (1.0, 0.88, 0.72)
    sun_data.angle = math.radians(1.5)
    sun_obj = bpy.data.objects.new(name="Sun_Sunset_Rim", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(52), math.radians(14), math.radians(45))
    bpy.context.collection.objects.link(sun_obj)

    # Ngọn lửa cháy từ chiến thuyền
    fire_data = bpy.data.lights.new(name="Fire_Glow_Light", type='POINT')
    fire_data.energy = 6500.0
    fire_data.color = (1.0, 0.38, 0.06)
    fire_data.shadow_soft_size = 1.8
    fire_obj = bpy.data.objects.new(name="Fire_Glow_Light", object_data=fire_data)
    fire_obj.location = (-4.0, 8.8, 3.8)
    bpy.context.collection.objects.link(fire_obj)

    # Ánh sáng dịu mát từ nền trời (Sky Fill)
    fill_data = bpy.data.lights.new(name="Sky_Fill", type='SUN')
    fill_data.energy = 1.2
    fill_data.color = (0.45, 0.60, 0.78)
    fill_obj = bpy.data.objects.new(name="Sky_Fill", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-32), math.radians(-18), math.radians(-42))
    bpy.context.collection.objects.link(fill_obj)

    # 6. CAMERA ĐẶC TẢ
    print("-> Đang căn chỉnh Camera...")
    cam_data = bpy.data.cameras.new("Hero_Camera_Stakes")
    cam_data.lens = 48.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 5.15
    cam_data.dof.aperture_fstop = 3.5

    cam_obj = bpy.data.objects.new("Hero_Camera_Stakes", cam_data)
    cam_obj.location = (0.05, -6.85, 1.55)
    cam_obj.rotation_euler = (math.radians(82.5), math.radians(0), math.radians(0))
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 7. XUẤT ẢNH & FILE BLEND
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    out_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    render_file = os.path.join(out_dir, "anh_dac_ta_coc_bach_dang_sieu_thuc.png")
    scene.render.filepath = render_file

    blend_file = os.path.join(out_dir, "bai_coc_bach_dang_sieu_thuc.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"-> Đã lưu file Blend tại: {blend_file}")

    print("-> Bắt đầu kết xuất ảnh 1080p...")
    bpy.ops.render.render(write_still=True)
    print(f"=== ĐÃ HOÀN TẤT RENDER ẢNH TẠI: {render_file} ===")

if __name__ == "__main__":
    main()
