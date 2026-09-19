import bpy
from mathutils import Vector

soldier = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
vg_L = soldier.vertex_groups.get('hand.L')
vg_R = soldier.vertex_groups.get('hand.R')

pts_L = [v.co for v in soldier.data.vertices if any(g.group == vg_L.index and g.weight > 0.5 for g in v.groups)]
pts_R = [v.co for v in soldier.data.vertices if any(g.group == vg_R.index and g.weight > 0.5 for g in v.groups)]

# Khi xoay 90 độ quanh Z: (x, y, z) -> (-y, x, z)
# Hãy in ra tọa độ gốc của Hand L và Hand R
cL = sum(pts_L, Vector()) / len(pts_L)
cR = sum(pts_R, Vector()) / len(pts_R)

print(f"Original Soldier Hand L: X={cL.x:.3f}, Y={cL.y:.3f}, Z={cL.z:.3f}")
print(f"Original Soldier Hand R: X={cR.x:.3f}, Y={cR.y:.3f}, Z={cR.z:.3f}")

# Sau khi xoay rot_facing = Euler((0, 0, pi/2)):
# x' = -y, y' = x, z' = z
cL_rot = Vector((-cL.y, cL.x, cL.z))
cR_rot = Vector((-cR.y, cR.x, cR.z))
print(f"Rotated Hand L: X={cL_rot.x:.3f}, Y={cL_rot.y:.3f}, Z={cL_rot.z:.3f}")
print(f"Rotated Hand R: X={cR_rot.x:.3f}, Y={cR_rot.y:.3f}, Z={cR_rot.z:.3f}")
