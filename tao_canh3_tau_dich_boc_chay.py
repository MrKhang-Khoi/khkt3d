# -*- coding: utf-8 -*-
"""
TẠO CẢNH 3: SOÁI HẠM HOÀNG THÁO ĐÂM CỌC VÀ BỐC CHÁY SIÊU THỰC - BẠCH ĐẰNG 938
Quy chuẩn Lịch sử và Đồ họa Điện ảnh 3D PBR
"""
import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

def clear_old_fire_elements():
    prefix_list = ['Lua_', 'Khoi_', 'Tan_Tro_', 'HoaTien_', 'VetToac_', 'Light_LuaChay_', 'Camera_Canh3_LauThuyen_BocChay']
    to_delete = [o for o in bpy.data.objects if any(o.name.startswith(p) for p in prefix_list)]
    for o in to_delete:
        bpy.data.objects.remove(o, do_unlink=True)
    print(f"Đã dọn dẹp {len(to_delete)} vật thể lửa khói cũ.")

def ensure_materials():
    # 1. Mat_Lua_Chay_PBR
    mat_fire = bpy.data.materials.get("Mat_Lua_Chay_PBR")
    if not mat_fire:
        mat_fire = bpy.data.materials.new(name="Mat_Lua_Chay_PBR")
        mat_fire.use_nodes = True
    
    nt = mat_fire.node_tree
    nt.nodes.clear()
    
    node_out = nt.nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    
    node_emit = nt.nodes.new(type='ShaderNodeEmission')
    node_emit.location = (350, 0)
    node_emit.inputs['Strength'].default_value = 28.0
    
    node_cr = nt.nodes.new(type='ShaderNodeValToRGB')
    node_cr.location = (50, 0)
    node_cr.color_ramp.interpolation = 'EASE'
    node_cr.color_ramp.elements[0].position = 0.15
    node_cr.color_ramp.elements[0].color = (0.05, 0.0, 0.0, 1.0)
    
    el1 = node_cr.color_ramp.elements[1]
    el1.position = 0.40
    el1.color = (1.0, 0.08, 0.005, 1.0)
    
    el2 = node_cr.color_ramp.elements.new(0.68)
    el2.color = (1.0, 0.45, 0.02, 1.0)
    
    el3 = node_cr.color_ramp.elements.new(0.88)
    el3.color = (1.0, 0.90, 0.15, 1.0)
    
    el4 = node_cr.color_ramp.elements.new(0.98)
    el4.color = (1.0, 1.0, 0.85, 1.0)
    
    node_noise = nt.nodes.new(type='ShaderNodeTexNoise')
    node_noise.location = (-200, 0)
    node_noise.inputs['Scale'].default_value = 3.8
    node_noise.inputs['Detail'].default_value = 4.0
    node_noise.inputs['Roughness'].default_value = 0.65
    
    node_coord = nt.nodes.new(type='ShaderNodeTexCoord')
    node_coord.location = (-400, 0)
    
    nt.links.new(node_coord.outputs['Object'], node_noise.inputs['Vector'])
    nt.links.new(node_noise.outputs['Fac'], node_cr.inputs['Fac'])
    nt.links.new(node_cr.outputs['Color'], node_emit.inputs['Color'])
    nt.links.new(node_emit.outputs['Emission'], node_out.inputs['Surface'])
    
    # 2. Mat_Khoi_Den_PBR
    mat_smoke = bpy.data.materials.get("Mat_Khoi_Den_PBR")
    if not mat_smoke:
        mat_smoke = bpy.data.materials.new(name="Mat_Khoi_Den_PBR")
        mat_smoke.use_nodes = True
        
    nt_s = mat_smoke.node_tree
    nt_s.nodes.clear()
    out_s = nt_s.nodes.new(type='ShaderNodeOutputMaterial')
    out_s.location = (400, 0)
    bsdf_s = nt_s.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf_s.location = (100, 0)
    bsdf_s.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
    bsdf_s.inputs['Roughness'].default_value = 0.96
    bsdf_s.inputs['Specular IOR Level'].default_value = 0.05
    nt_s.links.new(bsdf_s.outputs['BSDF'], out_s.inputs['Surface'])
    
    # 3. Mat_Tan_Tro_PBR
    mat_ember = bpy.data.materials.get("Mat_Tan_Tro_PBR")
    if not mat_ember:
        mat_ember = bpy.data.materials.new(name="Mat_Tan_Tro_PBR")
        mat_ember.use_nodes = True
        
    nt_e = mat_ember.node_tree
    nt_e.nodes.clear()
    out_e = nt_e.nodes.new(type='ShaderNodeOutputMaterial')
    out_e.location = (400, 0)
    emit_e = nt_e.nodes.new(type='ShaderNodeEmission')
    emit_e.location = (100, 0)
    emit_e.inputs['Color'].default_value = (1.0, 0.40, 0.03, 1.0)
    emit_e.inputs['Strength'].default_value = 35.0
    nt_e.links.new(emit_e.outputs['Emission'], out_e.inputs['Surface'])
    
    # 4. Mat_Go_Chay_Xem
    mat_wood_char = bpy.data.materials.get("Mat_Go_Chay_Xem")
    if not mat_wood_char:
        mat_wood_char = bpy.data.materials.new(name="Mat_Go_Chay_Xem")
        mat_wood_char.use_nodes = True
        nt_w = mat_wood_char.node_tree
        nt_w.nodes.clear()
        out_w = nt_w.nodes.new(type='ShaderNodeOutputMaterial')
        out_w.location = (400, 0)
        bsdf_w = nt_w.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf_w.location = (100, 0)
        bsdf_w.inputs['Base Color'].default_value = (0.04, 0.025, 0.015, 1.0)
        bsdf_w.inputs['Roughness'].default_value = 0.90
        nt_w.links.new(bsdf_w.outputs['BSDF'], out_w.inputs['Surface'])
        
    return mat_fire, mat_smoke, mat_ember, mat_wood_char

def create_hull_breach_and_splinters(master, mat_wood_char, mat_ember):
    mesh = bpy.data.meshes.new("Mesh_VetToac_ManThuyen")
    obj = bpy.data.objects.new("VetToac_ManThuyen_NamHan", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    cx, cy, cz = 0.5, 2.38, 0.35
    num_rim = 14
    rim_verts = []
    for i in range(num_rim):
        angle = 2 * math.pi * i / num_rim
        rx = 1.35 * math.cos(angle) + random.uniform(-0.15, 0.15)
        rz = 0.75 * math.sin(angle) + random.uniform(-0.10, 0.10)
        ry = random.uniform(-0.08, 0.08)
        v = bm.verts.new((cx + rx, cy + ry, cz + rz))
        rim_verts.append(v)
        
    for i in range(num_rim):
        v0 = rim_verts[i]
        v1 = rim_verts[(i + 1) % num_rim]
        dx = (v0.co.x + v1.co.x) * 0.5 - cx
        dz = (v0.co.z + v1.co.z) * 0.5 - cz
        length = random.uniform(0.4, 0.85)
        tip_x = cx + dx * (1.0 + length)
        tip_y = cy + random.uniform(0.25, 0.65)
        tip_z = cz + dz * (1.0 + length) + random.uniform(-0.15, 0.25)
        v_tip = bm.verts.new((tip_x, tip_y, tip_z))
        bm.faces.new((v0, v1, v_tip))
        thick = 0.06
        v0_in = bm.verts.new((v0.co.x, v0.co.y - thick, v0.co.z))
        v1_in = bm.verts.new((v1.co.x, v1.co.y - thick, v1.co.z))
        bm.faces.new((v0, v0_in, v1_in, v1))
        
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_wood_char)
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    return obj

def create_fire_arrows(master, mat_wood_char, mat_fire):
    mesh = bpy.data.meshes.new("Mesh_HoaTien_DaiViet")
    obj = bpy.data.objects.new("HoaTien_DaiViet_Cluster", mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    
    arrow_targets = [
        (1.2, -0.7, 6.2, 0.3, -0.4, 0.8),
        (2.1, -0.5, 7.5, 0.2, -0.3, 0.6),
        (1.5, -0.6, 8.8, 0.4, -0.2, 0.9),
        (2.6, -0.4, 6.8, 0.1, -0.5, 0.7),
        (0.8, -0.8, 9.2, 0.3, -0.3, 0.5),
        (1.9, -0.6, 10.2, 0.2, -0.4, 0.8),
        (0.2, 2.4, 1.8, 0.5, 0.2, -0.6),
        (1.1, 2.4, 2.2, 0.4, 0.1, -0.5),
        (2.3, 2.3, 1.5, 0.6, 0.3, -0.7),
        (-0.5, 2.4, 2.0, 0.5, 0.0, -0.4),
        (-1.8, 0.5, 5.2, 0.2, 0.4, -0.8),
        (-2.4, -0.6, 5.8, 0.3, -0.3, 0.7),
        (-2.0, 1.2, 4.6, 0.4, 0.2, -0.5),
        (-3.1, 0.2, 6.2, 0.1, 0.5, -0.9),
    ]
    
    for tx, ty, tz, rx, ry, rz in arrow_targets:
        rot_mat = Euler((rx, ry, rz), 'XYZ').to_matrix()
        forward = rot_mat @ Vector((0, 0, 1))
        side = rot_mat @ Vector((1, 0, 0))
        up = rot_mat @ Vector((0, 1, 0))
        p_base = Vector((tx, ty, tz))
        p_tip = p_base - forward * 0.95
        
        r_shaft = 0.015
        shaft_v_base = []
        shaft_v_tip = []
        for a_idx in range(6):
            ang = 2 * math.pi * a_idx / 6
            offset = (side * math.cos(ang) + up * math.sin(ang)) * r_shaft
            shaft_v_base.append(bm.verts.new(p_base + offset))
            shaft_v_tip.append(bm.verts.new(p_tip + offset))
            
        for a_idx in range(6):
            b1 = shaft_v_base[a_idx]
            b2 = shaft_v_base[(a_idx + 1) % 6]
            t1 = shaft_v_tip[a_idx]
            t2 = shaft_v_tip[(a_idx + 1) % 6]
            bm.faces.new((b1, b2, t2, t1))
            
        r_fire = 0.09
        p_ball = p_base - forward * 0.15
        ball_verts = []
        for b_i in range(8):
            ang = 2 * math.pi * b_i / 8
            bo = (side * math.cos(ang) + up * math.sin(ang)) * r_fire
            bv = bm.verts.new(p_ball + bo + forward * random.uniform(-0.04, 0.04))
            ball_verts.append(bv)
        bv_tip = bm.verts.new(p_base + forward * 0.05)
        bv_back = bm.verts.new(p_ball - forward * 0.15)
        for b_i in range(8):
            b_next = (b_i + 1) % 8
            bm.faces.new((ball_verts[b_i], ball_verts[b_next], bv_tip))
            bm.faces.new((ball_verts[b_next], ball_verts[b_i], bv_back))
            
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_fire)
    mesh.materials.append(mat_wood_char)
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    return obj

def build_flame_geometry(name, center, scale_xyz, tilt_angle, mat_fire, master):
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    cx, cy, cz = center
    sx, sy, sz = scale_xyz
    
    flame_tongues = [
        (0.0, 0.0, 1.0, 1.0, 0.0),
        (0.25 * sx, -0.15 * sy, 0.85, 0.75, 0.2),
        (-0.28 * sx, 0.10 * sy, 0.78, 0.70, -0.25),
        (0.12 * sx, 0.22 * sy, 0.92, 0.65, 0.15),
        (-0.15 * sx, -0.20 * sy, 0.70, 0.60, -0.18),
        (0.35 * sx, 0.12 * sy, 0.60, 0.50, 0.35),
    ]
    
    for ox, oy, h_rat, w_rat, tw in flame_tongues:
        base_x = cx + ox
        base_y = cy + oy
        h = sz * h_rat
        w = sx * w_rat * 0.5
        
        layers_z = [0.0, 0.22 * h, 0.50 * h, 0.78 * h, h]
        layer_radii = [0.4 * w, 1.0 * w, 0.75 * w, 0.35 * w, 0.02 * w]
        
        layer_verts = []
        for l_idx, (lz, lr) in enumerate(zip(layers_z, layer_radii)):
            wind_drift_x = (lz / h)**1.4 * 0.65 * sx
            wind_drift_y = -(lz / h)**1.4 * 0.35 * sy
            l_v = []
            num_sec = 8
            for s_i in range(num_sec):
                ang = 2 * math.pi * s_i / num_sec + tw * (lz / h)
                vx = base_x + wind_drift_x + lr * math.cos(ang) + random.uniform(-0.05, 0.05) * lr
                vy = base_y + wind_drift_y + lr * 0.65 * math.sin(ang) + random.uniform(-0.05, 0.05) * lr
                vz = cz + lz
                v = bm.verts.new((vx, vy, vz))
                l_v.append(v)
            layer_verts.append(l_v)
            
        for l_idx in range(len(layers_z) - 1):
            lv1 = layer_verts[l_idx]
            lv2 = layer_verts[l_idx + 1]
            for s_i in range(num_sec):
                s_next = (s_i + 1) % num_sec
                bm.faces.new((lv1[s_i], lv1[s_next], lv2[s_next], lv2[s_i]))
                
        top_tip = bm.verts.new((base_x + 0.75 * sx, base_y - 0.40 * sy, cz + h + 0.1 * sz))
        top_ring = layer_verts[-1]
        for s_i in range(num_sec):
            s_next = (s_i + 1) % num_sec
            bm.faces.new((top_ring[s_i], top_ring[s_next], top_tip))
            
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_fire)
    
    disp = obj.modifiers.new(name="Fire_Distort", type='DISPLACE')
    tex = bpy.data.textures.new(name=f"Tex_Fire_{name}", type='CLOUDS')
    tex.noise_scale = 0.65
    tex.noise_depth = 2
    disp.texture = tex
    disp.strength = 0.28
    
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    return obj

def build_smoke_column(name, base_pos, height, max_radius, mat_smoke, master):
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bx, by, bz = base_pos
    num_puffs = 18
    
    for i in range(num_puffs):
        t = i / (num_puffs - 1)
        r = 0.8 + (max_radius - 0.8) * (t**0.7) + random.uniform(-0.2, 0.3)
        pz = bz + t * height
        px = bx + (t**1.3) * 7.5 + random.uniform(-0.5, 0.5)
        py = by - (t**1.3) * 4.8 + random.uniform(-0.5, 0.5)
        
        num_u = 8
        num_v = 6
        puff_layers = []
        for v_i in range(num_v):
            phi = math.pi * v_i / (num_v - 1)
            rz_ring = r * math.sin(phi)
            pz_ring = pz + r * math.cos(phi) * 0.85
            ring_verts = []
            for u_i in range(num_u):
                theta = 2 * math.pi * u_i / num_u
                noise_disp = random.uniform(-0.15, 0.20) * r
                vx = px + (rz_ring + noise_disp) * math.cos(theta)
                vy = py + (rz_ring + noise_disp) * 0.85 * math.sin(theta)
                vz = pz_ring + random.uniform(-0.1, 0.1) * r
                ring_verts.append(bm.verts.new((vx, vy, vz)))
            puff_layers.append(ring_verts)
            
        for v_i in range(num_v - 1):
            r1 = puff_layers[v_i]
            r2 = puff_layers[v_i + 1]
            for u_i in range(num_u):
                u_next = (u_i + 1) % num_u
                bm.faces.new((r1[u_i], r1[u_next], r2[u_next], r2[u_i]))
                
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_smoke)
    
    disp = obj.modifiers.new(name="Smoke_Turbulence", type='DISPLACE')
    tex = bpy.data.textures.new(name=f"Tex_Smoke_{name}", type='CLOUDS')
    tex.noise_scale = 1.2
    tex.noise_depth = 3
    disp.texture = tex
    disp.strength = 0.55
    
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    return obj

def build_embers_cluster(name, center, spread_xyz, count, mat_ember, master):
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    cx, cy, cz = center
    sx, sy, sz = spread_xyz
    
    for _ in range(count):
        ex = cx + random.uniform(-sx, sx) + (random.random()**1.5) * 2.5
        ey = cy + random.uniform(-sy, sy) - (random.random()**1.5) * 1.8
        ez = cz + random.uniform(-0.2 * sz, sz)
        er = random.uniform(0.04, 0.12)
        v1 = bm.verts.new((ex, ey, ez + er))
        v2 = bm.verts.new((ex + er * 0.9, ey - er * 0.5, ez - er * 0.5))
        v3 = bm.verts.new((ex - er * 0.9, ey - er * 0.5, ez - er * 0.5))
        v4 = bm.verts.new((ex, ey + er * 0.9, ez - er * 0.5))
        bm.faces.new((v1, v2, v3))
        bm.faces.new((v1, v3, v4))
        bm.faces.new((v1, v4, v2))
        bm.faces.new((v2, v4, v3))
        
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_ember)
    obj.parent = master
    obj.matrix_parent_inverse = master.matrix_world.inverted()
    return obj

def create_dynamic_firelights(master):
    light_data_main = bpy.data.lights.new(name="Data_Light_LuaChay_Main", type='POINT')
    light_data_main.color = (1.0, 0.32, 0.04)
    light_data_main.energy = 0.0
    light_data_main.shadow_soft_size = 1.2
    
    light_obj_main = bpy.data.objects.new("Light_LuaChay_HoangThao_Chinh", light_data_main)
    light_obj_main.location = (0.8, -0.3, 6.5)
    bpy.context.collection.objects.link(light_obj_main)
    light_obj_main.parent = master
    light_obj_main.matrix_parent_inverse = master.matrix_world.inverted()
    
    light_data_water = bpy.data.lights.new(name="Data_Light_LuaChay_Water", type='POINT')
    light_data_water.color = (1.0, 0.15, 0.01)
    light_data_water.energy = 0.0
    light_data_water.shadow_soft_size = 0.6
    
    light_obj_water = bpy.data.objects.new("Light_LuaChay_VetToac_Nuoc", light_data_water)
    light_obj_water.location = (0.5, 2.3, 0.2)
    bpy.context.collection.objects.link(light_obj_water)
    light_obj_water.parent = master
    light_obj_water.matrix_parent_inverse = master.matrix_world.inverted()
    
    return light_obj_main, light_obj_water

def animate_fire_and_lights(fire_objs, smoke_objs, breach_obj, arrow_obj, embers_obj, light_main, light_water):
    for obj in fire_objs + smoke_objs + [embers_obj]:
        obj.scale = (0.0001, 0.0001, 0.0001)
        obj.keyframe_insert(data_path="scale", frame=1)
        obj.keyframe_insert(data_path="scale", frame=115)
        obj.scale = (0.22, 0.22, 0.25)
        obj.keyframe_insert(data_path="scale", frame=128)
        obj.scale = (0.68, 0.68, 0.72)
        obj.keyframe_insert(data_path="scale", frame=145)
        obj.scale = (1.0, 1.0, 1.0)
        obj.keyframe_insert(data_path="scale", frame=165)
        obj.scale = (1.15, 1.15, 1.20)
        obj.keyframe_insert(data_path="scale", frame=200)
        obj.scale = (1.12, 1.12, 1.18)
        obj.keyframe_insert(data_path="scale", frame=240)
        
    breach_obj.scale = (0.0001, 0.0001, 0.0001)
    breach_obj.keyframe_insert(data_path="scale", frame=1)
    breach_obj.keyframe_insert(data_path="scale", frame=135)
    breach_obj.scale = (0.5, 0.5, 0.5)
    breach_obj.keyframe_insert(data_path="scale", frame=142)
    breach_obj.scale = (1.0, 1.0, 1.0)
    breach_obj.keyframe_insert(data_path="scale", frame=150)
    breach_obj.keyframe_insert(data_path="scale", frame=240)
    
    arrow_obj.scale = (0.0001, 0.0001, 0.0001)
    arrow_obj.keyframe_insert(data_path="scale", frame=1)
    arrow_obj.keyframe_insert(data_path="scale", frame=118)
    arrow_obj.scale = (1.0, 1.0, 1.0)
    arrow_obj.keyframe_insert(data_path="scale", frame=122)
    arrow_obj.keyframe_insert(data_path="scale", frame=240)
    
    lm = light_main.data
    lm.energy = 0.0
    lm.keyframe_insert(data_path="energy", frame=1)
    lm.keyframe_insert(data_path="energy", frame=115)
    lm.energy = 600.0
    lm.keyframe_insert(data_path="energy", frame=130)
    lm.energy = 2200.0
    lm.keyframe_insert(data_path="energy", frame=148)
    lm.energy = 3600.0
    lm.keyframe_insert(data_path="energy", frame=165)
    lm.energy = 3800.0
    lm.keyframe_insert(data_path="energy", frame=240)
    
    if lm.animation_data and lm.animation_data.action:
        fcs = getattr(lm.animation_data.action, 'fcurves', None)
        if not fcs and hasattr(lm.animation_data.action, 'layers'):
            try:
                fcs = lm.animation_data.action.layers[0].strips[0].channelbags[0].fcurves
            except Exception:
                fcs = None
        if fcs:
            for fc in fcs:
                if 'energy' in fc.data_path:
                    noise_mod = fc.modifiers.new(type='NOISE')
                    noise_mod.scale = 3.5
                    noise_mod.strength = 750.0
                    noise_mod.depth = 1
                    noise_mod.blend_type = 'ADD'
                    noise_mod.use_restricted_range = True
                    noise_mod.frame_start = 125
                    noise_mod.frame_end = 240
                
    lw = light_water.data
    lw.energy = 0.0
    lw.keyframe_insert(data_path="energy", frame=1)
    lw.keyframe_insert(data_path="energy", frame=138)
    lw.energy = 1200.0
    lw.keyframe_insert(data_path="energy", frame=150)
    lw.energy = 1800.0
    lw.keyframe_insert(data_path="energy", frame=170)
    lw.energy = 1900.0
    lw.keyframe_insert(data_path="energy", frame=240)
    
    if lw.animation_data and lw.animation_data.action:
        fcs = getattr(lw.animation_data.action, 'fcurves', None)
        if not fcs and hasattr(lw.animation_data.action, 'layers'):
            try:
                fcs = lw.animation_data.action.layers[0].strips[0].channelbags[0].fcurves
            except Exception:
                fcs = None
        if fcs:
            for fc in fcs:
                if 'energy' in fc.data_path:
                    noise_mod = fc.modifiers.new(type='NOISE')
                    noise_mod.scale = 2.8
                    noise_mod.strength = 450.0
                    noise_mod.blend_type = 'ADD'
                    noise_mod.use_restricted_range = True
                    noise_mod.frame_start = 140
                    noise_mod.frame_end = 240

def create_cinematic_fire_camera(scene):
    cam_name = "Camera_Canh3_LauThuyen_BocChay"
    cam_data = bpy.data.cameras.get(cam_name)
    if not cam_data:
        cam_data = bpy.data.cameras.new(name=cam_name)
        
    cam_data.lens = 26.0
    cam_data.clip_start = 0.2
    cam_data.clip_end = 800.0
    cam_data.dof.use_dof = False
    
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.collection.objects.link(cam_obj)
        
    cam_obj.location = Vector((-6.2, 0.2, 0.1))
    cam_obj.rotation_euler = Euler((math.radians(81.0), math.radians(0.0), math.radians(-123.0)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=130)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=130)
    
    cam_obj.location = Vector((-4.6, 1.5, -0.15))
    cam_obj.rotation_euler = Euler((math.radians(83.5), math.radians(0.0), math.radians(-127.5)), 'XYZ')
    cam_obj.keyframe_insert(data_path="location", frame=240)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=240)
    
    marker_name = "Canh3_LauThuyen_BocChay"
    marker = None
    for m in scene.timeline_markers:
        if m.name == marker_name or m.frame == 130:
            marker = m
            marker.name = marker_name
            marker.frame = 130
            break
    if not marker:
        marker = scene.timeline_markers.new(marker_name, frame=130)
    marker.camera = cam_obj
    return cam_obj

def run_pipeline():
    print("=== BẮT ĐẦU DỰNG CẢNH 3: TÀU ĐỊCH BỊ CỌC ĐÂM, BỐC CHÁY SIÊU THỰC ===")
    master = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
    if not master:
        raise RuntimeError("Không tìm thấy LauThuyen_NamHan_HoangThao_Master trong Scene!")
        
    clear_old_fire_elements()
    mat_fire, mat_smoke, mat_ember, mat_wood_char = ensure_materials()
    
    breach_obj = create_hull_breach_and_splinters(master, mat_wood_char, mat_ember)
    print("✓ Đã tạo vết toác lườn tàu và 18 mảnh dăm gỗ.")
    
    arrow_obj = create_fire_arrows(master, mat_wood_char, mat_fire)
    print("✓ Đã cắm 14 mũi hỏa tiễn bốc lửa trên buồm nan và mạn thuyền.")
    
    lua_buom = build_flame_geometry("Lua_BuomNan_CotChinh", (1.7, -0.6, 6.8), (3.2, 1.8, 6.8), 0.15, mat_fire, master)
    lua_lau = build_flame_geometry("Lua_LauChiHuy_MaiNgoi", (-2.3, 0.0, 5.2), (3.8, 2.6, 4.2), -0.10, mat_fire, master)
    lua_man = build_flame_geometry("Lua_VetToac_ManThuyen", (0.5, 2.3, 0.7), (2.0, 1.2, 2.8), 0.25, mat_fire, master)
    fire_objs = [lua_buom, lua_lau, lua_man]
    print("✓ Đã dựng 3 cụm ngọn lửa PBR cuộn xoáy.")
    
    khoi_chinh = build_smoke_column("Khoi_Den_Cuon_CotChinh", (1.5, -0.5, 8.5), 16.5, 4.8, mat_smoke, master)
    khoi_man = build_smoke_column("Khoi_Den_ManThuyen_Thap", (0.5, 2.3, 1.2), 6.5, 2.2, mat_smoke, master)
    smoke_objs = [khoi_chinh, khoi_man]
    print("✓ Đã dựng 2 cột khói đen muội than bạt theo gió mùa đông bắc.")
    
    embers_obj = build_embers_cluster("Tan_Tro_ThanHong_Cluster", (1.2, -0.4, 7.5), (2.5, 1.8, 4.5), 60, mat_ember, master)
    print("✓ Đã tạo 60 đốm tàn tro than hồng phát sáng.")
    
    light_main, light_water = create_dynamic_firelights(master)
    print("✓ Đã thiết lập 2 nguồn sáng động Dynamic Firelight.")
    
    animate_fire_and_lights(fire_objs, smoke_objs, breach_obj, arrow_obj, embers_obj, light_main, light_water)
    print("✓ Đã cài đặt hoạt họa Keyframe chuyển pha từ F120 đến F240.")
    
    cam_obj = create_cinematic_fire_camera(bpy.context.scene)
    print("✓ Đã thiết lập Camera_Canh3_LauThuyen_BocChay và Timeline Marker tại Frame 130.")
    
    bpy.context.view_layer.update()
    print("=== HOÀN TẤT DỰNG CẢNH 3 THÀNH CÔNG RỰC RỠ! ===")

if __name__ == "__main__":
    run_pipeline()
