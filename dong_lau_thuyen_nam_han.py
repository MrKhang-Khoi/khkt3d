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

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def build_river(mat):
    mesh = bpy.data.meshes.new("Song_Nuoc_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=32, y_segments=32, size=50.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Song_BachDang_MatNuoc", mesh)
    obj.location = (0, 0, 0.0)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def setup_lighting_and_camera():
    sun_data = bpy.data.lights.new(name="Sun_NamHan_Dawn", type='SUN')
    sun_data.energy = 5.5
    sun_data.color = (1.0, 0.95, 0.88)
    sun_data.angle = math.radians(2.5)
    sun_obj = bpy.data.objects.new(name="Sun_NamHan_Dawn", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(40), math.radians(18), math.radians(65))
    bpy.context.collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new(name="Sky_Fill_Light", type='SUN')
    fill_data.energy = 2.5
    fill_data.color = (0.75, 0.85, 0.96)
    fill_obj = bpy.data.objects.new(name="Sky_Fill_Light", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-40), math.radians(-25), math.radians(-30))
    bpy.context.collection.objects.link(fill_obj)

    # Camera góc 3/4 bao quát toàn bộ con tàu khổng lồ và 2 tầng lâu đài
    cam_data = bpy.data.cameras.new("CinemaCamera_Enemy")
    cam_data.lens = 38.0
    cam_obj = bpy.data.objects.new("CinemaCamera_Enemy", cam_data)
    cam_obj.location = (24.0, -22.0, 11.5)
    cam_obj.rotation_euler = (math.radians(67), math.radians(0), math.radians(48))
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

def main():
    print("=== DỰNG LÂU THUYỀN CHIẾN HẠM NAM HÁN (LƯU HOẰNG THÁO 938) ===")
    reset_scene()

    mats = create_southern_han_materials()

    # Thêm vật liệu nước sông
    m_water = bpy.data.materials.new('Mat_SongBachDang_Nuoc')
    m_water.diffuse_color = (0.08, 0.22, 0.22, 0.8)
    m_water.use_nodes = True
    bsdf_w = m_water.node_tree.nodes.get('Principled BSDF')
    if bsdf_w:
        bsdf_w.inputs['Base Color'].default_value = (0.05, 0.18, 0.18, 1.0)
        bsdf_w.inputs['Roughness'].default_value = 0.04
        bsdf_w.inputs['Metallic'].default_value = 0.1
        if 'Transmission Weight' in bsdf_w.inputs:
            bsdf_w.inputs['Transmission Weight'].default_value = 0.85
        elif 'Transmission' in bsdf_w.inputs:
            bsdf_w.inputs['Transmission'].default_value = 0.85
        if 'IOR' in bsdf_w.inputs:
            bsdf_w.inputs['IOR'].default_value = 1.333

    enemy_ship = build_southern_han_tower_warship(mats, location=Vector((0, 0, 0)), rotation_z=0.0)
    river = build_river(m_water)
    setup_lighting_and_camera()

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

    out_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    blend_path = os.path.join(out_dir, "lau_thuyen_nam_han_938.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f" ĐÃ LƯU LÂU THUYỀN NAM HÁN TẠI: {blend_path}")

    # Render ảnh chất lượng 1080p kiểm chứng
    render_path = os.path.join(out_dir, "anh_lau_thuyen_nam_han_chi_tiet.png")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = render_path
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH LÂU THUYỀN TẠI: {render_path}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
