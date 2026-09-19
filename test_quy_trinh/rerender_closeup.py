import bpy, os
from mathutils import Vector

scene = bpy.data.scenes.get("Scene_Coc_BachDang_938")
cam = bpy.data.objects.get("Cam_Coc_DauSat_Final")
if scene and cam:
    cam.location = Vector((1.0, -2.4, 2.1))
    look_target = Vector((0.85, 0.0, 1.45))
    look_dir = look_target - cam.location
    cam.rotation_euler = look_dir.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 55.0
    scene.camera = cam
    out_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/anh_coc_cancanh_dau_sat.png'
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True, scene=scene.name)
    import shutil
    artifact_path = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_coc_cancanh_dau_sat.png'
    shutil.copyfile(out_path, artifact_path)
    print("Re-rendered closeup iron cap successfully!")
