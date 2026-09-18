with open(r"c:\Users\HPZBook\Desktop\TEST_BLENDER\build_step1_crewed_fleet.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Title & Frame End
text = text.replace(
    'print("=== [VIETNAM-SIM MASTER] TÍCH HỢP TOÀN BỘ QUÂN LÍNH LÊN 34 CHIẾN THUYỀN ===")',
    'print("=== [VIETNAM-SIM MASTER] BƯỚC 2: GIAO CHIẾN KHIÊU KHÍCH VÀ THUYỀN TA GIẢ THUA RÚT LUI (160 FRAMES) ===")'
)
text = text.replace('scene.frame_end = 80', 'scene.frame_end = 160')

# 2. Water Animation 1 to 160
old_water_anim = """for f in range(1, 81):
    zt = 0.85 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)"""

new_water_anim = """for f in range(1, 161):
    zt = 0.85 + math.sin(f * 0.06) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)"""
text = text.replace(old_water_anim, new_water_anim)

# 3. Dai Viet Rower Animation (1 to 160)
old_rower_anim = """            for f in range(1, 81):
                stroke_phase = (f + idx * 2) * 0.35
                pitch_rower = math.sin(stroke_phase) * math.radians(11.0)
                r_obj.rotation_euler = (0, pitch_rower, 0)
                r_obj.keyframe_insert(data_path='rotation_euler', frame=f)"""

new_rower_anim = """            for f in range(1, 161):
                if f <= 60:
                    sp = (f + idx * 2) * 0.35
                elif f <= 90:
                    sp = (60 + idx * 2) * 0.35 + (f - 60) * 0.45
                else:
                    sp = (60 + idx * 2) * 0.35 + 30 * 0.45 + (f - 90) * 0.60
                pitch_rower = math.sin(sp) * math.radians(12.0)
                r_obj.rotation_euler = (0, pitch_rower, 0)
                r_obj.keyframe_insert(data_path='rotation_euler', frame=f)"""
text = text.replace(old_rower_anim, new_rower_anim)

# 4. Dai Viet Boat Movement & Oars (1 to 160)
old_dv_root_anim = """    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = py + prog * 12.0
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.14) * 0.025
        
        pitch = math.sin((f + idx * 4) * 0.16) * math.radians(0.45)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa mái chèo khua nước
    oar_obj = None
    for c in s_root.children_recursive:
        if 'Mai_Cheo' in c.name or 'Cheo' in c.name:
            oar_obj = c
            break
    if oar_obj:
        oar_anim = oar_obj.animation_data_create()
        oar_act = bpy.data.actions.new(name=f"Act_Oar_{s_name}")
        oar_anim.action = oar_act
        for f in range(1, 81):
            stroke_phase = (f + idx * 2) * 0.35
            rz = math.sin(stroke_phase) * math.radians(12.0)
            ry = math.cos(stroke_phase) * math.radians(5.0)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)"""

new_dv_root_anim = """    for f in range(1, 161):
        turn_dir = 1.0 if px <= 0 else -1.0
        if f <= 60:
            prog1 = (f - 1) / 59.0
            cur_y = py + prog1 * 9.0
            cur_x = px
            yaw = 0.0
            roll = 0.0
        elif f <= 90:
            prog2 = (f - 60) / 30.0
            cur_y = py + 9.0 + math.sin(prog2 * math.pi * 0.5) * 2.0 - (prog2 ** 2) * 4.0
            cur_x = px + math.sin(prog2 * math.pi) * 3.0 * turn_dir
            yaw = turn_dir * prog2 * math.pi
            roll = turn_dir * math.sin(prog2 * math.pi) * math.radians(2.5)
        else:
            prog3 = (f - 90) / 70.0
            start_ret_y = py + 7.0
            cur_y = start_ret_y - (prog3 ** 1.15) * 52.0
            cur_x = px + turn_dir * 1.5
            yaw = turn_dir * math.pi
            roll = 0.0

        cur_z = 0.85 + math.sin((f + idx * 3) * 0.14) * 0.022
        pitch = math.sin((f + idx * 4) * 0.16) * math.radians(0.40)
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa mái chèo khua nước
    oar_obj = None
    for c in s_root.children_recursive:
        if 'Mai_Cheo' in c.name or 'Cheo' in c.name:
            oar_obj = c
            break
    if oar_obj:
        oar_anim = oar_obj.animation_data_create()
        oar_act = bpy.data.actions.new(name=f"Act_Oar_{s_name}")
        oar_anim.action = oar_act
        for f in range(1, 161):
            if f <= 60:
                sp = (f + idx * 2) * 0.35
            elif f <= 90:
                sp = (60 + idx * 2) * 0.35 + (f - 60) * 0.45
            else:
                sp = (60 + idx * 2) * 0.35 + 30 * 0.45 + (f - 90) * 0.60
            rz = math.sin(sp) * math.radians(13.0)
            ry = math.cos(sp) * math.radians(5.5)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)"""
text = text.replace(old_dv_root_anim, new_dv_root_anim)

# 5. Nam Han Fleet Movement & Oars (1 to 160)
old_han_root_anim = """    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = py - prog * 15.0
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.10) * 0.018
        
        pitch = math.sin((f + idx * 2) * 0.12) * math.radians(0.3)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa 24 mái chèo Nam Hán quạt nước
    oar_obj = None
    for c in h_root.children_recursive:
        if 'MaiCheo' in c.name or 'Cheo' in c.name:
            oar_obj = c
            break
    if oar_obj:
        oar_anim = oar_obj.animation_data_create()
        oar_act = bpy.data.actions.new(name=f"Act_Oar_{h_name}")
        oar_anim.action = oar_act
        for f in range(1, 81):
            stroke_phase = (f + idx * 2) * 0.30
            rz = math.sin(stroke_phase) * math.radians(9.0)
            ry = math.cos(stroke_phase) * math.radians(3.5)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)"""

new_han_root_anim = """    for f in range(1, 161):
        if f <= 60:
            prog1 = (f - 1) / 59.0
            cur_y = py - prog1 * 10.0
        elif f <= 90:
            prog2 = (f - 60) / 30.0
            cur_y = py - 10.0 - prog2 * 7.0
        else:
            prog3 = (f - 90) / 70.0
            # Dốc toàn lực truy kích, vượt qua bãi cọc
            cur_y = py - 17.0 - (prog3 ** 1.1) * 36.0
            
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.10) * 0.018
        pitch = math.sin((f + idx * 2) * 0.12) * math.radians(0.3)
        roll = 0.0
        yaw = 0.0
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # Hoạt họa 24 mái chèo Nam Hán quạt nước
    oar_obj = None
    for c in h_root.children_recursive:
        if 'MaiCheo' in c.name or 'Cheo' in c.name:
            oar_obj = c
            break
    if oar_obj:
        oar_anim = oar_obj.animation_data_create()
        oar_act = bpy.data.actions.new(name=f"Act_Oar_{h_name}")
        oar_anim.action = oar_act
        for f in range(1, 161):
            if f <= 90:
                sp = (f + idx * 2) * 0.30
            else:
                sp = (90 + idx * 2) * 0.30 + (f - 90) * 0.45
            rz = math.sin(sp) * math.radians(9.5)
            ry = math.cos(sp) * math.radians(4.0)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)"""
text = text.replace(old_han_root_anim, new_han_root_anim)

# 6. Update Camera to follow full action
old_cam = """cam_obj.location = (0.0, -135.0, 68.0)
cam_obj.rotation_euler = (math.radians(63), 0, 0)"""

new_cam = """cam_obj.location = (0.0, -150.0, 72.0)
cam_obj.rotation_euler = (math.radians(62), 0, 0)"""
text = text.replace(old_cam, new_cam)

with open(r"c:\Users\HPZBook\Desktop\TEST_BLENDER\build_step2_tactical_retreat.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Created build_step2_tactical_retreat.py successfully!")
