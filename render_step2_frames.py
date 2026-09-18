import bpy

scene = bpy.context.scene
cam = bpy.data.objects.get('Camera_ChienTruong_Headon')
if cam:
    scene.camera = cam

# Frame 85: Turnaround phase
scene.frame_set(85)
scene.render.filepath = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_step2_frame85_quay_dau.png"
bpy.ops.render.render(write_still=True)
print("Rendered Frame 85 successfully!")

# Frame 140: Full retreat & pursuit phase
scene.frame_set(140)
scene.render.filepath = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_step2_frame140_truy_kich.png"
bpy.ops.render.render(write_still=True)
print("Rendered Frame 140 successfully!")

# Reset to frame 1
scene.frame_set(1)
bpy.context.view_layer.update()
