import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

ship = bpy.data.objects.get("Thuyen_Chien_NgoQuyen_938")
cmd = bpy.data.objects.get("Crew_Cmd_DV_01_SoaiTienPhong_Ta")
deck = bpy.data.objects.get("San_Boong_Thuyen")
floor = bpy.data.objects.get("Van_San_LongThuyen_Kin")

print("CMD loc:", cmd.location)
print("Deck bounds:", [(v.co.x, v.co.z) for v in deck.data.vertices if v.co.x < -3.0] if deck and deck.data else "No deck")
print("Floor loc:", floor.location if floor else "No floor")

# Check if there are any other objects near X = -3.6
for c in ship.children:
    if abs(c.location.x - (-3.6)) < 1.0:
        print(f"Near stern: {c.name}, type={c.type}, loc={c.location}")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
