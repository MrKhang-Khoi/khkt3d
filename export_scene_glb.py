import bpy
import os

export_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\bach_dang_battle_optimized.glb'

print(f"Exporting scene to {export_path}...")

# Select objects to export: Mount, Mudflat, Trees, Water, Stakes, Ships
bpy.ops.object.select_all(action='DESELECT')

export_objs = []
for ob in bpy.context.scene.objects:
    # Skip camera, lights, and hidden template trees
    if ob.type in ['CAMERA', 'LIGHT']:
        continue
    if ob.location.x > 400: # Template trees
        continue
    export_objs.append(ob)
    ob.select_set(True)

print(f"Selected {len(export_objs)} objects for export.")

bpy.ops.export_scene.gltf(
    filepath=export_path,
    export_format='GLB',
    use_selection=True,
    export_apply=False,
    export_animations=True,
    export_materials='EXPORT',
    export_image_format='AUTO'
)

file_size = os.path.getsize(export_path)
print(f"GLB Export SUCCESS! File size: {file_size / (1024*1024):.2f} MB")
