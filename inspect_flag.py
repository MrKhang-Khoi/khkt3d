import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

flag = bpy.data.objects.get("CoLenh_NguHanh_DinhBuom")
if flag:
    print("Flag:", flag.name, "type:", flag.type, "loc:", flag.location)
    if flag.data:
        print("Flag data:", flag.data.name, "verts:", len(flag.data.vertices), "polys:", len(flag.data.polygons))
        print("Flag mats:", [m.name for m in flag.data.materials if m])
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
