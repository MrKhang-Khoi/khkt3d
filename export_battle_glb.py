"""
PIPELINE GLTF/GLB EXPORTER: NƯỚNG ANIMATION & XUẤT BẢN WEB3D CHUẨN QUỐC TẾ
Xuất file: web3d_export/bach_dang_battle_optimized.glb
Tuân thủ Mục IV trong QUY_TRINH_SAN_XUAT_3D_BACH_DANG_938.md (chuẩn ISO/IEC 12113)
"""

import bpy
import os
import sys

def main():
    print("=== [PIPELINE] BẮT ĐẦU NƯỚNG ANIMATION VÀ XUẤT GLTF 2.0 (GLB) ===")
    base_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    scene_blend = os.path.join(base_dir, "scenes", "dai_chien_bach_dang_assembly.blend")
    output_glb = os.path.join(base_dir, "web3d_export", "bach_dang_battle_optimized.glb")

    # Mở file assembly
    bpy.ops.wm.open_mainfile(filepath=scene_blend)

    # Đảm bảo toàn bộ tài nguyên được local hóa trong session export để nhúng 100% vào GLB nhị phân
    bpy.ops.object.select_all(action='SELECT')
    try:
        bpy.ops.object.make_local(type='ALL')
    except Exception as e:
        print(f"Make local notice: {e}")

    # Cấu hình nướng toàn bộ 300 frames chuyển động
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 300

    print(f"-> Đang xuất khẩu ra tệp GLB chuẩn quốc tế: {output_glb}...")
    bpy.ops.export_scene.gltf(
        filepath=output_glb,
        export_format='GLB',
        export_image_format='AUTO',
        export_animations=True,
        export_bake_animation=True,
        export_animation_mode='ACTIVE_ACTIONS', # Nướng tất cả Actions đang active trên timeline
        export_optimize_animation_size=True,
        export_materials='EXPORT',
        export_lights=False,
        export_cameras=True
    )

    if os.path.exists(output_glb):
        file_size_mb = os.path.getsize(output_glb) / (1024 * 1024)
        print(f"=== [PIPELINE] XUẤT THÀNH CÔNG GLB: {output_glb} ({file_size_mb:.2f} MB) ===")
    else:
        print("LỖI: Không tìm thấy tệp GLB xuất ra!")

if __name__ == "__main__":
    main()
