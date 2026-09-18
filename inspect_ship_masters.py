import bpy
import os

base_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships"
thuyen_path = os.path.join(base_dir, "thuyen_ta_ngoquyen_master.blend")
lau_path = os.path.join(base_dir, "lau_thuyen_namhan_master.blend")

print("=== INSPECT THUYEN TA MASTER ===")
with bpy.data.libraries.load(thuyen_path) as (df, dt):
    print("Collections:", df.collections)
    print("Objects:", df.objects)

print("\n=== INSPECT LAU THUYEN MASTER ===")
with bpy.data.libraries.load(lau_path) as (df, dt):
    print("Collections:", df.collections)
    print("Objects:", df.objects)
