import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

print("=== CHECKING FOR STRAY OBJECTS ===")
for o in bpy.data.objects:
    if any(k in o.name.lower() for k in ['colenh', 'flag', 'co_', 'cube', 'sphere']):
        print(f"Candidate stray: {o.name}, parent: {o.parent.name if o.parent else 'None'}, pos: {o.location}")

buom = bpy.data.objects.get("Buom_CanhDoi_BachDang")
if buom:
    print("Buom children:")
    for c in buom.children:
        print(f"  {c.name}: type={c.type}, mesh={c.data.name if c.data else None}, loc={c.location}")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
