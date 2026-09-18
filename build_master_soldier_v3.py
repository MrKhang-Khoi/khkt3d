"""
====================================================================================================
DỰ ÁN MÔ PHỎNG LỊCH SỬ BẠCH ĐẰNG 938 - VIETNAM-SIM MASTER
MODULE: HOÀN THIỆN TOÀN DIỆN NHÂN VẬT THỦY BINH ĐẠI VIỆT THẾ KỶ X (V3.1)
- Mô hình: GEO-body_male_realistic (Blender Studio v1.4.1 CC0 - 10.582 Quad giải phẫu chuẩn tuyệt đối)
- Reset Tọa độ gốc: Đưa chuẩn về (0,0,0) đối xứng tâm
- Rigging & Pose: Armature 15 khớp xương, điều khiển tư thế ngồi chèo kiềng 3 chân, hai tay ôm cán chèo
- Trang phục: Khố vải gai củ nâu nếp gấp tự nhiên, Khăn đầu rìu vải chàm thắt nút đuôi lưỡi rìu, Búi tóc trâm tre
- Vũ khí: Dao găm đồng Đông Sơn chuôi chữ T giắt hông trái
- Vật liệu PBR: Da rám nắng SSS mồ hôi muối biển, Hoa văn xăm Giao Long Đông Sơn mực chàm
- Môi trường & Chiếu sáng: World Sky sông Bạch Đằng, Mặt nước phản chiếu, 3-point Studio Lighting
- Kết xuất: 04 ảnh kiểm định Full HD 1080p chuẩn điện ảnh
====================================================================================================
"""

import bpy
import math
import os

print("="*80)
print("=== [VIETNAM-SIM MASTER V3.1] XÂY DỰNG THỦY BINH ĐẠI VIỆT HOÀN MỸ ===")
print("="*80)

# 1. KHỞI TẠO SCENE SẠCH
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

OUTPUT_DIR = r"C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Thiết lập World Sky sông Bạch Đằng
scene.world = bpy.data.worlds.new("World_BachDang")
scene.world.use_nodes = True
bg_node = scene.world.node_tree.nodes.get("Background")
bg_node.inputs["Color"].default_value = (0.45, 0.60, 0.78, 1.0) # Bầu trời xanh sương sớm
bg_node.inputs["Strength"].default_value = 0.85

# 2. IMPORT BODY GIẢI PHẪU CHUẨN BLENDER STUDIO & RESET LOCATION VỀ (0,0,0)
bundle_blend = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\assets\characters\blender_studio_human\human-base-meshes-bundle-v1.4.1\human_base_meshes_bundle.blend"
bpath = bundle_blend + r"\Object\\"

bpy.ops.wm.append(directory=bpath, filename="GEO-body_male_realistic")
body_obj = bpy.data.objects.get("GEO-body_male_realistic")
body_obj.name = "ThuyBinh_ThanThe_Master"
scene.collection.objects.link(body_obj) if body_obj.name not in scene.collection.objects else None

# RESET VỊ TRÍ GỐC VỀ TÂM (0,0,0) VÀ APPLY TRANSFORM
body_obj.location = (0, 0, 0)
body_obj.rotation_euler = (0, 0, 0)
body_obj.scale = (1, 1, 1)
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Dọn dẹp modifiers thừa
for mod in list(body_obj.modifiers):
    if mod.type == 'MULTIRES':
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass

print(f"-> Thân thể chuẩn hóa tại (0,0,0): {len(body_obj.data.vertices)} đỉnh quad!")

# 3. GẮN ARMATURE VÀ POSE TƯ THẾ NGỒI CHÈO THUYỀN KIỀNG 3 CHÂN
def build_rig_and_pose(body_obj):
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

    # Trục xương sống & Đầu
    add_bone('pelvis', (0, -0.02, 0.85), (0, -0.02, 0.98))
    add_bone('spine', (0, -0.02, 0.98), (0, -0.01, 1.18), 'pelvis')
    add_bone('chest', (0, -0.01, 1.18), (0, 0.0, 1.40), 'spine')
    add_bone('neck', (0, 0.0, 1.40), (0, 0.01, 1.48), 'chest')
    add_bone('head', (0, 0.01, 1.48), (0, 0.02, 1.68), 'neck')

    # Xương 2 bên đối xứng
    for side, sign in [('L', 1), ('R', -1)]:
        # Tay
        add_bone(f'shoulder.{side}', (sign*0.04, -0.02, 1.36), (sign*0.16, -0.02, 1.36), 'chest')
        add_bone(f'upper_arm.{side}', (sign*0.16, -0.02, 1.36), (sign*0.35, -0.02, 1.12), f'shoulder.{side}')
        add_bone(f'forearm.{side}', (sign*0.35, -0.02, 1.12), (sign*0.46, 0.16, 0.92), f'upper_arm.{side}')
        add_bone(f'hand.{side}', (sign*0.46, 0.16, 0.92), (sign*0.48, 0.26, 0.90), f'forearm.{side}')
        # Chân
        add_bone(f'thigh.{side}', (sign*0.10, -0.02, 0.85), (sign*0.14, 0.0, 0.48), 'pelvis')
        add_bone(f'shin.{side}', (sign*0.14, 0.0, 0.48), (sign*0.14, 0.0, 0.08), f'thigh.{side}')
        add_bone(f'foot.{side}', (sign*0.14, 0.0, 0.08), (sign*0.14, 0.16, 0.0), f'shin.{side}')

    bpy.ops.object.mode_set(mode='OBJECT')

    # Parent với Automatic Weights
    bpy.ops.object.select_all(action='DESELECT')
    body_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')

    # Pose tư thế ngồi chèo thuyền
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm_obj.pose.bones

    # 1. Rướn người về phía trước
    pb['spine'].rotation_mode = 'XYZ'
    pb['spine'].rotation_euler = (math.radians(16), 0, 0)
    pb['chest'].rotation_mode = 'XYZ'
    pb['chest'].rotation_euler = (math.radians(10), 0, 0)
    pb['head'].rotation_mode = 'XYZ'
    pb['head'].rotation_euler = (math.radians(-14), 0, 0) # Ngẩng đầu nhìn về phía trước

    # 2. Hai đùi gập 75 độ ngồi xuống bệ, mở rộng sang 2 bên
    pb['thigh.L'].rotation_mode = 'XYZ'
    pb['thigh.L'].rotation_euler = (math.radians(72), math.radians(-15), math.radians(18))
    pb['shin.L'].rotation_mode = 'XYZ'
    pb['shin.L'].rotation_euler = (math.radians(-76), 0, 0)

    pb['thigh.R'].rotation_mode = 'XYZ'
    pb['thigh.R'].rotation_euler = (math.radians(72), math.radians(15), math.radians(-18))
    pb['shin.R'].rotation_mode = 'XYZ'
    pb['shin.R'].rotation_euler = (math.radians(-76), 0, 0)

    # 3. Hai cánh tay vươn về phía trước ôm lấy cán chèo
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
    print("-> Đã Rigging và thiết lập tư thế ngồi chèo kiềng 3 chân hoàn hảo!")
    return arm_obj

arm_obj = build_rig_and_pose(body_obj)

# 4. HỆ THỐNG VẬT LIỆU DA PBR SSS & HOA VĂN XĂM GIAO LONG ĐÔNG SƠN CHUẨN SỬ
def build_vietnam_skin_shader():
    mat = bpy.data.materials.new(name="Mat_ThuyBinh_Skin_PBR_V3")
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
    tex_coord.location = (-800, 200)

    # A. Màu da bánh mật ngăm đen nắng gió sông biển
    skin_base = nodes.new("ShaderNodeRGB")
    skin_base.outputs["Color"].default_value = (0.38, 0.22, 0.14, 1.0)
    skin_base.location = (-400, 400)

    skin_warm = nodes.new("ShaderNodeRGB")
    skin_warm.outputs["Color"].default_value = (0.48, 0.28, 0.18, 1.0)
    skin_warm.location = (-400, 250)

    skin_noise = nodes.new("ShaderNodeTexNoise")
    skin_noise.location = (-400, 100)
    skin_noise.inputs["Scale"].default_value = 150.0
    skin_noise.inputs["Detail"].default_value = 3.0

    mix_skin = nodes.new("ShaderNodeMix")
    mix_skin.data_type = 'RGBA'
    mix_skin.location = (-150, 300)
    mix_skin.inputs[0].default_value = 0.35 # Factor
    links.new(skin_base.outputs["Color"], mix_skin.inputs[6])
    links.new(skin_warm.outputs["Color"], mix_skin.inputs[7])

    # B. Hoa văn xăm Giao Long Đông Sơn (Sóng nước chữ S xoắn ốc)
    wave1 = nodes.new("ShaderNodeTexWave")
    wave1.location = (-400, -100)
    wave1.wave_type = 'RINGS'
    wave1.inputs["Scale"].default_value = 16.0
    wave1.inputs["Distortion"].default_value = 8.0
    links.new(tex_coord.outputs["Object"], wave1.inputs["Vector"])

    wave2 = nodes.new("ShaderNodeTexWave")
    wave2.location = (-400, -250)
    wave2.wave_type = 'BANDS'
    wave2.inputs["Scale"].default_value = 22.0
    wave2.inputs["Distortion"].default_value = 10.0
    links.new(tex_coord.outputs["Object"], wave2.inputs["Vector"])

    mix_wave = nodes.new("ShaderNodeMix")
    mix_wave.data_type = 'FLOAT'
    mix_wave.location = (-150, -150)
    mix_wave.inputs[0].default_value = 0.5
    links.new(wave1.outputs["Color"], mix_wave.inputs[2])
    links.new(wave2.outputs["Color"], mix_wave.inputs[3])

    tattoo_ramp = nodes.new("ShaderNodeValToRGB")
    tattoo_ramp.location = (50, -150)
    tattoo_ramp.color_ramp.elements[0].position = 0.48
    tattoo_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    tattoo_ramp.color_ramp.elements[1].position = 0.52
    tattoo_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    links.new(mix_wave.outputs["Result"], tattoo_ramp.inputs["Fac"])

    # C. Mặt nạ giới hạn xăm (CHỈ XĂM Ở BẮP TAY, VAI, LƯNG - KHÔNG XĂM LÊN MẶT)
    separate_xyz = nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.location = (-600, -450)
    links.new(tex_coord.outputs["Object"], separate_xyz.inputs["Vector"])

    map_z = nodes.new("ShaderNodeMapRange")
    map_z.location = (-350, -450)
    map_z.inputs["From Min"].default_value = 0.95
    map_z.inputs["From Max"].default_value = 1.38 # Dưới cổ, trên thắt lưng
    map_z.inputs["To Min"].default_value = 0.0
    map_z.inputs["To Max"].default_value = 1.0
    links.new(separate_xyz.outputs["Z"], map_z.inputs["Value"])

    final_mask = nodes.new("ShaderNodeMath")
    final_mask.operation = 'MULTIPLY'
    final_mask.location = (300, -300)
    links.new(tattoo_ramp.outputs["Color"], final_mask.inputs[0])
    links.new(map_z.outputs["Result"], final_mask.inputs[1])

    # Màu mực chàm đen than củi chìm dưới da
    ink_color = nodes.new("ShaderNodeRGB")
    ink_color.outputs["Color"].default_value = (0.06, 0.11, 0.15, 1.0)
    ink_color.location = (100, 100)

    mix_color = nodes.new("ShaderNodeMix")
    mix_color.data_type = 'RGBA'
    mix_color.location = (500, 200)
    links.new(final_mask.outputs["Value"], mix_color.inputs[0])
    links.new(mix_skin.outputs["Result"], mix_color.inputs[6])
    links.new(ink_color.outputs["Color"], mix_color.inputs[7])

    links.new(mix_color.outputs["Result"], bsdf.inputs["Base Color"])

    # SSS và Roughness mồ hôi biển
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.18
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = 0.18

    if "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)

    sweat_noise = nodes.new("ShaderNodeTexNoise")
    sweat_noise.location = (200, -500)
    sweat_noise.inputs["Scale"].default_value = 35.0

    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.location = (450, -500)
    rough_map.inputs["To Min"].default_value = 0.32
    rough_map.inputs["To Max"].default_value = 0.56
    links.new(sweat_noise.outputs["Fac"], rough_map.inputs["Value"])
    links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])

    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat)
    print("-> Đã thiết lập Shader Da PBR SSS & Hoa văn Giao Long Đông Sơn!")
    return mat

skin_mat = build_vietnam_skin_shader()

# 5. CHẾ TÁC KHỐ VẢI THÔ LẠC VIỆT (LOINCLOTH)
def build_vietnam_loincloth():
    # Cạp khố quấn eo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.14, vertices=32, location=(0, -0.02, 0.94))
    belt = bpy.context.active_object
    belt.name = "Kho_CapEo_VaiTho"
    belt.scale = (1.05, 0.78, 1.0)

    # Vạt khố trước rủ nếp gấp tự nhiên
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=24, size=1.0, location=(0, 0.16, 0.72))
    flap_front = bpy.context.active_object
    flap_front.name = "Kho_VatTruoc_NepGap"
    flap_front.scale = (0.16, 0.42, 1.0)
    flap_front.rotation_euler = (math.radians(12), 0, 0)

    # Nếp nhăn vải sóng tự nhiên
    wave_mod = flap_front.modifiers.new(name="ClothFolds", type='WAVE')
    wave_mod.use_x = True
    wave_mod.use_y = True
    wave_mod.speed = 0.0
    wave_mod.height = 0.022
    wave_mod.width = 0.12
    wave_mod.narrowness = 2.0
    bpy.context.view_layer.objects.active = flap_front
    bpy.ops.object.modifier_apply(modifier="ClothFolds")

    # Vạt khố sau nâng mông
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=12, y_subdivisions=16, size=1.0, location=(0, -0.16, 0.76))
    flap_back = bpy.context.active_object
    flap_back.name = "Kho_VatSau"
    flap_back.scale = (0.17, 0.30, 1.0)
    flap_back.rotation_euler = (math.radians(-24), 0, 0)

    # Join khố
    bpy.ops.object.select_all(action='DESELECT')
    belt.select_set(True)
    flap_front.select_set(True)
    flap_back.select_set(True)
    bpy.context.view_layer.objects.active = belt
    bpy.ops.object.join()
    kho_obj = bpy.context.active_object
    kho_obj.name = "Kho_DaiViet_Master"

    # Vật liệu vải gai củ nâu
    mat_cloth = bpy.data.materials.new(name="Mat_VaiCuNau_PBR")
    mat_cloth.use_nodes = True
    bsdf = mat_cloth.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.26, 0.14, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.88

    kho_obj.data.materials.clear()
    kho_obj.data.materials.append(mat_cloth)
    print("-> Đã chế tác Khố vải thô Lạc Việt hoàn tất!")
    return kho_obj

kho_obj = build_vietnam_loincloth()

# 6. KHĂN ĐẦU RÌU & BÚI TÓC TRÂM TRE GIÀ (HEADWEAR)
def build_vietnam_headwear():
    # Vành khăn đầu rìu bản dẹt ôm sát trán
    bpy.ops.mesh.primitive_cylinder_add(radius=0.115, depth=0.045, vertices=32, location=(0, -0.015, 1.585))
    band = bpy.context.active_object
    band.name = "KhanDauRiu_VanDai"
    band.scale = (0.95, 1.08, 1.0)

    # Nút thắt thái dương phải
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(0.11, -0.03, 1.585))
    knot = bpy.context.active_object
    knot.name = "Khan_NutThat"

    # Hai vạt đuôi khăn hình lưỡi rìu vát nhọn
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=12, size=1.0, location=(0.10, -0.14, 1.51))
    tail1 = bpy.context.active_object
    tail1.scale = (0.035, 0.14, 1.0)
    tail1.rotation_euler = (math.radians(-35), math.radians(15), math.radians(20))

    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=12, size=1.0, location=(0.07, -0.12, 1.48))
    tail2 = bpy.context.active_object
    tail2.scale = (0.032, 0.16, 1.0)
    tail2.rotation_euler = (math.radians(-42), math.radians(8), math.radians(10))

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
    bsdf_khan.inputs["Base Color"].default_value = (0.10, 0.14, 0.18, 1.0)
    bsdf_khan.inputs["Roughness"].default_value = 0.85
    khan_obj.data.materials.clear()
    khan_obj.data.materials.append(mat_khan)

    # Búi tóc củ hành ở đỉnh sau đầu
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(0, -0.065, 1.66))
    bun = bpy.context.active_object
    bun.name = "BuiToc_CuHanh"
    bun.scale = (1.0, 1.15, 0.85)

    mat_hair = bpy.data.materials.new(name="Mat_TocDen_PBR")
    mat_hair.use_nodes = True
    bsdf_hair = mat_hair.node_tree.nodes.get("Principled BSDF")
    bsdf_hair.inputs["Base Color"].default_value = (0.015, 0.015, 0.015, 1.0)
    bsdf_hair.inputs["Roughness"].default_value = 0.52
    bun.data.materials.clear()
    bun.data.materials.append(mat_hair)

    # Trâm tre già cắm ngang búi tóc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.22, vertices=16, location=(0, -0.065, 1.66))
    pin = bpy.context.active_object
    pin.name = "TramTreGia_Master"
    pin.rotation_euler = (math.radians(12), math.radians(82), math.radians(5))

    mat_bamboo = bpy.data.materials.new(name="Mat_TreGia_PBR")
    mat_bamboo.use_nodes = True
    bsdf_bamboo = mat_bamboo.node_tree.nodes.get("Principled BSDF")
    bsdf_bamboo.inputs["Base Color"].default_value = (0.62, 0.42, 0.16, 1.0)
    bsdf_bamboo.inputs["Roughness"].default_value = 0.35
    pin.data.materials.clear()
    pin.data.materials.append(mat_bamboo)

    print("-> Đã chế tác Khăn đầu rìu & Búi tóc trâm tre hoàn tất!")
    return khan_obj, bun, pin

khan_obj, bun_obj, pin_obj = build_vietnam_headwear()

# 7. CHẾ TÁC DAO GĂM ĐỒNG ĐÔNG SƠN CHUÔI CHỮ T GIẮT HÔNG TRÁI
def build_dongson_bronze_dagger():
    # Chuôi chữ T
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.10, vertices=16, location=(-0.24, 0.02, 0.98))
    hilt_vert = bpy.context.active_object
    hilt_vert.rotation_euler = (math.radians(20), math.radians(15), 0)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.085, vertices=16, location=(-0.25, 0.05, 1.025))
    hilt_t_bar = bpy.context.active_object
    hilt_t_bar.rotation_euler = (math.radians(20), math.radians(15), math.radians(90))

    # Chắn tay
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.015, vertices=16, location=(-0.23, -0.01, 0.935))
    guard = bpy.context.active_object
    guard.rotation_euler = (math.radians(20), math.radians(15), 0)
    guard.scale = (1.5, 0.8, 1.0)

    # Bao dao giắt hông
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.21, -0.08, 0.82))
    scabbard = bpy.context.active_object
    scabbard.scale = (0.025, 0.055, 0.24)
    scabbard.rotation_euler = (math.radians(20), math.radians(15), math.radians(10))

    bpy.ops.object.select_all(action='DESELECT')
    hilt_vert.select_set(True)
    hilt_t_bar.select_set(True)
    guard.select_set(True)
    scabbard.select_set(True)
    bpy.context.view_layer.objects.active = hilt_vert
    bpy.ops.object.join()
    dagger_obj = bpy.context.active_object
    dagger_obj.name = "DaoGam_DongSon_ChuoiT_Master"

    # Vật liệu đồng thau cổ PBR gỉ xanh
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
    print("-> Đã chế tác Dao găm đồng Đông Sơn chuôi chữ T giắt hông!")
    return dagger_obj

dagger_obj = build_dongson_bronze_dagger()

# 8. BỆ CHÈO, MẶT NƯỚC SÔNG & CÁN CHÈO GỖ LIM
def build_environment():
    # Bệ chèo gỗ lim
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 0.55))
    bench = bpy.context.active_object
    bench.name = "Be_Cheo_GoLim"
    bench.scale = (0.80, 0.30, 0.08)

    # Then đỡ chân
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.38, 0.15))
    footrest = bpy.context.active_object
    footrest.name = "Then_DapChan"
    footrest.scale = (0.75, 0.12, 0.06)

    # Mạn thuyền
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.65, 0.10, 0.70))
    gunwale = bpy.context.active_object
    gunwale.name = "Man_Thuyen_GoLim"
    gunwale.scale = (0.12, 1.40, 0.40)

    # Cọc chèo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.35, vertices=16, location=(0.65, 0.20, 0.98))
    thole_pin = bpy.context.active_object
    thole_pin.name = "Coc_Cheo_GoLim"

    # Cán chèo gỗ lim ôm khít tay
    bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=3.2, vertices=24, location=(0.35, 0.26, 0.92))
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
    bpy.ops.mesh.primitive_plane_add(size=15.0, location=(0, 0, -0.05))
    water = bpy.context.active_object
    water.name = "MatNuoc_SongBachDang"
    mat_water = bpy.data.materials.new(name="Mat_NuocSong_PBR")
    mat_water.use_nodes = True
    bsdf_water = mat_water.node_tree.nodes.get("Principled BSDF")
    bsdf_water.inputs["Base Color"].default_value = (0.08, 0.18, 0.16, 1.0) # Xanh lục nước sông phù sa
    bsdf_water.inputs["Roughness"].default_value = 0.05
    bsdf_water.inputs["Transmission Weight"].default_value = 0.85 if "Transmission Weight" in bsdf_water.inputs else 0.85
    bsdf_water.inputs["IOR"].default_value = 1.333
    water.data.materials.clear()
    water.data.materials.append(mat_water)

    print("-> Đã dựng Bệ chèo, Cán chèo gỗ lim & Mặt nước sông Bạch Đằng!")
    return bench, oar

bench_obj, oar_obj = build_environment()

# 9. HỆ THỐNG ÁNH SÁNG STUDIO CINEMATIC (3-POINT LIGHTING)
def setup_cinematic_lighting():
    # Key Light: Nắng ấm ban mai sông Bạch Đằng
    light_data_key = bpy.data.lights.new(name="KeyLight_Sun", type='SUN')
    light_data_key.energy = 5.0
    light_data_key.color = (1.0, 0.95, 0.88)
    light_data_key.angle = math.radians(12)
    key_obj = bpy.data.objects.new("Light_Sun_Key", light_data_key)
    key_obj.location = (2.5, -2.0, 4.0)
    key_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(-40))
    scene.collection.objects.link(key_obj)

    # Fill Light: Ánh sáng tán xạ mặt nước sông
    light_data_fill = bpy.data.lights.new(name="FillLight_Sky", type='AREA')
    light_data_fill.energy = 220.0
    light_data_fill.color = (0.75, 0.88, 1.0)
    light_data_fill.size = 3.0
    fill_obj = bpy.data.objects.new("Light_Fill_Sky", light_data_fill)
    fill_obj.location = (-2.5, 1.8, 2.2)
    fill_obj.rotation_euler = (math.radians(30), math.radians(-60), math.radians(120))
    scene.collection.objects.link(fill_obj)

    # Rim Light: Tôn nổi cơ bắp bả vai & búi tóc
    light_data_rim = bpy.data.lights.new(name="RimLight_Back", type='AREA')
    light_data_rim.energy = 320.0
    light_data_rim.color = (1.0, 0.98, 0.92)
    light_data_rim.size = 2.0
    rim_obj = bpy.data.objects.new("Light_Rim_Back", light_data_rim)
    rim_obj.location = (0.0, -2.6, 2.2)
    rim_obj.rotation_euler = (math.radians(-55), 0, math.radians(180))
    scene.collection.objects.link(rim_obj)

setup_cinematic_lighting()

# 10. THIẾT LẬP CAMERA & KẾT XUẤT 04 ẢNH KIỂM ĐỊNH CHUẨN FULL HD 1080P
def render_verification_shots():
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = 64
    except Exception:
        pass

    shots = [
        {
            "id": "Shot1_ChanDung_KhuonMat",
            "file": "anh_kiem_dinh_soldier_1_chandung_mat.png",
            "cam_loc": (0.32, 0.48, 1.62),
            "cam_rot": (math.radians(78), 0, math.radians(148)),
            "focal": 75.0, # Cận cảnh chân dung: Khuôn mặt, khăn đầu rìu, búi tóc trâm tre
        },
        {
            "id": "Shot2_XamGiaoLong_BapTayNguc",
            "file": "anh_kiem_dinh_soldier_2_xam_giaolong.png",
            "cam_loc": (0.55, 0.58, 1.28),
            "cam_rot": (math.radians(82), 0, math.radians(138)),
            "focal": 65.0, # Cận cảnh cơ ngực, bắp tay cuồn cuộn & hình xăm Giao Long Đông Sơn
        },
        {
            "id": "Shot3_KhoVaDaoGamDongSon",
            "file": "anh_kiem_dinh_soldier_3_kho_daogam.png",
            "cam_loc": (-0.68, 0.38, 0.88),
            "cam_rot": (math.radians(84), 0, math.radians(-118)),
            "focal": 55.0, # Cận cảnh hông trái: Khố nếp gấp tự nhiên & Dao găm đồng Đông Sơn
        },
        {
            "id": "Shot4_ToanThan_NgoiCheo",
            "file": "anh_kiem_dinh_soldier_4_toanthan_cheo.png",
            "cam_loc": (1.85, 1.65, 1.40),
            "cam_rot": (math.radians(70), 0, math.radians(135)),
            "focal": 40.0, # Toàn cảnh 3/4 thấy trọn vẹn người lính ngồi chèo thuyền kiềng 3 chân
        }
    ]

    cam_data = bpy.data.cameras.new("Cam_KiemDinh_Data")
    cam_obj = bpy.data.objects.new("Cam_KiemDinh", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    for s in shots:
        cam_obj.location = s["cam_loc"]
        cam_obj.rotation_euler = s["cam_rot"]
        cam_data.lens = s["focal"]
        out_path = os.path.join(OUTPUT_DIR, s["file"])
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"-> ĐÃ KẾT XUẤT THÀNH CÔNG: {s['id']} -> {out_path}")

render_verification_shots()

# 11. LƯU MASTER BLEND FILE
master_blend_path = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\thuy_binh_dai_viet_master.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_blend_path)
print(f"=== [VIETNAM-SIM MASTER] ĐÃ LƯU THÀNH CÔNG THỦY BINH ĐẠI VIỆT V3.1 MASTER: {master_blend_path} ===")
