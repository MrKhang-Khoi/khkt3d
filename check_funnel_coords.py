import bpy

print("--- KIEM TRA DOI HINH DAI VIET MOI ---")
for ob in bpy.data.objects:
    if ob.name.startswith("Root_DV_"):
        mw = ob.matrix_world.translation
        print(f"{ob.name}: Loc = ({mw.x:.1f}, {mw.y:.1f}, {mw.z:.2f}), Rot_Roll = {ob.rotation_euler.y:.2f}")

print("\n--- KIEM TRA CO LENH & TRONG TRAN ---")
f = bpy.data.objects.get("CoLenh_NguHanh")
d = bpy.data.objects.get("TrongTran_KhieuChien")
print("CoLenh_NguHanh:", f.name if f else "None", "Parent:", f.parent.name if f and f.parent else "None")
print("TrongTran_KhieuChien:", d.name if d else "None", "Parent:", d.parent.name if d and d.parent else "None")