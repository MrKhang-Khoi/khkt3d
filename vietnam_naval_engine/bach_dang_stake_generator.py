"""
HỆ THỐNG SINH CỌC BẠCH ĐẰNG SIÊU THỰC (HYPER-REALISTIC BẠCH ĐẰNG STAKE ENGINE) - V4
Chuẩn hóa màu sắc khảo cổ học: Gỗ Lim ngâm bùn sình đen mun (Charcoal aged ironwood),
Mũi sắt rèn xám chì phong hóa, nước sông Bạch Đằng xanh thẫm cuộn sóng bọt trắng.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

def create_photoreal_stake_materials():
    """Tạo bộ 3 vật liệu PBR procedural đỉnh cao cho Cọc Bạch Đằng"""
    mats = {}

    # -------------------------------------------------------------
    # 1. THÂN GỖ LIM CỔ NGÂM BÙN (Mat_GoLim_CocBachDang) - Index 0
    # Màu đen mun than, nâu sẫm, thớ gỗ nứt dọc cực sâu
    # -------------------------------------------------------------
    m_wood = bpy.data.materials.new('Mat_GoLim_CocBachDang')
    m_wood.diffuse_color = (0.03, 0.02, 0.015, 1.0)
    m_wood.use_nodes = True
    nw = m_wood.node_tree.nodes
    lw = m_wood.node_tree.links
    nw.clear()

    out_w = nw.new('ShaderNodeOutputMaterial')
    bsdf_w = nw.new('ShaderNodeBsdfPrincipled')
    lw.new(bsdf_w.outputs['BSDF'], out_w.inputs['Surface'])

    # Coordinates & Mapping (Scale Z = 0.04 kéo giãn thớ gỗ theo chiều dọc thân cọc)
    tc_w = nw.new('ShaderNodeTexCoord')
    mp_w = nw.new('ShaderNodeMapping')
    mp_w.inputs['Scale'].default_value = (5.0, 5.0, 0.04)
    lw.new(tc_w.outputs['Object'], mp_w.inputs['Vector'])

    noise_grain = nw.new('ShaderNodeTexNoise')
    noise_grain.inputs['Scale'].default_value = 14.0
    noise_grain.inputs['Detail'].default_value = 14.0
    noise_grain.inputs['Roughness'].default_value = 0.72
    noise_grain.inputs['Distortion'].default_value = 0.8
    lw.new(mp_w.outputs['Vector'], noise_grain.inputs['Vector'])

    # Rãnh nứt dọc Voronoi sâu
    mp_voro = nw.new('ShaderNodeMapping')
    mp_voro.inputs['Scale'].default_value = (3.0, 3.0, 0.08)
    lw.new(tc_w.outputs['Object'], mp_voro.inputs['Vector'])

    voro_crack = nw.new('ShaderNodeTexVoronoi')
    voro_crack.voronoi_dimensions = '3D'
    voro_crack.feature = 'DISTANCE_TO_EDGE'
    voro_crack.inputs['Scale'].default_value = 4.0
    lw.new(mp_voro.outputs['Vector'], voro_crack.inputs['Vector'])

    cr_crack = nw.new('ShaderNodeValToRGB')
    cr_crack.color_ramp.elements[0].position = 0.03
    cr_crack.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cr_crack.color_ramp.elements[1].position = 0.30
    cr_crack.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    lw.new(voro_crack.outputs['Distance'], cr_crack.inputs['Fac'])

    mix_texture = nw.new('ShaderNodeMix')
    mix_texture.data_type = 'FLOAT'
    mix_texture.blend_type = 'MULTIPLY'
    mix_texture.inputs['Factor'].default_value = 0.85
    lw.new(noise_grain.outputs['Fac'], mix_texture.inputs[2])
    lw.new(cr_crack.outputs['Color'], mix_texture.inputs[3])

    # Màu gỗ Lim ngâm bùn sình: Màu than mun đậm, nâu sẫm, viền xám tro
    cr_wood_color = nw.new('ShaderNodeValToRGB')
    cr_wood_color.color_ramp.elements[0].position = 0.08
    cr_wood_color.color_ramp.elements[0].color = (0.012, 0.009, 0.007, 1.0) # Khe nứt đen mun
    cr_wood_color.color_ramp.elements[1].position = 0.50
    cr_wood_color.color_ramp.elements[1].color = (0.045, 0.032, 0.022, 1.0) # Vỏ gỗ Lim nâu đen
    cr_wood_color.color_ramp.elements.new(0.85)
    cr_wood_color.color_ramp.elements[2].color = (0.11, 0.095, 0.08, 1.0)  # Thớ vỏ khô xám tro mốc
    lw.new(mix_texture.outputs['Result'], cr_wood_color.inputs['Fac'])
    lw.new(cr_wood_color.outputs['Color'], bsdf_w.inputs['Base Color'])

    bump_bark = nw.new('ShaderNodeBump')
    bump_bark.inputs['Strength'].default_value = 0.80
    bump_bark.inputs['Distance'].default_value = 0.05
    lw.new(mix_texture.outputs['Result'], bump_bark.inputs['Height'])
    lw.new(bump_bark.outputs['Normal'], bsdf_w.inputs['Normal'])

    # Gradient ngập nước (Roughness): Chân ngập nước bóng ướt, thân trên khô ráp
    sep_xyz = nw.new('ShaderNodeSeparateXYZ')
    lw.new(tc_w.outputs['Generated'], sep_xyz.inputs['Vector'])

    cr_wet = nw.new('ShaderNodeValToRGB')
    cr_wet.color_ramp.elements[0].position = 0.18
    cr_wet.color_ramp.elements[0].color = (0.08, 0.08, 0.08, 1.0) # Ngập nước bóng loáng
    cr_wet.color_ramp.elements[1].position = 0.42
    cr_wet.color_ramp.elements[1].color = (0.85, 0.85, 0.85, 1.0) # Thân trên khô ráp
    lw.new(sep_xyz.outputs['Z'], cr_wet.inputs['Fac'])
    lw.new(cr_wet.outputs['Color'], bsdf_w.inputs['Roughness'])

    mats['lim_wood'] = m_wood

    # -------------------------------------------------------------
    # 2. LÕI GỖ VẠT NHỌN BẰNG RÌU (Mat_LoiGo_RiuDeo) - Index 1
    # Gỗ lõi màu xám tro phong hóa, sớ dọc
    # -------------------------------------------------------------
    m_carved = bpy.data.materials.new('Mat_LoiGo_RiuDeo')
    m_carved.diffuse_color = (0.16, 0.14, 0.12, 1.0)
    m_carved.use_nodes = True
    nc = m_carved.node_tree.nodes
    lc = m_carved.node_tree.links
    nc.clear()

    out_c = nc.new('ShaderNodeOutputMaterial')
    bsdf_c = nc.new('ShaderNodeBsdfPrincipled')
    bsdf_c.inputs['Roughness'].default_value = 0.70
    lc.new(bsdf_c.outputs['BSDF'], out_c.inputs['Surface'])

    tc_c = nc.new('ShaderNodeTexCoord')
    mp_c = nc.new('ShaderNodeMapping')
    mp_c.inputs['Scale'].default_value = (4.0, 4.0, 0.06)
    lc.new(tc_c.outputs['Object'], mp_c.inputs['Vector'])

    noise_c = nc.new('ShaderNodeTexNoise')
    noise_c.inputs['Scale'].default_value = 16.0
    noise_c.inputs['Detail'].default_value = 12.0
    noise_c.inputs['Roughness'].default_value = 0.65
    lc.new(mp_c.outputs['Vector'], noise_c.inputs['Vector'])

    cr_c = nc.new('ShaderNodeValToRGB')
    cr_c.color_ramp.elements[0].position = 0.20
    cr_c.color_ramp.elements[0].color = (0.05, 0.04, 0.03, 1.0) # Rãnh sớ
    cr_c.color_ramp.elements[1].position = 0.65
    cr_c.color_ramp.elements[1].color = (0.18, 0.16, 0.13, 1.0) # Gỗ lõi xám bạc phong hóa
    lc.new(noise_c.outputs['Fac'], cr_c.inputs['Fac'])
    lc.new(cr_c.outputs['Color'], bsdf_c.inputs['Base Color'])

    bump_c = nc.new('ShaderNodeBump')
    bump_c.inputs['Strength'].default_value = 0.50
    bump_c.inputs['Distance'].default_value = 0.03
    lc.new(noise_c.outputs['Fac'], bump_c.inputs['Height'])
    lc.new(bump_c.outputs['Normal'], bsdf_c.inputs['Normal'])

    mats['carved_wood'] = m_carved

    # -------------------------------------------------------------
    # 3. MŨI SẮT RÈN BỌC NGỌN (Mat_MuiSat_RenCo) - Index 2
    # Sắt rèn cổ xám chì ánh bạc, điểm đốm rỉ sét mờ
    # -------------------------------------------------------------
    m_iron = bpy.data.materials.new('Mat_MuiSat_RenCo')
    m_iron.diffuse_color = (0.22, 0.23, 0.25, 1.0)
    m_iron.use_nodes = True
    ni = m_iron.node_tree.nodes
    li = m_iron.node_tree.links
    ni.clear()

    out_i = ni.new('ShaderNodeOutputMaterial')
    bsdf_i = ni.new('ShaderNodeBsdfPrincipled')
    bsdf_i.inputs['Metallic'].default_value = 0.92
    bsdf_i.inputs['Roughness'].default_value = 0.35
    li.new(bsdf_i.outputs['BSDF'], out_i.inputs['Surface'])

    tc_i = ni.new('ShaderNodeTexCoord')
    noise_i = ni.new('ShaderNodeTexNoise')
    noise_i.inputs['Scale'].default_value = 28.0
    noise_i.inputs['Detail'].default_value = 10.0
    noise_i.inputs['Roughness'].default_value = 0.55
    li.new(tc_i.outputs['Object'], noise_i.inputs['Vector'])

    cr_iron = ni.new('ShaderNodeValToRGB')
    cr_iron.color_ramp.elements[0].position = 0.30
    cr_iron.color_ramp.elements[0].color = (0.20, 0.22, 0.24, 1.0) # Sắt xám chì đậm
    cr_iron.color_ramp.elements[1].position = 0.65
    cr_iron.color_ramp.elements[1].color = (0.38, 0.25, 0.15, 1.0) # Oxit rỉ phong hóa
    li.new(noise_i.outputs['Fac'], cr_iron.inputs['Fac'])
    li.new(cr_iron.outputs['Color'], bsdf_i.inputs['Base Color'])

    bump_i = ni.new('ShaderNodeBump')
    bump_i.inputs['Strength'].default_value = 0.30
    bump_i.inputs['Distance'].default_value = 0.02
    li.new(noise_i.outputs['Fac'], bump_i.inputs['Height'])
    li.new(bump_i.outputs['Normal'], bsdf_i.inputs['Normal'])

    mats['iron_cap'] = m_iron

    return mats


def build_hyperrealistic_stake(
    bm,
    pos=Vector((0, 0, 0)),
    height=2.85,
    base_radius=0.17,
    tilt_angle_y=8.0,
    tilt_angle_x=-3.0,
    seed=101,
    stake_type='iron_capped'
):
    """
    Sinh 1 cọc Bạch Đằng siêu thực trong Unified BMesh:
    - 0: Gỗ Lim thân cọc
    - 1: Gỗ lõi đẽo vạt nhọn
    - 2: Mũi sắt rèn
    """
    rot_m = Matrix.Rotation(math.radians(tilt_angle_y), 4, 'Y') @ Matrix.Rotation(math.radians(tilt_angle_x), 4, 'X')
    trans_m = Matrix.Translation(pos) @ rot_m

    tip_length = 0.78
    wood_height = height - tip_length
    num_slices = 24
    slice_dz = wood_height / num_slices
    num_radial = 18

    # 1. THÂN GỖ HỮU CƠ
    trunk_rings = []
    for si in range(num_slices + 1):
        z_curr = si * slice_dz
        t_z = si / num_slices

        rad_curr = base_radius * (1.0 - t_z * 0.16)

        bow_x = math.sin(t_z * math.pi * 0.8 + seed) * 0.028
        bow_y = math.cos(t_z * math.pi * 0.6 + seed * 1.4) * 0.020

        ring = []
        for ri in range(num_radial):
            ang = (ri / num_radial) * 2.0 * math.pi

            w1 = math.sin(ang * 3.0 + seed * 2.1 + t_z * 4.0) * 0.015
            w2 = math.cos(ang * 5.0 + seed * 1.5) * 0.010

            knot = 0.0
            if 0.35 < t_z < 0.55 and abs(ang - 1.2) < 0.55:
                knot = math.cos((ang - 1.2) * 2.8) * math.sin((t_z - 0.35) / 0.2 * math.pi) * 0.025

            r_total = max(0.06, rad_curr + w1 + w2 + knot)

            if t_z > 0.80:
                t_taper = (t_z - 0.80) / 0.20
                r_total *= (1.0 - t_taper * 0.18)

            pt_local = Vector((r_total * math.cos(ang) + bow_x, r_total * math.sin(ang) + bow_y, z_curr))
            pt_world = trans_m @ pt_local
            ring.append(bm.verts.new(pt_world))
        trunk_rings.append(ring)

    for si in range(num_slices):
        for ri in range(num_radial):
            rn = (ri + 1) % num_radial
            f = bm.faces.new([trunk_rings[si][ri], trunk_rings[si][rn], trunk_rings[si+1][rn], trunk_rings[si+1][ri]])
            f.material_index = 0

    f_bottom = bm.faces.new([trunk_rings[0][i] for i in reversed(range(num_radial))])
    f_bottom.material_index = 0

    # 2. PHẦN ĐẦU CỌC (TIP)
    bow_top_x = math.sin(math.pi * 0.8 + seed) * 0.028
    bow_top_y = math.cos(math.pi * 0.6 + seed * 1.4) * 0.020
    top_wood_ring = trunk_rings[-1]

    if stake_type == 'carved_wood':
        carve_slices = 12
        carve_dz = tip_length / carve_slices
        carve_rings = []
        base_carve_rad = base_radius * 0.82

        for ci in range(carve_slices + 1):
            z_c = wood_height + ci * carve_dz
            t_c = ci / carve_slices

            r_nom = base_carve_rad * (1.0 - t_c) + 0.005
            c_ring = []
            for ri in range(num_radial):
                ang = (ri / num_radial) * 2.0 * math.pi
                axe_facet = math.cos(ang * 2.5) ** 2 * 0.022 * (1.0 - t_c)
                crack_split = math.sin(ang * 2.0 + seed) * 0.005
                r_final = max(0.004, r_nom * 0.88 + axe_facet + crack_split)
                pt = trans_m @ Vector((r_final * math.cos(ang) + bow_top_x, r_final * math.sin(ang) + bow_top_y, z_c))
                c_ring.append(bm.verts.new(pt))
            carve_rings.append(c_ring)

        for ri in range(num_radial):
            rn = (ri + 1) % num_radial
            f = bm.faces.new([top_wood_ring[ri], top_wood_ring[rn], carve_rings[0][rn], carve_rings[0][ri]])
            f.material_index = 1

        for ci in range(carve_slices):
            for ri in range(num_radial):
                rn = (ri + 1) % num_radial
                f = bm.faces.new([carve_rings[ci][ri], carve_rings[ci][rn], carve_rings[ci+1][rn], carve_rings[ci+1][ri]])
                f.material_index = 1

        tip_wood_vert = bm.verts.new(trans_m @ Vector((bow_top_x, bow_top_y, height + 0.02)))
        for ri in range(num_radial):
            rn = (ri + 1) % num_radial
            f = bm.faces.new([carve_rings[-1][ri], carve_rings[-1][rn], tip_wood_vert])
            f.material_index = 1

    else:
        cap_slices = 12
        cap_dz = tip_length / cap_slices
        cap_rings = []
        base_iron_rad = base_radius * 0.82

        for ci in range(cap_slices + 1):
            z_cap = wood_height + ci * cap_dz
            t_c = ci / cap_slices

            r_c = base_iron_rad * (1.0 - t_c ** 0.85) + 0.004
            if ci == 0:
                r_c += 0.010

            c_ring = []
            for ri in range(num_radial):
                ang = (ri / num_radial) * 2.0 * math.pi
                hammer_facet = math.cos(ang * 4.0) * 0.005 * (1.0 - t_c)
                r_final = max(0.003, r_c + hammer_facet)
                pt = trans_m @ Vector((r_final * math.cos(ang) + bow_top_x, r_final * math.sin(ang) + bow_top_y, z_cap))
                c_ring.append(bm.verts.new(pt))
            cap_rings.append(c_ring)

        for ri in range(num_radial):
            rn = (ri + 1) % num_radial
            f = bm.faces.new([top_wood_ring[ri], top_wood_ring[rn], cap_rings[0][rn], cap_rings[0][ri]])
            f.material_index = 2

        for ci in range(cap_slices):
            for ri in range(num_radial):
                rn = (ri + 1) % num_radial
                f = bm.faces.new([cap_rings[ci][ri], cap_rings[ci][rn], cap_rings[ci+1][rn], cap_rings[ci+1][ri]])
                f.material_index = 2

        tip_vertex = bm.verts.new(trans_m @ Vector((bow_top_x, bow_top_y, height + 0.02)))
        for ri in range(num_radial):
            rn = (ri + 1) % num_radial
            f = bm.faces.new([cap_rings[-1][ri], cap_rings[-1][rn], tip_vertex])
            f.material_index = 2

        # Đai nẹp và đinh tán rèn
        collar_z = wood_height + 0.035
        for di in range(8):
            d_ang = (di / 8.0) * 2.0 * math.pi
            rivet_r = base_iron_rad + 0.012
            rivet_center = trans_m @ Vector((
                rivet_r * math.cos(d_ang) + bow_top_x,
                rivet_r * math.sin(d_ang) + bow_top_y,
                collar_z
            ))
            res = bmesh.ops.create_cone(
                bm, cap_ends=True, segments=6,
                radius1=0.014, radius2=0.014, depth=0.022,
                matrix=Matrix.Translation(rivet_center)
            )
            for v in res['verts']:
                for f in v.link_faces:
                    f.material_index = 2
