# -*- coding: utf-8 -*-
"""
HOÀN THIỆN SIÊU THỰC CẢNH 3: SOÁI HẠM HOÀNG THÁO BỊ CỌC ĐÂM VÀ BỐC CHÁY
- Lưỡi lửa 3D đa tầng (Multi-layered Ribbon Flame Tongues)
- Shader lửa chân thực PBR (Depth & Shading, chống bloom bẹp trắng)
- Vết cháy xém loang lổ than đen trên buồm nan tre
- Góc máy Ultra-Wide Hero Shot bắt trọn từ cọc đâm mạn nước đến khói lửa buồm nan
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

def clear_old_flames():
    """Xóa các object lửa cũ để thay bằng hệ thống lưỡi lửa 3D đa tầng mới"""
    flame_names = ['Lua_BuomNan_CotChinh', 'Lua_LauChiHuy_MaiNgoi', 'Lua_VetToac_ManThuyen', 'Lua_Bam_BuomNan_Tre']
    for n in flame_names:
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    print("✓ Đã gỡ bỏ các khối lửa cũ.")

def build_advanced_fire_material():
    """
    Shader Lửa PBR Điện Ảnh:
    Kết hợp Principled BSDF (tạo khối, bóng đổ, độ sâu bề mặt) 
    và Emission được điều biến bằng Noise Texture 3D.
    """
    mat = bpy.data.materials.get("Mat_Lua_Chay_PBR")
    if not mat:
        mat = bpy.data.materials.new(name="Mat_Lua_Chay_PBR")
    mat.use_nodes = True
    
    nt = mat.node_tree
    nt.nodes.clear()
    
    node_out = nt.nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (700, 0)
    
    node_bsdf = nt.nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (350, 0)
    node_bsdf.inputs['Roughness'].default_value = 0.45
    node_bsdf.inputs['Specular IOR Level'].default_value = 0.2
    
    # Texture Noise điều biến ngọn lửa
    node_coord = nt.nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-450, 0)
    
    node_noise = nt.nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-250, 0)
    node_noise.inputs['Scale'].default_value = 3.2
    node_noise.inputs['Detail'].default_value = 5.0
    node_noise.inputs['Roughness'].default_value = 0.65
    nt.links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])
    
    # ColorRamp cho Base Color (Màu bề mặt lửa: Đỏ thẫm -> Cam than hồng)
    node_cr_base = nt.nodes.new(type='ShaderNodeValToRGB')
    node_cr_base.location = (50, 100)
    node_cr_base.color_ramp.elements[0].position = 0.1
    node_cr_base.color_ramp.elements[0].color = (0.05, 0.01, 0.002, 1.0) # Muội đen rìa
    node_cr_base.color_ramp.elements[1].position = 0.6
    node_cr_base.color_ramp.elements[1].color = (0.85, 0.15, 0.01, 1.0) # Đỏ thẫm
    node_cr_base.color_ramp.elements.new(0.95).color = (1.0, 0.45, 0.02, 1.0) # Cam rực
    nt.links.new(node_noise.outputs['Fac'], node_cr_base.inputs['Fac'])
    nt.links.new(node_cr_base.outputs['Color'], node_bsdf.inputs['Base Color'])
    
    # ColorRamp cho Emission Color & Strength (Màu phát sáng: Đỏ -> Cam -> Vàng cam)
    node_cr_emit = nt.nodes.new(type='ShaderNodeValToRGB')
    node_cr_emit.location = (50, -150)
    node_cr_emit.color_ramp.elements[0].position = 0.15
    node_cr_emit.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0) # Tắt phát sáng ở viền muội khói
    node_cr_emit.color_ramp.elements[1].position = 0.50
    node_cr_emit.color_ramp.elements[1].color = (1.0, 0.22, 0.01, 1.0) # Đỏ cam
    
    el_gold = node_cr_emit.color_ramp.elements.new(0.85)
    el_gold.color = (1.0, 0.72, 0.08, 1.0) # Vàng cam ấm áp
    
    el_core = node_cr_emit.color_ramp.elements.new(0.98)
    el_core.color = (1.0, 0.95, 0.65, 1.0) # Vàng rực lõi
    
    nt.links.new(node_noise.outputs['Fac'], node_cr_emit.inputs['Fac'])
    nt.links.new(node_cr_emit.outputs['Color'], node_bsdf.inputs['Emission Color'])
    
    # Math node nhân hệ số Emission vừa phải (5.5) chống bloom bẹp trắng
    node_math = nt.nodes.new(type='ShaderNodeMath')
    node_math.location = (150, -350)
    node_math.operation = 'MULTIPLY'
    node_math.inputs[1].default_value = 5.8
    nt.links.new(node_noise.outputs['Fac'], node_math.inputs[0])
    nt.links.new(node_math.outputs['Value'], node_bsdf.inputs['Emission Strength'])
    
    nt.links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    print("✓ Đã nâng cấp Shader Lửa PBR đa tầng hoàn mỹ.")
    return mat

def create_ribbon_flame_tongue(bm, origin, height, width, twist_factor, wind_drift, num_segments=10):
    """
    Tạo một lưỡi lửa 3D uốn lượn hình ngọn giáo nhọn (Ribbon Flame Tongue)
    """
    ox, oy, oz = origin
    w_drift_x, w_drift_y = wind_drift
    
    verts_left = []
    verts_right = []
    
    for i in range(num_segments + 1):
        t = i / float(num_segments) # 0.0 -> 1.0
        
        # Chiều cao
        cz = oz + t * height
        
        # Bề rộng: nở rộng ở 30% chiều cao rồi vuốt nhọn ở đỉnh
        w = width * math.sin(math.pi * (t**0.65))
        
        # Độ lệch theo gió (nghiêng dạt theo luồng gió mùa đông bắc)
        cx = ox + (t**1.4) * w_drift_x
        cy = oy + (t**1.4) * w_drift_y
        
        # Độ xoắn uốn lượn sin
        twist = math.sin(t * math.pi * 2.2 + twist_factor) * 0.25 * width
        
        # Góc xoay mặt phẳng lưỡi lửa
        ang = twist_factor + t * 0.8
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        
        vl = bm.verts.new((cx - w * cos_a * 0.5 + twist, cy - w * sin_a * 0.5, cz))
        vr = bm.verts.new((cx + w * cos_a * 0.5 + twist, cy + w * sin_a * 0.5, cz))
        verts_left.append(vl)
        verts_right.append(vr)
        
    for i in range(num_segments):
        bm.faces.new((verts_left[i], verts_right[i], verts_right[i+1], verts_left[i+1]))

def create_multi_layer_flame_cluster(name, tongues_spec, mat_fire, master):
    """
    Dựng cụm ngọn lửa từ nhiều lưỡi lửa 3D đan xen
    tongues_spec: list of tuples (ox, oy, oz, height, width, twist, wind_drift)
    """
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    for ox, oy, oz, h, w, tw, wd in tongues_spec:
        create_ribbon_flame_tongue(bm, (ox, oy, oz), h, w, tw, wd, num_segments=10)
        
    bm.to_mesh(mesh)
    bm.free()
    
    mesh.materials.append(mat_fire)
    for p in mesh.polygons:
        p.use_smooth = True
        
    # Thêm modifier Displace sóng gió
    disp = obj.modifiers.new(name="Flames_Wave", type='DISPLACE')
    tex = bpy.data.textures.new(name=f"Tex_Flames_{name}", type='CLOUDS')
    tex.noise_scale = 0.8
    tex.noise_depth = 2
    disp.texture = tex
    disp.strength = 0.22
    
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    return obj

def build_all_new_flame_clusters(master, mat_fire):
    """
    Dựng 3 cụm ngọn lửa mới với các dải lưỡi lửa uốn lượn sống động
    """
    # 1. Cụm Lửa Buồm Nan Tre Chính (8 lưỡi lửa cao từ 3.5m đến 7.5m)
    # Buồm chính ở X = 1.7, Y = -0.6, Z = 5.0 - 11.5
    sail_tongues = [
        # (ox, oy, oz, height, width, twist, (w_drift_x, w_drift_y))
        (1.2, -0.65, 5.0, 6.8, 1.4, 0.2, (1.8, -0.9)),
        (1.8, -0.55, 5.4, 7.5, 1.6, 0.8, (2.2, -1.1)),
        (2.3, -0.45, 5.2, 6.5, 1.3, -0.5, (1.6, -0.8)),
        (0.8, -0.75, 5.8, 5.5, 1.2, 1.2, (1.4, -0.7)),
        (2.6, -0.35, 6.0, 5.8, 1.1, -0.8, (1.9, -1.0)),
        (1.5, -0.60, 6.8, 5.2, 1.5, 0.4, (2.0, -1.0)),
        (1.9, -0.50, 7.5, 4.5, 1.2, -0.3, (1.5, -0.8)),
        (1.1, -0.70, 7.2, 4.8, 1.0, 0.9, (1.6, -0.9)),
    ]
    lua_buom = create_multi_layer_flame_cluster("Lua_BuomNan_CotChinh", sail_tongues, mat_fire, master)
    
    # 2. Cụm Lửa Lầu Chỉ Huy & Mái Ngói (6 lưỡi lửa bốc từ vì kèo cửa sổ)
    # Lầu ở X = -2.3, Y = 0.0, Z = 3.5 - 6.5
    cabin_tongues = [
        (-2.0, 0.4, 3.8, 4.5, 1.2, 0.3, (1.5, -0.7)),
        (-2.5, -0.4, 4.0, 5.2, 1.4, -0.4, (1.8, -0.9)),
        (-1.7, -0.2, 4.2, 4.8, 1.3, 0.7, (1.6, -0.8)),
        (-2.8, 0.3, 4.5, 4.2, 1.1, -0.6, (1.4, -0.7)),
        (-2.2, 0.0, 5.2, 3.8, 1.5, 0.1, (1.5, -0.8)),
        (-2.6, -0.2, 5.5, 3.5, 1.0, 0.5, (1.3, -0.6)),
    ]
    lua_lau = create_multi_layer_flame_cluster("Lua_LauChiHuy_MaiNgoi", cabin_tongues, mat_fire, master)
    
    # 3. Cụm Lửa Vết Toác Lườn Tàu (Nơi cọc đâm, Z = 0.3 - 2.8)
    breach_tongues = [
        (0.4, 2.35, 0.4, 2.8, 0.85, 0.1, (0.8, -0.4)),
        (0.6, 2.30, 0.6, 3.2, 0.95, -0.3, (1.0, -0.5)),
        (0.2, 2.40, 0.5, 2.5, 0.75, 0.4, (0.7, -0.3)),
        (0.8, 2.25, 0.8, 2.6, 0.80, -0.2, (0.9, -0.4)),
    ]
    lua_breach = create_multi_layer_flame_cluster("Lua_VetToac_ManThuyen", breach_tongues, mat_fire, master)
    
    # Thiết lập Keyframes cho 3 cụm ngọn lửa mới
    for obj in [lua_buom, lua_lau, lua_breach]:
        obj.scale = (0.0001, 0.0001, 0.0001)
        obj.keyframe_insert(data_path="scale", frame=1)
        obj.keyframe_insert(data_path="scale", frame=115)
        obj.scale = (0.25, 0.25, 0.25)
        obj.keyframe_insert(data_path="scale", frame=128)
        obj.scale = (0.70, 0.70, 0.70)
        obj.keyframe_insert(data_path="scale", frame=145)
        obj.scale = (1.0, 1.0, 1.0)
        obj.keyframe_insert(data_path="scale", frame=165)
        obj.scale = (1.15, 1.15, 1.15)
        obj.keyframe_insert(data_path="scale", frame=200)
        obj.scale = (1.12, 1.12, 1.12)
        obj.keyframe_insert(data_path="scale", frame=240)
        
    print("✓ Đã dựng xong toàn bộ 3 cụm ngọn lửa 3D đa tầng siêu thực.")
    return [lua_buom, lua_lau, lua_breach]

def add_charred_burn_marks_to_sail():
    """
    Thêm vết cháy xém than đen loang lổ trên buồm nan tre của Nam Hán
    """
    mat = bpy.data.materials.get("Mat_NamHan_BuomNan_ThoHoang")
    if not mat or not mat.use_nodes:
        return
    nt = mat.node_tree
    
    # Tìm BSDF Principled
    bsdf = nt.nodes.get("Principled BSDF") or nt.nodes.get("BSDF_PRINCIPLED")
    if not bsdf:
        return
        
    # Tạo node Noise và ColorRamp cho vết cháy xém than đen
    node_coord = nt.nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-600, 200)
    
    node_noise_burn = nt.nodes.new(type='ShaderNodeTexNoise')
    node_noise_burn.location = (-400, 200)
    node_noise_burn.inputs['Scale'].default_value = 2.8
    node_noise_burn.inputs['Detail'].default_value = 6.0
    node_noise_burn.inputs['Roughness'].default_value = 0.75
    nt.links.new(node_coord.outputs['Object'], node_noise_burn.inputs['Vector'])
    
    node_cr_burn = nt.nodes.new(type='ShaderNodeValToRGB')
    node_cr_burn.location = (-200, 200)
    node_cr_burn.color_ramp.interpolation = 'EASE'
    node_cr_burn.color_ramp.elements[0].position = 0.35
    node_cr_burn.color_ramp.elements[0].color = (0.015, 0.012, 0.01, 1.0) # Vết cháy than đen kịt
    node_cr_burn.color_ramp.elements[1].position = 0.58
    node_cr_burn.color_ramp.elements[1].color = (0.45, 0.22, 0.08, 1.0) # Vùng xém nâu sẫm
    node_cr_burn.color_ramp.elements.new(0.72).color = (0.82, 0.72, 0.58, 1.0) # Màu buồm nan tre nguyên bản
    
    nt.links.new(node_noise_burn.outputs['Fac'], node_cr_burn.inputs['Fac'])
    nt.links.new(node_cr_burn.outputs['Color'], bsdf.inputs['Base Color'])
    
    print("✓ Đã thêm vết cháy xém than đen loang lổ trên buồm nan tre.")

def setup_master_hero_camera(scene):
    """
    Thiết lập góc quay Hero Shot Ultra-Wide hoàn hảo cho Camera_Canh3_LauThuyen_BocChay:
    - Bắt trọn từ mớn nước, đầu cọc cắm thủng ván thuyền đến đỉnh buồm nan rực lửa và cột khói vút trời.
    """
    cam_name = "Camera_Canh3_LauThuyen_BocChay"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(name=cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.collection.objects.link(cam_obj)
        
    cam_obj.data.lens = 20.0 # Góc siêu rộng điện ảnh 20mm
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 1000.0
    
    # Frame 130: Bắt đầu chuyển cảnh sang hạm đội giặc mắc cạn
    cam_obj.location = Vector((-8.5, -5.5, 2.5))
    cam_obj.rotation_euler = Euler((math.radians(72.0), math.radians(0.0), math.radians(-126.0)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=130)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=130)
    
    # Frame 160: Cọc sắt đâm toác lườn, ngọn lửa bùng phát
    cam_obj.location = Vector((-7.2, -4.2, 1.9))
    cam_obj.rotation_euler = Euler((math.radians(74.5), math.radians(0.0), math.radians(-128.5)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=160)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=160)
    
    # Frame 200: Cháy dữ dội cực đại, soái hạm nghiêng lật
    cam_obj.location = Vector((-6.0, -3.0, 1.4))
    cam_obj.rotation_euler = Euler((math.radians(77.0), math.radians(0.0), math.radians(-131.0)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=200)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=200)
    
    # Frame 240: Kết thúc cảnh 3
    cam_obj.location = Vector((-5.5, -2.5, 1.2))
    cam_obj.rotation_euler = Euler((math.radians(78.5), math.radians(0.0), math.radians(-132.5)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=240)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=240)
    
    # Cập nhật marker
    marker_name = "Canh3_LauThuyen_BocChay"
    marker = None
    for m in scene.timeline_markers:
        if m.name == marker_name or m.frame == 130:
            marker = m
            break
    if not marker:
        marker = scene.timeline_markers.new(marker_name, frame=130)
    marker.name = marker_name
    marker.frame = 130
    marker.camera = cam_obj
    
    print("✓ Đã thiết lập Hero Ultra-Wide Camera góc máy điện ảnh hoàn hảo.")

def save_master_blend():
    """Lưu lại master blend file sau khi nâng cấp hoàn thiện"""
    blend_path = r"C:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_step3_counter_offensive.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Đã lưu Master Scene vào: {blend_path}")

def run_master_pipeline():
    print("=== BẮT ĐẦU HOÀN THIỆN SIÊU THỰC CẢNH 3 ===")
    master = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
    if not master:
        raise RuntimeError("Không tìm thấy LauThuyen_NamHan_HoangThao_Master!")
        
    clear_old_flames()
    mat_fire = build_advanced_fire_material()
    build_all_new_flame_clusters(master, mat_fire)
    add_charred_burn_marks_to_sail()
    setup_master_hero_camera(bpy.context.scene)
    bpy.context.view_layer.update()
    save_master_blend()
    print("=== HOÀN TẤT HOÀN THIỆN SIÊU THỰC 100%! ===")

if __name__ == "__main__":
    run_master_pipeline()
