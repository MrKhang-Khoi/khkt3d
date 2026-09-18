"""
PIPELINE ASSET BUILDER: LÂU THUYỀN NAM HÁN MASTER ASSET
Tạo tệp: assets/ships/lau_thuyen_namhan_master.blend
Chứa Collection: Collection_Lau_Thuyen_NamHan
Animation: Action_Lau_Thuyen_CrashSink (Tiến công -> Đâm cọc hãm tốc -> Lật nghiêng chìm)
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

from enemy_warship import create_southern_han_materials, build_southern_han_tower_warship

def main():
    print("=== [PIPELINE] DỰNG MASTER ASSET: LÂU THUYỀN NAM HÁN ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    col = bpy.data.collections.new("Collection_Lau_Thuyen_NamHan")
    bpy.context.scene.collection.children.link(col)

    mats_enemy = create_southern_han_materials()

    # Dựng lâu thuyền tại gốc tọa độ
    ship_root = build_southern_han_tower_warship(mats_enemy, location=Vector((0, 0, 0)), rotation_z=0.0)

    # Đảm bảo toàn bộ hệ thống object thuộc Collection_Lau_Thuyen_NamHan
    def link_hierarchy(ob):
        if ob.name not in col.objects:
            col.objects.link(ob)
        for child in ob.children:
            link_hierarchy(child)

    link_hierarchy(ship_root)

    # GÁN ANIMATION: ACTION_LAU_THUYEN_CRASHSINK (300 FRAMES)
    print("-> Đang nướng Action_Lau_Thuyen_CrashSink (Tiến -> Đâm cọc -> Nghiêng lật)...")
    anim_data = ship_root.animation_data_create()
    action = bpy.data.actions.new(name="Action_Lau_Thuyen_CrashSink")
    anim_data.action = action

    for f in range(1, 301):
        t = f / 24.0

        if f < 105:
            # Giai đoạn 1: Đuổi theo thuyền Đại Việt với vận tốc nhanh
            # Y từ 16.0m xuống 4.0m
            progress = f / 105.0
            y_pos = 16.0 - progress * 12.0
            x_pos = -1.5 + progress * 0.5
            z_pos = math.sin(t * 2.2) * 0.05
            pitch = math.sin(t * 1.8) * math.radians(1.5)
            roll = math.cos(t * 1.5) * math.radians(1.2)
            yaw = math.radians(180) # Hướng mũi xuôi theo dòng triều

        elif f < 135:
            # Giai đoạn 2: Đâm trúng bãi cọc ngầm tại Frame 110!
            # Mũi tàu khựng lại đột ngột, dềnh lên rồi chao nghiêng dữ dội
            crash_t = (f - 105) / 30.0 # 0 -> 1
            y_pos = 4.0 - crash_t * 0.8 # Quán tính đẩy nhẹ thêm 80cm rồi dừng hẳn
            x_pos = -1.0
            # Mũi dềnh lên rồi sụt xuống
            z_pos = math.sin(crash_t * math.pi) * 0.22 - crash_t * 0.35
            pitch = -math.sin(crash_t * math.pi) * math.radians(4.0) + crash_t * math.radians(6.0)
            # Nghiêng mạn lệch tâm do cọc đâm toác lườn
            roll = crash_t * math.radians(24.0)
            yaw = math.radians(180) + crash_t * math.radians(12.0) # Thân tàu bị xoay lệch

        else:
            # Giai đoạn 3: Mắc cạn vỡ mạn, nước tràn vào chìm dần, triều rút cạn
            settle_t = (f - 135) / 165.0 # 0 -> 1
            y_pos = 3.2
            x_pos = -1.0
            z_pos = -0.35 - settle_t * 0.45 # Chìm sâu thêm 45cm
            pitch = math.radians(6.0) + math.sin(t * 1.0) * math.radians(0.5) * (1.0 - settle_t)
            roll = math.radians(24.0) + settle_t * math.radians(3.5) # Nghiêng tới 27.5 độ!
            yaw = math.radians(192)

        ship_root.location = (x_pos, y_pos, z_pos)
        ship_root.rotation_euler = Euler((pitch, roll, yaw))

        ship_root.keyframe_insert(data_path="location", frame=f)
        ship_root.keyframe_insert(data_path="rotation_euler", frame=f)

    out_file = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships\lau_thuyen_namhan_master.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    print(f"=== ĐÃ TẠO THÀNH CÔNG MASTER ASSET: {out_file} ===")

if __name__ == "__main__":
    main()
