import bpy
import os

print("=== [VIETNAM-SIM MASTER] ĐANG NƯỚNG ANIMATION & XUẤT BẢN WEB3D GLTF 2.0 (GLB) ===")

WS_DIR = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
out_glb = os.path.join(WS_DIR, "web3d_export", "bach_dang_step3_counter_offensive.glb")
os.makedirs(os.path.dirname(out_glb), exist_ok=True)

# Tối ưu hóa trước khi xuất
# Đảm bảo timeline 1-240
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 240

# Xuất khẩu glTF 2.0 chuẩn ISO/IEC 12113
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    export_image_format='AUTO',
    export_animations=True,
    export_bake_animation=True,
    export_animation_mode='ACTIONS',
    export_skins=True,
    export_morph=True,
    export_morph_animation=True,
    export_optimize_animation_size=True,
    export_apply=False
)

print(f"=== XUẤT THÀNH CÔNG FILE GLB PHÂN CẢNH 3: {out_glb} ===")
