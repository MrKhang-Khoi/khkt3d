import bpy

scene = bpy.context.scene
scene.frame_set(140)
bpy.context.view_layer.update()

for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()
            with bpy.context.temp_override(window=window, area=area):
                bpy.ops.screen.screenshot_area(filepath=r'C:\Users\HPZBook\Desktop\TEST_BLENDER\anh_step2_viewport_f140.png')
            print("Captured anh_step2_viewport_f140.png successfully!")
            break
