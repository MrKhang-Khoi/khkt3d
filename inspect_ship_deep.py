import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
print("=== INSPECTING DETAILED OBJECTS ===")
for obj in ship.children:
    print(f"Name: {obj.name}, Type: {obj.type}, Pos: {obj.location}")
    if obj.type == 'MESH':
        poly_count = len(obj.data.polygons)
        vert_count = len(obj.data.vertices)
        mats = [m.name for m in obj.data.materials if m]
        print(f"  Mesh: {obj.data.name}, Verts: {vert_count}, Polys: {poly_count}, Mats: {mats}")
    elif obj.type == 'EMPTY':
        print(f"  Empty children: {[c.name for c in obj.children]}")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
