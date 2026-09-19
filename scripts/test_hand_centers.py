import bpy
from mathutils import Vector, Euler, Matrix

soldier = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
rot_facing = Euler((0, 0, 1.5707963)).to_matrix().to_4x4()
vg_L = soldier.vertex_groups.get('hand.L')
vg_R = soldier.vertex_groups.get('hand.R')

pts_L = [rot_facing @ v.co for v in soldier.data.vertices if any(g.group == vg_L.index and g.weight > 0.5 for g in v.groups)]
pts_R = [rot_facing @ v.co for v in soldier.data.vertices if any(g.group == vg_R.index and g.weight > 0.5 for g in v.groups)]

c_L = sum(pts_L, Vector()) / len(pts_L)
c_R = sum(pts_R, Vector()) / len(pts_R)

print("Center Hand L (after rot_facing):", c_L)
print("Center Hand R (after rot_facing):", c_R)
