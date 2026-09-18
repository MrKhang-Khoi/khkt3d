import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

flag = bpy.data.objects.get("CoLenh_NguHanh_DinhBuom")
if flag:
    mw = flag.matrix_world
    coords = [mw @ v.co for v in flag.data.vertices]
    min_x = min(c.x for c in coords)
    max_x = max(c.x for c in coords)
    min_z = min(c.z for c in coords)
    max_z = max(c.z for c in coords)
    print(f"Flag World X: [{min_x:.2f}, {max_x:.2f}], Z: [{min_z:.2f}, {max_z:.2f}]")
    mat = flag.data.materials[0] if flag.data.materials else None
    if mat and mat.use_nodes:
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf:
            print("Base color:", [round(x, 2) for x in bsdf.inputs['Base Color'].default_value])
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
