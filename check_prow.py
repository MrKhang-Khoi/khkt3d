import bpy
from mathutils import Vector

prow = bpy.data.objects.get('Mui_ChimLac_DongSon')
stern = bpy.data.objects.get('Than_Thuyen_GoLim')

if prow and stern:
    prow_co = prow.matrix_world.translation
    stern_verts = [v.co for v in stern.data.vertices]
    # Local min and max on X and Y
    min_x = min(v.x for v in stern_verts)
    max_x = max(v.x for v in stern_verts)
    min_y = min(v.y for v in stern_verts)
    max_y = max(v.y for v in stern_verts)
    print(f"Stern local X range: {min_x:.2f} to {max_x:.2f}")
    print(f"Stern local Y range: {min_y:.2f} to {max_y:.2f}")
    prow_loc = prow.location
    print(f"Prow local loc: ({prow_loc.x:.2f}, {prow_loc.y:.2f}, {prow_loc.z:.2f})")
