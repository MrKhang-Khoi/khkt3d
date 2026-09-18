import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy
print("HELLO FROM BLENDER LIVE!")
print("Objects count:", len(bpy.data.objects))
main_ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
if main_ship:
    print("Found main ship:", main_ship.name)
    print("Children:", [c.name for c in main_ship.children])
else:
    print("Main ship not found")
""")
print("Status:", res.get("status"))
print("Output:", res.get("result", {}).get("result"))
