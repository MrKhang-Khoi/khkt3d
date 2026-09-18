# PERFECT LOOKDEV FRAMING AND LOCAL DYNAMICS
import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler, Matrix

WS_DIR = r'C:\Users\HPZBook\Desktop\TEST_BLENDER'
ENGINE_DIR = os.path.join(WS_DIR, 'vietnam_naval_engine')
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from bach_dang_stake_generator import create_photoreal_stake_materials, build_hyperrealistic_stake
from pbr_materials import get_vietnam_naval_materials
from viet_ship_builder import build_vietnamese_warship
from enemy_warship import create_southern_han_materials, build_southern_han_tower_warship

def setup_lookdev_studio(target_loc, cam_loc, lens=45.0):
    scene = bpy.context.scene
    # Key
    key_data = bpy.data.lights.new('LookDev_KeyLight', 'SUN')
    key_data.energy = 4.8
    key_data.color = (1.0, 0.96, 0.90)
    key_obj = bpy.data.objects.new('LookDev_KeyLight', key_data)
    key_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(40))
    scene.collection.objects.link(key_obj)

    # Fill
    fill_data = bpy.data.lights.new('LookDev_FillLight', 'SUN')
    fill_data.energy = 2.4
    fill_data.color = (0.78, 0.88, 1.0)
    fill_obj = bpy.data.objects.new('LookDev_FillLight', fill_data)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-20), math.radians(-120))
    scene.collection.objects.link(fill_obj)

    # Rim
    rim_data = bpy.data.lights.new('LookDev_RimLight', 'SUN')
    rim_data.energy = 3.2
    rim_data.color = (0.92, 0.95, 1.0)
    rim_obj = bpy.data.objects.new('LookDev_RimLight', rim_data)
    rim_obj.rotation_euler = (math.radians(-60), 0, math.radians(180))
    scene.collection.objects.link(rim_obj)

    # Camera
    cam_data = bpy.data.cameras.new('LookDev_Camera')
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new('LookDev_Camera', cam_data)
    cam_obj.location = cam_loc
    direction = target_loc - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

def build_coc_master():
    print('=== 1. TÁI TẠO MASTER ASSET: CỌC BẠCH ĐẰNG ===')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('Collection_Coc_BachDang')
    bpy.context.scene.collection.children.link(col)

    mats_stake = create_photoreal_stake_materials()

    configs = [
        ('Coc_Chinh_BitSat', Vector((0.0, 0.0, 0.0)), 3.15, 0.18, 5.0, -2.0, 101, 'iron_capped'),
        ('Coc_Nghieng_GoLim', Vector((-1.1, 0.3, 0.0)), 2.75, 0.16, 14.0, -7.0, 202, 'carved_wood'),
        ('Coc_Gay_MuiSat', Vector((1.1, 0.4, 0.0)), 2.60, 0.15, 12.0, 6.0, 303, 'iron_capped')
    ]

    for name, pos, h, rad, ry, rx, sd, stype in configs:
        bm = bmesh.new()
        build_hyperrealistic_stake(bm, pos=Vector((0, 0, 0)), height=h, base_radius=rad,
                                   tilt_angle_y=ry, tilt_angle_x=rx, seed=sd, stake_type=stype)
        mesh = bpy.data.meshes.new(f'Mesh_{name}')
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        obj.location = pos
        obj.data.materials.append(mats_stake['lim_wood'])
        obj.data.materials.append(mats_stake['carved_wood'])
        obj.data.materials.append(mats_stake['iron_cap'])
        for p in obj.data.polygons:
            p.use_smooth = True
        col.objects.link(obj)

    setup_lookdev_studio(target_loc=Vector((0, 0.2, 1.3)), cam_loc=Vector((3.4, -4.2, 2.3)), lens=50.0)

    out_file = os.path.join(WS_DIR, 'assets', 'props', 'coc_bach_dang_master.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    bpy.context.scene.render.filepath = os.path.join(WS_DIR, 'audit_pass_coc.png')
    bpy.ops.render.render(write_still=True)
    print('-> Coc Done')

def build_thuyen_ta_master():
    print('=== 2. TÁI TẠO MASTER ASSET: THUYỀN CHIẾN ĐẠI VIỆT ===')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('Collection_Thuyen_Ta')
    bpy.context.scene.collection.children.link(col)

    mats = get_vietnam_naval_materials()
    root_ship = build_vietnamese_warship(mats)

    def link_hierarchy(ob):
        if ob.name not in col.objects:
            col.objects.link(ob)
        for child in ob.children:
            link_hierarchy(child)

    link_hierarchy(root_ship)

    # Motion action: Dao động dập dềnh sóng nước tại chỗ (Local Heave / Pitch / Roll)
    # Giúp asset khi link vào bất kỳ vị trí nào trên sông đều tự động bập bềnh chân thực!
    anim_data = root_ship.animation_data_create()
    action = bpy.data.actions.new(name='Action_Thuyen_Ta_WaveMotion')
    anim_data.action = action

    for f in range(1, 301):
        t = f / 24.0
        z_heave = math.sin(t * 2.8) * 0.08
        pitch = math.sin(t * 2.4) * math.radians(2.8)
        roll = math.cos(t * 1.9) * math.radians(2.2)

        root_ship.location = (0.0, 0.0, z_heave)
        root_ship.rotation_euler = Euler((pitch, roll, 0))
        root_ship.keyframe_insert(data_path='location', frame=f)
        root_ship.keyframe_insert(data_path='rotation_euler', frame=f)

    # Frame 1: Ship is at (0, 0, 0)
    bpy.context.scene.frame_set(1)

    setup_lookdev_studio(target_loc=Vector((0.0, 0.0, 1.8)), cam_loc=Vector((11.5, -11.0, 5.0)), lens=42.0)

    out_file = os.path.join(WS_DIR, 'assets', 'ships', 'thuyen_ta_ngoquyen_master.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    bpy.context.scene.render.filepath = os.path.join(WS_DIR, 'audit_pass_thuyen_ta.png')
    bpy.ops.render.render(write_still=True)
    print('-> Thuyen Ta Done')

def build_lau_thuyen_master():
    print('=== 3. TÁI TẠO MASTER ASSET: LÂU THUYỀN NAM HÁN ===')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    col = bpy.data.collections.new('Collection_Lau_Thuyen_NamHan')
    bpy.context.scene.collection.children.link(col)

    mats_enemy = create_southern_han_materials()
    ship_root = build_southern_han_tower_warship(mats_enemy, location=Vector((0, 0, 0)), rotation_z=0.0)

    def link_hierarchy(ob):
        if ob.name not in col.objects:
            col.objects.link(ob)
        for child in ob.children:
            link_hierarchy(child)

    link_hierarchy(ship_root)

    anim_data = ship_root.animation_data_create()
    action = bpy.data.actions.new(name='Action_Lau_Thuyen_WaveMotion')
    anim_data.action = action

    for f in range(1, 301):
        t = f / 24.0
        z_heave = math.sin(t * 2.2) * 0.06
        pitch = math.sin(t * 1.8) * math.radians(1.6)
        roll = math.cos(t * 1.5) * math.radians(1.3)

        ship_root.location = (0.0, 0.0, z_heave)
        ship_root.rotation_euler = Euler((pitch, roll, 0))
        ship_root.keyframe_insert(data_path='location', frame=f)
        ship_root.keyframe_insert(data_path='rotation_euler', frame=f)

    bpy.context.scene.frame_set(1)

    # Frame the massive fortress warship heroically
    setup_lookdev_studio(target_loc=Vector((0.0, 0.0, 3.2)), cam_loc=Vector((15.5, -15.5, 7.5)), lens=38.0)

    out_file = os.path.join(WS_DIR, 'assets', 'ships', 'lau_thuyen_namhan_master.blend')
    bpy.ops.wm.save_as_mainfile(filepath=out_file)
    bpy.context.scene.render.filepath = os.path.join(WS_DIR, 'audit_pass_lau_thuyen.png')
    bpy.ops.render.render(write_still=True)
    print('-> Lau Thuyen Done')

if __name__ == '__main__':
    build_coc_master()
    build_thuyen_ta_master()
    build_lau_thuyen_master()
    print('=== ALL 3 REBUILT AND RENDERED PERFECTLY ===')
