import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
print("=== SHIP DETAILS ===")
print("Ship loc:", ship.location)
for child in ship.children:
    print(f"Child: {child.name}, type: {child.type}, loc: {child.location}")
    if "Cmd" in child.name or "Trong" in child.name or "Linh" in child.name:
        print(f"   Mesh: {child.data.name if child.data else None}")
        if child.data and hasattr(child.data, 'materials'):
            print(f"   Mats: {[m.name for m in child.data.materials if m]}")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
