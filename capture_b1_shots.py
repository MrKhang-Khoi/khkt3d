import bpy

def capture_frame(f_num, out_path):
    scene = bpy.context.scene
    scene.frame_set(f_num)
    bpy.context.view_layer.update()
    
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
                with bpy.context.temp_override(window=window, area=area):
                    bpy.ops.screen.screenshot_area(filepath=out_path)
                print(f"Captured frame {f_num} to {out_path}")
                return

capture_frame(1, r'C:\Users\HPZBook\Desktop\TEST_BLENDER\b1_frame_1.png')
capture_frame(45, r'C:\Users\HPZBook\Desktop\TEST_BLENDER\b1_frame_45.png')
