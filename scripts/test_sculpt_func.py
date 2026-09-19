import bpy, bmesh, math
from mathutils import Vector, Matrix, Euler

# 1. Hàm cuộn tròn bàn tay thành Power Grip ôm quanh trục cán chèo
def sculpt_power_grip(mesh, vg_name, oar_axis_pt, oar_axis_dir, grip_radius=0.042):
    vg = mesh.vertex_groups.get(vg_name) if hasattr(mesh, "vertex_groups") else None
    if not vg:
        return
    
    axis_norm = oar_axis_dir.normalized()
    
    # Duyệt qua các vertex thuộc bàn tay
    for v in mesh.data.vertices:
        w = 0.0
        for g in v.groups:
            if g.group == vg.index:
                w = g.weight
                break
        if w > 0.3:
            # Hình chiếu của vertex lên trục cán chèo
            p = v.co
            rel = p - oar_axis_pt
            proj_len = rel.dot(axis_norm)
            p_on_axis = oar_axis_pt + axis_norm * proj_len
            
            # Vector từ trục tới vertex
            radial = p - p_on_axis
            dist = radial.length
            if dist > 0.001:
                radial_norm = radial.normalized()
                # Cuộn tròn các ngón tay ôm sát bán kính cán chèo + da tay (~4.2cm)
                # Dùng trọng số w để làm mượt dần từ cổ tay vào ngón tay
                target_dist = grip_radius + 0.008 * math.sin(p.z * 20.0)
                new_p = p_on_axis + radial_norm * (dist * (1.0 - w) + target_dist * w)
                v.co = new_p

print("Đã nạp hàm sculpt_power_grip")
