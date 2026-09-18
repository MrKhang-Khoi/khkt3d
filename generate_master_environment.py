"""
PIPELINE ENVIRONMENT BUILDER: MẶT NƯỚC SÔNG BẠCH ĐẰNG & THỦY TRIỀU RÚT
Tạo tệp: environments/river_water_tide.blend
Chứa Collection: Collection_Environment_Water
Animation: Action_Tidal_Descent (Hạ mực nước triều từ +1.4m xuống -1.8m qua 300 frame)
Tuân thủ Mục II.4 trong QUY_TRINH_SAN_XUAT_3D_BACH_DANG_938.md
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector

def main():
    print("=== [PIPELINE] DỰNG MASTER ASSET: MẶT NƯỚC & THỦY TRIỀU ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    col = bpy.data.collections.new("Collection_Environment_Water")
    bpy.context.scene.collection.children.link(col)

    # 1. Vật liệu PBR Mặt nước sông Bạch Đằng (Đậm sắc xanh rêu trầm, gợn sóng, bọt trắng)
    m_water = bpy.data.materials.new('Mat_Nuoc_SongBachDang_Tide')
    m_water.diffuse_color = (0.015, 0.055, 0.065, 0.95)
    m_water.use_nodes = True
    nw = m_water.node_tree.nodes
    lw = m_water.node_tree.links
    nw.clear()

    out_wat = nw.new('ShaderNodeOutputMaterial')
    bsdf_wat = nw.new('ShaderNodeBsdfPrincipled')
    lw.new(bsdf_wat.outputs['BSDF'], out_wat.inputs['Surface'])

    # Coordinates & Noise cho sóng nước và bọt sóng cuộn
    tc_wat = nw.new('ShaderNodeTexCoord')
    noise_wave = nw.new('ShaderNodeTexNoise')
    noise_wave.inputs['Scale'].default_value = 8.0
    noise_wave.inputs['Detail'].default_value = 8.0
    noise_wave.inputs['Roughness'].default_value = 0.50
    lw.new(tc_wat.outputs['Object'], noise_wave.inputs['Vector'])

    cr_foam = nw.new('ShaderNodeValToRGB')
    cr_foam.color_ramp.elements[0].position = 0.58
    cr_foam.color_ramp.elements[0].color = (0.012, 0.048, 0.052, 1.0) # Sông Bạch Đằng xanh rêu sâu thẫm
    cr_foam.color_ramp.elements[1].position = 0.70
    cr_foam.color_ramp.elements[1].color = (0.88, 0.93, 0.95, 1.0) # Bọt trắng xóa
    lw.new(noise_wave.outputs['Fac'], cr_foam.inputs['Fac'])
    lw.new(cr_foam.outputs['Color'], bsdf_wat.inputs['Base Color'])

    bsdf_wat.inputs['Roughness'].default_value = 0.08
    bsdf_wat.inputs['Metallic'].default_value = 0.04
    if 'Transmission Weight' in bsdf_wat.inputs:
        bsdf_wat.inputs['Transmission Weight'].default_value = 0.45
    elif 'Transmission' in bsdf_wat.inputs:
        bsdf_wat.inputs['Transmission'].default_value = 0.45

    bump_wat = nw.new('ShaderNodeBump')
    bump_wat.inputs['Strength'].default_value = 0.35
    bump_wat.inputs['Distance'].default_value = 0.05
    lw.new(noise_wave.outputs['Fac'], bump_wat.inputs['Height'])
    lw.new(bump_wat.outputs['Normal'], bsdf_wat.inputs['Normal'])

    # 2. Lưới mặt phẳng nước sông 80m x 80m
    mesh_water = bpy.data.meshes.new("Mesh_River_Plane")
    bm_wat = bmesh.new()
    bmesh.ops.create_grid(bm_wat, x_segments=64, y_segments=64, size=80.0)

    for v in bm_wat.verts:
        v.co.z = math.sin(v.co.x * 0.5 + v.co.y * 0.8) * 0.04 + math.cos(v.co.x * 0.9) * 0.025

    bm_wat.to_mesh(mesh_water)
    bm_wat.free()

    obj_water = bpy.data.objects.new("River_Water_Plane", mesh_water)
    obj_water.data.materials.append(m_water)
    col.objects.link(obj_water)
    for p in obj_water.data.polygons:
        p.use_smooth = True

    # 3. GÁN ANIMATION: ACTION_TIDAL_DESCENT (300 FRAMES)
    # Mô phỏng mực nước rút từ +1.4m (triều cường ngập bãi cọc) xuống -1.8m (triều kiệt trơ bãi cọc)
    print("-> Đang nướng Action_Tidal_Descent (Hạ mực nước triều)...")
    anim_data = obj_water.animation_data_create()
    action = bpy.data.actions.new(name="Action_Tidal_Descent")
    anim_data.action = action

    for f in range(1, 301):
        # Đường cong rút triều tự nhiên (S-curve tanh/smoothstep)
        prog = (f - 1) / 299.0 # 0 -> 1
        # Bắt đầu cao (+1.4m), hạ dần, rút nhanh nhất ở khoảng giữa (f: 90 - 210), rồi ổn định ở mức kiệt (-1.8m)
        s_curve = 3.0 * (prog ** 2) - 2.0 * (prog ** 3)
        z_level = 1.40 - s_curve * 3.20 # Từ +1.4m -> -1.80m

        obj_water.location = (0.0, 0.0, z_level)
        obj_water.keyframe_insert(data_path="location", frame=f)

    out_file = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\environments\river_water_tide.blend"
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    print(f"=== ĐÃ TẠO THÀNH CÔNG MASTER ASSET: {out_file} ===")

if __name__ == "__main__":
    main()
