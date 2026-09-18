import bpy
import math
from mathutils import Euler

def capture_phase(frame_num, img_path):
    scene = bpy.context.scene
    scene.frame_set(frame_num)
    
    # Adjust 3D viewport
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                r3d = area.spaces.active.region_3d
                r3d.view_perspective = 'PERSP'
                r3d.view_distance = 80.0
                r3d.view_location = (-5.0, -10.0, 3.0)
                r3d.view_rotation = Euler((math.radians(64), 0.0, math.radians(38)), 'XYZ').to_quaternion()

    # Capture viewport
    area_v3d = None
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area_v3d = area
                break
    if area_v3d:
        with bpy.context.temp_override(area=area_v3d):
            bpy.ops.screen.screenshot_area(filepath=img_path)
    print(f"Captured frame {frame_num} -> {img_path}")

capture_phase(1, r'C:\Users\HPZBook\Desktop\TEST_BLENDER\phase1_trieu_dang.png')
capture_phase(85, r'C:\Users\HPZBook\Desktop\TEST_BLENDER\phase2_truy_kich.png')
capture_phase(160, r'C:\Users\HPZBook\Desktop\TEST_BLENDER\phase3_dam_coc.png')
capture_phase(240, r'C:\Users\HPZBook\Desktop\TEST_BLENDER\phase4_phan_cong.png')
