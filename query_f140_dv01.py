import bpy

scene = bpy.context.scene
scene.frame_set(140)
bpy.context.view_layer.update()

root_dv = bpy.data.objects.get('Root_DV_01_SoaiTienPhong_Ta')
if root_dv:
    pos = root_dv.matrix_world.translation
    rot = root_dv.rotation_euler
    print('DV_01 at frame 140:', pos, 'rotation:', rot)
