"""
PIPELINE ASSEMBLY: ĐẠI CHIẾN BẠCH ĐẰNG 938 ASSEMBLY SCENE
Lắp ráp sân khấu tổng thể bằng Linking và Library Overrides từ các Master Assets:
- assets/props/coc_bach_dang_master.blend
- environments/river_water_tide.blend
- assets/ships/thuyen_ta_ngoquyen_master.blend
- assets/ships/lau_thuyen_namhan_master.blend
Tuân thủ Mục III & Mục IV trong QUY_TRINH_SAN_XUAT_3D_BACH_DANG_938.md
"""

import bpy
import math
import os
import sys
from mathutils import Vector, Euler

def main():
    print("=== [PIPELINE] LẮP RÁP SÂN KHẤU TỔNG THỂ (ASSEMBLY SCENE) ===")
    base_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 300
    scene.render.fps = 24

    # 1. LIÊN KẾT BÃI CỌC BẠCH ĐẰNG (LINK COLLECTION)
    coc_path = os.path.join(base_dir, "assets", "props", "coc_bach_dang_master.blend")
    with bpy.data.libraries.load(coc_path, link=True) as (data_from, data_to):
        data_to.collections = ["Collection_Coc_BachDang"]
    col_coc = data_to.collections[0]
    inst_coc = bpy.data.objects.new("Inst_Coc_BachDang", None)
    inst_coc.instance_type = 'COLLECTION'
    inst_coc.instance_collection = col_coc
    scene.collection.objects.link(inst_coc)
    print("-> Đã Link Collection_Coc_BachDang")

    # 2. LIÊN KẾT MẶT NƯỚC SÔNG & THỦY TRIỀU
    water_path = os.path.join(base_dir, "environments", "river_water_tide.blend")
    with bpy.data.libraries.load(water_path, link=True) as (data_from, data_to):
        data_to.collections = ["Collection_Environment_Water"]
    col_wat = data_to.collections[0]
    inst_wat = bpy.data.objects.new("Inst_Water_Tide", None)
    inst_wat.instance_type = 'COLLECTION'
    inst_wat.instance_collection = col_wat
    scene.collection.objects.link(inst_wat)
    # Tạo Library Override để nhận chuyển động triều rút
    override_wat = inst_wat.override_hierarchy_create(scene, bpy.context.view_layer)
    print("-> Đã Link & Override Collection_Environment_Water")

    # 3. LIÊN KẾT THUYỀN CHIẾN ĐẠI VIỆT (THUYỀN TA)
    thuyen_path = os.path.join(base_dir, "assets", "ships", "thuyen_ta_ngoquyen_master.blend")
    with bpy.data.libraries.load(thuyen_path, link=True) as (data_from, data_to):
        data_to.collections = ["Collection_Thuyen_Ta"]
    col_thuyen = data_to.collections[0]
    inst_thuyen = bpy.data.objects.new("Inst_Thuyen_Ta", None)
    inst_thuyen.instance_type = 'COLLECTION'
    inst_thuyen.instance_collection = col_thuyen
    scene.collection.objects.link(inst_thuyen)
    override_thuyen = inst_thuyen.override_hierarchy_create(scene, bpy.context.view_layer)
    print("-> Đã Link & Override Collection_Thuyen_Ta")

    # 4. LIÊN KẾT LÂU THUYỀN NAM HÁN (THUYỀN ĐỊCH)
    lau_path = os.path.join(base_dir, "assets", "ships", "lau_thuyen_namhan_master.blend")
    with bpy.data.libraries.load(lau_path, link=True) as (data_from, data_to):
        data_to.collections = ["Collection_Lau_Thuyen_NamHan"]
    col_lau = data_to.collections[0]
    inst_lau = bpy.data.objects.new("Inst_Lau_Thuyen_NamHan", None)
    inst_lau.instance_type = 'COLLECTION'
    inst_lau.instance_collection = col_lau
    scene.collection.objects.link(inst_lau)
    override_lau = inst_lau.override_hierarchy_create(scene, bpy.context.view_layer)
    print("-> Đã Link & Override Collection_Lau_Thuyen_NamHan")

    # 5. BẦU TRỜI & ÁNH SÁNG ĐIỆN ẢNH (CINEMATIC BATTLE ATMOSPHERE)
    world = bpy.data.worlds.new("World_DaiChien_BachDang")
    scene.world = world
    world.use_nodes = True
    nw_sky = world.node_tree.nodes
    lw_sky = world.node_tree.links
    nw_sky.clear()

    out_sky = nw_sky.new('ShaderNodeOutputWorld')
    bg_sky = nw_sky.new('ShaderNodeBackground')
    bg_sky.inputs['Color'].default_value = (0.10, 0.08, 0.09, 1.0)
    bg_sky.inputs['Strength'].default_value = 0.85
    lw_sky.new(bg_sky.outputs['Background'], out_sky.inputs['Surface'])

    # Ánh nắng chiều Đông Bắc (Sun Rim Light)
    sun_data = bpy.data.lights.new(name="Sun_Winter_Rim", type='SUN')
    sun_data.energy = 5.5
    sun_data.color = (1.0, 0.88, 0.72)
    sun_obj = bpy.data.objects.new(name="Sun_Winter_Rim", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(52), math.radians(14), math.radians(45))
    scene.collection.objects.link(sun_obj)

    # Lửa chiến hạm bốc cháy
    fire_data = bpy.data.lights.new(name="Fire_Ship_Glow", type='POINT')
    fire_data.energy = 8000.0
    fire_data.color = (1.0, 0.35, 0.05)
    fire_obj = bpy.data.objects.new(name="Fire_Ship_Glow", object_data=fire_data)
    fire_obj.location = (-1.0, 3.5, 4.0)
    scene.collection.objects.link(fire_obj)

    # 6. CAMERA ĐIỆN ẢNH THEO DÕI TOÀN CẢNH TRẬN ĐÁNH
    cam_data = bpy.data.cameras.new("Main_Battle_Camera")
    cam_data.lens = 42.0
    cam_obj = bpy.data.objects.new("Main_Battle_Camera", cam_data)
    # Góc máy từ trên cao nhìn bao quát bãi cọc và hai cánh thuyền
    cam_obj.location = (14.0, -18.0, 11.0)
    cam_obj.rotation_euler = (math.radians(65.0), math.radians(0), math.radians(35.0))
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 7. LƯU TỆP SÂN KHẤU TỔNG THỂ
    scene_file = os.path.join(base_dir, "scenes", "dai_chien_bach_dang_assembly.blend")
    bpy.ops.wm.save_as_mainfile(filepath=scene_file)
    print(f"=== [PIPELINE] ĐÃ LẮP RÁP THÀNH CÔNG SÂN KHẤU TỔNG THỂ: {scene_file} ===")

if __name__ == "__main__":
    main()
