"""
PIPELINE ASSET BUILDER: BÃI CỌC BẠCH ĐẰNG MASTER ASSET (ĐÃ TỰ ĐỘNG SỬA ĐẠT CHUẨN)
Tạo tệp: assets/props/coc_bach_dang_master.blend
Chứa Collection: Collection_Coc_BachDang
Gồm 3 vật thể Master độc lập:
  1. Coc_Chinh_BitSat (Hero stake - Bịt sắt rèn, đinh tán)
  2. Coc_Nghieng_GoLim (Cọc nghiêng - Lõi gỗ vạt rìu đẽo)
  3. Coc_Gay_MuiSat (Cọc phong hóa - Chóp sắt nhọn)
Kèm hệ thống Camera & Lighting LookDev trung tính 3 điểm.
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler, Matrix

engine_dir = rC:\Users\HPZBook\Desktop\TEST_BLENDER\vietnam_naval_engine
if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from bach_dang_stake_generator import (
    create_photoreal_stake_materials,
    build_hyperrealistic_stake
)

def setup_lookdev_studio(target_loc=Vector((0, 0, 1.2))):
    key_data = bpy.data.lights.new(LookDev_KeyLight, 'SUN')
    key_data.energy = 4.5
    key_data.color = (1.0, 0.97, 0.92)
    key_obj = bpy.data.objects.new(LookDev_KeyLight, key_data)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(40))
    bpy.context.scene.collection.objects.link(key_obj)

    fill_data = bpy.data.lights.new(LookDev_FillLight, 'SUN')
    fill_data.energy = 2.2
    fill_data.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new(LookDev_FillLight, fill_data)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-20), math.radians(-120))
    bpy.context.scene.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(LookDev_RimLight, 'SUN')
    rim_data.energy = 2.8
    rim_data.color = (0.9, 0.95, 1.0)
    rim_obj = bpy.data.objects.new(LookDev_RimLight, rim_data)
    rim_obj.rotation_euler = (math.radians(-60), 0, math.radians(180))
    bpy.context.scene.collection.objects.link(rim_obj)

    cam_data = bpy.data.cameras.new(LookDev_Camera)
    cam_data.lens = 50.0
    cam_obj = bpy.data.objects.new(LookDev_Camera, cam_data)
    cam_obj.location = (3.6, -4.2, 2.6)
    direction = target_loc - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

def create_single_master_prop(col, mats, name, pos, height, radius, tilt_y, tilt_x, seed, stype):
    bm = bmesh.new()
    build_hyperrealistic_stake(
        bm,
        pos=Vector((0, 0, 0)),
        height=height,
        base_radius=radius,
        tilt_angle_y=tilt_y,
        tilt_angle_x=tilt_x,
        seed=seed,
        stake_type=stype
    )
    mesh = bpy.data.meshes.new(fMesh_{name})
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = pos
    obj.data.materials.append(mats['lim_wood'])
    obj.data.materials.append(mats['carved_wood'])
    obj.data.materials.append(mats['iron_cap'])

    for p in obj.data.polygons:
        p.use_smooth = True

    col.objects.link(obj)
    return obj

def main():
    print(=== [PIPELINE REBUILD] DỰNG LẠI MASTER ASSET: CỌC BẠCH ĐẰNG ===)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    col = bpy.data.collections.new(Collection_Coc_BachDang)
    bpy.context.scene.collection.children.link(col)

    mats_stake = create_photoreal_stake_materials()

    obj_hero = create_single_master_prop(
        col, mats_stake,
        name=Coc_Chinh_BitSat,
        pos=Vector((0.0, 0.0, 0.0)),
        height=3.10, base_radius=0.18,
        tilt_y=5.0, tilt_x=-2.0,
        seed=101, stype='iron_capped'
    )

    obj_tilted = create_single_master_prop(
        col, mats_stake,
        name=Coc_Nghieng_GoLim,
        pos=Vector((-1.2, 0.4, 0.0)),
        height=2.75, base_radius=0.16,
        tilt_y=14.0, tilt_x=-7.0,
        seed=202, stype='carved_wood'
    )

    obj_weathered = create_single_master_prop(
        col, mats_stake,
        name=Coc_Gay_MuiSat,
        pos=Vector((1.3, 0.5, 0.0)),
        height=2.60, base_radius=0.15,
        tilt_y=12.0, tilt_x=6.0,
        seed=303, stype='iron_capped'
    )

    bm_mud = bmesh.new()
    bmesh.ops.create_grid(bm_mud, x_segments=8, y_segments=8, size=6.0)
    mesh_mud = bpy.data.meshes.new(Mesh_Bun_DaySong)
    bm_mud.to_mesh(mesh_mud)
    bm_mud.free()
    obj_mud = bpy.data.objects.new(DaySong_BunLay, mesh_mud)
    obj_mud.location = (0, 0, 0.0)
    obj_mud.data.materials.append(mats_stake['lim_wood'])
    bpy.context.scene.collection.objects.link(obj_mud)

    setup_lookdev_studio(target_loc=Vector((0, 0.2, 1.4)))

    out_file = rC:\Users\HPZBook\Desktop\TEST_BLENDER\assets\props\coc_bach_dang_master.blend
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    print(f=== ĐÃ TÁI TẠO THÀNH CÔNG MASTER ASSET CỌC: {out_file} ===)

if __name__ == __main__:
    main()
