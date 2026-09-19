import bpy
from mathutils import Vector, Matrix, Euler

soldier = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
rot_facing = Euler((0, 0, 1.5707963)).to_matrix().to_4x4()

# Biến dạng mềm cánh tay để 2 bàn tay đón đúng trục cán chèo dốc 31 độ
def align_arms_to_oar(mesh, is_stbd=False):
    side_sign = -1.0 if is_stbd else 1.0
    
    # Mục tiêu vị trí của 2 bàn tay
    # Tay trong (Inboard): Y ~ -0.05 * side_sign, Z ~ 0.95
    # Tay ngoài (Outboard): Y ~ 0.40 * side_sign, Z ~ 0.70
    p_in_target = Vector((0.45, -0.05 * side_sign, 0.95))
    p_out_target = Vector((0.45, 0.40 * side_sign, 0.70))
    
    # Trục cán chèo
    axis_dir = (p_out_target - p_in_target).normalized()
    
    # Nhóm vertex tay ngoài và tay trong
    vg_out_name = 'hand.L' if not is_stbd else 'hand.R'
    vg_in_name = 'hand.R' if not is_stbd else 'hand.L'
    
    vg_out = mesh.vertex_groups.get(vg_out_name)
    vg_in = mesh.vertex_groups.get(vg_in_name)
    
    # Dịch chuyển và cuộn tròn ngón tay
    for vg, target_p in [(vg_in, p_in_target), (vg_out, p_out_target)]:
        if not vg:
            continue
        # Lấy tâm hiện tại
        pts = [v.co for v in mesh.data.vertices if any(g.group == vg.index and g.weight > 0.5 for g in v.groups)]
        if not pts:
            continue
        cur_center = sum(pts, Vector()) / len(pts)
        delta = target_p - cur_center
        
        for v in mesh.data.vertices:
            w = 0.0
            for g in v.groups:
                if g.group == vg.index:
                    w = g.weight
                    break
            if w > 0.1:
                # Dịch chuyển bàn tay về trục cán chèo
                v.co += delta * w
                # Cuộn tròn thành nắm đấm ôm cán chèo bán kính 3.8cm
                p = v.co
                rel = p - p_in_target
                proj = rel.dot(axis_dir)
                p_on_axis = p_in_target + axis_dir * proj
                rad = p - p_on_axis
                if rad.length > 0.001:
                    v.co = p_on_axis + rad.normalized() * (0.038 * w + rad.length * (1.0 - w))

print("Đã nạp align_arms_to_oar")
