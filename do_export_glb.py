import bpy
import os

out_dir = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export"
os.makedirs(out_dir, exist_ok=True)
glb_path = os.path.join(out_dir, "thuyen_daiviet_master.glb")

ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
if not ship:
    print("ERROR: Thuyen_Chien_NgoQuyen_938 not found")
else:
    bpy.ops.object.select_all(action='DESELECT')
    def select_tree(obj):
        obj.select_set(True)
        for c in obj.children:
            select_tree(c)
    select_tree(ship)
    bpy.context.view_layer.objects.active = ship
    
    # Export selection only
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        use_selection=True,
        export_format='GLB',
        export_apply=False
    )
    print("Successfully exported GLB:", glb_path)
    print("File size:", os.path.getsize(glb_path), "bytes")
