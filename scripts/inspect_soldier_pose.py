import bpy

arm = bpy.data.objects.get('Rig_ThuyBinh_Seated')
if arm:
    print("=== RIG_THUYBINH_SEATED BONES ===")
    for pb in arm.pose.bones:
        mode = pb.rotation_mode
        rot = tuple(round(v, 3) for v in (pb.rotation_euler if mode == 'XYZ' else pb.rotation_quaternion))
        print(f"{pb.name}: mode={mode}, rot={rot}")
