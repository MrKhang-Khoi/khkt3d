import bpy
import math
from mathutils import Vector, Euler, Matrix

def build_thuy_binh_master():
    # 1. Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # Configure render settings
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    
    # 2. Import Base-Mesh
    glb_path = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\assets\characters\male_base_mesh.glb"
    bpy.ops.import_scene.gltf(filepath=glb_path)
    
    # Clean dummy objects
    if 'Icosphere' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Icosphere'], do_unlink=True)
        
    rig = bpy.data.objects.get('metarig')
    body = bpy.data.objects.get('mesh')
    
    body.name = "ThuyBinh_Body"
    rig.name = "ThuyBinh_Rig"
    
    # 3. Scale and align height to exactly 1.62m
    # Current height is 1.9446m -> scale factor = 1.62 / 1.9446 = 0.833076
    scale_factor = 1.62 / 1.9446
    rig.scale = (scale_factor, scale_factor, scale_factor)
    
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    
    # Align feet to floor Z = 0.0
    coords = [body.matrix_world @ v.co for v in body.data.vertices]
    min_z = min(c.z for c in coords)
    shift_z = -min_z
    rig.location.z += shift_z
    
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.transform_apply(location=True)
    
    # Recalculate normals clean
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Smooth shading
    for poly in body.data.polygons:
        poly.use_smooth = True
        
    # Add Subdivision Surface for organic muscle flow
    subsurf = body.modifiers.new('Subsurf', 'SUBSURF')
    subsurf.levels = 1
    subsurf.render_levels = 2
    
    print("Step 1 & 2: Base-mesh aligned to 1.62m, feet on ground.")
    
    # 4. Create Materials (LookDev PBR)
    # 4.1 Da Người Việt Cổ (Sun-tanned warm bronze skin)
    mat_skin = bpy.data.materials.new("Mat_DaNguoi_VietCo")
    mat_skin.use_nodes = True
    bsdf_skin = mat_skin.node_tree.nodes.get("Principled BSDF")
    if bsdf_skin:
        # #8C5A38 = (0.549, 0.353, 0.220) in sRGB -> Linear: (0.26, 0.10, 0.04)
        bsdf_skin.inputs['Base Color'].default_value = (0.35, 0.18, 0.09, 1.0)
        bsdf_skin.inputs['Roughness'].default_value = 0.42
        # SSS for human fleshy translucency
        if 'Subsurface Weight' in bsdf_skin.inputs:
            bsdf_skin.inputs['Subsurface Weight'].default_value = 0.15
            bsdf_skin.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.15)
            bsdf_skin.inputs['Subsurface Scale'].default_value = 0.05
        elif 'Subsurface' in bsdf_skin.inputs:
            bsdf_skin.inputs['Subsurface'].default_value = 0.15
            bsdf_skin.inputs['Subsurface Color'].default_value = (0.6, 0.15, 0.08, 1.0)
            
    body.data.materials.clear()
    body.data.materials.append(mat_skin)
    
    # 4.2 Tóc Đen Cổ Truyền
    mat_hair = bpy.data.materials.new("Mat_Toc_Den")
    mat_hair.use_nodes = True
    bsdf_hair = mat_hair.node_tree.nodes.get("Principled BSDF")
    if bsdf_hair:
        bsdf_hair.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        bsdf_hair.inputs['Roughness'].default_value = 0.55
        
    # 4.3 Khăn Đỏ Đầu Rìu
    mat_band = bpy.data.materials.new("Mat_Khan_DauRiu")
    mat_band.use_nodes = True
    bsdf_band = mat_band.node_tree.nodes.get("Principled BSDF")
    if bsdf_band:
        bsdf_band.inputs['Base Color'].default_value = (0.45, 0.04, 0.04, 1.0) # Madder Red
        bsdf_band.inputs['Roughness'].default_value = 0.78
        
    # 4.4 Khố Vải Thô Củ Nâu
    mat_cloth = bpy.data.materials.new("Mat_Kho_VaiCham")
    mat_cloth.use_nodes = True
    bsdf_cloth = mat_cloth.node_tree.nodes.get("Principled BSDF")
    if bsdf_cloth:
        bsdf_cloth.inputs['Base Color'].default_value = (0.12, 0.07, 0.04, 1.0) # Coarse Brown Hemp
        bsdf_cloth.inputs['Roughness'].default_value = 0.85
        
    # 4.5 Cán Chèo Gỗ Lim
    mat_wood = bpy.data.materials.new("Mat_CanCheo_GoLim")
    mat_wood.use_nodes = True
    bsdf_wood = mat_wood.node_tree.nodes.get("Principled BSDF")
    if bsdf_wood:
        bsdf_wood.inputs['Base Color'].default_value = (0.15, 0.08, 0.04, 1.0) # Ironwood
        bsdf_wood.inputs['Roughness'].default_value = 0.38
        
    # 5. Dựng Đạo Cụ & Phục Sức (Step 3)
    # 5.1 Búi Tóc Củ Tỏi (Topknot on back/crown of head)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.048, location=(-0.06, 0.0, 1.54))
    topknot = bpy.context.active_object
    topknot.name = "Bui_Toc_CuToi"
    topknot.scale = (0.85, 0.85, 1.15) # oval bun shape
    bpy.ops.object.transform_apply(scale=True)
    topknot.data.materials.append(mat_hair)
    
    # Ring/cord wrapping base of topknot
    bpy.ops.mesh.primitive_torus_add(major_radius=0.038, minor_radius=0.008, location=(-0.05, 0.0, 1.51))
    hair_cord = bpy.context.active_object
    hair_cord.name = "Day_Buoc_Toc"
    hair_cord.rotation_euler = (0, math.radians(25), 0)
    hair_cord.data.materials.append(mat_band)
    
    # 5.2 Khăn Đỏ Đầu Rìu (Headband with axe-blade knot)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.092, minor_radius=0.016, location=(-0.005, 0.0, 1.48))
    headband = bpy.context.active_object
    headband.name = "Khan_DauRiu_Vong"
    headband.scale = (1.05, 0.88, 0.9) # fit human head circumference
    bpy.ops.object.transform_apply(scale=True)
    headband.data.materials.append(mat_band)
    
    # Flaps of the headband knot (Axe blade shaped ends - Khan Dau Riu)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.032, depth=0.11, location=(-0.065, 0.095, 1.49))
    flap1 = bpy.context.active_object
    flap1.name = "Khan_DauRiu_Ta1"
    flap1.rotation_euler = (math.radians(35), math.radians(-30), math.radians(60))
    flap1.scale = (0.35, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    flap1.data.materials.append(mat_band)
    
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.026, depth=0.09, location=(-0.08, 0.085, 1.46))
    flap2 = bpy.context.active_object
    flap2.name = "Khan_DauRiu_Ta2"
    flap2.rotation_euler = (math.radians(20), math.radians(-45), math.radians(40))
    flap2.scale = (0.35, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    flap2.data.materials.append(mat_band)
    
    # Join hair & headband parts and parent to head bone
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [topknot, hair_cord, headband, flap1, flap2]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = headband
    bpy.ops.object.join()
    head_gear = bpy.context.active_object
    head_gear.name = "PhucSuc_Dau_KhanToc"
    
    head_gear.parent = rig
    head_gear.parent_type = 'BONE'
    head_gear.parent_bone = 'spine.005'
    
    # 5.3 Khố Vải Thô (Loincloth)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.138, minor_radius=0.024, location=(0.005, 0.0, 0.77))
    loincloth = bpy.context.active_object
    loincloth.name = "Kho_Cap_Lung"
    loincloth.scale = (0.85, 1.08, 0.8) # fit oval hips
    bpy.ops.object.transform_apply(scale=True)
    loincloth.data.materials.append(mat_cloth)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.105, 0.0, 0.64))
    front_flap = bpy.context.active_object
    front_flap.name = "Kho_Ta_Truoc"
    front_flap.scale = (0.015, 0.085, 0.16)
    front_flap.rotation_euler = (0, math.radians(-12), 0)
    bpy.ops.object.transform_apply(scale=True)
    front_flap.data.materials.append(mat_cloth)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.18, location=(0.0, 0.0, 0.72))
    crotch_wrap = bpy.context.active_object
    crotch_wrap.name = "Kho_Dung_Quan"
    crotch_wrap.rotation_euler = (math.radians(90), 0, 0)
    crotch_wrap.scale = (0.75, 0.6, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    crotch_wrap.data.materials.append(mat_cloth)
    
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [loincloth, front_flap, crotch_wrap]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = loincloth
    bpy.ops.object.join()
    loincloth_mesh = bpy.context.active_object
    loincloth_mesh.name = "TrangPhuc_Kho_ThuyBinh"
    
    loincloth_mesh.parent = rig
    loincloth_mesh.parent_type = 'BONE'
    loincloth_mesh.parent_bone = 'spine'
    
    # 5.4 Ghế Ngồi Xà Ngang (Thwart bench) & Sàn Thuyền (Deck Floor)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.35))
    bench = bpy.context.active_object
    bench.name = "Xa_Ngang_NgoiCheo"
    bench.scale = (0.24, 0.85, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    bench.data.materials.append(mat_wood)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.38, 0.0, 0.05))
    foot_brace = bpy.context.active_object
    foot_brace.name = "Go_Dap_Chan"
    foot_brace.scale = (0.12, 0.70, 0.08)
    foot_brace.rotation_euler = (0, math.radians(-25), 0)
    bpy.ops.object.transform_apply(scale=True)
    foot_brace.data.materials.append(mat_wood)
    
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.0, 0.0, 0.0))
    deck = bpy.context.active_object
    deck.name = "San_Thuyen_Studio"
    deck.data.materials.append(mat_wood)
    
    # 5.5 Cán Chèo Gỗ Lim (Reference Oar & Rowlock)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0225, depth=2.7, location=(0.32, -0.10, 0.62))
    oar = bpy.context.active_object
    oar.name = "Can_Cheo_GoLim"
    oar.rotation_euler = (math.radians(12), math.radians(72), math.radians(18))
    oar.data.materials.append(mat_wood)
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.020, depth=0.45, location=(0.38, -0.65, 0.65))
    pin = bpy.context.active_object
    pin.name = "Coc_Cheo_Go"
    pin.data.materials.append(mat_wood)
    
    # 6. Pose Rig & Khóa Khớp Bàn Tay (Step 4)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    
    def rot_bone(pb_name, rx, ry, rz):
        pb = rig.pose.bones.get(pb_name)
        if pb:
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
            
    # 6.1 Legs sitting on thwart
    rot_bone('thigh.L', -68, 5, 18)
    rot_bone('shin.L', 72, 0, -5)
    rot_bone('foot.L', -12, 0, 0)
    
    rot_bone('thigh.R', 68, -5, 18)
    rot_bone('shin.R', -72, 0, -5)
    rot_bone('foot.R', 12, 0, 0)
    
    # 6.2 Spine leaning forward 22 deg (Rowing drive phase)
    rot_bone('spine.001', 12, 0, 0)
    rot_bone('spine.002', 8, 0, 0)
    rot_bone('spine.003', 5, 0, 0)
    rot_bone('spine.004', -3, 0, 0)
    rot_bone('spine.005', -5, 0, 0)
    
    # 6.3 Arms reaching forward to grip oar
    rot_bone('upper_arm.L', 42, -15, 18)
    rot_bone('forearm.L', 38, 10, 15)
    rot_bone('hand.L', 5, -8, -12)
    
    rot_bone('upper_arm.R', 38, 12, -22)
    rot_bone('forearm.R', 44, -8, -16)
    rot_bone('hand.R', -5, 8, 12)
    
    # 6.4 Fingers curling tightly around oar shaft (Grip posture)
    for f in ['f_index', 'f_middle', 'f_ring', 'f_pinky']:
        rot_bone(f'{f}.01.L', 10, 0, 55)
        rot_bone(f'{f}.02.L', 0, 0, 65)
        rot_bone(f'{f}.03.L', 0, 0, 50)
    rot_bone('thumb.01.L', 25, 0, -35)
    rot_bone('thumb.02.L', 0, 0, -45)
    rot_bone('thumb.03.L', 0, 0, -35)
    
    for f in ['f_index', 'f_middle', 'f_ring', 'f_pinky']:
        rot_bone(f'{f}.01.R', -10, 0, -55)
        rot_bone(f'{f}.02.R', 0, 0, -65)
        rot_bone(f'{f}.03.R', 0, 0, -50)
    rot_bone('thumb.01.R', -25, 0, 35)
    rot_bone('thumb.02.R', 0, 0, 45)
    rot_bone('thumb.03.R', 0, 0, 35)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.update()
    
    # Fine-tune oar location to pass through hands
    hand_l = rig.matrix_world @ rig.pose.bones['hand.L'].head
    hand_r = rig.matrix_world @ rig.pose.bones['hand.R'].head
    mid_hand = (hand_l + hand_r) * 0.5
    oar.location = mid_hand + Vector((0.02, 0.0, -0.01))
    
    print(f"Step 4: Rowing pose set. Hand L={hand_l}, Hand R={hand_r}")
    
    # 7. Studio 3-Point Lighting Setup
    key_data = bpy.data.lights.new("KeyLight", 'SUN')
    key_data.energy = 4.0
    key_data.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new("KeyLight", key_data)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(52), math.radians(22), math.radians(-42))
    
    fill_data = bpy.data.lights.new("FillLight", 'SUN')
    fill_data.energy = 1.6
    fill_data.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(35), math.radians(-25), math.radians(55))
    
    rim_data = bpy.data.lights.new("RimLight", 'SUN')
    rim_data.energy = 2.8
    rim_data.color = (1.0, 0.95, 0.88)
    rim_obj = bpy.data.objects.new("RimLight", rim_data)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(120), math.radians(15), math.radians(140))
    
    # 8. Render 3 Studio Validation Shots
    cams = {}
    
    # Shot 1: Head & Face Close-up
    cam1_data = bpy.data.cameras.new("Cam_Shot1_Head")
    cam1_data.lens = 85
    cam1 = bpy.data.objects.new("Cam_Shot1_Head", cam1_data)
    bpy.context.scene.collection.objects.link(cam1)
    cam1.location = (0.95, -0.42, 1.56)
    cam1.rotation_euler = (math.radians(82), math.radians(0), math.radians(65))
    cams['Shot1_Head'] = (cam1, r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_kiem_dinh_1_can_canh_khuon_mat.png")
    
    # Shot 2: Hand-to-Oar Grip Detail
    cam2_data = bpy.data.cameras.new("Cam_Shot2_HandGrip")
    cam2_data.lens = 100
    cam2 = bpy.data.objects.new("Cam_Shot2_HandGrip", cam2_data)
    bpy.context.scene.collection.objects.link(cam2)
    cam2.location = (0.88, 0.18, 0.96)
    cam2.rotation_euler = (math.radians(60), math.radians(0), math.radians(72))
    cams['Shot2_HandGrip'] = (cam2, r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_kiem_dinh_2_can_canh_tay_nam_cheo.png")
    
    # Shot 3: Full Body Rowing Pose 3/4 Perspective
    cam3_data = bpy.data.cameras.new("Cam_Shot3_FullBody")
    cam3_data.lens = 50
    cam3 = bpy.data.objects.new("Cam_Shot3_FullBody", cam3_data)
    bpy.context.scene.collection.objects.link(cam3)
    cam3.location = (2.35, -1.85, 1.25)
    cam3.rotation_euler = (math.radians(70), math.radians(0), math.radians(52))
    cams['Shot3_FullBody'] = (cam3, r"c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_kiem_dinh_3_toan_than_ngoi_cheo.png")
    
    # Render all 3 shots
    for name, (c_obj, out_path) in cams.items():
        bpy.context.scene.camera = c_obj
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {name} -> {out_path}")
        
    # Save the master blend file
    save_path = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\thuy_binh_dai_viet_master.blend"
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"Master file saved: {save_path}")

if __name__ == '__main__':
    build_thuy_binh_master()
