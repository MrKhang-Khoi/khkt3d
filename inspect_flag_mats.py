import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

flag = bpy.data.objects.get("CoLenh_NguHanh_DuoiThuyen")
if flag:
    print("Flag mats:", [m.name for m in flag.data.materials])
    for i, poly in enumerate(flag.data.polygons[:10]):
        print(f"Poly {i}: mat_index = {poly.material_index}")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
