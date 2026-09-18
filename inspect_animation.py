import bpy

scene = bpy.context.scene
print('Frame start:', scene.frame_start, 'Frame end:', scene.frame_end, 'Current:', scene.frame_current, 'FPS:', scene.render.fps)

# Check animation data on roots
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        act = o.animation_data.action
        print(f'{o.name}: Action {act.name}, range: {act.frame_range[0]} - {act.frame_range[1]}')
