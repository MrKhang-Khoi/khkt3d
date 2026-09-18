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
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Ambient World Lighting
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.55, 0.65, 0.75, 1.0)
        bg.inputs["Strength"].default_value = 1.2

    mats = create_southern_han_materials()
    ship = build_southern_han_tower_warship(mats, location=Vector((0, 0, 0)), rotation_z=0.0)

    # Sun Light chiếu thẳng vào sườn tàu
    sun_data = bpy.data.lights.new(name="Sun_Side", type='SUN')
    sun_data.energy = 5.0
    sun_data.color = (1.0, 0.98, 0.92)
    sun_obj = bpy.data.objects.new(name="Sun_Side", object_data=sun_data)
    sun_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(25))
    bpy.context.collection.objects.link(sun_obj)

    # Fill Light
    fill_data = bpy.data.lights.new(name="Fill_Side", type='SUN')
    fill_data.energy = 2.5
    fill_data.color = (0.8, 0.9, 1.0)
    fill_obj = bpy.data.objects.new(name="Fill_Side", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-15), math.radians(-40))
    bpy.context.collection.objects.link(fill_obj)

    # Camera đặt ở khoảng cách 15m nhìn thẳng vào sườn lầu đài (Framing giống hệt ảnh người dùng)
    cam_data = bpy.data.cameras.new("Camera_CloseUp")
    cam_data.lens = 42.0
    cam_obj = bpy.data.objects.new("Camera_CloseUp", cam_data)
    cam_obj.location = (-2.5, -15.5, 4.6)
    cam_obj.rotation_euler = (math.radians(87), math.radians(0), math.radians(0))
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    out_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    render_file = os.path.join(out_dir, "anh_so_sanh_can_canh_lau_dai.png")
    scene.render.filepath = render_file

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out_dir, "lau_thuyen_nam_han_can_canh.blend"))
    bpy.ops.render.render(write_still=True)
    print(f" ĐÃ RENDER ẢNH CẬN CẢNH LÂU ĐÀI TẠI: {render_file}")

if __name__ == "__main__":
    main()
