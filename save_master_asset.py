import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy
bpy.ops.wm.save_as_mainfile(filepath=r"c:\\Users\\HPZBook\\Desktop\\TEST_BLENDER\\assets\\ships\\thuyen_ta_ngoquyen_master.blend", copy=True)
print("Saved master asset copy!")
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
