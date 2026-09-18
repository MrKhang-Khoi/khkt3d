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
    
    # 2. Materials
    # 2.1 Da Người Việt Cổ (Sun-tanned warm bronze skin)
    mat_skin = bpy.data.materials.new('Mat_DaNguoi_VietCo')
    mat_skin.use_nodes = True
    bsdf_skin = mat_skin.node_tree.nodes.get('Principled BSDF')
    bsdf_skin.inputs['Base Color'].default_value = (0.36, 0.18, 0.09, 1.0) # Warm bronze
    bsdf_skin.inputs['Roughness'].default_value = 0.42
    if 'Subsurface Weight' in bsdf_skin.inputs:
        bsdf_skin.inputs['Subsurface Weight'].default_value = 0.18
        bsdf_skin.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.15)
        bsdf_skin.inputs['Subsurface Scale'].default_value = 0.05
    elif 'Subsurface' in bsdf_skin.inputs:
        bsdf_skin.inputs['Subsurface'].default_value = 0.18
        bsdf_skin.inputs['Subsurface Color'].default_value = (0.6, 0.15, 0.08, 1.0)
        
    # 2.2 Tóc Đen Cổ Truyền
    mat_hair = bpy.data.materials.new('Mat_Toc_Den')
    mat_hair.use_nodes = True
    bsdf_hair = mat_hair.node_tree.nodes.get('Principled BSDF')
    bsdf_hair.inputs['Base Color'].default_value = (0.012, 0.012, 0.012, 1.0)
    bsdf_hair.inputs['Roughness'].default_value = 0.50
    
    # 2.3 Khăn Đỏ Đầu Rìu
    mat_band = bpy.data.materials.new('Mat_Khan_DauRiu')
    mat_band.use_nodes = True
    bsdf_band = mat_band.node_tree.nodes.get('Principled BSDF')
    bsdf_band.inputs['Base Color'].default_value = (0.48, 0.04, 0.04, 1.0) # Rich Madder Red
    bsdf_band.inputs['Roughness'].default_value = 0.72
    
    # 2.4 Khố Vải Thô Củ Nâu
    mat_cloth = bpy.data.materials.new('Mat_Kho_VaiCham')
    mat_cloth.use_nodes = True
    bsdf_cloth = mat_cloth.node_tree.nodes.get('Principled BSDF')
    bsdf_cloth.inputs['Base Color'].default_value = (0.12, 0.07, 0.04, 1.0) # Coarse Brown Hemp
    bsdf_cloth.inputs['Roughness'].default_value = 0.85
    
    # 2.5 Cán Chèo Gỗ Lim & Xà Ngang Thuyền
    mat_wood = bpy.data.materials.new('Mat_CanCheo_GoLim')
    mat_wood.use_nodes = True
    bsdf_wood = mat_wood.node_tree.nodes.get('Principled BSDF')
    bsdf_wood.inputs['Base Color'].default_value = (0.14, 0.07, 0.035, 1.0) # Aged Ironwood
    bsdf_wood.inputs['Roughness'].default_value = 0.38
    
    # 3. Import Base-Mesh Body
    glb_body = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\assets\characters\male_base_mesh.glb'
    bpy.ops.import_scene.gltf(filepath=glb_body)
    if 'Icosphere' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Icosphere'], do_unlink=True)
        
    rig = bpy.data.objects['metarig']
    body = bpy.data.objects['mesh']
    body.name = 'ThuyBinh_Body'
    rig.name = 'ThuyBinh_Rig'
    
    # Delete generic mannequin head vertices (keep neck and collarbones intact)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode='EDIT')
    import bmesh
    bm = bmesh.from_edit_mesh(body.data)
    to_del = [v for v in bm.verts if v.co.z > 0.75]
    bmesh.ops.delete(bm, geom=to_del, context='VERTS')
    bmesh.update_edit_mesh(body.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Scale body to 1.62m
    s_body = 1.62 / 1.9446
    rig.scale = (s_body, s_body, s_body)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.transform_apply(scale=True)
    
    # Align feet to floor Z = 0.0
    coords = [body.matrix_world @ v.co for v in body.data.vertices]
    shift_z = -min(c.z for c in coords)
    rig.location.z += shift_z
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.transform_apply(location=True)
    
    body.data.materials.clear()
    body.data.materials.append(mat_skin)
    for p in body.data.polygons:
        p.use_smooth = True
        
    # 4. Import & Position Realistic Head Sculpt
    glb_head = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\assets\characters\lee_perry_smith.glb'
    bpy.ops.import_scene.gltf(filepath=glb_head)
    head = bpy.data.objects['LeePerrySmith']
    head.name = 'ThuyBinh_Head_Sculpt'
    
    for o in list(bpy.context.scene.objects):
        if o.type == 'EMPTY' and o.name in ['Camera', 'Lamp']:
            bpy.data.objects.remove(o, do_unlink=True)
            
    # Scale head to height ~0.24m
    s_head = 0.24 / 7.9451
    head.scale = (s_head, s_head, s_head)
    head.rotation_mode = 'XYZ'
    head.rotation_euler = (0, 0, math.radians(90)) # Face +X
    bpy.context.view_layer.objects.active = head
    head.select_set(True)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    
    # Position head on neck
    head.location = (0.015, 0.0, 1.44)
    bpy.ops.object.transform_apply(location=True)
    
    head.data.materials.clear()
    head.data.materials.append(mat_skin)
    for p in head.data.polygons:
        p.use_smooth = True
        
    # 5. Phục Sức Đầu: Tóc Đen, Búi Tóc Củ Tỏi & Khăn Đỏ Đầu Rìu
    # 5.1 Tóc nền (Hair cap dome)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.082, location=(-0.015, 0.0, 1.515))
    hair_cap = bpy.context.active_object
    hair_cap.name = 'Toc_Nen_Dau'
    hair_cap.scale = (0.95, 0.88, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    hair_cap.data.materials.append(mat_hair)
    for p in hair_cap.data.polygons:
        p.use_smooth = True
        
    # 5.2 Búi Tóc Củ Tỏi (Topknot bun)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.038, location=(-0.082, 0.0, 1.540))
    topknot = bpy.context.active_object
    topknot.name = 'Bui_Toc_CuToi'
    topknot.scale = (0.85, 0.85, 1.1)
    bpy.ops.object.transform_apply(scale=True)
    topknot.data.materials.append(mat_hair)
    for p in topknot.data.polygons:
        p.use_smooth = True
        
    # Dây buộc chân búi tóc
    bpy.ops.mesh.primitive_torus_add(major_radius=0.030, minor_radius=0.005, location=(-0.074, 0.0, 1.515))
    hair_cord = bpy.context.active_object
    hair_cord.rotation_euler = (0, math.radians(22), 0)
    hair_cord.data.materials.append(mat_band)
    for p in hair_cord.data.polygons:
        p.use_smooth = True
        
    # 5.3 Khăn Đỏ Đầu Rìu (Headband ribbon)
    bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=16, major_radius=0.081, minor_radius=0.007, location=(-0.006, 0.0, 1.515))
    headband = bpy.context.active_object
    headband.name = 'Khan_DauRiu_Vong'
    headband.rotation_euler = (0, math.radians(-7), 0)
    headband.scale = (1.02, 0.88, 1.2)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    headband.data.materials.append(mat_band)
    for p in headband.data.polygons:
        p.use_smooth = True
        
    # 2 tà khăn vát hình lưỡi rìu xéo bên mang tai
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.024, depth=0.095, location=(-0.065, 0.088, 1.510))
    flap1 = bpy.context.active_object
    flap1.rotation_euler = (math.radians(35), math.radians(-30), math.radians(60))
    flap1.scale = (0.35, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    flap1.data.materials.append(mat_band)
    for p in flap1.data.polygons:
        p.use_smooth = True
        
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.020, depth=0.080, location=(-0.078, 0.078, 1.485))
    flap2 = bpy.context.active_object
    flap2.rotation_euler = (math.radians(20), math.radians(-45), math.radians(40))
    flap2.scale = (0.35, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    flap2.data.materials.append(mat_band)
    for p in flap2.data.polygons:
        p.use_smooth = True
        
    # Join head, hair and headband into a single head assembly
    bpy.ops.object.select_all(action='DESELECT')
    for o in [head, hair_cap, topknot, hair_cord, headband, flap1, flap2]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = head
    bpy.ops.object.join()
    head_assembly = bpy.context.active_object
    head_assembly.name = 'ThuyBinh_Head_Assembly'
    
    # Weight head assembly to spine.005 with Armature Modifier
    vg_head = head_assembly.vertex_groups.new(name='spine.005')
    vg_head.add(list(range(len(head_assembly.data.vertices))), 1.0, 'REPLACE')
    mod_head = head_assembly.modifiers.new('Armature', 'ARMATURE')
    mod_head.object = rig
    
    # 6. Trang Phục: Khố Vải Thô Củ Nâu (Loincloth)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.138, minor_radius=0.022, location=(0.005, 0.0, 0.77))
    loincloth = bpy.context.active_object
    loincloth.name = 'Kho_Cap_Lung'
    loincloth.scale = (0.85, 1.08, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    loincloth.data.materials.append(mat_cloth)
    for p in loincloth.data.polygons:
        p.use_smooth = True
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.105, 0.0, 0.64))
    front_flap = bpy.context.active_object
    front_flap.name = 'Kho_Ta_Truoc'
    front_flap.scale = (0.015, 0.085, 0.16)
    front_flap.rotation_euler = (0, math.radians(-12), 0)
    bpy.ops.object.transform_apply(scale=True)
    front_flap.data.materials.append(mat_cloth)
    for p in front_flap.data.polygons:
        p.use_smooth = True
        
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.18, location=(0.0, 0.0, 0.72))
    crotch_wrap = bpy.context.active_object
    crotch_wrap.rotation_euler = (math.radians(90), 0, 0)
    crotch_wrap.scale = (0.75, 0.6, 0.85)
    bpy.ops.object.transform_apply(scale=True)
    crotch_wrap.data.materials.append(mat_cloth)
    for p in crotch_wrap.data.polygons:
        p.use_smooth = True
        
    # Join loincloth parts
    bpy.ops.object.select_all(action='DESELECT')
    for o in [loincloth, front_flap, crotch_wrap]:
        o.select_set(True)
    bpy.context.view_layer.objects.active = loincloth
    bpy.ops.object.join()
    loincloth_assembly = bpy.context.active_object
    loincloth_assembly.name = 'ThuyBinh_Kho_Assembly'
    
    vg_kho = loincloth_assembly.vertex_groups.new(name='spine')
    vg_kho.add(list(range(len(loincloth_assembly.data.vertices))), 1.0, 'REPLACE')
    mod_kho = loincloth_assembly.modifiers.new('Armature', 'ARMATURE')
    mod_kho.object = rig
    
    # 7. Ghế Ngồi Xà Ngang, Gờ Đạp Chân & Sàn Thuyền
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.02, 0.0, 0.35))
    bench = bpy.context.active_object
    bench.name = 'Xa_Ngang_NgoiCheo'
    bench.scale = (0.24, 0.90, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    bench.data.materials.append(mat_wood)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.38, 0.0, 0.06))
    foot_brace = bpy.context.active_object
    foot_brace.name = 'Go_Dap_Chan'
    foot_brace.scale = (0.12, 0.75, 0.08)
    foot_brace.rotation_euler = (0, math.radians(-25), 0)
    bpy.ops.object.transform_apply(scale=True)
    foot_brace.data.materials.append(mat_wood)
    
    bpy.ops.mesh.primitive_plane_add(size=4.5, location=(0.0, 0.0, 0.0))
    deck = bpy.context.active_object
    deck.name = 'San_Thuyen_Studio'
    deck.data.materials.append(mat_wood)
    
    # 8. Pose Rig & Động Học Khóa Khớp Bàn Tay (Kinematics)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')
    
    def rot_bone(pb_name, rx, ry, rz):
        pb = rig.pose.bones.get(pb_name)
        if pb:
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
            
    # 8.1 Legs sitting on thwart
    rot_bone('thigh.L', -68, 5, 18)
    rot_bone('shin.L', 72, 0, -5)
    rot_bone('foot.L', -12, 0, 0)
    
    rot_bone('thigh.R', 68, -5, 18)
    rot_bone('shin.R', -72, 0, -5)
    rot_bone('foot.R', 12, 0, 0)
    
    # 8.2 Spine leaning forward 20 deg (Rowing drive phase)
    rot_bone('spine.001', 10, 0, 0)
    rot_bone('spine.002', 6, 0, 0)
    rot_bone('spine.003', 4, 0, 0)
    rot_bone('spine.004', -2, 0, 0)
    rot_bone('spine.005', -3, 0, 0)
    
    # 8.3 Arms reaching forward to hold oar
    rot_bone('upper_arm.L', 42, -12, 16)
    rot_bone('forearm.L', 36, 12, 14)
    rot_bone('hand.L', 8, -6, -10)
    
    rot_bone('upper_arm.R', 40, 10, -20)
    rot_bone('forearm.R', 42, -8, -14)
    rot_bone('hand.R', -8, 6, 10)
    
    # 8.4 5 Fingers curled tightly around oar cylinder (3 phalanges each)
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
    
    # 9. Cán Chèo Gỗ Lim Mẫu (Reference Oar & Rowlock) - ALIGNED MATHEMATICALLY TO HANDS
    hand_l = rig.matrix_world @ rig.pose.bones['hand.L'].head
    hand_r = rig.matrix_world @ rig.pose.bones['hand.R'].head
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0225, depth=2.7)
    oar = bpy.context.active_object
    oar.name = 'Can_Cheo_GoLim'
    oar.data.materials.append(mat_wood)
    for p in oar.data.polygons:
        p.use_smooth = True
        
    # Align oar axis with the line connecting Hand L and Hand R
    oar_dir = (hand_r - hand_l).normalized()
    handle_end = hand_l - oar_dir * 0.45
    oar_center = handle_end + oar_dir * 1.35
    oar.location = oar_center
    rot_quat = Vector((0, 0, 1)).rotation_difference(oar_dir)
    oar.rotation_mode = 'QUATERNION'
    oar.rotation_quaternion = rot_quat
    
    # Cọc chèo gỗ (Rowlock pin)
    pin_loc = handle_end + oar_dir * 1.6
    bpy.ops.mesh.primitive_cylinder_add(radius=0.020, depth=0.45, location=(pin_loc.x, pin_loc.y, pin_loc.z - 0.05))
    pin = bpy.context.active_object
    pin.name = 'Coc_Cheo_Go'
    pin.data.materials.append(mat_wood)
    for p in pin.data.polygons:
        p.use_smooth = True
        
    # 10. Studio 3-Point Lighting Setup
    key_data = bpy.data.lights.new('KeyLight', 'SUN')
    key_data.energy = 4.0
    key_data.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new('KeyLight', key_data)
    bpy.context.scene.collection.objects.link(key_obj)
    key_obj.rotation_euler = (math.radians(52), math.radians(22), math.radians(-42))
    
    fill_data = bpy.data.lights.new('FillLight', 'SUN')
    fill_data.energy = 1.6
    fill_data.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new('FillLight', fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(35), math.radians(-25), math.radians(55))
    
    rim_data = bpy.data.lights.new('RimLight', 'SUN')
    rim_data.energy = 2.8
    rim_data.color = (1.0, 0.95, 0.88)
    rim_obj = bpy.data.objects.new('RimLight', rim_data)
    bpy.context.scene.collection.objects.link(rim_obj)
    rim_obj.rotation_euler = (math.radians(120), math.radians(15), math.radians(140))
    
    # 11. Render 3 Studio Validation Shots with Track-To Constraints
    head_center = rig.matrix_world @ rig.pose.bones['spine.005'].head + Vector((0.02, 0.0, 0.06))
    target_head = bpy.data.objects.new('Target_Head', None)
    bpy.context.scene.collection.objects.link(target_head)
    target_head.location = head_center
    
    target_hand = bpy.data.objects.new('Target_Hand', None)
    bpy.context.scene.collection.objects.link(target_hand)
    target_hand.location = hand_l
    
    target_torso = bpy.data.objects.new('Target_Torso', None)
    bpy.context.scene.collection.objects.link(target_torso)
    target_torso.location = (0.15, 0.0, 0.65)
    
    # Cam 1: Head & Face Close-up
    cam1_data = bpy.data.cameras.new('Cam1_Head')
    cam1_data.lens = 85
    cam1 = bpy.data.objects.new('Cam1_Head', cam1_data)
    bpy.context.scene.collection.objects.link(cam1)
    cam1.location = (head_center.x + 0.70, head_center.y - 0.28, head_center.z + 0.04)
    tt1 = cam1.constraints.new('TRACK_TO')
    tt1.target = target_head
    tt1.track_axis = 'TRACK_NEGATIVE_Z'
    tt1.up_axis = 'UP_Y'
    
    # Cam 2: Hand Grip Macro Detail (Looking tightly at Left Hand gripping oar)
    cam2_data = bpy.data.cameras.new('Cam2_HandGrip')
    cam2_data.lens = 100
    cam2 = bpy.data.objects.new('Cam2_HandGrip', cam2_data)
    bpy.context.scene.collection.objects.link(cam2)
    cam2.location = (hand_l.x + 0.45, hand_l.y - 0.32, hand_l.z + 0.25)
    tt2 = cam2.constraints.new('TRACK_TO')
    tt2.target = target_hand
    tt2.track_axis = 'TRACK_NEGATIVE_Z'
    tt2.up_axis = 'UP_Y'
    
    # Cam 3: Full Body Rowing Pose 3/4 View
    cam3_data = bpy.data.cameras.new('Cam3_FullBody')
    cam3_data.lens = 45
    cam3 = bpy.data.objects.new('Cam3_FullBody', cam3_data)
    bpy.context.scene.collection.objects.link(cam3)
    cam3.location = (2.2, -1.8, 1.25)
    tt3 = cam3.constraints.new('TRACK_TO')
    tt3.target = target_torso
    tt3.track_axis = 'TRACK_NEGATIVE_Z'
    tt3.up_axis = 'UP_Y'
    
    shots = [
        ('Shot1_Head', cam1, r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_kiem_dinh_1_can_canh_khuon_mat.png'),
        ('Shot2_HandGrip', cam2, r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_kiem_dinh_2_can_canh_tay_nam_cheo.png'),
        ('Shot3_FullBody', cam3, r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_kiem_dinh_3_toan_than_ngoi_cheo.png')
    ]
    
    for name, cam_obj, out_path in shots:
        bpy.context.scene.camera = cam_obj
        bpy.context.scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"Rendered {name} -> {out_path}")
        
    save_path = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\thuy_binh_dai_viet_master.blend'
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"Master file saved: {save_path}")

if __name__ == '__main__':
    build_thuy_binh_master()
