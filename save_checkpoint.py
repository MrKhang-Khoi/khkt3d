import bpy

save_path = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_step2_checkpoint.blend"
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"Saved checkpoint successfully to {save_path}!")
