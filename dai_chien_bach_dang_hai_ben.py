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
from viet_ship_builder import build_vietnamese_warship, build_historic_stakes
from enemy_warship import create_southern_han_materials, build_southern_han_tower_warship

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def build_wide_river(mat):
    mesh = bpy.data.meshes.new("Song_BachDang_Wide_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=48, y_segments=48, size=80.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("Song_BachDang_MatNuoc_Rong", mesh)
    obj.location = (0, 0, -0.05)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def setup_battle_lighting_and_camera():
    sun_data = bpy.data.lights.new(name="Sun_Dawn_Light", type='SUN')
    sun_data.energy = 5.5
    sun_data.color = (1.0, 0.95, 0.88)
    sun_data.angle = math.radians(2.5)
    sun_obj = bpy.data.objects.new(name="Sun_Dawn_Light", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(42), math.radians(15), math.radians(60))
    bpy.context.collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new(name="Sky_Fill_Light", type='SUN')
    fill_data.energy = 2.5
    fill_data.color = (0.75, 0.85, 0.96)
    fill_obj = bpy.data.objects.new(name="Sky_Fill_Light", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-40), math.radians(-25), math.radians(-30))
    bpy.context.collection.objects.link(fill_obj)

    cam_data = bpy.data.cameras.new("CinemaCamera_Battle")
    cam_data.lens = 32.0
    cam_obj = bpy.data.objects.new("CinemaCamera_Battle", cam_data)
    # Camera góc rộng trên cao nhìn xéo từ phía sau-bên mạn thuyền Việt thấy Lâu thuyền Nam Hán đang đâm vào bãi cọc
    cam_obj.location = (25.0, -26.0, 14.5)
    cam_obj.rotation_euler = (math.radians(65), math.radians(0), math.radians(45))
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

def main():
    print("=== DỰNG TOÀN CẢNH ĐẠI CHIẾN BẠCH ĐẰNG 938: THUYỀN TA ĐỐI ĐẦU THUYỀN ĐỊCH ===")
    reset_scene()

    mats_vn = get_vietnam_naval_materials()
    mats_enemy = create_southern_han_materials()

    # 1. Thuyền Ta: Thuyền chiến Ngô Quyền buồm cánh dơi nan tre củ nâu (Nhỏ gọn, mớn nước nông, cơ động)
    vn_ship = build_vietnamese_warship(mats_vn)
    vn_ship.location = Vector((9.0, -4.5, 0.0))
    vn_ship.rotation_euler = Euler((0, 0, math.radians(-15)))

    # 2. Thuyền Địch: Lâu thuyền Nam Hán Lưu Hoằng Tháo (Khổng lồ, mớn nước sâu 2.4m, 2 tầng lâu đài, buồm nan chữ nhật)
    # Đang lao vào vùng nước hiểm và chạm cọc
    enemy_ship = build_southern_han_tower_warship(mats_enemy, location=Vector((-12.0, 5.0, -0.2)), rotation_z=math.radians(-8))

    # 3. Trận địa bãi cọc gỗ lim bịt sắt đón ngọn nước thủy triều rút
    stakes = build_historic_stakes(mats_vn['wood_lim'], mats_vn['iron'])
    stakes.location = Vector((-1.0, 0, 0))

    # Thêm hàng cọc thứ 2 đâm vào mạn thuyền giặc
    stakes2 = build_historic_stakes(mats_vn['wood_lim'], mats_vn['iron'])
    stakes2.location = Vector((-7.5, 3.5, 0))

    # 4. Mặt nước sông Bạch Đằng
    river = build_wide_river(mats_vn['river'])

    setup_battle_lighting_and_camera()

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

    out_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    blend_path = os.path.join(out_dir, "dai_chien_bach_dang_hai_ben.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f" ĐÃ LƯU ĐẠI CHIẾN BẠCH ĐẰNG TẠI: {blend_path}")

    # Render ảnh chất lượng 1080p kiểm chứng
    render_path = os.path.join(out_dir, "anh_dai_chien_bach_dang_hai_ben.png")
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = render_path
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH ĐẠI CHIẾN TẠI: {render_path}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
