"""
PIPELINE ASSET BUILDER: THUYỀN CHIẾN ĐẠI VIỆT (NGÔ QUYỀN) MASTER ASSET
Tạo tệp: assets/ships/thuyen_ta_ngoquyen_master.blend
Chứa Collection: Collection_Thuyen_Ta
Animation: Action_Thuyen_Ta_Float (Chuyển động dập dềnh sóng & lướt nhử địch)
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

from pbr_materials import get_vietnam_naval_materials
from batten_sail import create_vietnamese_batwing_sail

def main():
    print("=== [PIPELINE] DỰNG MASTER ASSET: THUYỀN CHIẾN ĐẠI VIỆT ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    col = bpy.data.collections.new("Collection_Thuyen_Ta")
    bpy.context.scene.collection.children.link(col)

    mats = get_vietnam_naval_materials()

    # Tạo Empty Root điều khiển toàn bộ thuyền
    root_ship = bpy.data.objects.new("Thuyen_Ta_Master_Root", None)
    col.objects.link(root_ship)

    # 1. Thân thuyền đáy nông lướt sóng
    mesh_hull = bpy.data.meshes.new("Mesh_Hull_DaiViet")
    bm_hull = bmesh.new()

    stations_x = [-4.5, -3.8, -2.8, -1.5,  0.0,  1.5,  2.8,  3.8,  4.5]
    beam_w     = [ 0.12, 0.55, 0.88, 1.05, 1.10, 1.05, 0.88, 0.55, 0.12]
    sheer_z    = [ 0.95, 0.62, 0.44, 0.35, 0.32, 0.35, 0.44, 0.62, 0.95]
    keel_z     = [-0.20,-0.45,-0.58,-0.65,-0.68,-0.65,-0.58,-0.45,-0.20]

    rings = []
    for i in range(len(stations_x)):
        x, bw, sz, kz = stations_x[i], beam_w[i], sheer_z[i], keel_z[i]
        pts = [
            Vector((x, -bw, sz)),
            Vector((x, -bw * 0.92, kz + (sz-kz)*0.45)),
            Vector((x, -bw * 0.50, kz + (sz-kz)*0.10)),
            Vector((x,  0.0,       kz)),
            Vector((x,  bw * 0.50, kz + (sz-kz)*0.10)),
            Vector((x,  bw * 0.92, kz + (sz-kz)*0.45)),
            Vector((x,  bw, sz))
        ]
        rings.append([bm_hull.verts.new(p) for p in pts])

    for i in range(len(rings) - 1):
        r1, r2 = rings[i], rings[i+1]
        for j in range(len(r1) - 1):
            bm_hull.faces.new([r1[j], r1[j+1], r2[j+1], r2[j]])

    bm_hull.to_mesh(mesh_hull)
    bm_hull.free()

    obj_hull = bpy.data.objects.new("Than_Thuyen_GoLim", mesh_hull)
    obj_hull.parent = root_ship
    obj_hull.data.materials.append(mats['wood_hull'])
    col.objects.link(obj_hull)
    for p in obj_hull.data.polygons:
        p.use_smooth = True

    # 2. Cột buồm và Buồm cánh dơi nan tre củ nâu
    create_vietnamese_batwing_sail(
        mats, parent_obj=root_ship,
        mast_pos=Vector((0.6, 0, 0)),
        mast_height=4.8,
        sail_angle_deg=25.0
    )

    # Đưa tất cả các object con vào collection
    def link_hierarchy(ob):
        if ob.name not in col.objects:
            col.objects.link(ob)
        for child in ob.children:
            link_hierarchy(child)

    link_hierarchy(root_ship)

    # 3. GÁN ANIMATION: ACTION_THUYEN_TA_FLOAT (300 FRAMES)
    # Thuyền lướt nhẹ, dập dềnh sóng nước (Pitch, Roll, Heave)
    print("-> Đang nướng Action_Thuyen_Ta_Float (Pitch/Roll/Heave)...")
    anim_data = root_ship.animation_data_create()
    action = bpy.data.actions.new(name="Action_Thuyen_Ta_Float")
    anim_data.action = action

    for f in range(1, 301):
        t = f / 24.0 # Thời gian giây (24 FPS)

        # Di chuyển lướt rút lui qua bãi cọc nhử địch
        y_pos = -8.0 - (f / 300.0) * 14.0 # từ -8m tới -22m
        # Sóng dập dềnh
        z_heave = math.sin(t * 2.8) * 0.08
        pitch = math.sin(t * 2.4) * math.radians(2.8)
        roll = math.cos(t * 1.9) * math.radians(2.2)

        root_ship.location = (0.5, y_pos, z_heave)
        root_ship.rotation_euler = Euler((pitch, roll, math.radians(-5)))

        root_ship.keyframe_insert(data_path="location", frame=f)
        root_ship.keyframe_insert(data_path="rotation_euler", frame=f)

    out_file = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships\thuyen_ta_ngoquyen_master.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    print(f"=== ĐÃ TẠO THÀNH CÔNG MASTER ASSET: {out_file} ===")

if __name__ == "__main__":
    main()
