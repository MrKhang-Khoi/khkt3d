import bpy

scene = bpy.context.scene
scene.frame_set(150)

# Set viewport camera to frame the entire battle scene (mountain, river, ships, stakes, forest)
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'PERSP'
            r3d.view_distance = 110.0
            r3d.view_location = (-10.0, -10.0, 5.0)
            import math
            from mathutils import Euler
            r3d.view_rotation = Euler((math.radians(64), 0.0, math.radians(45)), 'XYZ').to_quaternion()
print("Set to Frame 150 and adjusted Viewport!")
