import bpy
from mathutils import Vector

def check_obj_dims(obj_name):
    ob = bpy.data.objects.get(obj_name)
    if ob:
        verts = [v.co for v in ob.data.vertices]
        min_x = min(v.x for v in verts)
        max_x = max(v.x for v in verts)
        min_y = min(v.y for v in verts)
        max_y = max(v.y for v in verts)
        min_z = min(v.z for v in verts)
        max_z = max(v.z for v in verts)
        print(f"{obj_name}: X[{min_x:.2f}, {max_x:.2f}], Y[{min_y:.2f}, {max_y:.2f}], Z[{min_z:.2f}, {max_z:.2f}]")

check_obj_dims("Mai_Cheo_Thuyen")
check_obj_dims("NamHan_24MaiCheo_HangNang")