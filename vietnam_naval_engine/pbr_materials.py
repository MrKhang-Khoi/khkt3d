import bpy

def get_vietnam_naval_materials():
    mats = {}

    # 1. Gỗ Lim cổ thụ đóng thuyền
    m_wood = bpy.data.materials.new('Mat_GoLim_ThuyenTa')
    m_wood.diffuse_color = (0.20, 0.11, 0.05, 1.0)
    m_wood.use_nodes = True
    nodes = m_wood.node_tree.nodes
    links = m_wood.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = 0.52
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tc = nodes.new('ShaderNodeTexCoord')
    mp = nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0, 16.0, 1.0)
    links.new(tc.outputs['Object'], mp.inputs['Vector'])
    n1 = nodes.new('ShaderNodeTexNoise')
    n1.inputs['Scale'].default_value = 35.0
    n1.inputs['Detail'].default_value = 10.0
    links.new(mp.outputs['Vector'], n1.inputs['Vector'])
    cr = nodes.new('ShaderNodeValToRGB')
    cr.color_ramp.elements[0].position = 0.3
    cr.color_ramp.elements[0].color = (0.12, 0.06, 0.03, 1.0)
    cr.color_ramp.elements[1].position = 0.7
    cr.color_ramp.elements[1].color = (0.28, 0.16, 0.08, 1.0)
    links.new(n1.outputs['Fac'], cr.inputs['Fac'])
    links.new(cr.outputs['Color'], bsdf.inputs['Base Color'])
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.12
    bump.inputs['Distance'].default_value = 0.02
    links.new(n1.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    mats['wood_hull'] = m_wood
    mats['wood_lim'] = m_wood

    # 2. Vải buồm cánh dơi nhuộm củ nâu truyền thống (Sẫm màu da bò, vân dệt thô mộc)
    m_sail = bpy.data.materials.new('Mat_Buom_CanhDoi_CuNau')
    m_sail.diffuse_color = (0.46, 0.28, 0.15, 1.0) # Màu nâu củ nâu đậm chất Việt
    m_sail.use_nodes = True
    ns = m_sail.node_tree.nodes
    ls = m_sail.node_tree.links
    ns.clear()
    out_s = ns.new('ShaderNodeOutputMaterial')
    bsdf_s = ns.new('ShaderNodeBsdfPrincipled')
    bsdf_s.inputs['Roughness'].default_value = 0.88
    ls.new(bsdf_s.outputs['BSDF'], out_s.inputs['Surface'])
    tc_s = ns.new('ShaderNodeTexCoord')
    n_s = ns.new('ShaderNodeTexNoise')
    n_s.inputs['Scale'].default_value = 65.0
    n_s.inputs['Detail'].default_value = 8.0
    ls.new(tc_s.outputs['Object'], n_s.inputs['Vector'])
    cr_s = ns.new('ShaderNodeValToRGB')
    cr_s.color_ramp.elements[0].position = 0.35
    cr_s.color_ramp.elements[0].color = (0.38, 0.22, 0.11, 1.0) # Vết loang củ nâu sẫm
    cr_s.color_ramp.elements[1].position = 0.75
    cr_s.color_ramp.elements[1].color = (0.52, 0.32, 0.18, 1.0) # Sắc nâu cánh gián
    ls.new(n_s.outputs['Fac'], cr_s.inputs['Fac'])
    ls.new(cr_s.outputs['Color'], bsdf_s.inputs['Base Color'])
    bump_s = ns.new('ShaderNodeBump')
    bump_s.inputs['Strength'].default_value = 0.14
    bump_s.inputs['Distance'].default_value = 0.015
    ls.new(n_s.outputs['Fac'], bump_s.inputs['Height'])
    ls.new(bump_s.outputs['Normal'], bsdf_s.inputs['Normal'])
    mats['sail_cloth'] = m_sail

    # 3. Nan tre và ngõng buồm vót cật tre bóng mờ
    m_bamboo = bpy.data.materials.new('Mat_Tre_NanBuom')
    m_bamboo.diffuse_color = (0.68, 0.52, 0.24, 1.0)
    m_bamboo.use_nodes = True
    bsdf_b = m_bamboo.node_tree.nodes.get('Principled BSDF')
    if bsdf_b:
        bsdf_b.inputs['Base Color'].default_value = (0.65, 0.48, 0.22, 1.0)
        bsdf_b.inputs['Roughness'].default_value = 0.45
    mats['bamboo'] = m_bamboo

    # 4. Dây thừng bện gai / xơ dừa
    m_rope = bpy.data.materials.new('Mat_DayThung_Rigging')
    m_rope.diffuse_color = (0.55, 0.45, 0.32, 1.0)
    m_rope.use_nodes = True
    bsdf_r = m_rope.node_tree.nodes.get('Principled BSDF')
    if bsdf_r:
        bsdf_r.inputs['Base Color'].default_value = (0.50, 0.40, 0.28, 1.0)
        bsdf_r.inputs['Roughness'].default_value = 0.90
    mats['rope'] = m_rope

    # 5. Đồng cổ Đông Sơn
    m_bronze = bpy.data.materials.new('Mat_DongCo_DongSon')
    m_bronze.diffuse_color = (0.75, 0.55, 0.22, 1.0)
    m_bronze.use_nodes = True
    bsdf_br = m_bronze.node_tree.nodes.get('Principled BSDF')
    if bsdf_br:
        bsdf_br.inputs['Base Color'].default_value = (0.70, 0.50, 0.20, 1.0)
        bsdf_br.inputs['Metallic'].default_value = 0.88
        bsdf_br.inputs['Roughness'].default_value = 0.35
    mats['bronze'] = m_bronze

    # 6. Sắt rèn cổ (Mũi cọc lim bọc sắt)
    m_iron = bpy.data.materials.new('Mat_SatRen_MuiCoc')
    m_iron.diffuse_color = (0.15, 0.15, 0.17, 1.0)
    m_iron.use_nodes = True
    bsdf_i = m_iron.node_tree.nodes.get('Principled BSDF')
    if bsdf_i:
        bsdf_i.inputs['Base Color'].default_value = (0.14, 0.14, 0.16, 1.0)
        bsdf_i.inputs['Metallic'].default_value = 0.92
        bsdf_i.inputs['Roughness'].default_value = 0.40
    mats['iron'] = m_iron

    # 7. Khiên mây đan sơn then đỏ
    m_shield = bpy.data.materials.new('Mat_KhienMay_SonThen')
    m_shield.diffuse_color = (0.68, 0.14, 0.10, 1.0)
    m_shield.use_nodes = True
    bsdf_sh = m_shield.node_tree.nodes.get('Principled BSDF')
    if bsdf_sh:
        bsdf_sh.inputs['Base Color'].default_value = (0.65, 0.13, 0.09, 1.0)
        bsdf_sh.inputs['Roughness'].default_value = 0.38
    mats['shield'] = m_shield

    # 8. Nước sông Bạch Đằng
    m_water = bpy.data.materials.new('Mat_SongBachDang_Nuoc')
    m_water.diffuse_color = (0.08, 0.22, 0.22, 0.8)
    m_water.use_nodes = True
    bsdf_w = m_water.node_tree.nodes.get('Principled BSDF')
    if bsdf_w:
        bsdf_w.inputs['Base Color'].default_value = (0.05, 0.18, 0.18, 1.0)
        bsdf_w.inputs['Roughness'].default_value = 0.04
        bsdf_w.inputs['Metallic'].default_value = 0.1
        if 'Transmission Weight' in bsdf_w.inputs:
            bsdf_w.inputs['Transmission Weight'].default_value = 0.85
        elif 'Transmission' in bsdf_w.inputs:
            bsdf_w.inputs['Transmission'].default_value = 0.85
        if 'IOR' in bsdf_w.inputs:
            bsdf_w.inputs['IOR'].default_value = 1.333
    mats['river'] = m_water

    return mats
