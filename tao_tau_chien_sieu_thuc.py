import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

def reset_scene():
    """Làm sạch toàn bộ scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_plank_wood_material(name, color_dark, color_mid, color_light):
    """
    TẠO VẬT LIỆU VÁN GỖ ĐÓNG TÀU CHUẨN XÁC:
    Các ván gỗ chạy ngang thân tàu (trục Y), có rãnh ghép ván và vân thớ tự nhiên.
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (800, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-700, 0)

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-500, 0)
    # Scale để ván gỗ chạy dài theo thân tàu
    mapping.inputs['Scale'].default_value = (1.5, 0.1, 8.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Wave Texture theo trục Z để tạo các tấm ván gỗ ngang
    wave_tex = nodes.new(type='ShaderNodeTexWave')
    wave_tex.location = (-250, 100)
    wave_tex.wave_type = 'BANDS'
    wave_tex.bands_direction = 'Z'
    wave_tex.inputs['Scale'].default_value = 2.2
    wave_tex.inputs['Distortion'].default_value = 1.2
    wave_tex.inputs['Detail'].default_value = 2.0
    links.new(mapping.outputs['Vector'], wave_tex.inputs['Vector'])

    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (60, 100)
    color_ramp.color_ramp.interpolation = 'EASE'
    
    color_ramp.color_ramp.elements[0].position = 0.0
    color_ramp.color_ramp.elements[0].color = color_dark
    
    elem_mid = color_ramp.color_ramp.elements.new(0.5)
    elem_mid.color = color_mid
    
    color_ramp.color_ramp.elements[2].position = 1.0
    color_ramp.color_ramp.elements[2].color = color_light

    links.new(wave_tex.outputs['Color'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # Bump Map rãnh ván gỗ
    bump = nodes.new(type='ShaderNodeBump')
    bump.location = (180, -180)
    bump.inputs['Strength'].default_value = 0.3
    bump.inputs['Distance'].default_value = 0.05
    links.new(wave_tex.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def create_ocean_water_material():
    """Tạo vật liệu nước biển sâu ngọc bích có độ phản xạ gương."""
    mat = bpy.data.materials.new(name="Mat_OceanWater_PBR")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.015, 0.12, 0.24, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.04
        bsdf.inputs['Metallic'].default_value = 0.1
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.8
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = 0.8
        if 'IOR' in bsdf.inputs:
            bsdf.inputs['IOR'].default_value = 1.333
    return mat

def apply_bevel_and_smooth(obj, width=0.06, segments=3):
    """Bo vát cạnh và làm mượt mặt đa giác."""
    for poly in obj.data.polygons:
        poly.use_smooth = True
    bevel = obj.modifiers.new(name="Bevel_SoftEdge", type='BEVEL')
    bevel.width = width
    bevel.segments = segments
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = math.radians(35)

def make_cone_mesh(bm, r1, r2, depth, segments=16, matrix=None):
    mat = matrix if matrix is not None else Matrix.Identity(4)
    return bmesh.ops.create_cone(
        bm, cap_ends=True, cap_tris=False, segments=segments,
        radius1=r1, radius2=r2, depth=depth, matrix=mat
    )

def build_high_quality_warship():
    """Dựng tàu chiến tinh xảo với các chi tiết chuẩn game."""
    mat_hull = create_plank_wood_material(
        "Mat_Hull_Oak",
        color_dark=(0.14, 0.08, 0.04, 1.0),
        color_mid=(0.28, 0.16, 0.09, 1.0),
        color_light=(0.42, 0.26, 0.14, 1.0)
    )
    mat_deck = create_plank_wood_material(
        "Mat_Deck_Pine",
        color_dark=(0.32, 0.20, 0.11, 1.0),
        color_mid=(0.52, 0.35, 0.20, 1.0),
        color_light=(0.68, 0.48, 0.28, 1.0)
    )
    mat_sail = bpy.data.materials.new("Mat_Cloth_Sail")
    mat_sail.use_nodes = True
    bsdf_sail = mat_sail.node_tree.nodes.get("Principled BSDF")
    if bsdf_sail:
        bsdf_sail.inputs['Base Color'].default_value = (0.92, 0.88, 0.80, 1.0)
        bsdf_sail.inputs['Roughness'].default_value = 0.85

    mat_iron = bpy.data.materials.new("Mat_Cannon_Iron")
    mat_iron.use_nodes = True
    bsdf_iron = mat_iron.node_tree.nodes.get("Principled BSDF")
    if bsdf_iron:
        bsdf_iron.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bsdf_iron.inputs['Metallic'].default_value = 0.92
        bsdf_iron.inputs['Roughness'].default_value = 0.25

    mat_gold = bpy.data.materials.new("Mat_Helm_Gold")
    mat_gold.use_nodes = True
    bsdf_gold = mat_gold.node_tree.nodes.get("Principled BSDF")
    if bsdf_gold:
        bsdf_gold.inputs['Base Color'].default_value = (0.85, 0.65, 0.15, 1.0)
        bsdf_gold.inputs['Metallic'].default_value = 0.9
        bsdf_gold.inputs['Roughness'].default_value = 0.2

    # 1. Master Root Empty
    root = bpy.data.objects.new("Warship_Master", None)
    root.empty_display_type = 'ARROWS'
    root.empty_display_size = 2.0
    bpy.context.collection.objects.link(root)

    # 2. Thân tàu cong khí động học
    hull_mesh = bpy.data.meshes.new("Realistic_Hull_Mesh")
    hull_obj = bpy.data.objects.new("Warship_Hull", hull_mesh)
    bpy.context.collection.objects.link(hull_obj)
    hull_obj.parent = root

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 10.0 # Dài 10m
        v.co.x *= 3.4  # Rộng 3.4m
        v.co.z *= 2.2  # Cao 2.2m

        # Uốn đường cong vỏ tàu
        norm_y = v.co.y / 5.0 # -1.0 đến +1.0
        if v.co.y > 0: # Mũi tàu
            t = v.co.y / 5.0
            v.co.x *= max(0.1, 1.0 - (t ** 1.5) * 0.8)
            v.co.z += (t ** 1.3) * 1.2 # Mũi hếch kiêu hãnh rẽ sóng
        else: # Đuôi tàu (Poop deck cao tầng)
            t = abs(v.co.y) / 5.0
            v.co.z += (t ** 1.2) * 1.0
            v.co.x *= max(0.4, 1.0 - t * 0.3)

        # Đáy lườn thuyền vát hẹp
        if v.co.z < 0:
            v.co.x *= 0.5

    hull_mesh.materials.append(mat_hull)
    bm.to_mesh(hull_mesh)
    bm.free()
    apply_bevel_and_smooth(hull_obj, width=0.08, segments=3)

    # 3. Boong Tàu
    deck_mesh = bpy.data.meshes.new("Deck_Mesh")
    deck_obj = bpy.data.objects.new("Warship_Deck", deck_mesh)
    bpy.context.collection.objects.link(deck_obj)
    deck_obj.parent = root
    deck_obj.location = (0, 0, 0.4)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.y *= 9.4
        v.co.x *= 2.9 * max(0.18, 1.0 - (abs(v.co.y) / 5.0) ** 1.8)
        v.co.z *= 0.15
    deck_mesh.materials.append(mat_deck)
    bm.to_mesh(deck_mesh)
    bm.free()
    apply_bevel_and_smooth(deck_obj, width=0.04, segments=2)

    # 4. Boong Tầng Đuôi (Quarterdeck Cabin)
    cabin_mesh = bpy.data.meshes.new("Quarterdeck_Mesh")
    cabin_obj = bpy.data.objects.new("Quarterdeck_Cabin", cabin_mesh)
    bpy.context.collection.objects.link(cabin_obj)
    cabin_obj.parent = root
    cabin_obj.location = (0, -3.2, 1.4)

    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 2.4 * (0.85 if v.co.y < 0 else 1.0)
        v.co.y *= 2.6
        v.co.z *= 1.2
    cabin_mesh.materials.append(mat_hull)
    bm.to_mesh(cabin_mesh)
    bm.free()
    apply_bevel_and_smooth(cabin_obj, width=0.06, segments=3)

    # 5. Lan Can & Con Tiện
    railing_mesh = bpy.data.meshes.new("Railings_Mesh")
    railing_obj = bpy.data.objects.new("Warship_Railings", railing_mesh)
    bpy.context.collection.objects.link(railing_obj)
    railing_obj.parent = root

    bm = bmesh.new()
    for side in [1.0, -1.0]:
        for y_step in range(-16, 18, 4):
            y_pos = y_step * 0.25
            x_pos = side * 1.45 * max(0.2, 1.0 - (abs(y_pos) / 5.0) ** 2)
            z_base = 0.5 + 0.15 * ((y_pos / 5.0) ** 2)
            make_cone_mesh(bm, 0.035, 0.035, 0.7, segments=8, 
                           matrix=Matrix.Translation((x_pos, y_pos, z_base + 0.35)))
    railing_mesh.materials.append(mat_hull)
    bm.to_mesh(railing_mesh)
    bm.free()

    # 6. Mũi tàu chéo đón sóng (Bowsprit)
    bow_mesh = bpy.data.meshes.new("Bowsprit_Mesh")
    bow_obj = bpy.data.objects.new("Bowsprit", bow_mesh)
    bpy.context.collection.objects.link(bow_obj)
    bow_obj.parent = root
    bow_obj.location = (0, 5.0, 1.6)
    bow_obj.rotation_euler = Euler((math.radians(-24), 0, 0))

    bm = bmesh.new()
    make_cone_mesh(bm, 0.16, 0.04, 4.5, segments=16)
    bow_mesh.materials.append(mat_hull)
    bm.to_mesh(bow_mesh)
    bm.free()
    apply_bevel_and_smooth(bow_obj, width=0.03, segments=2)

    # 7. Cột buồm chính & 2 Cánh buồm vải uốn cong 3D
    mast_mesh = bpy.data.meshes.new("Main_Mast_Mesh")
    mast_obj = bpy.data.objects.new("Main_Mast", mast_mesh)
    bpy.context.collection.objects.link(mast_obj)
    mast_obj.parent = root
    mast_obj.location = (0, 0.4, 0.4)

    bm = bmesh.new()
    # Cột gỗ cao 10.5m
    make_cone_mesh(bm, 0.22, 0.12, 10.5, segments=16, 
                   matrix=Matrix.Translation((0, 0, 5.25)))
    
    # 2 Xà ngang treo buồm
    mat_rot_yard = Euler((0, math.radians(90), 0)).to_matrix().to_4x4()
    make_cone_mesh(bm, 0.09, 0.05, 6.4, segments=12, 
                   matrix=Matrix.Translation((0, 0, 4.8)) @ mat_rot_yard)
    make_cone_mesh(bm, 0.07, 0.04, 4.6, segments=12, 
                   matrix=Matrix.Translation((0, 0, 8.4)) @ mat_rot_yard)

    # Buồm dưới (Mainsail) phồng căng 3D
    mat_rot_sail = Euler((math.radians(90), 0, 0)).to_matrix().to_4x4()
    bmesh.ops.create_grid(bm, x_segments=12, y_segments=12, size=2.8, 
                          matrix=Matrix.Translation((0, 0.3, 3.4)) @ mat_rot_sail)
    for v in bm.verts[-169:]:
        v.co.x *= 1.15
        v.co.z = v.co.z * 0.65 + 3.4
        v.co.y += math.sin((v.co.z - 1.7) / 1.7 * math.pi) * 0.6

    # Buồm trên (Topsail)
    bmesh.ops.create_grid(bm, x_segments=10, y_segments=10, size=2.0, 
                          matrix=Matrix.Translation((0, 0.3, 7.0)) @ mat_rot_sail)
    for v in bm.verts[-121:]:
        v.co.x *= 1.1
        v.co.z = v.co.z * 0.65 + 7.0
        v.co.y += math.sin((v.co.z - 5.7) / 1.3 * math.pi) * 0.45

    mast_mesh.materials.append(mat_hull)
    mast_mesh.materials.append(mat_sail)
    for p in mast_mesh.polygons:
        if p.index >= 120:
            p.material_index = 1
    bm.to_mesh(mast_mesh)
    bm.free()
    apply_bevel_and_smooth(mast_obj, width=0.03, segments=2)

    # 8. Dây chão uốn lượn thật
    curve_data = bpy.data.curves.new("Rigging_Ropes_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.02
    curve_data.bevel_resolution = 3
    
    curve_obj = bpy.data.objects.new("Rigging_Ropes", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.parent = root
    
    rope_mat = bpy.data.materials.new("Mat_Rope")
    rope_mat.use_nodes = True
    rope_mat.node_tree.nodes.get("Principled BSDF").inputs['Base Color'].default_value = (0.22, 0.16, 0.10, 1.0)
    curve_data.materials.append(rope_mat)

    for side in [1.45, -1.45]:
        for y_target in [-1.5, 0.5, 2.5]:
            spline = curve_data.splines.new(type='BEZIER')
            spline.bezier_points.add(1)
            spline.bezier_points[0].co = Vector((0, 0.4, 8.4))
            spline.bezier_points[0].handle_left_type = 'AUTO'
            spline.bezier_points[0].handle_right_type = 'AUTO'
            spline.bezier_points[1].co = Vector((side, y_target, 0.6))
            spline.bezier_points[1].handle_left_type = 'AUTO'
            spline.bezier_points[1].handle_right_type = 'AUTO'

    # 9. Khẩu pháo đại bác
    for side, sign in [("Port", 1.0), ("Stbd", -1.0)]:
        for idx, y_pos in enumerate([-1.6, 1.8]):
            c_mesh = bpy.data.meshes.new(f"Cannon_{side}_{idx}_Mesh")
            c_obj = bpy.data.objects.new(f"Cannon_{side}_{idx}", c_mesh)
            bpy.context.collection.objects.link(c_obj)
            c_obj.parent = root
            c_obj.location = (sign * 1.45, y_pos, 0.65)
            c_obj.rotation_euler = Euler((0, math.radians(sign * 6), math.radians(sign * 90)))

            bm = bmesh.new()
            make_cone_mesh(bm, 0.16, 0.24, 1.5, segments=16, matrix=Matrix.Translation((0, 0, 0.4)))
            make_cone_mesh(bm, 0.22, 0.16, 0.3, segments=16, matrix=Matrix.Translation((0, 0, 1.25)))
            bmesh.ops.create_cube(bm, size=0.5, matrix=Matrix.Translation((0, 0, -0.15)))
            c_mesh.materials.append(mat_iron)
            c_mesh.materials.append(mat_hull)
            for p in c_mesh.polygons:
                if p.index >= 32:
                    p.material_index = 1
            bm.to_mesh(c_mesh)
            bm.free()
            apply_bevel_and_smooth(c_obj, width=0.03, segments=2)

    # 10. Bánh lái bằng đồng đúc
    helm_mesh = bpy.data.meshes.new("Helm_Mesh")
    helm_obj = bpy.data.objects.new("Warship_Helm", helm_mesh)
    bpy.context.collection.objects.link(helm_obj)
    helm_obj.parent = root
    helm_obj.location = (0, -3.6, 2.5)
    helm_obj.rotation_euler = Euler((math.radians(16), 0, 0))

    bm = bmesh.new()
    make_cone_mesh(bm, 0.42, 0.42, 0.05, segments=20)
    for deg in range(0, 360, 45):
        rad = math.radians(deg)
        m_rot = Euler((0, 0, rad)).to_matrix().to_4x4()
        make_cone_mesh(bm, 0.03, 0.03, 1.1, segments=8, matrix=m_rot)
    helm_mesh.materials.append(mat_gold)
    bm.to_mesh(helm_mesh)
    bm.free()
    apply_bevel_and_smooth(helm_obj, width=0.02, segments=2)

    return root

def build_ocean_with_foam():
    """Tạo mặt biển sống động với Ocean Modifier và vật liệu nước biển sâu."""
    bpy.ops.mesh.primitive_plane_add(size=140.0, location=(0, 0, -0.2))
    ocean = bpy.context.active_object
    ocean.name = "Ocean_Water_Realistic"

    ocean_mat = create_ocean_water_material()
    ocean.data.materials.append(ocean_mat)

    ocean_mod = ocean.modifiers.new(name="OceanWaves", type='OCEAN')
    ocean_mod.geometry_mode = 'GENERATE'
    ocean_mod.repeat_x = 2
    ocean_mod.repeat_y = 2
    ocean_mod.spatial_size = 60
    ocean_mod.resolution = 14
    ocean_mod.wave_scale = 1.2
    ocean_mod.choppiness = 1.4
    ocean_mod.wind_velocity = 18.0
    ocean_mod.wave_alignment = 0.7

    total_frames = 180
    ocean_mod.time = 1.0
    ocean_mod.keyframe_insert(data_path="time", frame=1)
    ocean_mod.time = 8.0
    ocean_mod.keyframe_insert(data_path="time", frame=total_frames)

    return ocean

def animate_warship_realistic_buoyancy(root_obj, total_frames=180):
    """Hoạt ảnh bám sóng 6 bậc tự do (6-DoF)."""
    root_obj.animation_data_create()
    action = bpy.data.actions.new(name="Ship_Realistic_Sailing")
    root_obj.animation_data.action = action

    bpy.context.scene.render.fps = 30
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = total_frames

    ship_speed = 2.4
    wavelength = 15.0

    for f in range(1, total_frames + 1):
        t = f / 30.0
        y_pos = (t * ship_speed) - 8.0

        k1 = 2.0 * math.pi / wavelength
        phase1 = k1 * y_pos - (t * 2.8)
        phase2 = t * 1.5

        heave_z = 0.58 * math.sin(phase1) + 0.22 * math.sin(phase1 * 2.2)
        pitch_x = -0.19 * math.cos(phase1) - 0.05 * math.cos(phase1 * 2.2)
        roll_y = 0.12 * math.sin(phase2) + 0.04 * math.cos(phase1 * 0.8)
        yaw_z = 0.035 * math.sin(phase2 * 0.5)

        root_obj.location = Vector((0.0, y_pos, heave_z))
        root_obj.rotation_mode = 'XYZ'
        root_obj.rotation_euler = Euler((pitch_x, roll_y, yaw_z), 'XYZ')

        root_obj.keyframe_insert(data_path="location", frame=f)
        root_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    # Làm mượt đường cong F-Curves
    fcurves_list = []
    if hasattr(action, 'fcurves') and action.fcurves:
        fcurves_list = list(action.fcurves)
    elif hasattr(action, 'layers'):
        for layer in action.layers:
            for strip in getattr(layer, 'strips', []):
                for bag in getattr(strip, 'channelbags', []):
                    fcurves_list.extend(list(getattr(bag, 'fcurves', [])))

    for fc in fcurves_list:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = 'AUTO_CLAMPED'
            kp.handle_right_type = 'AUTO_CLAMPED'

def setup_cinema_camera_and_lighting(root_obj):
    """
    BỐ CỤC ĐIỆN ẢNH CHUẨN XÁC:
    - Bầu trời World HDRI / Ambient ánh sáng tự nhiên.
    - Mặt trời chiếu xiên tạo bóng đổ đổ dài trên mặt biển.
    - Camera đặt ở góc toàn cảnh (Telephoto/Cinema lens 32mm) bắt trọn toàn bộ con tàu.
    """
    # 1. World Background (Ánh sáng môi trường tự nhiên)
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Ocean_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.35, 0.60, 0.85, 1.0) # Màu trời trong xanh
        bg.inputs['Strength'].default_value = 1.2

    # 2. Đèn Mặt Trời Vàng Hoàng Hôn
    sun_data = bpy.data.lights.new("Sun_KeyLight", type='SUN')
    sun_data.energy = 8.0
    sun_data.color = (1.0, 0.85, 0.65)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = Euler((math.radians(45), math.radians(18), math.radians(-50)))

    # 3. Tạo Target Empty tại giữa thân tàu để Camera luôn ngắm chuẩn
    target_empty = bpy.data.objects.new("Cam_Aim_Target", None)
    target_empty.empty_display_size = 1.0
    bpy.context.collection.objects.link(target_empty)
    target_empty.parent = root_obj
    target_empty.location = (0, 0, 3.5) # Ngắm vào giữa cột buồm và thân tàu

    # 4. Camera Điện Ảnh Toàn Cảnh
    cam_data = bpy.data.cameras.new("Cinema_Master_Cam")
    cam_data.lens = 32 # Ống kính góc rộng vừa phải để lấy toàn cảnh
    cam_obj = bpy.data.objects.new("Cinema_Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Khóa ngắm Camera vào Target
    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = target_empty
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Camera bám theo tàu ở khoảng cách 22m để thấy trọn vẹn
    cam_obj.parent = root_obj
    cam_obj.location = (16.0, -18.0, 8.5)

def main():
    print("=== BẮT ĐẦU TẠO CHIẾN THUYỀN CHÂN THẬT CHUẨN BLENDER ===")
    reset_scene()
    
    warship_root = build_high_quality_warship()
    ocean = build_ocean_with_foam()
    animate_warship_realistic_buoyancy(warship_root, total_frames=180)
    setup_cinema_camera_and_lighting(warship_root)

    desktop_dir = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
    os.makedirs(desktop_dir, exist_ok=True)
    
    blend_file = os.path.join(desktop_dir, "chien_thuyen_sieu_thuc.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f" ĐÃ LƯU FILE BLENDER GỐC TẠI: {blend_file}")

    # Render ảnh bằng chứng chất lượng cao 1080p tại Frame 45
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.frame_set(45)
    
    render_img = os.path.join(desktop_dir, "anh_kiem_chung_tau_chien.png")
    scene.render.filepath = render_img
    try:
        bpy.ops.render.render(write_still=True)
        print(f" ĐÃ RENDER ẢNH BẰNG CHỨNG TẠI: {render_img}")
    except Exception as e:
        print(f" Lỗi render: {e}")

if __name__ == "__main__":
    main()
