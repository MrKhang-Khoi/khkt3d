import bpy

scene = bpy.context.scene
scene.frame_set(1)
scene.render.filepath = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\render_step1_headon.png"
scene.render.image_settings.file_format = 'PNG'

# Deselect all
for ob in bpy.context.selected_objects:
    ob.select_set(False)

bpy.ops.render.render(write_still=True)
print("Render completed: c:\\Users\\HPZBook\\Desktop\\TEST_BLENDER\\render_step1_headon.png")