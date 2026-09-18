import bpy
import bmesh
import math
import random
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM MASTER] NÃƒâ€šNG CÃ¡ÂºÂ¤P BÃ†Â¯Ã¡Â»Å¡C 1: Ã„ÂÃ¡Â»Ëœ NÃƒâ€°T CAO, Ã„ÂÃ¡Â»ËœI HÃƒÅ’NH CÃƒÂNH Ãƒâ€°N, MÃƒÂI CHÃƒË†O KHUA NÃ†Â¯Ã¡Â»Å¡C ===")

# 1. DÃ¡Â»Å’N DÃ¡ÂºÂ¸P SÃ¡ÂºÂ CH CÃ¡ÂºÂ¢NH
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

for col in list(bpy.data.collections):
    if col.name != 'Collection':
        bpy.data.collections.remove(col)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 80
scene.render.fps = 24
scene.frame_current = 1

# CÃ¡ÂºÂ¥u hÃƒÂ¬nh mÃƒÂ u sÃ¡ÂºÂ¯c & Ã„â€˜Ã¡Â»â„¢ tÃ†Â°Ã†Â¡ng phÃ¡ÂºÂ£n cao (High Contrast, khÃ¡Â»Â­ mÃ¡Â»Â)
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = 0.1
if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    scene.eevee.shadow_resolution_scale = 2.0
    scene.eevee.shadow_pool_size = '1024'

col_env = bpy.data.collections.new('01_DiaHinh_SongNui')
col_coc = bpy.data.collections.new('02_TranDia_BaiCoc')
col_ta = bpy.data.collections.new('03_HamDoi_DaiViet_TienPhong')
col_dich = bpy.data.collections.new('04_HamDoi_NamHan_DaiHamDoi')
col_light = bpy.data.collections.new('05_ChieuSang_KhiQuyen')

for c in [col_env, col_coc, col_ta, col_dich, col_light]:
    scene.collection.children.link(c)

# 2. BÃ¡ÂºÂ¦U TRÃ¡Â»Å“I & ÃƒÂNH SÃƒÂNG TÃ†Â¯Ã†Â NG PHÃ¡ÂºÂ¢N RÃƒâ€¢ NÃƒâ€°T (KHÃ¡Â»Â¬ SÃ†Â¯Ã†Â NG MÃƒâ„¢ BÃ¡ÂºÂ C MÃƒâ‚¬U)
world = bpy.data.worlds.get('World_Step1_Master') or bpy.data.worlds.new('World_Step1_Master')
scene.world = world
world.use_nodes = True
nw = world.node_tree.nodes
lw = world.node_tree.links
nw.clear()
out_w = nw.new('ShaderNodeOutputWorld')
bg_w = nw.new('ShaderNodeBackground')
# GiÃ¡ÂºÂ£m tÃƒÂ¡n xÃ¡ÂºÂ¡ mÃƒÂ´i trÃ†Â°Ã¡Â»Âng Ã„â€˜Ã¡Â»Æ’ bÃƒÂ³ng Ã„â€˜Ã¡Â»â€¢ sÃ¡ÂºÂ¯c nÃƒÂ©t
bg_w.inputs['Color'].default_value = (0.28, 0.36, 0.44, 1.0)
bg_w.inputs['Strength'].default_value = 0.85
lw.new(bg_w.outputs['Background'], out_w.inputs['Surface'])

# MÃ¡ÂºÂ·t trÃ¡Â»Âi chiÃ¡ÂºÂ¿u xiÃƒÂªn sÃ¡ÂºÂ¯c nÃƒÂ©t
sun_data = bpy.data.lights.new(name="Sun_Winter", type='SUN')
sun_data.energy = 7.2
sun_data.color = (1.0, 0.97, 0.91)
sun_data.angle = math.radians(0.4) # GÃƒÂ³c hÃ¡ÂºÂ¹p -> BÃƒÂ³ng Ã„â€˜Ã¡Â»â€¢ sÃ¡ÂºÂ¯c nÃƒÂ©t, khÃƒÂ´ng bÃ¡Â»â€¹ nhÃƒÂ²e
sun_obj = bpy.data.objects.new(name="Sun_Winter", object_data=sun_data)
sun_obj.rotation_euler = (math.radians(58), math.radians(12), math.radians(35))
col_light.objects.link(sun_obj)

# 3. DÃƒÆ’Y NÃƒÅ¡I Ã„ÂÃƒÂ VÃƒâ€I BÃ¡Â»Å“ TÃƒâ€šY (TRÃƒâ‚¬NG KÃƒÅ NH, X = -135m)
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_TrangKenh',
    mesh_size_x=110.0,
    mesh_size_y=600.0,
    subdivision_x=110,
    subdivision_y=180,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=0.85,
    noise_depth=8,
    offset=0.88,
    gain=3.8,
    height=0.55,
    height_invert=False,
    edge_falloff='3',
    falloff_x=7.0,
    falloff_y=7.0,
    smooth_mesh=True,
    refresh=True
)
mount_west = bpy.context.active_object
mount_west.name = 'DayNui_Karst_TrangKenh_BoTay'
mount_west.location = (-135.0, 15.0, 0.0)
mount_west.scale = (1.0, 1.0, 50.0)

mat_karst = bpy.data.materials.new('Mat_DaKarst_PBR')
mat_karst.use_nodes = True
bsdf_k = next((n for n in mat_karst.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_k:
    bsdf_k.inputs['Base Color'].default_value = (0.09, 0.11, 0.10, 1.0)
    bsdf_k.inputs['Roughness'].default_value = 0.85
mount_west.data.materials.append(mat_karst)
if mount_west.name not in col_env.objects: col_env.objects.link(mount_west)
if mount_west.name in scene.collection.objects: scene.collection.objects.unlink(mount_west)

# 4. DÃƒÆ’Y NÃƒÅ¡I Ã„ÂÃƒÂ BÃ¡Â»Å“ Ã„ÂÃƒâ€NG (QUÃ¡ÂºÂ¢NG YÃƒÅ N, X = +135m)
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Nui_Karst_QuangYen',
    mesh_size_x=110.0,
    mesh_size_y=600.0,
    subdivision_x=110,
    subdivision_y=180,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=0.85,
    noise_depth=8,
    offset=0.85,
    gain=3.6,
    height=0.52,
    height_invert=False,
    edge_falloff='3',
    falloff_x=7.0,
    falloff_y=7.0,
    smooth_mesh=True,
    refresh=True
)
mount_east = bpy.context.active_object
mount_east.name = 'DayNui_Karst_QuangYen_BoDong'
mount_east.location = (135.0, 15.0, 0.0)
mount_east.scale = (1.0, 1.0, 48.0)
mount_east.data.materials.append(mat_karst)
if mount_east.name not in col_env.objects: col_env.objects.link(mount_east)
if mount_east.name in scene.collection.objects: scene.collection.objects.unlink(mount_east)

# 5. MÃ¡ÂºÂ¶T NÃ†Â¯Ã¡Â»Å¡C SÃƒâ€NG BÃ¡ÂºÂ CH Ã„ÂÃ¡ÂºÂ°NG (SÃ¡ÂºÂªM MÃƒâ‚¬U, TRONG VÃƒâ‚¬ TÃ†Â¯Ã†Â NG PHÃ¡ÂºÂ¢N Ã„ÂÃ¡ÂºÂ¸P)
bm_w = bmesh.new()
bmesh.ops.create_grid(bm_w, x_segments=120, y_segments=180, size=650.0)
mesh_w = bpy.data.meshes.new('Mesh_SongBachDang_MatNuoc')
bm_w.to_mesh(mesh_w)
bm_w.free()
obj_water = bpy.data.objects.new('MatNuoc_SongBachDang_Chinh', mesh_w)
obj_water.location = (0, 0, 0.85)

mat_wat = bpy.data.materials.new('Mat_NuocSong_Reflective_PBR')
mat_wat.use_nodes = True
nw_wat = mat_wat.node_tree.nodes
lw_wat = mat_wat.node_tree.links
bsdf_w = next((n for n in nw_wat if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf_w:
    # NÃ†Â°Ã¡Â»â€ºc xanh ngÃ¡Â»Âc sÃ¡ÂºÂ«m Ã„â€˜Ã¡ÂºÂ­m Ã„â€˜ÃƒÂ , tÃ†Â°Ã†Â¡ng phÃ¡ÂºÂ£n tuyÃ¡Â»â€¡t Ã„â€˜Ã¡ÂºÂ¹p vÃ¡Â»â€ºi buÃ¡Â»â€œm vÃƒÂ ng
    bsdf_w.inputs['Base Color'].default_value = (0.02, 0.08, 0.11, 1.0)
    bsdf_w.inputs['Roughness'].default_value = 0.09
    bsdf_w.inputs['Metallic'].default_value = 0.15
    tex_noise = nw_wat.new('ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 24.0
    tex_noise.inputs['Detail'].default_value = 4.0
    bump_node = nw_wat.new('ShaderNodeBump')
    bump_node.inputs['Strength'].default_value = 0.12
    bump_node.inputs['Distance'].default_value = 0.08
    lw_wat.new(tex_noise.outputs['Fac'], bump_node.inputs['Height'])
    lw_wat.new(bump_node.outputs['Normal'], bsdf_w.inputs['Normal'])

obj_water.data.materials.append(mat_wat)
col_env.objects.link(obj_water)

anim_w = obj_water.animation_data_create()
act_w = bpy.data.actions.new(name='Action_ThuyTrieu')
anim_w.action = act_w
for f in range(1, 81):
    zt = 0.85 + math.sin(f * 0.08) * 0.015
    obj_water.location = (0, 0, zt)
    obj_water.keyframe_insert(data_path='location', frame=f)

# 6. BÃƒÆ’I CÃ¡Â»Å’C BÃ¡ÂºÂ CH Ã„ÂÃ¡ÂºÂ°NG (CHÃƒÅ’M SÃƒâ€šU 0.7m DÃ†Â¯Ã¡Â»Å¡I NÃ†Â¯Ã¡Â»Å¡C TRIÃ¡Â»â‚¬U CÃ†Â¯Ã¡Â»Å“NG)
assembly_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\scenes\dai_chien_bach_dang_assembly.blend'
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Coc_BachDang']

hero_stakes = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'Coc' in ob.name:
                hero_stakes.append(ob)
                col_coc.objects.link(ob)

for ob in hero_stakes:
    ob.location.z -= 2.65

random.seed(938)
if hero_stakes:
    master_coc = hero_stakes[0]
    for idx in range(65):
        cx = random.uniform(-90.0, 90.0)
        cy = random.uniform(-8.0, 10.0)
        cz = random.uniform(-3.1, -2.8)
        slant_x = random.uniform(-4.0, 4.0)
        slant_y = random.uniform(-40.0, -55.0)
        
        c_inst = master_coc.copy()
        c_inst.name = f"Coc_NgapSau_{idx+1}"
        c_inst.location = (cx, cy, cz)
        c_inst.rotation_euler = (math.radians(slant_y), math.radians(slant_x), 0)
        col_coc.objects.link(c_inst)

# 7. NÃ¡ÂºÂ P MASTER SHIPS
with bpy.data.libraries.load(assembly_path, link=False) as (data_from, data_to):
    data_to.collections = ['Collection_Thuyen_Ta', 'Collection_Lau_Thuyen_NamHan']

ta_master_objs = []
dich_master_objs = []
for c_imp in data_to.collections:
    if c_imp:
        for ob in c_imp.objects:
            if 'NamHan' in ob.name or 'LauThuyen' in ob.name:
                dich_master_objs.append(ob)
            elif 'Coc' not in ob.name:
                ta_master_objs.append(ob)

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
master_dich_root = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')

def clone_ship_clean(source_root, prefix_name, target_col):
    objs = [source_root] + list(source_root.children_recursive)
    mapping = {}
    for o in objs:
        new_o = o.copy()
        new_o.name = f"{prefix_name}_{o.name}"
        new_o.animation_data_clear()
        mapping[o] = new_o
        target_col.objects.link(new_o)
    for o in objs:
        new_o = mapping[o]
        if o.parent and o.parent in mapping:
            new_o.parent = mapping[o.parent]
            new_o.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        else:
            new_o.parent = None
    return mapping[source_root]

master_ta_root.animation_data_clear()
master_dich_root.animation_data_clear()
for o in ta_master_objs:
    o.animation_data_clear()
    if o.name not in col_ta.objects: col_ta.objects.link(o)
for o in dich_master_objs:
    o.animation_data_clear()
    if o.name not in col_dich.objects: col_dich.objects.link(o)

# CÃ¡ÂºÂ¬P NHÃ¡ÂºÂ¬T VÃ¡ÂºÂ¬T LIÃ¡Â»â€ U BUÃ¡Â»â€™M VÃƒâ‚¬NG RÃ†Â M Ã„ÂÃ¡ÂºÂ¶C TRÃ†Â¯NG Ã„ÂÃ¡ÂºÂ I VIÃ¡Â»â€ T (TÃ†Â¯Ã†Â NG PHÃ¡ÂºÂ¢N NÃ¡Â»â€I BÃ¡ÂºÂ¬T)
for mat in bpy.data.materials:
    if 'Buom_CanhDoi' in mat.name:
        if mat.use_nodes:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                # VÃƒÂ ng rÃ†Â¡m Ã¡ÂºÂ¥m ÃƒÂ¡p nÃ¡Â»â€¢i bÃ¡ÂºÂ­t nhÃ†Â° Ã¡ÂºÂ£nh mÃ¡ÂºÂ«u
                bsdf.inputs['Base Color'].default_value = (0.86, 0.65, 0.22, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.55
    elif 'NamHan_BuomNan' in mat.name:
        if mat.use_nodes:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if bsdf:
                # MÃƒÂ u vÃ¡ÂºÂ£i thÃƒÂ´ ngÃƒÂ /kem sÃ¡ÂºÂ¡ch sÃ¡ÂºÂ½
                bsdf.inputs['Base Color'].default_value = (0.78, 0.74, 0.65, 1.0)
                bsdf.inputs['Roughness'].default_value = 0.60

# =========================================================================
# A. Ã„ÂÃ¡Â»ËœI THUYÃ¡Â»â‚¬N Ã„ÂÃ¡ÂºÂ I VIÃ¡Â»â€ T (8 THUYÃ¡Â»â‚¬N) - THÃ¡ÂºÂ¾ TRÃ¡ÂºÂ¬N CÃƒÂNH Ãƒâ€°N NGHI BINH (SPLIT ECHELON)
# Chia 2 phÃƒÂ¢n Ã„â€˜Ã¡Â»â„¢i TÃ¡ÂºÂ£ DÃ¡Â»Â±c vÃƒÂ  HÃ¡Â»Â¯u DÃ¡Â»Â±c, mÃ¡Â»Å¸ toang luÃ¡Â»â€œng nÃ†Â°Ã¡Â»â€ºc sÃƒÂ¢u 44m Ã¡Â»Å¸ giÃ¡Â»Â¯a
# CÃ¡Â»Â± ly khiÃƒÂªu chiÃ¡ÂºÂ¿n cÃƒÂ¡ch tÃƒÂ u giÃ¡ÂºÂ·c 60m (an toÃƒÂ n, ngoÃƒÂ i tÃ¡ÂºÂ§m nÃ¡Â»Â lÃ¡Â»â€ºn)
# KHÃƒâ€NG BAO GIÃ¡Â»Å“ BÃ¡Â»Å  CÃ¡ÂºÂ¢N Ã„ÂÃ†Â¯Ã¡Â»Å“NG KHI BÃ¡ÂºÂº LÃƒÂI THÃƒÂO CHÃ¡ÂºÂ Y
# =========================================================================
viet_fleet_data = [
    # TÃƒÂªn, X, Y, Scale
    # PHÃƒâ€šN Ã„ÂÃ¡Â»ËœI CÃƒÂNH TÃ¡ÂºÂ¢ (BÃ¡Â»Å“ TÃƒâ€šY - MEN THEO CHÃƒâ€šN NÃƒÅ¡I TRÃƒâ‚¬NG KÃƒÅ NH)
    ("DV_Ta_01_DauCanh",   -22.0,  -38.0, 1.05), # MÃ…Â©i khiÃƒÂªu chiÃ¡ÂºÂ¿n cÃƒÂ¡nh tÃ¡ÂºÂ£
    ("DV_Ta_02_TrungCanh", -38.0,  -52.0, 1.00),
    ("DV_Ta_03_HauCanh",   -54.0,  -66.0, 0.95),
    ("DV_Ta_04_KhoaDuoi",  -70.0,  -80.0, 0.90),

    # PHÃƒâ€šN Ã„ÂÃ¡Â»ËœI CÃƒÂNH HÃ¡Â»Â®U (BÃ¡Â»Å“ Ã„ÂÃƒâ€NG - MEN THEO BÃ¡Â»Å“ QUÃ¡ÂºÂ¢NG YÃƒÅ N)
    ("DV_Huu_01_DauCanh",   +22.0,  -38.0, 1.05), # MÃ…Â©i khiÃƒÂªu chiÃ¡ÂºÂ¿n cÃƒÂ¡nh hÃ¡Â»Â¯u
    ("DV_Huu_02_TrungCanh", +38.0,  -52.0, 1.00),
    ("DV_Huu_03_HauCanh",   +54.0,  -66.0, 0.95),
    ("DV_Huu_04_KhoaDuoi",  +70.0,  -80.0, 0.90)
]

for idx, (s_name, px, py, scl) in enumerate(viet_fleet_data):
    if idx == 0:
        s_root = master_ta_root
    else:
        s_root = clone_ship_clean(master_ta_root, f"Ta_{idx}", col_ta)
    
    s_root.location = (0, 0, 0)
    s_root.rotation_euler = (0, 0, math.radians(90))
    s_root.scale = (scl, scl, scl)
    
    root_e = bpy.data.objects.new(f"Root_{s_name}", None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_ta.objects.link(root_e)
    s_root.parent = root_e
    
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Act_{s_name}")
    anim.action = act
    
    # 1. HoÃ¡ÂºÂ¡t hÃ¡Â»Âa di chuyÃ¡Â»Æ’n tiÃ¡ÂºÂ¿n lÃ†Â°Ã¡Â»â€ºt sÃƒÂ³ng rÃƒÂµ rÃ¡Â»â€¡t (tiÃ¡ÂºÂ¿n 14m trong 80 frame)
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = py + prog * 14.0  # TiÃ¡ÂºÂ¿n lÃ†Â°Ã¡Â»â€ºt sÃƒÂ³ng mÃ¡ÂºÂ¡nh mÃ¡ÂºÂ½, rÃƒÂµ rÃ¡Â»â€¡t tÃ¡Â»Â« xa!
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.14) * 0.025
        
        pitch = math.sin((f + idx * 4) * 0.16) * math.radians(0.45)
        roll = 0.0  # LEVEL KEEL, KHÃƒâ€NG NGHIÃƒÅ NG
        yaw = 0.0   # HÃ†Â¯Ã¡Â»Å¡NG BÃ¡ÂºÂ®C (+Y)
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # 2. HoÃ¡ÂºÂ¡t hÃ¡Â»Âa mÃƒÂ¡i chÃƒÂ¨o khua nÃ†Â°Ã¡Â»â€ºc nhÃ¡Â»â€¹p nhÃƒÂ ng (Rowing Oars Cycle)
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
            # QuÃ¡ÂºÂ¡t mÃƒÂ¡i chÃƒÂ¨o tÃ¡Â»â€ºi lui quanh trÃ¡Â»Â¥c Z
            rz = math.sin(stroke_phase) * math.radians(12.0)
            # NhÃ¡ÂºÂ¥c lÃƒÂªn vÃƒÂ  cÃ¡ÂºÂ¯m xuÃ¡Â»â€˜ng nÃ†Â°Ã¡Â»â€ºc quanh trÃ¡Â»Â¥c Y
            ry = math.cos(stroke_phase) * math.radians(5.0)
            oar_obj.rotation_euler = (0, ry, rz)
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)

print("-> Ã„ÂÃ¡Â»â„¢i thuyÃ¡Â»Ân Ã„ÂÃ¡ÂºÂ¡i ViÃ¡Â»â€¡t (8 thuyÃ¡Â»Ân - CÃƒÂ¡nh Ãƒâ€°n, mÃƒÂ¡i chÃƒÂ¨o khua nÃ†Â°Ã¡Â»â€ºc) hoÃƒÂ n tÃ¡ÂºÂ¥t!")

# =========================================================================
# B. Ã„ÂÃ¡ÂºÂ I HÃ¡ÂºÂ M Ã„ÂÃ¡Â»ËœI NAM HÃƒÂN (26 CHIÃ¡ÂºÂ¾N HÃ¡ÂºÂ M) - MÃƒÂI CHÃƒË†O KHUA NÃ†Â¯Ã¡Â»Å¡C Ã„ÂÃ¡Â»â€™NG LOÃ¡ÂºÂ T
# =========================================================================
han_fleet_data = [
    # Ã„ÂÃ¡Â»Â¢T 1: THÃƒÅ  Ã„ÂÃ¡Â»ËœI TIÃƒÅ N PHONG (ÃƒÂp sÃƒÂ¡t tuyÃ¡ÂºÂ¿n cÃ¡Â»Âc, Y = +25 Ã„â€˜Ã¡ÂºÂ¿n +38) - 8 TÃƒÂ u trÃ¡ÂºÂ£i rÃ¡Â»â„¢ng X = -75 Ã„â€˜Ã¡ÂºÂ¿n +75
    ("NH_W1_01", -75.0, 36.0, 0.75),
    ("NH_W1_02", -54.0, 30.0, 0.80),
    ("NH_W1_03", -32.0, 26.0, 0.85),
    ("NH_W1_04", -11.0, 24.0, 0.90),
    ("NH_W1_05", +11.0, 24.0, 0.90),
    ("NH_W1_06", +32.0, 26.0, 0.85),
    ("NH_W1_07", +54.0, 30.0, 0.80),
    ("NH_W1_08", +75.0, 36.0, 0.75),

    # Ã„ÂÃ¡Â»Â¢T 2: THÃƒÅ  Ã„ÂÃ¡Â»ËœI TRUNG QUÃƒâ€šN (SoÃƒÂ¡i hÃ¡ÂºÂ¡m HoÃ¡ÂºÂ±ng ThÃƒÂ¡o Ã¡Â»Å¸ giÃ¡Â»Â¯a, Y = +56 Ã„â€˜Ã¡ÂºÂ¿n +80) - 9 TÃƒÂ u
    ("NH_W2_01", -85.0, 74.0, 0.80),
    ("NH_W2_02", -60.0, 64.0, 0.85),
    ("NH_W2_03", -30.0, 60.0, 0.90),
    ("NH_W2_SoaiHam_LauThuyen_HoangThao", 0.0, 56.0, 1.35), # SOÃƒÂI HÃ¡ÂºÂ M 3 TÃ¡ÂºÂ¦NG HOÃ¡ÂºÂ°NG THÃƒÂO
    ("NH_W2_05", +30.0, 60.0, 0.90),
    ("NH_W2_06", +60.0, 64.0, 0.85),
    ("NH_W2_07", +85.0, 74.0, 0.80),
    ("NH_W2_08", -45.0, 82.0, 0.80),
    ("NH_W2_09", +45.0, 82.0, 0.80),

    # Ã„ÂÃ¡Â»Â¢T 3: THÃƒÅ  Ã„ÂÃ¡Â»ËœI HÃ¡ÂºÂ¬U QUÃƒâ€šN & TIÃ¡ÂºÂ¾P VIÃ¡Â»â€ N (Y = +100 Ã„â€˜Ã¡ÂºÂ¿n +150) - 9 TÃƒÂ u
    ("NH_W3_01", -72.0, 110.0, 0.80),
    ("NH_W3_02", -36.0, 105.0, 0.85),
    ("NH_W3_03",   0.0, 102.0, 0.90),
    ("NH_W3_04", +36.0, 105.0, 0.85),
    ("NH_W3_05", +72.0, 110.0, 0.80),
    ("NH_W3_06", -54.0, 130.0, 0.80),
    ("NH_W3_07", +20.0, 126.0, 0.80),
    ("NH_W3_08", -24.0, 146.0, 0.75),
    ("NH_W3_09", +50.0, 142.0, 0.75),
]

for idx, (h_name, px, py, scl) in enumerate(han_fleet_data):
    if idx == 11:
        h_root = master_dich_root
    else:
        h_root = clone_ship_clean(master_dich_root, f"Dich_{idx}", col_dich)
        
    h_root.location = (0, 0, 0)
    h_root.rotation_euler = (0, 0, math.radians(-90))
    h_root.scale = (scl, scl, scl)
    
    root_e = bpy.data.objects.new(f"Root_{h_name}", None)
    root_e.empty_display_type = 'PLAIN_AXES'
    root_e.empty_display_size = 0.2
    col_dich.objects.link(root_e)
    h_root.parent = root_e
    
    anim = root_e.animation_data_create()
    act = bpy.data.actions.new(name=f"Act_{h_name}")
    anim.action = act
    
    # 1. HoÃ¡ÂºÂ¡t hÃ¡Â»Âa lao thÃ¡ÂºÂ³ng xuÃ¡Â»â€˜ng phÃƒÂ­a Nam (tiÃ¡ÂºÂ¿n 16m trong 80 frame)
    for f in range(1, 81):
        prog = (f - 1) / 79.0
        cur_y = py - prog * 16.0  # Lao nhanh xuÃ¡Â»â€˜ng phÃƒÂ­a Nam (-Y)
        cur_x = px
        cur_z = 0.85 + math.sin((f + idx * 3) * 0.10) * 0.018
        
        pitch = math.sin((f + idx * 2) * 0.12) * math.radians(0.3)
        roll = 0.0  # LEVEL KEEL
        yaw = 0.0   # HÃ†Â¯Ã¡Â»Å¡NG NAM (-Y)
        
        root_e.location = (cur_x, cur_y, cur_z)
        root_e.rotation_euler = (pitch, roll, yaw)
        root_e.keyframe_insert(data_path='location', frame=f)
        root_e.keyframe_insert(data_path='rotation_euler', frame=f)

    # 2. HoÃ¡ÂºÂ¡t hÃ¡Â»Âa 24 mÃƒÂ¡i chÃƒÂ¨o hÃ¡ÂºÂ¡ng nÃ¡ÂºÂ·ng khua nÃ†Â°Ã¡Â»â€ºc nhÃ¡Â»â€¹p nhÃƒÂ ng
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
            oar_obj.keyframe_insert(data_path='rotation_euler', frame=f)

print(f"-> Ã„ÂÃ¡ÂºÂ¡i HÃ¡ÂºÂ¡m Ã„â€˜Ã¡Â»â„¢i Nam HÃƒÂ¡n ({len(han_fleet_data)} chiÃ¡ÂºÂ¿n hÃ¡ÂºÂ¡m - mÃƒÂ¡i chÃƒÂ¨o khua nÃ†Â°Ã¡Â»â€ºc) hoÃƒÂ n tÃ¡ÂºÂ¥t!")

# 8. CAMERA Ã„ÂIÃ¡Â»â€ N Ã¡ÂºÂ¢NH TOÃƒâ‚¬N CÃ¡ÂºÂ¢NH SÃ¡ÂºÂ®C NÃƒâ€°T
cam_data = bpy.data.cameras.new("Cam_Headon_Master")
cam_data.lens = 26.0
cam_data.clip_end = 1800.0
cam_obj = bpy.data.objects.new("Camera_ChienTruong_Headon", cam_data)

cam_obj.location = (0.0, -135.0, 68.0)
cam_obj.rotation_euler = (math.radians(63), 0, 0)
col_light.objects.link(cam_obj)
scene.camera = cam_obj

# CÃ¡ÂºÂ­p nhÃ¡ÂºÂ­t Viewport 3D
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True
                    space.overlay.show_relationship_lines = False
            r3d = area.spaces.active.region_3d
            r3d.view_perspective = 'PERSP'
            r3d.view_distance = 160.0
            r3d.view_location = (0.0, 15.0, 5.0)
            r3d.view_rotation = Euler((math.radians(63), 0.0, 0.0), 'XYZ').to_quaternion()

for ob in bpy.context.selected_objects:
    ob.select_set(False)

scene.frame_set(1)
try:
    bpy.ops.screen.animation_play()
except:
    pass

print("=== [VIETNAM-SIM MASTER] NÃƒâ€šNG CÃ¡ÂºÂ¤P BÃ†Â¯Ã¡Â»Å¡C 1 TOÃƒâ‚¬N DIÃ¡Â»â€ N THÃƒâ‚¬NH CÃƒâ€NG 100%! ===")