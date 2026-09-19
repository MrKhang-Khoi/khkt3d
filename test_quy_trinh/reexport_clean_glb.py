import bpy, os

# Chỉ chọn thân cọc, đầu sắt, và bùn đáy (bỏ khối nước che tầm nhìn)
target_objs = [
    bpy.data.objects.get("Coc_Than_GoLim_938"),
    bpy.data.objects.get("Coc_Dau_Bit_Sat_938"),
    bpy.data.objects.get("DiaHinh_TangBun_DaySong")
]

bpy.ops.object.select_all(action='DESELECT')
for o in target_objs:
    if o:
        o.select_set(True)
bpy.context.view_layer.objects.active = target_objs[0]

out_glb = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/coc_bach_dang_938.glb'
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    use_selection=True,
    export_format='GLB',
    export_apply=True,
    export_yup=True,
    export_materials='EXPORT'
)
print("Re-exported GLB clean (No water occlusion):", out_glb, "Size:", os.path.getsize(out_glb))
