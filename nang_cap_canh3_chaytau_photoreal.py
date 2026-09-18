# -*- coding: utf-8 -*-
"""
NÂNG CẤP SIÊU THỰC PHÂN CẢNH SOÁI HẠM NAM HÁN BỐC CHÁY - BẠCH ĐẰNG 938
Tối ưu Shader ngọn lửa, làm mượt cột khói đen, bổ sung lưỡi lửa ôm buồm nan và hoàn thiện góc máy điện ảnh Hero Shot.
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler

def upgrade_fire_material():
    """
    Tinh chỉnh Mat_Lua_Chay_PBR:
    - Chống bloom bẹp trắng: giảm Emission Strength xuống 11.5, nén dải trắng nóng vào tâm.
    - Tạo các vân xoáy lưỡi lửa vi tế (Noise Texture chi tiết cao).
    - Thêm độ trong suốt Alpha ở rìa ngọn lửa để nhìn xuyên thấy buồm nan và khung gỗ cháy xém phía sau.
    """
    mat = bpy.data.materials.get("Mat_Lua_Chay_PBR")
    if not mat:
        return
    mat.use_nodes = True
    mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else 'OPAQUE'
    
    nt = mat.node_tree
    nt.nodes.clear()
    
    node_out = nt.nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (800, 0)
    
    node_mix = nt.nodes.new(type='ShaderNodeMixShader')
    node_mix.location = (600, 0)
    
    node_trans = nt.nodes.new(type='ShaderNodeBsdfTransparent')
    node_trans.location = (400, 100)
    
    node_emit = nt.nodes.new(type='ShaderNodeEmission')
    node_emit.location = (400, -100)
    node_emit.inputs['Strength'].default_value = 12.5
    
    # ColorRamp dải màu lửa PBR
    node_cr = nt.nodes.new(type='ShaderNodeValToRGB')
    node_cr.location = (100, -100)
    node_cr.color_ramp.interpolation = 'CARDINAL'
    
    node_cr.color_ramp.elements[0].position = 0.05
    node_cr.color_ramp.elements[0].color = (0.02, 0.005, 0.001, 1.0) # Muội khói nâu đen
    
    el1 = node_cr.color_ramp.elements[1]
    el1.position = 0.28
    el1.color = (0.85, 0.06, 0.002, 1.0) # Đỏ thẫm viền lửa
    
    el2 = node_cr.color_ramp.elements.new(0.55)
    el2.color = (1.0, 0.38, 0.015, 1.0) # Cam rực rỡ
    
    el3 = node_cr.color_ramp.elements.new(0.82)
    el3.color = (1.0, 0.85, 0.12, 1.0) # Vàng cam
    
    el4 = node_cr.color_ramp.elements.new(0.96)
    el4.color = (1.0, 0.98, 0.82, 1.0) # Lõi vàng trắng
    
    # ColorRamp điều khiển độ mờ Alpha
    node_cr_alpha = nt.nodes.new(type='ShaderNodeValToRGB')
    node_cr_alpha.location = (100, 150)
    node_cr_alpha.color_ramp.interpolation = 'EASE'
    node_cr_alpha.color_ramp.elements[0].position = 0.12
    node_cr_alpha.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0) # Trong suốt ở rìa
    node_cr_alpha.color_ramp.elements[1].position = 0.38
    node_cr_alpha.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0) # Đục dần vào trong
    
    # Texture Noise tạo xoáy ngọn lửa
    node_noise = nt.nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-150, 0)
    node_noise.inputs['Scale'].default_value = 5.2
    node_noise.inputs['Detail'].default_value = 6.0
    node_noise.inputs['Roughness'].default_value = 0.68
    
    node_coord = nt.nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-350, 0)
    
    nt.links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])
    nt.links.new(node_noise.outputs['Fac'], node_cr.inputs['Fac'])
    nt.links.new(node_noise.outputs['Fac'], node_cr_alpha.inputs['Fac'])
    nt.links.new(node_cr.outputs['Color'], node_emit.inputs['Color'])
    
    nt.links.new(node_cr_alpha.outputs['Color'], node_mix.inputs['Fac'])
    nt.links.new(node_trans.outputs['BSDF'], node_mix.inputs[1])
    nt.links.new(node_emit.outputs['Emission'], node_mix.inputs[2])
    nt.links.new(node_mix.outputs['Shader'], node_out.inputs['Surface'])
    
    print("✓ Đã nâng cấp Mat_Lua_Chay_PBR với dải màu quang học và độ trong suốt viền lửa.")

def smooth_and_refine_smoke():
    """
    Bật Shade Smooth và thêm Subdivision Surface cho 2 cột khói đen muội than
    """
    for name in ['Khoi_Den_Cuon_CotChinh', 'Khoi_Den_ManThuyen_Thap']:
        obj = bpy.data.objects.get(name)
        if obj and obj.type == 'MESH':
            # Shade Smooth
            for p in obj.data.polygons:
                p.use_smooth = True
            
            # Subsurf
            has_subsurf = any(m.type == 'SUBSURF' for m in obj.modifiers)
            if not has_subsurf:
                sub = obj.modifiers.new(name="Subsurf_Smoke", type='SUBSURF')
                sub.levels = 1
                sub.render_levels = 1
                
            # Tinh chỉnh độ nhám vật liệu
            mat = bpy.data.materials.get("Mat_Khoi_Den_PBR")
            if mat and mat.use_nodes:
                bsdf = mat.node_tree.nodes.get('Principled BSDF')
                if bsdf:
                    bsdf.inputs['Roughness'].default_value = 0.98
                    bsdf.inputs['Base Color'].default_value = (0.018, 0.018, 0.022, 1.0)
                    
    print("✓ Đã bật Shade Smooth và làm mịn các cột khói đen muội than.")

def add_sail_clinging_flames(master, mat_fire):
    """
    Thêm các lưỡi lửa mỏng ôm sát mặt cong của buồm nan tre (Sail-Clinging Flames)
    """
    name = "Lua_Bam_BuomNan_Tre"
    old_obj = bpy.data.objects.get(name)
    if old_obj:
        bpy.data.objects.remove(old_obj, do_unlink=True)
        
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    # Dựng các mảng lửa mỏng cong bám dọc theo cánh buồm nan
    # Buồm chính ở quanh X = 1.7m, Y = -0.6m, Z = 4.5m -> 11.5m
    for s_idx in range(6):
        bx = 1.2 + s_idx * 0.45 + random.uniform(-0.1, 0.1)
        by = -0.65 + random.uniform(-0.15, 0.15)
        bz = 5.2 + s_idx * 0.7
        h = random.uniform(2.8, 4.5)
        w = random.uniform(0.35, 0.65)
        
        # 4 đỉnh hình dải lửa uốn lượn
        v1 = bm.verts.new((bx - w*0.5, by, bz))
        v2 = bm.verts.new((bx + w*0.5, by, bz))
        v3 = bm.verts.new((bx + w*0.3 + 0.35, by - 0.2, bz + h*0.5))
        v4 = bm.verts.new((bx - w*0.3 + 0.35, by - 0.2, bz + h*0.5))
        v5 = bm.verts.new((bx + 0.65, by - 0.4, bz + h))
        
        bm.faces.new((v1, v2, v3, v4))
        bm.faces.new((v4, v3, v5))
        
    bm.to_mesh(mesh)
    bm.free()
    
    mesh.materials.append(mat_fire)
    for p in mesh.polygons:
        p.use_smooth = True
        
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    
    # Keyframe tương ứng
    obj.scale = (0.0001, 0.0001, 0.0001)
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.keyframe_insert(data_path="scale", frame=120)
    obj.scale = (0.45, 0.45, 0.45)
    obj.keyframe_insert(data_path="scale", frame=135)
    obj.scale = (1.0, 1.0, 1.0)
    obj.keyframe_insert(data_path="scale", frame=165)
    obj.scale = (1.15, 1.15, 1.15)
    obj.keyframe_insert(data_path="scale", frame=240)
    
    print("✓ Đã thêm các dải lửa bám ôm dọc buồm nan tre.")
    return obj

def refine_firelights():
    """
    Giảm độ chói đốm specular của đèn trên mặt nước để phản chiếu mềm mại và lung linh
    """
    for l_name in ['Light_LuaChay_HoangThao_Chinh', 'Light_LuaChay_VetToac_Nuoc']:
        obj = bpy.data.objects.get(l_name)
        if obj and obj.type == 'LIGHT':
            obj.data.specular_factor = 0.35
            obj.data.shadow_soft_size = 2.0
    print("✓ Đã làm dịu vệt phản chiếu đốm sáng trên mặt nước.")

def setup_hero_cinematic_camera(scene):
    """
    Căn chỉnh Camera_Canh3_LauThuyen_BocChay thành góc Hero Cinematic Shot tuyệt đối:
    - Góc nhìn thấp ngang mớn nước, lọt qua khe giữa các cọc ngầm
    - Nhìn thấy cọc sắt cắm thủng lườn mạn Tả, dăm gỗ nứt toác, lầu và buồm rực lửa
    """
    cam_name = "Camera_Canh3_LauThuyen_BocChay"
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        return
        
    cam_obj.data.lens = 24.0 # Siêu rộng điện ảnh
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 1000.0
    
    # Tọa độ thế giới căn chỉnh chuẩn xác:
    # Ở F160: Master ở (-0.68, 4.88, -1.47), nghiêng 25 độ
    # Cọc Coc_Hero_03_GoLim ở (-1.2, 1.8, -0.7)
    # Đặt camera tại (-3.8, -1.5, 0.6), nhìn chếch lên (0.0, 4.2, 2.8)
    
    # Frame 130 (Bắt đầu chuyển sang cảnh cháy tàu)
    cam_obj.location = Vector((-4.2, -2.2, 0.8))
    # Tính góc Euler hướng về tâm tàu
    cam_obj.rotation_euler = Euler((math.radians(76.0), math.radians(0.0), math.radians(-132.0)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=130)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=130)
    
    # Frame 160 (Cọc đâm toác lườn, lửa bùng phát)
    cam_obj.location = Vector((-3.6, -1.2, 0.55))
    cam_obj.rotation_euler = Euler((math.radians(78.5), math.radians(0.0), math.radians(-135.0)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=160)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=160)
    
    # Frame 200 (Soái hạm nghiêng lật, bốc cháy cực đại)
    cam_obj.location = Vector((-3.2, -0.5, 0.45))
    cam_obj.rotation_euler = Euler((math.radians(80.5), math.radians(0.0), math.radians(-137.0)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=200)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=200)
    
    # Frame 240
    cam_obj.location = Vector((-3.0, 0.0, 0.40))
    cam_obj.rotation_euler = Euler((math.radians(81.5), math.radians(0.0), math.radians(-138.5)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=240)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=240)
    
    print("✓ Đã căn chỉnh Camera Hero Shot điện ảnh hoàn mỹ.")

def run_upgrade():
    print("=== BẮT ĐẦU TINH CHỈNH SIÊU THỰC CẢNH TÀU BỐC CHÁY ===")
    master = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
    if not master:
        raise RuntimeError("Không tìm thấy LauThuyen_NamHan_HoangThao_Master!")
        
    upgrade_fire_material()
    smooth_and_refine_smoke()
    mat_fire = bpy.data.materials.get("Mat_Lua_Chay_PBR")
    add_sail_clinging_flames(master, mat_fire)
    refine_firelights()
    setup_hero_cinematic_camera(bpy.context.scene)
    
    bpy.context.view_layer.update()
    print("=== HOÀN TẤT TINH CHỈNH THÀNH CÔNG! ===")

if __name__ == "__main__":
    run_upgrade()
