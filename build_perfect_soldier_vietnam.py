import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix, Quaternion

print("================================================================================")
print("=== [VIETNAM-SIM MASTER] HOÀN THIỆN TOÀN DIỆN NHÂN VẬT THỦY BINH ĐẠI VIỆT 938 ===")
print("=== CHUẨN SỬ: ĐẠI VIỆT SỬ KÝ TOÀN THƯ - KHỐ, XĂM GIAO LONG, DAO GĂM ĐỒNG ===")
print("================================================================================")

WS_DIR = r"C:\Users\HPZBook\Desktop\TEST_BLENDER"
CHAR_DIR = os.path.join(WS_DIR, "assets", "characters")
GLB_BODY = os.path.join(CHAR_DIR, "male_base_mesh.glb")
GLB_HEAD = os.path.join(CHAR_DIR, "lee_perry_smith.glb")

# 1. DỌN DẸP SẠCH TOÀN BỘ CẢNH ĐỂ XÂY DỰNG MASTER MỚI
for ob in list(bpy.context.scene.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)
scene = bpy.context.scene

# Cấu hình Render Studio HD 1080p AgX
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = 0.15

if hasattr(scene, 'eevee'):
    scene.eevee.use_raytracing = True
    scene.eevee.shadow_resolution_scale = 2.0

col_soldier = bpy.data.collections.new("Collection_ThuyBinh_DaiViet_Master")
col_props = bpy.data.collections.new("Collection_Props_BoatStudio")
col_lights = bpy.data.collections.new("Collection_Studio_Lighting")
col_cams = bpy.data.collections.new("Collection_Studio_Cameras")

for c in [col_soldier, col_props, col_lights, col_cams]:
    scene.collection.children.link(c)

# 2. HỆ THỐNG VẬT LIỆU PBR SIÊU THỰC
mat_skin = bpy.data.materials.new('Mat_DaNguoi_VietCo_Master')
mat_skin.use_nodes = True
nodes = mat_skin.node_tree.nodes
links = mat_skin.node_tree.links
nodes.clear()

out_node = nodes.new('ShaderNodeOutputMaterial')
bsdf_skin = nodes.new('ShaderNodeBsdfPrincipled')
bsdf_skin.location = (400, 0)
links.new(bsdf_skin.outputs['BSDF'], out_node.inputs['Surface'])

col_base_skin = (0.36, 0.18, 0.09, 1.0)
col_tattoo = (0.05, 0.08, 0.10, 1.0)

tex_coord = nodes.new('ShaderNodeTexCoord')
mapping_tat = nodes.new('ShaderNodeMapping')
mapping_tat.inputs['Scale'].default_value = (8.0, 14.0, 6.0)
links.new(tex_coord.outputs['Object'], mapping_tat.inputs['Vector'])

noise_tat = nodes.new('ShaderNodeTexNoise')
noise_tat.inputs['Scale'].default_value = 12.0
noise_tat.inputs['Detail'].default_value = 6.0
noise_tat.inputs['Roughness'].default_value = 0.7
links.new(mapping_tat.outputs['Vector'], noise_tat.inputs['Vector'])

voronoi_tat = nodes.new('ShaderNodeTexVoronoi')
voronoi_tat.inputs['Scale'].default_value = 18.0
links.new(mapping_tat.outputs['Vector'], voronoi_tat.inputs['Vector'])

mix_tat = nodes.new('ShaderNodeMix')
mix_tat.data_type = 'FLOAT'
mix_tat.blend_type = 'MULTIPLY'
mix_tat.inputs['Factor'].default_value = 0.85
links.new(noise_tat.outputs['Fac'], mix_tat.inputs['A'])
links.new(voronoi_tat.outputs['Distance'], mix_tat.inputs['B'])

ramp_tat = nodes.new('ShaderNodeValToRGB')
ramp_tat.color_ramp.elements[0].position = 0.32
ramp_tat.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp_tat.color_ramp.elements[1].position = 0.65
ramp_tat.color_ramp.elements[1].color = (0.75, 0.75, 0.75, 1)
links.new(mix_tat.outputs['Result'], ramp_tat.inputs['Fac'])

mix_skin_col = nodes.new('ShaderNodeMix')
mix_skin_col.data_type = 'RGBA'
mix_skin_col.blend_type = 'MIX'
links.new(ramp_tat.outputs['Color'], mix_skin_col.inputs['Factor'])
mix_skin_col.inputs['A'].default_value = col_base_skin
mix_skin_col.inputs['B'].default_value = col_tattoo
links.new(mix_skin_col.outputs['Result'], bsdf_skin.inputs['Base Color'])

pore_noise = nodes.new('ShaderNodeTexNoise')
pore_noise.inputs['Scale'].default_value = 160.0
pore_noise.inputs['Detail'].default_value = 8.0
links.new(tex_coord.outputs['Object'], pore_noise.inputs['Vector'])

bump_skin = nodes.new('ShaderNodeBump')
bump_skin.inputs['Strength'].default_value = 0.045
bump_skin.inputs['Distance'].default_value = 0.015
links.new(pore_noise.outputs['Fac'], bump_skin.inputs['Height'])
links.new(bump_skin.outputs['Normal'], bsdf_skin.inputs['Normal'])

sweat_noise = nodes.new('ShaderNodeTexNoise')
sweat_noise.inputs['Scale'].default_value = 24.0
sweat_noise.inputs['Detail'].default_value = 4.0
links.new(tex_coord.outputs['Object'], sweat_noise.inputs['Vector'])

ramp_rough = nodes.new('ShaderNodeValToRGB')
ramp_rough.color_ramp.elements[0].position = 0.30
ramp_rough.color_ramp.elements[0].color = (0.28, 0.28, 0.28, 1)
ramp_rough.color_ramp.elements[1].position = 0.75
ramp_rough.color_ramp.elements[1].color = (0.62, 0.62, 0.62, 1)
links.new(sweat_noise.outputs['Fac'], ramp_rough.inputs['Fac'])
links.new(ramp_rough.outputs['Color'], bsdf_skin.inputs['Roughness'])

if 'Subsurface Weight' in bsdf_skin.inputs:
    bsdf_skin.inputs['Subsurface Weight'].default_value = 0.15
    bsdf_skin.inputs['Subsurface Radius'].default_value = (1.0, 0.35, 0.15)
    bsdf_skin.inputs['Subsurface Scale'].default_value = 0.04
elif 'Subsurface' in bsdf_skin.inputs:
    bsdf_skin.inputs['Subsurface'].default_value = 0.15
    bsdf_skin.inputs['Subsurface Color'].default_value = (0.65, 0.18, 0.09, 1.0)

mat_cloth = bpy.data.materials.new('Mat_Kho_VaiCham_Master')
mat_cloth.use_nodes = True
nodes_c = mat_cloth.node_tree.nodes
links_c = mat_cloth.node_tree.links
bsdf_cloth = next(n for n in nodes_c if n.type == 'BSDF_PRINCIPLED')
bsdf_cloth.inputs['Base Color'].default_value = (0.13, 0.075, 0.045, 1.0)
bsdf_cloth.inputs['Roughness'].default_value = 0.88
tex_c_coord = nodes_c.new('ShaderNodeTexCoord')
tex_c_wave = nodes_c.new('ShaderNodeTexWave')
tex_c_wave.inputs['Scale'].default_value = 140.0
tex_c_wave.inputs['Distortion'].default_value = 2.5
links_c.new(tex_c_coord.outputs['Object'], tex_c_wave.inputs['Vector'])
bump_cloth = nodes_c.new('ShaderNodeBump')
bump_cloth.inputs['Strength'].default_value = 0.18
links_c.new(tex_c_wave.outputs['Color'], bump_cloth.inputs['Height'])
links_c.new(bump_cloth.outputs['Normal'], bsdf_cloth.inputs['Normal'])

mat_bronze = bpy.data.materials.new('Mat_DaoGam_DongSon')
mat_bronze.use_nodes = True
bsdf_brz = next(n for n in mat_bronze.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_brz.inputs['Base Color'].default_value = (0.58, 0.42, 0.20, 1.0)
bsdf_brz.inputs['Metallic'].default_value = 0.88
bsdf_brz.inputs['Roughness'].default_value = 0.32

mat_scabbard = bpy.data.materials.new('Mat_BaoDao_GoSonThen')
mat_scabbard.use_nodes = True
bsdf_scb = next(n for n in mat_scabbard.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_scb.inputs['Base Color'].default_value = (0.06, 0.035, 0.02, 1.0)
bsdf_scb.inputs['Roughness'].default_value = 0.35

mat_band = bpy.data.materials.new('Mat_Khan_DauRiu_Master')
mat_band.use_nodes = True
bsdf_b = next(n for n in mat_band.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_b.inputs['Base Color'].default_value = (0.52, 0.04, 0.04, 1.0)
bsdf_b.inputs['Roughness'].default_value = 0.75

mat_bamboo = bpy.data.materials.new('Mat_TramTre_Gia_Master')
mat_bamboo.use_nodes = True
bsdf_bam = next(n for n in mat_bamboo.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_bam.inputs['Base Color'].default_value = (0.75, 0.58, 0.28, 1.0)
bsdf_bam.inputs['Roughness'].default_value = 0.38

mat_hair = bpy.data.materials.new('Mat_Toc_Den_Master')
mat_hair.use_nodes = True
bsdf_h = next(n for n in mat_hair.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_h.inputs['Base Color'].default_value = (0.015, 0.015, 0.015, 1.0)
bsdf_h.inputs['Roughness'].default_value = 0.50

mat_wood = bpy.data.materials.new('Mat_GoLim_Cheo_Master')
mat_wood.use_nodes = True
bsdf_w = next(n for n in mat_wood.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
bsdf_w.inputs['Base Color'].default_value = (0.15, 0.075, 0.038, 1.0)
bsdf_w.inputs['Roughness'].default_value = 0.36

print("-> Hệ thống vật liệu PBR siêu thực hoàn tất!")

# 3. NẠP BODY BASE-MESH & CHUẨN HÓA CHIỀU CAO 1M62
bpy.ops.import_scene.gltf(filepath=GLB_BODY)
if 'Icosphere' in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects['Icosphere'], do_unlink=True)

rig = bpy.data.objects['metarig']
body = bpy.data.objects['mesh']
body.name = 'ThuyBinh_Body'
rig.name = 'ThuyBinh_Rig'

s_body = 1.62 / 1.9446
rig.scale = (s_body, s_body, s_body)
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.transform_apply(scale=True)

bpy.context.view_layer.objects.active = body
body.select_set(True)
bpy.ops.object.transform_apply(scale=True)

coords = [body.matrix_world @ v.co for v in body.data.vertices]
shift_z = -min(c.z for c in coords)
rig.location.z += shift_z
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.transform_apply(location=True)

bpy.context.view_layer.objects.active = body
bpy.ops.object.mode_set(mode='EDIT')
bm_b = bmesh.from_edit_mesh(body.data)
for v in bm_b.verts:
    world_z = (body.matrix_world @ v.co).z
    if world_z > 1.38:
        v.co.x *= 0.15
        v.co.y *= 0.15
        v.co.z = 1.35 + (v.co.z - 1.35) * 0.1
bmesh.update_edit_mesh(body.data)
bpy.ops.object.mode_set(mode='OBJECT')

body.data.materials.clear()
body.data.materials.append(mat_skin)
for p in body.data.polygons:
    p.use_smooth = True

col_soldier.objects.link(rig)
col_soldier.objects.link(body)
if rig.name in scene.collection.objects: scene.collection.objects.unlink(rig)
if body.name in scene.collection.objects: scene.collection.objects.unlink(body)

# 4. NẠP KHUÔN MẶT 3D SCAN & PHỤC SỨC ĐẦU
bpy.ops.import_scene.gltf(filepath=GLB_HEAD)
head = bpy.data.objects['LeePerrySmith']
head.name = 'ThuyBinh_Head_Sculpt'

for o in list(bpy.context.scene.objects):
    if o.type == 'EMPTY' and o.name in ['Camera', 'Lamp']:
        bpy.data.objects.remove(o, do_unlink=True)

s_head = 0.24 / 7.9451
head.scale = (s_head, s_head, s_head)
head.rotation_euler = (0, 0, math.radians(90))
bpy.context.view_layer.objects.active = head
head.select_set(True)
bpy.ops.object.transform_apply(rotation=True, scale=True)

head.location = (0.015, 0.0, 1.44)
bpy.ops.object.transform_apply(location=True)
head.data.materials.clear()
head.data.materials.append(mat_skin)
for p in head.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.038, location=(-0.078, 0.0, 1.535))
topknot = bpy.context.active_object
topknot.name = 'Bui_Toc_CuToi_Master'
topknot.scale = (0.85, 0.85, 1.10)
bpy.ops.object.transform_apply(scale=True)
topknot.data.materials.append(mat_hair)
for p in topknot.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_cylinder_add(radius=0.0035, depth=0.15, location=(-0.078, 0.0, 1.535))
hairpin = bpy.context.active_object
hairpin.name = 'Tram_Tre_CaiToc_Master'
hairpin.rotation_euler = (math.radians(90), 0, math.radians(15))
hairpin.data.materials.append(mat_bamboo)
for p in hairpin.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_torus_add(major_segments=36, minor_segments=16, major_radius=0.081, minor_radius=0.0075, location=(0.004, 0.0, 1.514))
headband = bpy.context.active_object
headband.name = 'Khan_Dau_Riu_Vong'
headband.rotation_euler = (0, math.radians(-7), 0)
headband.scale = (1.02, 0.88, 1.20)
bpy.ops.object.transform_apply(rotation=True, scale=True)
headband.data.materials.append(mat_band)
for p in headband.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.024, depth=0.10, location=(-0.062, 0.086, 1.505))
flap1 = bpy.context.active_object
flap1.rotation_euler = (math.radians(35), math.radians(-30), math.radians(60))
flap1.scale = (0.35, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)
flap1.data.materials.append(mat_band)
for p in flap1.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.020, depth=0.085, location=(-0.075, 0.076, 1.480))
flap2 = bpy.context.active_object
flap2.rotation_euler = (math.radians(20), math.radians(-45), math.radians(40))
flap2.scale = (0.35, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)
flap2.data.materials.append(mat_band)
for p in flap2.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.076, location=(-0.012, 0.0, 1.505))
hair_cap = bpy.context.active_object
hair_cap.name = 'Toc_Nen_Dau'
hair_cap.scale = (0.88, 0.82, 0.72)
bpy.ops.object.transform_apply(scale=True)
hair_cap.data.materials.append(mat_hair)
for p in hair_cap.data.polygons:
    p.use_smooth = True

bpy.ops.object.select_all(action='DESELECT')
for o in [head, hair_cap, topknot, hairpin, headband, flap1, flap2]:
    o.select_set(True)
bpy.context.view_layer.objects.active = head
bpy.ops.object.join()
head_assembly = bpy.context.active_object
head_assembly.name = 'ThuyBinh_Head_Assembly'

vg_head = head_assembly.vertex_groups.new(name='spine.005')
vg_head.add(list(range(len(head_assembly.data.vertices))), 1.0, 'REPLACE')
mod_head = head_assembly.modifiers.new('Armature', 'ARMATURE')
mod_head.object = rig

col_soldier.objects.link(head_assembly)
if head_assembly.name in scene.collection.objects: scene.collection.objects.unlink(head_assembly)

print("-> Khuôn mặt 3D scan & Khăn đầu rìu, búi tóc trâm tre hoàn tất!")

# 5. TRANG PHỤC: KHỐ VẢI THÔ LẠC VIỆT (LOINCLOTH VỚI NẾP GẤP VẢI TỰ NHIÊN)
bpy.ops.mesh.primitive_torus_add(major_radius=0.140, minor_radius=0.024, location=(0.006, 0.0, 0.775))
loin_belt = bpy.context.active_object
loin_belt.name = 'Kho_Dai_Lung'
loin_belt.scale = (0.86, 1.08, 0.85)
bpy.ops.object.transform_apply(scale=True)
loin_belt.data.materials.append(mat_cloth)
for p in loin_belt.data.polygons:
    p.use_smooth = True

bm_ff = bmesh.new()
verts_ff = []
for zi, z_val in enumerate([0.76, 0.68, 0.60, 0.52, 0.44]):
    curve_x = 0.115 + math.sin(zi * 0.8) * 0.015 - (0.76 - z_val) * 0.08
    w_y = 0.055 + zi * 0.012
    v_l = bm_ff.verts.new((curve_x, -w_y, z_val))
    v_r = bm_ff.verts.new((curve_x, +w_y, z_val))
    verts_ff.append((v_l, v_r))

for i in range(len(verts_ff) - 1):
    bm_ff.faces.new([verts_ff[i][0], verts_ff[i+1][0], verts_ff[i+1][1], verts_ff[i][1]])

mesh_ff = bpy.data.meshes.new('Mesh_Kho_Ta_Truoc')
bm_ff.to_mesh(mesh_ff)
bm_ff.free()
obj_ff = bpy.data.objects.new('Kho_Ta_Truoc_Master', mesh_ff)
col_soldier.objects.link(obj_ff)
obj_ff.data.materials.append(mat_cloth)
for p in obj_ff.data.polygons:
    p.use_smooth = True

mod_sol = obj_ff.modifiers.new('Solidify', 'SOLIDIFY')
mod_sol.thickness = 0.004

bm_bf = bmesh.new()
verts_bf = []
for zi, z_val in enumerate([0.76, 0.68, 0.60, 0.53]):
    curve_x = -0.110 - (0.76 - z_val) * 0.04
    w_y = 0.050 + zi * 0.010
    v_l = bm_bf.verts.new((curve_x, -w_y, z_val))
    v_r = bm_bf.verts.new((curve_x, +w_y, z_val))
    verts_bf.append((v_l, v_r))

for i in range(len(verts_bf) - 1):
    bm_bf.faces.new([verts_bf[i][0], verts_bf[i+1][0], verts_bf[i+1][1], verts_bf[i][1]])

mesh_bf = bpy.data.meshes.new('Mesh_Kho_Ta_Sau')
bm_bf.to_mesh(mesh_bf)
bm_bf.free()
obj_bf = bpy.data.objects.new('Kho_Ta_Sau_Master', mesh_bf)
col_soldier.objects.link(obj_bf)
obj_bf.data.materials.append(mat_cloth)
for p in obj_bf.data.polygons:
    p.use_smooth = True

mod_sol_b = obj_bf.modifiers.new('Solidify', 'SOLIDIFY')
mod_sol_b.thickness = 0.004

bpy.ops.mesh.primitive_cylinder_add(radius=0.070, depth=0.19, location=(0.0, 0.0, 0.725))
crotch_wrap = bpy.context.active_object
crotch_wrap.rotation_euler = (math.radians(90), 0, 0)
crotch_wrap.scale = (0.76, 0.62, 0.88)
bpy.ops.object.transform_apply(scale=True)
crotch_wrap.data.materials.append(mat_cloth)
for p in crotch_wrap.data.polygons:
    p.use_smooth = True

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.024, location=(0.015, -0.145, 0.775))
knot = bpy.context.active_object
knot.name = 'Kho_Nut_That_Hong'
knot.scale = (1.2, 0.8, 0.9)
bpy.ops.object.transform_apply(scale=True)
knot.data.materials.append(mat_cloth)
for p in knot.data.polygons:
    p.use_smooth = True

bpy.ops.object.select_all(action='DESELECT')
for o in [loin_belt, obj_ff, obj_bf, crotch_wrap, knot]:
    o.select_set(True)
bpy.context.view_layer.objects.active = loin_belt
bpy.ops.object.join()
loincloth_assembly = bpy.context.active_object
loincloth_assembly.name = 'ThuyBinh_Kho_Master'

vg_kho = loincloth_assembly.vertex_groups.new(name='spine')
vg_kho.add(list(range(len(loincloth_assembly.data.vertices))), 1.0, 'REPLACE')
mod_kho = loincloth_assembly.modifiers.new('Armature', 'ARMATURE')
mod_kho.object = rig

if loincloth_assembly.name not in col_soldier.objects:
    col_soldier.objects.link(loincloth_assembly)
if loincloth_assembly.name in scene.collection.objects:
    scene.collection.objects.unlink(loincloth_assembly)

print("-> Trang phục Khố vải thô Lạc Việt với nếp gấp tự nhiên hoàn tất!")

# 6. KHÍ TÀI: DAO GĂM ĐỒNG ĐÔNG SƠN CHUÔI CHỮ T GIẮT HÔNG
bm_dag = bmesh.new()
verts_dag = [
    bm_dag.verts.new((0.0, -0.016, 0.0)),
    bm_dag.verts.new((0.0, +0.016, 0.0)),
    bm_dag.verts.new((0.005, 0.0, 0.0)),
    bm_dag.verts.new((-0.005, 0.0, 0.0)),
    bm_dag.verts.new((0.0, 0.0, 0.18))
]
bm_dag.faces.new([verts_dag[0], verts_dag[2], verts_dag[4]])
bm_dag.faces.new([verts_dag[2], verts_dag[1], verts_dag[4]])
bm_dag.faces.new([verts_dag[1], verts_dag[3], verts_dag[4]])
bm_dag.faces.new([verts_dag[3], verts_dag[0], verts_dag[4]])
mesh_blade = bpy.data.meshes.new("Mesh_Luoi_DaoGam_Dong")
bm_dag.to_mesh(mesh_blade)
bm_dag.free()
obj_blade = bpy.data.objects.new("DaoGam_DongSon_Luoi", mesh_blade)
scene.collection.objects.link(obj_blade)
obj_blade.data.materials.append(mat_bronze)

bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.085, location=(0, 0, -0.045))
hilt_grip = bpy.context.active_object
hilt_grip.data.materials.append(mat_bronze)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.090))
hilt_pommel = bpy.context.active_object
hilt_pommel.scale = (0.016, 0.065, 0.014)
bpy.ops.object.transform_apply(scale=True)
hilt_pommel.data.materials.append(mat_bronze)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.085))
scabbard = bpy.context.active_object
scabbard.name = 'BaoDao_GoSonThen'
scabbard.scale = (0.018, 0.042, 0.185)
bpy.ops.object.transform_apply(scale=True)
scabbard.data.materials.append(mat_scabbard)

bpy.ops.object.select_all(action='DESELECT')
for o in [obj_blade, hilt_grip, hilt_pommel, scabbard]:
    o.select_set(True)
bpy.context.view_layer.objects.active = scabbard
bpy.ops.object.join()
dagger = bpy.context.active_object
dagger.name = 'DaoGam_DongSon_GiatHong'

dagger.location = (0.02, 0.155, 0.76)
dagger.rotation_euler = (math.radians(25), math.radians(-32), math.radians(15))
vg_dag = dagger.vertex_groups.new(name='spine')
vg_dag.add(list(range(len(dagger.data.vertices))), 1.0, 'REPLACE')
mod_dag = dagger.modifiers.new('Armature', 'ARMATURE')
mod_dag.object = rig

col_soldier.objects.link(dagger)
if dagger.name in scene.collection.objects: scene.collection.objects.unlink(dagger)

print("-> Dao găm đồng Đông Sơn chuôi chữ T giắt hông hoàn tất!")

# 7. KHÔNG GIAN BỐI CẢNH THUYỀN MẪU
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.02, 0.0, 0.35))
bench = bpy.context.active_object
bench.name = 'Xa_Ngang_NgoiCheo'
bench.scale = (0.24, 1.25, 0.06)
bpy.ops.object.transform_apply(scale=True)
bench.data.materials.append(mat_wood)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.38, 0.0, 0.06))
foot_brace = bpy.context.active_object
foot_brace.name = 'Go_Dap_Chan'
foot_brace.scale = (0.12, 1.10, 0.08)
foot_brace.rotation_euler = (0, math.radians(-25), 0)
bpy.ops.object.transform_apply(scale=True)
foot_brace.data.materials.append(mat_wood)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.32, 0.65, 0.45))
gunwale_l = bpy.context.active_object
gunwale_l.name = 'Man_Thuyen_Trai'
gunwale_l.scale = (1.8, 0.12, 0.38)
bpy.ops.object.transform_apply(scale=True)
gunwale_l.data.materials.append(mat_wood)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.32, -0.65, 0.38))
gunwale_r = bpy.context.active_object
gunwale_r.name = 'Man_Thuyen_Phai'
gunwale_r.scale = (1.8, 0.10, 0.22)
bpy.ops.object.transform_apply(scale=True)
gunwale_r.data.materials.append(mat_wood)

bpy.ops.mesh.primitive_plane_add(size=5.0, location=(0.0, 0.0, 0.0))
deck = bpy.context.active_object
deck.name = 'San_Thuyen_Studio'
deck.data.materials.append(mat_wood)

for o in [bench, foot_brace, gunwale_l, gunwale_r, deck]:
    col_props.objects.link(o)
    if o.name in scene.collection.objects: scene.collection.objects.unlink(o)

# 8. POSE RIG & KHÓA KHỚP GIẢI PHẪU TƯ THẾ NGỒI CHÈO KIỀNG 3 CHÂN
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='POSE')

def rot_bone(pb_name, rx, ry, rz):
    pb = rig.pose.bones.get(pb_name)
    if pb:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))

rot_bone('thigh.L', -66, 6, 16)
rot_bone('shin.L', 70, 0, -4)
rot_bone('foot.L', -10, 0, 0)

rot_bone('thigh.R', 66, -6, 16)
rot_bone('shin.R', -70, 0, -4)
rot_bone('foot.R', 10, 0, 0)

rot_bone('spine.001', 9, 0, 0)
rot_bone('spine.002', 6, 0, 0)
rot_bone('spine.003', 4, 0, 0)
rot_bone('spine.004', -2, 0, 0)
rot_bone('spine.005', -3, 0, 0)

rot_bone('upper_arm.L', 42, -12, 16)
rot_bone('forearm.L', 36, 12, 14)
rot_bone('hand.L', 8, -6, -10)

rot_bone('upper_arm.R', 40, 10, -20)
rot_bone('forearm.R', 42, -8, -14)
rot_bone('hand.R', -8, 6, 10)

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

# 9. CÁN CHÈO GỖ LIM & CỌC CHÈO BE THUYỀN
hand_l = rig.matrix_world @ rig.pose.bones['hand.L'].head
hand_r = rig.matrix_world @ rig.pose.bones['hand.R'].head
palm_offset = Vector((0.055, 0.0, -0.005))
grip_l = hand_l + palm_offset
grip_r = hand_r + palm_offset

bpy.ops.mesh.primitive_cylinder_add(radius=0.0225, depth=3.2)
oar = bpy.context.active_object
oar.name = 'Can_Cheo_GoLim'
oar.data.materials.append(mat_wood)
for p in oar.data.polygons:
    p.use_smooth = True

oar_dir = (grip_l - grip_r).normalized()
handle_end = grip_r - oar_dir * 0.45
oar_center = handle_end + oar_dir * 1.60
oar.location = oar_center
rot_quat = Vector((0, 0, 1)).rotation_difference(oar_dir)
oar.rotation_mode = 'QUATERNION'
oar.rotation_quaternion = rot_quat

pin_loc = handle_end + oar_dir * 1.55
bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.45, location=(pin_loc.x, 0.65, 0.58))
pin = bpy.context.active_object
pin.name = 'Coc_Cheo_Go'
pin.data.materials.append(mat_wood)
for p in pin.data.polygons:
    p.use_smooth = True

col_soldier.objects.link(oar)
col_props.objects.link(pin)
if oar.name in scene.collection.objects: scene.collection.objects.unlink(oar)
if pin.name in scene.collection.objects: scene.collection.objects.unlink(pin)

# 10. HỆ THỐNG ÁNH SÁNG STUDIO ĐIỆN ẢNH (3-POINT LIGHTING + FILL CHI TIẾT)
key_data = bpy.data.lights.new('Studio_Key', 'SUN')
key_data.energy = 4.5
key_data.color = (1.0, 0.97, 0.92)
key_obj = bpy.data.objects.new('Studio_Key', key_data)
col_lights.objects.link(key_obj)
key_obj.rotation_euler = (math.radians(52), math.radians(22), math.radians(-42))

fill_data = bpy.data.lights.new('Studio_Fill', 'SUN')
fill_data.energy = 2.0
fill_data.color = (0.85, 0.92, 1.0)
fill_obj = bpy.data.objects.new('Studio_Fill', fill_data)
col_lights.objects.link(fill_obj)
fill_obj.rotation_euler = (math.radians(35), math.radians(-25), math.radians(55))

rim_data = bpy.data.lights.new('Studio_Rim', 'SUN')
rim_data.energy = 3.2
rim_data.color = (1.0, 0.95, 0.88)
rim_obj = bpy.data.objects.new('Studio_Rim', rim_data)
col_lights.objects.link(rim_obj)
rim_obj.rotation_euler = (math.radians(120), math.radians(15), math.radians(140))

# 11. THIẾT LẬP 4 CAMERA KIỂM ĐỊNH CHUYÊN SÂU TỪNG BỘ PHẬN
head_center = rig.matrix_world @ rig.pose.bones['spine.005'].head + Vector((0.02, 0.0, 0.06))
target_head = bpy.data.objects.new('Target_Head', None)
col_props.objects.link(target_head)
target_head.location = head_center

target_torso = bpy.data.objects.new('Target_Torso', None)
col_props.objects.link(target_torso)
target_torso.location = (0.08, 0.0, 1.05)

target_waist = bpy.data.objects.new('Target_Waist', None)
col_props.objects.link(target_waist)
target_waist.location = (0.05, 0.0, 0.75)

target_body = bpy.data.objects.new('Target_Body', None)
col_props.objects.link(target_body)
target_body.location = (0.15, 0.0, 0.82)

cam1_data = bpy.data.cameras.new('Cam1_ChanDung_Mat')
cam1_data.lens = 85
cam1 = bpy.data.objects.new('Cam1_ChanDung_Mat', cam1_data)
col_cams.objects.link(cam1)
cam1.location = (head_center.x + 0.68, head_center.y - 0.28, head_center.z + 0.04)
tt1 = cam1.constraints.new('TRACK_TO')
tt1.target = target_head
tt1.track_axis = 'TRACK_NEGATIVE_Z'
tt1.up_axis = 'UP_Y'

cam2_data = bpy.data.cameras.new('Cam2_XamMinh_GiaoLong')
cam2_data.lens = 65
cam2 = bpy.data.objects.new('Cam2_XamMinh_GiaoLong', cam2_data)
col_cams.objects.link(cam2)
cam2.location = (0.85, -0.65, 1.15)
tt2 = cam2.constraints.new('TRACK_TO')
tt2.target = target_torso
tt2.track_axis = 'TRACK_NEGATIVE_Z'
tt2.up_axis = 'UP_Y'

cam3_data = bpy.data.cameras.new('Cam3_Kho_Va_DaoGam')
cam3_data.lens = 75
cam3 = bpy.data.objects.new('Cam3_Kho_Va_DaoGam', cam3_data)
col_cams.objects.link(cam3)
cam3.location = (0.75, 0.55, 0.85)
tt3 = cam3.constraints.new('TRACK_TO')
tt3.target = target_waist
tt3.track_axis = 'TRACK_NEGATIVE_Z'
tt3.up_axis = 'UP_Y'

cam4_data = bpy.data.cameras.new('Cam4_ToanThan_NgoiCheo')
cam4_data.lens = 38
cam4 = bpy.data.objects.new('Cam4_ToanThan_NgoiCheo', cam4_data)
col_cams.objects.link(cam4)
cam4.location = (2.4, -2.0, 1.40)
tt4 = cam4.constraints.new('TRACK_TO')
tt4.target = target_body
tt4.track_axis = 'TRACK_NEGATIVE_Z'
tt4.up_axis = 'UP_Y'

# 12. KẾT XUẤT 04 ẢNH KIỂM ĐỊNH FULL HD 1080P
artifact_dir = r"C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c"
shots = [
    ('Shot1_ChanDung', cam1, os.path.join(artifact_dir, 'anh_kiem_dinh_soldier_1_chandung_mat.png')),
    ('Shot2_XamGiaoLong', cam2, os.path.join(artifact_dir, 'anh_kiem_dinh_soldier_2_xam_giaolong.png')),
    ('Shot3_KhoVaDaoGam', cam3, os.path.join(artifact_dir, 'anh_kiem_dinh_soldier_3_kho_daogam.png')),
    ('Shot4_ToanThan', cam4, os.path.join(artifact_dir, 'anh_kiem_dinh_soldier_4_toanthan_cheo.png'))
]

for name, cam_obj, out_path in shots:
    scene.camera = cam_obj
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"-> Đã kết xuất: {name} -> {out_path}")

save_path = os.path.join(WS_DIR, 'thuy_binh_dai_viet_master.blend')
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"=== [VIETNAM-SIM MASTER] ĐÃ LƯU THÀNH CÔNG THỦY BINH ĐẠI VIỆT MASTER: {save_path} ===")
