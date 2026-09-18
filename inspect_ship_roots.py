import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
print("Thuyen parent:", ship.parent.name if ship.parent else "None")
root1 = bpy.data.objects.get("Root_DV_01_SoaiTienPhong_Ta")
print("Root1 children:", [c.name for c in root1.children] if root1 else "None")
root2 = bpy.data.objects.get("Root_DV_02_SoaiTienPhong_Huu")
print("Root2 children:", [c.name for c in root2.children] if root2 else "None")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
