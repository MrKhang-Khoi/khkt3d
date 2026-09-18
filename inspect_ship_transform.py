import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

root = bpy.data.objects.get("Root_DV_01_SoaiTienPhong_Ta")
ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
print("Root loc:", root.location, "rot:", root.rotation_euler)
print("Ship loc:", ship.location, "rot:", ship.rotation_euler)
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
