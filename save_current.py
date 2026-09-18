import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy
bpy.ops.wm.save_mainfile()
print("Scene saved successfully to:", bpy.data.filepath)
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
