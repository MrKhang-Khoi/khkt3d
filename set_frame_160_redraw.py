import bpy

scene = bpy.context.scene
scene.frame_set(160)
bpy.context.view_layer.update()

for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

print("Frame 160 set and view layer updated!")
