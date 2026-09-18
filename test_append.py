import bpy

blend_path = 'C:/Users/HPZBook/Desktop/TEST_BLENDER/scenes/dai_chien_bach_dang_assembly.blend'
print("Testing append collection...")
with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan', 'Collection_Coc_BachDang']

print("Appended collections:", [c.name for c in data_to.collections if c])
for col in data_to.collections:
    if col and col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
print("Linked collections to scene successfully!")
print("Total objects in scene:", len(bpy.context.scene.objects))
