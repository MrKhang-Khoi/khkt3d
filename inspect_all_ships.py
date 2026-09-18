import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

print("=== ALL SHIPS IN SCENE ===")
for obj in bpy.data.objects:
    if obj.parent is None and ('Thuyen' in obj.name or 'Ham' in obj.name or 'LauThuyen' in obj.name or 'DV' in obj.name or 'NamHan' in obj.name):
        print(f"Root: {obj.name}, Pos: {obj.location}")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
