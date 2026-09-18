import bpy
import os

out_dir = r c:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export
os.makedirs(out_dir, exist_ok=True)

# 1. Export Thuyen Dai Viet Master
bpy.ops.wm.open_mainfile(filepath=rc:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships\thuyen_ta_ngoquyen_master.blend)
dv_glb_path = os.path.join(out_dir, thuyen_daiviet_master.glb)
bpy.ops.export_scene.gltf(
    filepath=dv_glb_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True
)
print(Exported Dai Viet GLB size:, os.path.getsize(dv_glb_path), bytes)

# 2. Export Lau Thuyen Nam Han Master
bpy.ops.wm.open_mainfile(filepath=rc:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships\lau_thuyen_namhan_master.blend)
nh_glb_path = os.path.join(out_dir, lau_thuyen_namhan_master.glb)
bpy.ops.export_scene.gltf(
    filepath=nh_glb_path,
    export_format='GLB',
    use_selection=False,
    export_apply=True
)
print(Exported Nam Han GLB size:, os.path.getsize(nh_glb_path), bytes)
