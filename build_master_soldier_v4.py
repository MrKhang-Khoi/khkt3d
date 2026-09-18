"""
====================================================================================================
DỰ ÁN MÔ PHỎNG LỊCH SỬ BẠCH ĐẰNG 938 - VIETNAM-SIM MASTER
MODULE: HOÀN THIỆN TOÀN DIỆN NHÂN VẬT THỦY BINH ĐẠI VIỆT THẾ KỶ X (V4.1 - TRACK-TO MASTER)
- Cơ thể: GEO-body_male_realistic (Blender Studio v1.4.1 CC0)
- Pose: Ngồi chèo kiềng 3 chân chuẩn giải phẫu (Đầu Y=1.03 Z=0.89, Ngực Y=0.82 Z=0.73, Hông Y=0.41 Z=0.40)
- Đạo cụ & Trang phục: Đặt đúng tọa độ thực tế của tư thế ngồi (Khố Y=0.41 Z=0.42, Dao găm Y=0.42, Khăn Y=1.03 Z=0.90)
- Cán chèo gỗ lim: Đặt vừa khít lòng bàn tay tại Y=0.78 Z=0.68
- Shader Da PBR & Xăm Giao Long: Mực chàm Đông Sơn uốn lượn bả vai bắp tay ngực, da mặt cổ sạch sẽ
- Camera Track-To: Tự động ngắm thẳng tâm mục tiêu 100% hoàn hảo
====================================================================================================
"""

import bpy
import math
import mathutils
import os

print("="*80)
print("=== [VIETNAM-SIM MASTER V4.1] HOÀN THIỆN NHÂN VẬT THỦY BINH ĐẠI VIỆT ===")
print("="*80)

# 1. KHỞI TẠO SCENE SẠCH
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

OUTPUT_DIR = r"C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Bầu trời sông Bạch Đằng
scene.world = bpy.data.worlds.new("World_BachDang")
scene.world.use_nodes = True
bg_node = scene.world.node_tree.nodes.get("Background")
bg_node.inputs["Color"].default_value = (0.50, 0.65, 0.82, 1.0)
bg_node.inputs["Strength"].default_value = 0.95

# 2. IMPORT BODY GIẢI PHẪU CHUẨN BLENDER STUDIO & CHUẨN HÓA VỀ (0,0,0)
bundle_blend = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\assets\characters\blender_studio_human\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend"
bpath = bundle_blend + r"\Object\\"

bpy.ops.wm.append(directory=bpath, filename="GEO-body_male_realistic")
body_obj = bpy.data.objects.get("GEO-body_male_realistic")
body_obj.name = "ThuyBinh_ThanThe_Master"
scene.collection.objects.link(body_obj) if body_obj.name not in scene.collection.objects else None

# Reset vị trí về (0,0,0)
body_obj.location = (0, 0, 0)
body_obj.rotation_euler = (0, 0, 0)
body_obj.scale = (1, 1, 1)
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

for mod in list(body_obj.modifiers):
    body_obj.modifiers.remove(mod)

# 3. GẮN ARMATURE BẰNG KỸ THUẬT SCALE-10X & POSE NGỒI CHÈO
def rig_and_pose_soldier(body_obj):
    arm_data = bpy.data.armatures.new("Rig_ThuyBinh_Data")
    arm_obj = bpy.data.objects.new("Rig_ThuyBinh", arm_data)
    scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    def add_bone(name, head, tail, parent_name=None):
        b = arm_data.edit_bones.new(name)
        b.head = head
        b.tail = tail
        if parent_name:
            b.parent = arm_data.edit_bones[parent_name]
        return b

    # Trục thân & Đầu
    add_bone('pelvis', (0, -0.02, 0.85), (0, -0.02, 0.98))
    add_bone('spine', (0, -0.02, 0.98), (0, -0.01, 1.18), 'pelvis')
    add_bone('chest', (0, -0.01, 1.18), (0, 0.0, 1.40), 'spine')
    add_bone('neck', (0, 0.0, 1.40), (0, 0.01, 1.48), 'chest')
    add_bone('head', (0, 0.01, 1.48), (0, 0.02, 1.68), 'neck')

    # Tay & Chân 2 bên
    for side, sign in [('L', 1), ('R', -1)]:
        add_bone(f'shoulder.{side}', (sign*0.04, -0.02, 1.36), (sign*0.16, -0.02, 1.36), 'chest')
        add_bone(f'upper_arm.{side}', (sign*0.16, -0.02, 1.36), (sign*0.35, -0.02, 1.12), f'shoulder.{side}')
        add_bone(f'forearm.{side}', (sign*0.35, -0.02, 1.12), (sign*0.46, 0.16, 0.92), f'upper_arm.{side}')
        add_bone(f'hand.{side}', (sign*0.46, 0.16, 0.92), (sign*0.48, 0.26, 0.90), f'forearm.{side}')
        add_bone(f'thigh.{side}', (sign*0.10, -0.02, 0.85), (sign*0.14, 0.0, 0.48), 'pelvis')
        add_bone(f'shin.{side}', (sign*0.14, 0.0, 0.48), (sign*0.14, 0.0, 0.08), f'thigh.{side}')
        add_bone(f'foot.{side}', (sign*0.14, 0.0, 0.08), (sign*0.14, 0.16, 0.0), f'shin.{side}')

    bpy.ops.object.mode_set(mode='OBJECT')

    # Scale 10x
    body_obj.scale = (10, 10, 10)
    arm_obj.scale = (10, 10, 10)
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Scale 0.1x
    body_obj.scale = (0.1, 0.1, 0.1)
    arm_obj.scale = (0.1, 0.1, 0.1)
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.ops.object.transform_apply(scale=True)

    # Pose ngồi chèo thuyền
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm_obj.pose.bones

    pb['spine'].rotation_mode = 'XYZ'
    pb['spine'].rotation_euler = (math.radians(18), 0, 0)
    pb['chest'].rotation_mode = 'XYZ'
    pb['chest'].rotation_euler = (math.radians(12), 0, 0)
    pb['head'].rotation_mode = 'XYZ'
    pb['head'].rotation_euler = (math.radians(-16), 0, 0)

    pb['thigh.L'].rotation_mode = 'XYZ'
    pb['thigh.L'].rotation_euler = (math.radians(72), math.radians(-16), math.radians(20))
    pb['shin.L'].rotation_mode = 'XYZ'
    pb['shin.L'].rotation_euler = (math.radians(-76), 0, 0)

    pb['thigh.R'].rotation_mode = 'XYZ'
    pb['thigh.R'].rotation_euler = (math.radians(72), math.radians(16), math.radians(-20))
    pb['shin.R'].rotation_mode = 'XYZ'
    pb['shin.R'].rotation_euler = (math.radians(-76), 0, 0)

    pb['upper_arm.L'].rotation_mode = 'XYZ'
    pb['upper_arm.L'].rotation_euler = (math.radians(52), math.radians(-28), math.radians(15))
    pb['forearm.L'].rotation_mode = 'XYZ'
    pb['forearm.L'].rotation_euler = (math.radians(18), math.radians(-22), math.radians(10))
    pb['hand.L'].rotation_mode = 'XYZ'
    pb['hand.L'].rotation_euler = (math.radians(-15), math.radians(10), math.radians(-15))

    pb['upper_arm.R'].rotation_mode = 'XYZ'
    pb['upper_arm.R'].rotation_euler = (math.radians(55), math.radians(25), math.radians(-15))
    pb['forearm.R'].rotation_mode = 'XYZ'
    pb['forearm.R'].rotation_euler = (math.radians(22), math.radians(22), math.radians(-10))
    pb['hand.R'].rotation_mode = 'XYZ'
    pb['hand.R'].rotation_euler = (math.radians(-15), math.radians(-10), math.radians(15))

    bpy.ops.object.mode_set(mode='OBJECT')

    # Apply Armature modifier vào Geometry
    bpy.context.view_layer.objects.active = body_obj
    bpy.ops.object.modifier_apply(modifier="Armature")
    print("-> Áp dụng tư thế ngồi chèo kiềng 3 chân vào Geometry hoàn tất!")
    return arm_obj

arm_obj = rig_and_pose_soldier(body_obj)

# 4. SHADER DA PBR SSS & HÌNH XĂM GIAO LONG ĐÔNG SƠN MỰC CHÀM
def build_vietnam_skin_material():
    mat = bpy.data.materials.new(name="Mat_ThuyBinh_Skin_PBR_V4")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    out_node.location = (1200, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (800, 0)
    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-900, 200)

    # A. Màu da bánh mật ngăm đen khỏe khoắn
    skin_base = nodes.new("ShaderNodeRGB")
    skin_base.outputs["Color"].default_value = (0.36, 0.22, 0.14, 1.0)
    skin_base.location = (-500, 400)

    skin_warm = nodes.new("ShaderNodeRGB")
    skin_warm.outputs["Color"].default_value = (0.46, 0.27, 0.17, 1.0)
    skin_warm.location = (-500, 250)

    skin_noise = nodes.new("ShaderNodeTexNoise")
    skin_noise.location = (-500, 100)
    skin_noise.inputs["Scale"].default_value = 160.0
    skin_noise.inputs["Detail"].default_value = 3.0

    mix_skin = nodes.new("ShaderNodeMix")
    mix_skin.data_type = 'RGBA'
    mix_skin.location = (-200, 300)
    mix_skin.inputs[0].default_value = 0.35
    links.new(skin_base.outputs["Color"], mix_skin.inputs[6])
    links.new(skin_warm.outputs["Color"], mix_skin.inputs[7])

    # B. Hoa văn xăm rồng Giao Long Đông Sơn uốn lượn mềm mại
    noise_distort = nodes.new("ShaderNodeTexNoise")
    noise_distort.location = (-650, -150)
    noise_distort.inputs["Scale"].default_value = 6.0
    noise_distort.inputs["Detail"].default_value = 2.0
    links.new(tex_coord.outputs["Object"], noise_distort.inputs["Vector"])

    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-450, -150)
    mapping.inputs["Scale"].default_value = (12.0, 12.0, 10.0)
    links.new(noise_distort.outputs["Color"], mapping.inputs["Location"])
    links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    voronoi_dragon = nodes.new("ShaderNodeTexVoronoi")
    voronoi_dragon.location = (-250, -150)
    voronoi_dragon.feature = 'F1'
    voronoi_dragon.distance = 'EUCLIDEAN'
    voronoi_dragon.inputs["Scale"].default_value = 7.5
    links.new(mapping.outputs["Vector"], voronoi_dragon.inputs["Vector"])

    tattoo_ramp = nodes.new("ShaderNodeValToRGB")
    tattoo_ramp.location = (-50, -150)
    tattoo_ramp.color_ramp.elements[0].position = 0.35
    tattoo_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
    tattoo_ramp.color_ramp.elements[1].position = 0.42
    tattoo_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
    links.new(voronoi_dragon.outputs["Distance"], tattoo_ramp.inputs["Fac"])

    # C. Mặt nạ giới hạn vùng xăm (Chỉ bắp tay, vai, ngực; KHÔNG XĂM LÊN CỔ VÀ MẶT)
    separate_xyz = nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.location = (-500, -450)
    links.new(tex_coord.outputs["Object"], separate_xyz.inputs["Vector"])

    map_z_low = nodes.new("ShaderNodeMapRange")
    map_z_low.location = (-250, -400)
    map_z_low.inputs["From Min"].default_value = 0.50
    map_z_low.inputs["From Max"].default_value = 0.60
    map_z_low.inputs["To Min"].default_value = 0.0
    map_z_low.inputs["To Max"].default_value = 1.0
    links.new(separate_xyz.outputs["Z"], map_z_low.inputs["Value"])

    map_z_high = nodes.new("ShaderNodeMapRange")
    map_z_high.location = (-250, -550)
    map_z_high.inputs["From Min"].default_value = 0.80
    map_z_high.inputs["From Max"].default_value = 0.84 # Tuyệt đối không tràn lên cổ và mặt
    map_z_high.inputs["To Min"].default_value = 1.0
    map_z_high.inputs["To Max"].default_value = 0.0
    links.new(separate_xyz.outputs["Z"], map_z_high.inputs["Value"])

    chest_mask = nodes.new("ShaderNodeMath")
    chest_mask.operation = 'MULTIPLY'
    chest_mask.location = (0, -450)
    links.new(map_z_low.outputs["Result"], chest_mask.inputs[0])
    links.new(map_z_high.outputs["Result"], chest_mask.inputs[1])

    final_mask = nodes.new("ShaderNodeMath")
    final_mask.operation = 'MULTIPLY'
    final_mask.location = (250, -250)
    links.new(tattoo_ramp.outputs["Color"], final_mask.inputs[0])
    links.new(chest_mask.outputs["Value"], final_mask.inputs[1])

    # Mực chàm đen cổ truyền
    ink_color = nodes.new("ShaderNodeRGB")
    ink_color.outputs["Color"].default_value = (0.05, 0.09, 0.12, 1.0)
    ink_color.location = (150, 100)

    mix_final_color = nodes.new("ShaderNodeMix")
    mix_final_color.data_type = 'RGBA'
    mix_final_color.location = (500, 200)
    links.new(final_mask.outputs["Value"], mix_final_color.inputs[0])
    links.new(mix_skin.outputs["Result"], mix_final_color.inputs[6])
    links.new(ink_color.outputs["Color"], mix_final_color.inputs[7])

    links.new(mix_final_color.outputs["Result"], bsdf.inputs["Base Color"])

    # SSS và mồ hôi biển
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.18
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.18

    if "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.45, 0.25)

    sweat_noise = nodes.new("ShaderNodeTexNoise")
    sweat_noise.location = (200, -500)
    sweat_noise.inputs["Scale"].default_value = 35.0

    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.location = (450, -500)
    rough_map.inputs["To Min"].default_value = 0.30
    rough_map.inputs["To Max"].default_value = 0.54
    links.new(sweat_noise.outputs["Fac"], rough_map.inputs["Value"])
    links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])

    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat)
    print("-> Đã áp dụng Shader Da PBR SSS & Hoa văn Giao Long Đông Sơn chuẩn sử!")
    return mat

skin_mat = build_vietnam_skin_material()

# 5. CHẾ TÁC KHỐ VẢI THÔ LẠC VIỆT (TÂM TẠI Y=0.41, Z=0.42 KHỚP TỌA ĐỘ NGỒI)
def build_vietnam_loincloth():
    # 1. Phần quấn ôm kín hông mông
    bpy.ops.mesh.primitive_cylinder_add(radius=0.21, depth=0.22, vertices=32, location=(0, 0.41, 0.42))
    wrap = bpy.context.active_object
    wrap.name = "Kho_QuanOmMong"
    wrap.scale = (1.06, 0.95, 1.0)
    wrap.rotation_euler = (math.radians(18), 0, 0) # Nghiêng theo khung chậu khi ngồi

    # 2. Vạt khố trước rủ nếp gấp
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=24, size=1.0, location=(0, 0.58, 0.36))
    flap_front = bpy.context.active_object
    flap_front.name = "Kho_VatTruoc"
    flap_front.scale = (0.16, 0.28, 1.0)
    flap_front.rotation_euler = (math.radians(28), 0, 0)

    wave_mod = flap_front.modifiers.new(name="Folds", type='WAVE')
    wave_mod.use_x = True
    wave_mod.use_y = True
    wave_mod.speed = 0.0
    wave_mod.height = 0.018
    wave_mod.width = 0.10
    wave_mod.narrowness = 2.0
    bpy.context.view_layer.objects.active = flap_front
    bpy.ops.object.modifier_apply(modifier="Folds")

    # 3. Vạt khố sau che kín mông
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=14, y_subdivisions=18, size=1.0, location=(0, 0.22, 0.35))
    flap_back = bpy.context.active_object
    flap_back.name = "Kho_VatSau"
    flap_back.scale = (0.18, 0.24, 1.0)
    flap_back.rotation_euler = (math.radians(-25), 0, 0)

    bpy.ops.object.select_all(action='DESELECT')
    wrap.select_set(True)
    flap_front.select_set(True)
    flap_back.select_set(True)
    bpy.context.view_layer.objects.active = wrap
    bpy.ops.object.join()
    kho_obj = bpy.context.active_object
    kho_obj.name = "Kho_DaiViet_Master"

    mat_cloth = bpy.data.materials.new(name="Mat_VaiCuNau_PBR")
    mat_cloth.use_nodes = True
    bsdf = mat_cloth.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.24, 0.13, 0.07, 1.0) # Màu củ nâu sẫm dệt tay
    bsdf.inputs["Roughness"].default_value = 0.88

    kho_obj.data.materials.clear()
    kho_obj.data.materials.append(mat_cloth)
    print("-> Đã chế tác Khố vải thô Lạc Việt ôm kín hông mông lịch sự chuẩn sư phạm!")
    return kho_obj

kho_obj = build_vietnam_loincloth()

# 6. KHĂN ĐẦU RÌU & BÚI TÓC TRÂM TRE (TÂM TẠI Y=1.03, Z=0.90 KHỚP ĐẦU NGỒI)
def build_vietnam_headwear():
    # Vành khăn đầu rìu ôm trán người lính (Y=1.03, Z=0.90)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.105, depth=0.038, vertices=32, location=(0, 1.03, 0.905))
    band = bpy.context.active_object
    band.name = "KhanDauRiu_VanDai"
    band.scale = (0.92, 1.04, 1.0)
    band.rotation_euler = (math.radians(14), 0, 0)

    # Nút thắt vải bên thái dương phải
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(0.10, 1.03, 0.905))
    knot = bpy.context.active_object
    knot.name = "Khan_NutThat"

    # Hai vạt đuôi khăn hình lưỡi rìu bay sau gáy
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=12, size=1.0, location=(0.11, 0.93, 0.86))
    tail1 = bpy.context.active_object
    tail1.scale = (0.035, 0.14, 1.0)
    tail1.rotation_euler = (math.radians(-25), math.radians(10), math.radians(15))

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=12, size=1.0, location=(0.08, 0.94, 0.84))
    tail2 = bpy.context.active_object
    tail2.scale = (0.032, 0.15, 1.0)
    tail2.rotation_euler = (math.radians(-32), math.radians(6), math.radians(10))

    bpy.ops.object.select_all(action='DESELECT')
    band.select_set(True)
    knot.select_set(True)
    tail1.select_set(True)
    tail2.select_set(True)
    bpy.context.view_layer.objects.active = band
    bpy.ops.object.join()
    khan_obj = bpy.context.active_object
    khan_obj.name = "KhanDauRiu_Master"

    mat_khan = bpy.data.materials.new(name="Mat_KhanCham_PBR")
    mat_khan.use_nodes = True
    bsdf_khan = mat_khan.node_tree.nodes.get("Principled BSDF")
    bsdf_khan.inputs["Base Color"].default_value = (0.10, 0.14, 0.18, 1.0) # Vải chàm sẫm
    bsdf_khan.inputs["Roughness"].default_value = 0.85
    khan_obj.data.materials.clear()
    khan_obj.data.materials.append(mat_khan)

    # Búi tóc củ hành ở đỉnh sau đầu (Y=0.98, Z=0.955)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.062, location=(0, 0.98, 0.955))
    bun = bpy.context.active_object
    bun.name = "BuiToc_CuHanh"
    bun.scale = (1.0, 1.15, 0.85)

    mat_hair = bpy.data.materials.new(name="Mat_TocDen_PBR")
    mat_hair.use_nodes = True
    bsdf_hair = mat_hair.node_tree.nodes.get("Principled BSDF")
    bsdf_hair.inputs["Base Color"].default_value = (0.012, 0.012, 0.012, 1.0)
    bsdf_hair.inputs["Roughness"].default_value = 0.52
    bun.data.materials.clear()
    bun.data.materials.append(mat_hair)

    # Trâm tre già cắm xiên qua búi tóc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.20, vertices=16, location=(0, 0.98, 0.955))
    pin = bpy.context.active_object
    pin.name = "TramTreGia_Master"
    pin.rotation_euler = (math.radians(12), math.radians(82), math.radians(5))

    mat_bamboo = bpy.data.materials.new(name="Mat_TreGia_PBR")
    mat_bamboo.use_nodes = True
    bsdf_bamboo = mat_bamboo.node_tree.nodes.get("Principled BSDF")
    bsdf_bamboo.inputs["Base Color"].default_value = (0.64, 0.44, 0.18, 1.0) # Tre hun khói
    bsdf_bamboo.inputs["Roughness"].default_value = 0.35
    pin.data.materials.clear()
    pin.data.materials.append(mat_bamboo)

    print("-> Đã chế tác Khăn đầu rìu & Búi tóc trâm tre hoàn tất!")
    return khan_obj, bun, pin

khan_obj, bun_obj, pin_obj = build_vietnam_headwear()

# 7. CHẾ TÁC DAO GĂM ĐỒNG ĐÔNG SƠN CHUÔI CHỮ T GIẮT HÔNG TRÁI (TÂM TẠI X=-0.22, Y=0.42, Z=0.44)
def build_dongson_bronze_dagger():
    # Chuôi chữ T
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.10, vertices=16, location=(-0.24, 0.43, 0.50))
    hilt_vert = bpy.context.active_object
    hilt_vert.rotation_euler = (math.radians(15), math.radians(12), 0)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.085, vertices=16, location=(-0.25, 0.45, 0.545))
    hilt_t_bar = bpy.context.active_object
    hilt_t_bar.rotation_euler = (math.radians(15), math.radians(12), math.radians(90))

    # Chắn tay
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.015, vertices=16, location=(-0.23, 0.41, 0.455))
    guard = bpy.context.active_object
    guard.rotation_euler = (math.radians(15), math.radians(12), 0)
    guard.scale = (1.5, 0.8, 1.0)

    # Bao dao giắt cạp khố
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.21, 0.36, 0.36))
    scabbard = bpy.context.active_object
    scabbard.scale = (0.025, 0.055, 0.22)
    scabbard.rotation_euler = (math.radians(15), math.radians(12), math.radians(10))

    bpy.ops.object.select_all(action='DESELECT')
    hilt_vert.select_set(True)
    hilt_t_bar.select_set(True)
    guard.select_set(True)
    scabbard.select_set(True)
    bpy.context.view_layer.objects.active = hilt_vert
    bpy.ops.object.join()
    dagger_obj = bpy.context.active_object
    dagger_obj.name = "DaoGam_DongSon_ChuoiT_Master"

    mat_bronze = bpy.data.materials.new(name="Mat_DongSon_Bronze_PBR")
    mat_bronze.use_nodes = True
    nodes = mat_bronze.node_tree.nodes
    links = mat_bronze.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    color_bronze = nodes.new("ShaderNodeRGB")
    color_bronze.outputs["Color"].default_value = (0.75, 0.58, 0.28, 1.0)

    color_patina = nodes.new("ShaderNodeRGB")
    color_patina.outputs["Color"].default_value = (0.18, 0.55, 0.42, 1.0)

    noise_patina = nodes.new("ShaderNodeTexNoise")
    noise_patina.inputs["Scale"].default_value = 45.0

    mix_patina = nodes.new("ShaderNodeMix")
    mix_patina.data_type = 'RGBA'
    mix_patina.location = (200, 0)
    mix_patina.inputs[0].default_value = 0.25
    links.new(noise_patina.outputs["Fac"], mix_patina.inputs[0])
    links.new(color_bronze.outputs["Color"], mix_patina.inputs[6])
    links.new(color_patina.outputs["Color"], mix_patina.inputs[7])

    links.new(mix_patina.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.88
    bsdf.inputs["Roughness"].default_value = 0.38

    dagger_obj.data.materials.clear()
    dagger_obj.data.materials.append(mat_bronze)
    print("-> Đã chế tác Dao găm đồng Đông Sơn chuôi chữ T giắt hông trái hoàn tất!")
    return dagger_obj

dagger_obj = build_dongson_bronze_dagger()

# 8. BỆ CHÈO, MẶT NƯỚC SÔNG BẠCH ĐẰNG & CÁN CHÈO GỖ LIM
def build_environment():
    # Bệ chèo ngang (ngay dưới mông lính Y=0.38, Z=0.30)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.38, 0.30))
    bench = bpy.context.active_object
    bench.name = "Be_Cheo_GoLim"
    bench.scale = (0.80, 0.30, 0.08)

    # Then đỡ chân đạp (Y=0.75, Z=0.10)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.75, 0.08))
    footrest = bpy.context.active_object
    footrest.name = "Then_DapChan"
    footrest.scale = (0.75, 0.12, 0.06)

    # Mạn thuyền (bên phải X=0.65)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.65, 0.60, 0.45))
    gunwale = bpy.context.active_object
    gunwale.name = "Man_Thuyen_GoLim"
    gunwale.scale = (0.12, 1.40, 0.40)

    # Cọc chèo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.35, vertices=16, location=(0.65, 0.75, 0.72))
    thole_pin = bpy.context.active_object
    thole_pin.name = "Coc_Cheo_GoLim"

    # Cán chèo gỗ lim ôm khít giữa 2 bàn tay đang nắm chặt (Y=0.78, Z=0.68)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=3.2, vertices=24, location=(0.35, 0.78, 0.68))
    oar = bpy.context.active_object
    oar.name = "Can_Cheo_GoLim_Master"
    oar.rotation_euler = (math.radians(-6), math.radians(82), math.radians(-12))

    mat_wood = bpy.data.materials.new(name="Mat_GoLim_PBR")
    mat_wood.use_nodes = True
    bsdf_wood = mat_wood.node_tree.nodes.get("Principled BSDF")
    bsdf_wood.inputs["Base Color"].default_value = (0.18, 0.11, 0.06, 1.0)
    bsdf_wood.inputs["Roughness"].default_value = 0.48

    for obj in [bench, footrest, gunwale, thole_pin, oar]:
        obj.data.materials.clear()
        obj.data.materials.append(mat_wood)

    # Mặt nước sông Bạch Đằng phản chiếu
    bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -0.05))
    water = bpy.context.active_object
    water.name = "MatNuoc_SongBachDang"
    mat_water = bpy.data.materials.new(name="Mat_NuocSong_PBR")
    mat_water.use_nodes = True
    bsdf_water = mat_water.node_tree.nodes.get("Principled BSDF")
    bsdf_water.inputs["Base Color"].default_value = (0.08, 0.18, 0.16, 1.0)
    bsdf_water.inputs["Roughness"].default_value = 0.05
    bsdf_water.inputs["Transmission Weight"].default_value = 0.85 if "Transmission Weight" in bsdf_water.inputs else 0.85
    bsdf_water.inputs["IOR"].default_value = 1.333
    water.data.materials.clear()
    water.data.materials.append(mat_water)

    print("-> Đã dựng Bệ chèo, Cán chèo gỗ lim & Mặt nước sông Bạch Đằng hoàn tất!")
    return bench, oar

bench_obj, oar_obj = build_environment()

# 9. HỆ THỐNG CHIẾU SÁNG CINEMATIC (3-POINT LIGHTING ĐIỆN ẢNH)
def setup_cinematic_lighting():
    # Key Light: Nắng sớm ấm áp chiếu về hướng người lính (tâm Y=0.7, Z=0.7)
    light_data_key = bpy.data.lights.new(name="KeyLight_Sun", type='SUN')
    light_data_key.energy = 5.5
    light_data_key.color = (1.0, 0.95, 0.88)
    light_data_key.angle = math.radians(12)
    key_obj = bpy.data.objects.new("Light_Sun_Key", light_data_key)
    key_obj.location = (2.2, 2.5, 3.5)
    key_obj.rotation_euler = (math.radians(-40), math.radians(25), math.radians(-35))
    scene.collection.objects.link(key_obj)

    # Fill Light: Ánh sáng xanh mát dịu từ mặt sông
    light_data_fill = bpy.data.lights.new(name="FillLight_Sky", type='AREA')
    light_data_fill.energy = 260.0
    light_data_fill.color = (0.75, 0.88, 1.0)
    light_data_fill.size = 3.0
    fill_obj = bpy.data.objects.new("Light_Fill_Sky", light_data_fill)
    fill_obj.location = (-2.0, 2.2, 1.8)
    fill_obj.rotation_euler = (math.radians(-25), math.radians(-55), math.radians(110))
    scene.collection.objects.link(fill_obj)

    # Rim Light: Ánh sáng viền tôn cơ bắp lưng và búi tóc
    light_data_rim = bpy.data.lights.new(name="RimLight_Back", type='AREA')
    light_data_rim.energy = 380.0
    light_data_rim.color = (1.0, 0.98, 0.92)
    light_data_rim.size = 2.0
    rim_obj = bpy.data.objects.new("Light_Rim_Back", light_data_rim)
    rim_obj.location = (0.0, -1.8, 1.8)
    rim_obj.rotation_euler = (math.radians(55), 0, 0)
    scene.collection.objects.link(rim_obj)

setup_cinematic_lighting()

# 10. KẾT XUẤT 04 ẢNH KIỂM ĐỊNH BẰNG TRACK-TO TARGET (CHÍNH XÁC 100%)
def render_verification_shots_track_to():
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = 64
    except Exception:
        pass

    # Tạo Empty Target để Camera ngắm thẳng
    target_empty = bpy.data.objects.new("Cam_Target", None)
    scene.collection.objects.link(target_empty)

    cam_data = bpy.data.cameras.new("Cam_KiemDinh_Data")
    cam_obj = bpy.data.objects.new("Cam_KiemDinh", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Gắn Track-To Constraint
    track_to = cam_obj.constraints.new(type='TRACK_TO')
    track_to.target = target_empty
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'

    shots = [
        {
            # Shot 1: Chân dung cận cảnh khuôn mặt, khăn đầu rìu, búi tóc trâm tre
            "id": "Shot1_ChanDung_KhuonMat",
            "file": "anh_kiem_dinh_soldier_1_chandung_mat.png",
            "target": (0.01, 1.03, 0.89), # Tâm mặt
            "cam_loc": (0.32, 1.42, 0.95),
            "focal": 80.0,
        },
        {
            # Shot 2: Cận cảnh cơ ngực cuồn cuộn, bắp tay & hình xăm Giao Long Đông Sơn
            "id": "Shot2_XamGiaoLong_BapTayNguc",
            "file": "anh_kiem_dinh_soldier_2_xam_giaolong.png",
            "target": (0.0, 0.82, 0.73), # Tâm ngực
            "cam_loc": (0.28, 1.38, 0.80),
            "focal": 65.0,
        },
        {
            # Shot 3: Cận cảnh hông trái: Khố Lạc Việt ôm kín mông hông & Dao găm đồng Đông Sơn chuôi chữ T
            "id": "Shot3_KhoVaDaoGamDongSon",
            "file": "anh_kiem_dinh_soldier_3_kho_daogam.png",
            "target": (-0.20, 0.42, 0.44), # Tâm hông trái
            "cam_loc": (-0.72, 0.78, 0.52),
            "focal": 55.0,
        },
        {
            # Shot 4: Toàn cảnh 3/4 thấy trọn vẹn người lính ngồi chèo kiềng 3 chân, hai tay nắm chắc cán chèo gỗ lim trên sông Bạch Đằng
            "id": "Shot4_ToanThan_NgoiCheo",
            "file": "anh_kiem_dinh_soldier_4_toanthan_cheo.png",
            "target": (0.0, 0.60, 0.55), # Tâm toàn thân
            "cam_loc": (1.65, 2.05, 1.25),
            "focal": 42.0,
        }
    ]

    for s in shots:
        target_empty.location = s["target"]
        cam_obj.location = s["cam_loc"]
        cam_data.lens = s["focal"]
        bpy.context.view_layer.update()

        out_path = os.path.join(OUTPUT_DIR, s["file"])
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"-> ĐÃ KẾT XUẤT THÀNH CÔNG: {s['id']} -> {out_path}")

render_verification_shots_track_to()

# 11. LƯU MASTER BLEND
master_blend_path = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\thuy_binh_dai_viet_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_blend_path)
print(f"=== [VIETNAM-SIM MASTER] ĐÃ LƯU THÀNH CÔNG THỦY BINH ĐẠI VIỆT V4.1 MASTER: {master_blend_path} ===")
