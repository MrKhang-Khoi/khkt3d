import bpy
import os

assembly_path = 'C:/Users/HPZBook/Desktop/TEST_BLENDER/scenes/dai_chien_bach_dang_assembly.blend'
print('Checking libraries...')
with bpy.data.libraries.load(assembly_path) as (df, dt):
    print('Collections:', df.collections)
    print('Objects:', df.objects)
