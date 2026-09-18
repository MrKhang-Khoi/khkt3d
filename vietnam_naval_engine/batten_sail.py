import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_vietnamese_batwing_sail(mats, parent_obj=None, mast_pos=Vector((0.8, 0, 0)), mast_height=5.6, sail_angle_deg=28.0):
    '''
    Thuật toán Khí động học Bézier tạo Cánh Buồm Cánh Dơi (Bat-wing Sail) Việt Nam:
    - Ngõng buồm trên (Yard) nghiêng chéo 48 độ vươn cao qua đỉnh cột buồm.
    - 6 nan tre (Battens) xòe hình cánh dơi/cánh én.
    - Mép sau lượn cong (Roach) và lượn sóng cánh dơi (Scalloped Leech).
    - Từng múi buồm phồng khí động học (Aerodynamic Camber).
    - Góc vát buồm đón gió (sail_angle_deg) mở rộng ra mạn thuyền để hứng trọn ánh sáng.
    '''
    root = bpy.data.objects.new('Buom_CanhDoi_BachDang', None)
    if parent_obj:
        root.parent = parent_obj
    bpy.context.collection.objects.link(root)

    # 1. CỘT BUỒM (MAST) & KHOEN BUỒM (PARRELS)
    mesh_mast = bpy.data.meshes.new('Cot_Buom_Mesh')
    bm_mast = bmesh.new()

    # Cột buồm gỗ lim hơi ngả về trước 2.5 độ (Rake forward)
    rot_mast = Matrix.Rotation(math.radians(-2.5), 4, 'Y')
    mat_mast = Matrix.Translation(mast_pos + Vector((0, 0, mast_height * 0.5 + 0.6))) @ rot_mast
    bmesh.ops.create_cone(
        bm_mast, cap_ends=True, segments=16,
        radius1=0.12, radius2=0.07, depth=mast_height,
        matrix=mat_mast
    )
    # Chỏm đỉnh cột buồm và ròng rọc
    mat_cap = Matrix.Translation(mast_pos + rot_mast @ Vector((0, 0, mast_height + 0.65)))
    bmesh.ops.create_icosphere(bm_mast, subdivisions=2, radius=0.09, matrix=mat_cap)

    bm_mast.to_mesh(mesh_mast)
    bm_mast.free()
    obj_mast = bpy.data.objects.new('Cot_Buom_GoLim', mesh_mast)
    obj_mast.parent = root
    obj_mast.data.materials.append(mats.get('wood_lim', mats['wood_hull']))
    bpy.context.collection.objects.link(obj_mast)
    for p in obj_mast.data.polygons:
        p.use_smooth = True

    # 2. HỆ THỐNG NAN TRE BUỒM CÁNH DƠI XOAY GÓC ĐÓN GIÓ (SAIL ANGLE TRANSFORM)
    # Buồm treo lệch sang mạn trái của cột (offset 0.12m) và xoay mở góc sail_angle_deg
    rot_sail = Matrix.Rotation(math.radians(sail_angle_deg), 4, 'Z')
    pivot = mast_pos + Vector((0, 0.12, 0))

    def transform_pt(rel_x, rel_z):
        # Tọa độ tương đối so với cột buồm
        vec = Vector((rel_x, 0.0, rel_z))
        rot_vec = rot_sail @ vec
        return pivot + rot_vec

    batten_defs = [
        # (index, start_rel_x, start_rel_z, end_rel_x, end_rel_z, radius)
        (0, -0.05, 1.15, -2.40, 1.30, 0.032), # Boom (Sào đáy)
        (1, -0.02, 1.85, -3.05, 2.15, 0.027), # Batten 1
        (2,  0.00, 2.65, -3.65, 3.20, 0.026), # Batten 2 (Bụng buồm cánh dơi vươn rộng nhất)
        (3,  0.02, 3.45, -3.45, 4.30, 0.024), # Batten 3
        (4,  0.05, 4.20, -2.85, 5.35, 0.022), # Batten 4
        (5,  0.35, 4.10, -1.85, 6.55, 0.036), # Yard (Ngõng trên vát chéo 50 độ vươn cao vút qua đỉnh cột buồm!)
    ]

    mesh_battens = bpy.data.meshes.new('Nan_Tre_Buom_Mesh')
    bm_battens = bmesh.new()

    batten_lines = []
    for idx, sx, sz, ex, ez, brad in batten_defs:
        p_start = transform_pt(sx, sz)
        p_end   = transform_pt(ex, ez)
        batten_lines.append((p_start, p_end))

        # Dựng nan tre 3D hình trụ
        diff = p_end - p_start
        length = diff.length
        mid = (p_start + p_end) * 0.5
        dir_vec = diff.normalized()

        up = Vector((0, 0, 1))
        rot_axis = up.cross(dir_vec)
        if rot_axis.length > 1e-4:
            rot_axis.normalize()
            rot_ang = math.acos(max(-1.0, min(1.0, up.dot(dir_vec))))
            rmat = Matrix.Rotation(rot_ang, 4, rot_axis)
        else:
            rmat = Matrix.Identity(4)

        mat_b = Matrix.Translation(mid) @ rmat
        bmesh.ops.create_cone(
            bm_battens, cap_ends=True, segments=12,
            radius1=brad, radius2=brad * 0.85, depth=length,
            matrix=mat_b
        )

        # Các đai mây buộc nan tre vào phên buồm
        for t_step in [0.2, 0.4, 0.6, 0.8]:
            pt_band = p_start + diff * t_step
            bmesh.ops.create_cone(
                bm_battens, cap_ends=True, segments=8,
                radius1=brad * 1.25, radius2=brad * 1.25, depth=0.035,
                matrix=Matrix.Translation(pt_band) @ rmat
            )

    bm_battens.to_mesh(mesh_battens)
    bm_battens.free()
    obj_battens = bpy.data.objects.new('Nan_Tre_Va_Ngong_Buom', mesh_battens)
    obj_battens.parent = root
    obj_battens.data.materials.append(mats['bamboo'])
    bpy.context.collection.objects.link(obj_battens)
    for p in obj_battens.data.polygons:
        p.use_smooth = True

    # 3. MẶT BUỒM CÁNH DƠI KHÍ ĐỘNG HỌC (5 KHOANG MÚI BUỒM PHỒNG GIÓ)
    mesh_cloth = bpy.data.meshes.new('Vai_Buom_CanhDoi_Mesh')
    bm_cloth = bmesh.new()

    u_segments = 14 # Dọc theo nan buồm
    v_segments = 6  # Giữa 2 nan buồm

    # Pháp tuyến đẩy gió vuông góc với mặt phẳng buồm
    wind_normal = (rot_sail @ Vector((0, 1, 0))).normalized()

    for i in range(len(batten_lines) - 1):
        p0_start, p0_end = batten_lines[i]
        p1_start, p1_end = batten_lines[i+1]

        panel_grid = []
        for v_idx in range(v_segments + 1):
            tv = v_idx / v_segments
            row = []

            edge_start = p0_start.lerp(p1_start, tv)
            edge_end   = p0_end.lerp(p1_end, tv)

            # Mép sau (Leech) lượn cong cánh dơi (Scalloped Edge)
            scallop = math.sin(tv * math.pi) * 0.12
            scallop_dir = (p0_start - p0_end).normalized() # Hướng vào trong thân buồm
            edge_end += scallop_dir * scallop

            for u_idx in range(u_segments + 1):
                tu = u_idx / u_segments

                base_pt = edge_start.lerp(edge_end, tu)

                # Độ phồng khí động học (Camber): phồng mạnh ở 1/3 buồm và ở giữa 2 nan
                camber_u = math.sin(tu * math.pi * 0.95)
                camber_v = math.sin(tv * math.pi)
                camber_disp = camber_u * camber_v * 0.28 # Phồng 28cm căng gió

                disp_pt = base_pt + wind_normal * camber_disp
                v = bm_cloth.verts.new(disp_pt)
                row.append(v)
            panel_grid.append(row)

        for v_idx in range(v_segments):
            for u_idx in range(u_segments):
                bm_cloth.faces.new([
                    panel_grid[v_idx][u_idx],
                    panel_grid[v_idx][u_idx+1],
                    panel_grid[v_idx+1][u_idx+1],
                    panel_grid[v_idx+1][u_idx]
                ])

    bm_cloth.to_mesh(mesh_cloth)
    bm_cloth.free()
    obj_cloth = bpy.data.objects.new('Mui_Buom_CanhDoi_PBR', mesh_cloth)
    obj_cloth.parent = root
    obj_cloth.data.materials.append(mats['sail_cloth'])
    bpy.context.collection.objects.link(obj_cloth)
    for p in obj_cloth.data.polygons:
        p.use_smooth = True

    sol = obj_cloth.modifiers.new('Solidify', 'SOLIDIFY')
    sol.thickness = 0.014
    sol.offset = 0.0

    sub = obj_cloth.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    # 4. HỆ THỐNG DÂY LÈO & RIGGING
    mesh_ropes = bpy.data.meshes.new('Day_Leo_Rigging_Mesh')
    bm_ropes = bmesh.new()

    yard_lift_pt = batten_lines[5][0] + (batten_lines[5][1] - batten_lines[5][0]) * 0.35
    mast_top_pt = mast_pos + Vector((0, 0, mast_height + 0.55))
    mast_base_pt = mast_pos + Vector((0.15, 0, 0.8))

    def make_rope_tube(p_a, p_b, radius=0.012, segs=6):
        d = p_b - p_a
        l = d.length
        if l < 1e-3: return
        mid = (p_a + p_b) * 0.5
        u = Vector((0, 0, 1))
        d_norm = d.normalized()
        ax = u.cross(d_norm)
        if ax.length > 1e-4:
            ax.normalize()
            ang = math.acos(max(-1.0, min(1.0, u.dot(d_norm))))
            rmat = Matrix.Rotation(ang, 4, ax)
        else:
            rmat = Matrix.Identity(4)
        m = Matrix.Translation(mid) @ rmat
        bmesh.ops.create_cone(bm_ropes, cap_ends=True, segments=segs, radius1=radius, radius2=radius, depth=l, matrix=m)

    make_rope_tube(yard_lift_pt, mast_top_pt, radius=0.016)
    make_rope_tube(mast_top_pt, mast_base_pt, radius=0.016)

    # Chùm dây lèo (Multiple Sheetlets) từ 5 nan tre dưới
    bridle_center = Vector((-3.0, 1.2, 1.6))
    helm_cleat = Vector((-5.0, 0.2, 0.7))

    for idx in range(5):
        tip_pt = batten_lines[idx][1]
        make_rope_tube(tip_pt, bridle_center, radius=0.009)

    make_rope_tube(bridle_center, helm_cleat, radius=0.018)

    # Khoen quai (Parrel rings) ôm quanh cột buồm
    for idx in range(1, 5):
        pt_luff = batten_lines[idx][0]
        pt_mast_mid = mast_pos + Vector((0, 0, pt_luff.z))
        bmesh.ops.create_cone(
            bm_ropes, cap_ends=True, segments=8,
            radius1=0.15, radius2=0.15, depth=0.035,
            matrix=Matrix.Translation(pt_mast_mid)
        )

    bm_ropes.to_mesh(mesh_ropes)
    bm_ropes.free()
    obj_ropes = bpy.data.objects.new('Day_Leo_Va_Rigging', mesh_ropes)
    obj_ropes.parent = root
    obj_ropes.data.materials.append(mats['rope'])
    bpy.context.collection.objects.link(obj_ropes)

    return root
