import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

scene_name = "Scene_Coc_SieuThuc_938"
if scene_name in bpy.data.scenes:
    scene = bpy.data.scenes[scene_name]
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    scene = bpy.data.scenes.new(scene_name)

bpy.context.window.scene = scene

# World Lighting
scene.world = bpy.data.worlds.new("World_BachDang_Coc")
scene.world.use_nodes = True
bg_node = scene.world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.55, 0.70, 0.85, 1.0)
    bg_node.inputs["Strength"].default_value = 1.2

# 1. BLUEPRINT REFERENCE PLANE (GATE 1)
sketch_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/references/phac_thao_coc_bach_dang_2d.png'
bp_plane = None
if os.path.exists(sketch_path):
    img = bpy.data.images.load(sketch_path, check_existing=True)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-1.1, 2.8, 0.8))
    bp_plane = bpy.context.active_object
    bp_plane.name = "REFERENCE_BLUEPRINT_PLANE_COC"
    bp_plane.scale = Vector((4.6, 2.6, 1.0))
    bp_plane.rotation_euler = Euler((math.pi / 2.0, 0, 0))
    
    mat_bp = bpy.data.materials.new(name="Mat_Blueprint_Coc")
    mat_bp.use_nodes = True
    bsdf = mat_bp.node_tree.nodes.get("Principled BSDF")
    tex_node = mat_bp.node_tree.nodes.new("ShaderNodeTexImage")
    tex_node.image = img
    mat_bp.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    mat_bp.node_tree.links.new(tex_node.outputs["Alpha"], bsdf.inputs["Alpha"])
    mat_bp.blend_method = 'BLEND'
    bp_plane.data.materials.append(mat_bp)

# 2. THÔNG SỐ VẬT LÝ KHẢO CỔ CỌC BẠCH ĐẰNG
angle_deg = 20.0
angle_rad = math.radians(angle_deg)
dir_coc = Vector((math.sin(angle_rad), 0, math.cos(angle_rad))).normalized()

wood_len = 2.40
iron_len = 0.40
p_goc = Vector((0.0, 0.0, -1.0)) # Cắm sâu 1.0m dưới bùn
p_junction = p_goc + dir_coc * wood_len
p_tip = p_junction + dir_coc * iron_len

rot_diff = Vector((0, 0, 1)).rotation_difference(dir_coc)
mat_rot = rot_diff.to_matrix().to_4x4()

# 3. DỰNG THÂN GỖ LIM GIÀ PBR
bm_wood = bmesh.new()
steps_z = 36
radial_segs = 32

verts_layers = []
for iz in range(steps_z + 1):
    frac = iz / steps_z
    r_base = 0.14 * (1.0 - frac) + 0.11 * frac
    z_local = frac * wood_len
    layer_verts = []
    for ir in range(radial_segs):
        theta = (ir / radial_segs) * 2.0 * math.pi
        noise_bark = 0.008 * math.sin(ir * 4.0 + frac * 10.0) + 0.006 * math.cos(ir * 8.0 - frac * 15.0)
        groove = -0.015 if (ir % 8 == 0 or ir % 8 == 1) else 0.0
        r_actual = max(0.08, r_base + noise_bark + groove)
        v_local = Vector((r_actual * math.cos(theta), r_actual * math.sin(theta), z_local - wood_len * 0.5))
        layer_verts.append(bm_wood.verts.new(v_local))
    verts_layers.append(layer_verts)

for iz in range(steps_z):
    for ir in range(radial_segs):
        v1 = verts_layers[iz][ir]
        v2 = verts_layers[iz][(ir + 1) % radial_segs]
        v3 = verts_layers[iz + 1][(ir + 1) % radial_segs]
        v4 = verts_layers[iz + 1][ir]
        bm_wood.faces.new([v1, v2, v3, v4])

v_bottom = bm_wood.verts.new(Vector((0, 0, -wood_len * 0.5)))
for ir in range(radial_segs):
    bm_wood.faces.new([v_bottom, verts_layers[0][(ir + 1) % radial_segs], verts_layers[0][ir]])

v_top = bm_wood.verts.new(Vector((0, 0, wood_len * 0.5)))
for ir in range(radial_segs):
    bm_wood.faces.new([v_top, verts_layers[steps_z][ir], verts_layers[steps_z][(ir + 1) % radial_segs]])

p_wood_center = p_goc + dir_coc * (wood_len * 0.5)
mat_wood_final = Matrix.Translation(p_wood_center) @ mat_rot
bmesh.ops.transform(bm_wood, matrix=mat_wood_final, verts=bm_wood.verts)

m_wood = bpy.data.meshes.new("Mesh_Than_Coc_GoLim_938")
bm_wood.to_mesh(m_wood)
bm_wood.free()

mat_wood = bpy.data.materials.new("Mat_GoLim_PBR_Real")
mat_wood.use_nodes = True
wn = mat_wood.node_tree.nodes
wl = mat_wood.node_tree.links
w_bsdf = wn.get("Principled BSDF")

tex_wood = wn.new("ShaderNodeTexNoise")
tex_wood.inputs["Scale"].default_value = 40.0
tex_wood.inputs["Detail"].default_value = 14.0
tex_wood.inputs["Roughness"].default_value = 0.8

ramp_wood = wn.new("ShaderNodeValToRGB")
ramp_wood.color_ramp.elements[0].position = 0.25
ramp_wood.color_ramp.elements[0].color = (0.09, 0.06, 0.04, 1.0) # Nâu đen yếm khí ngàn năm
ramp_wood.color_ramp.elements[1].position = 0.75
ramp_wood.color_ramp.elements[1].color = (0.28, 0.18, 0.12, 1.0) # Thớ gỗ lim già
wl.new(tex_wood.outputs["Fac"], ramp_wood.inputs["Fac"])
wl.new(ramp_wood.outputs["Color"], w_bsdf.inputs["Base Color"])

bump_wood = wn.new("ShaderNodeBump")
bump_wood.inputs["Strength"].default_value = 0.75
bump_wood.inputs["Distance"].default_value = 0.06
wl.new(tex_wood.outputs["Fac"], bump_wood.inputs["Height"])
wl.new(bump_wood.outputs["Normal"], w_bsdf.inputs["Normal"])
w_bsdf.inputs["Roughness"].default_value = 0.85

m_wood.materials.append(mat_wood)
obj_wood = bpy.data.objects.new("Coc_Than_GoLim_938", m_wood)
scene.collection.objects.link(obj_wood)

# 4. ĐẦU BỊT SẮT RÈN 4 CẠNH SẮC BÉN & ĐINH TÁN
bm_iron = bmesh.new()

tip_local = Vector((0, 0, iron_len))
base_half = 0.115
base_v = [
    Vector((-base_half, -base_half, 0)),
    Vector((base_half, -base_half, 0)),
    Vector((base_half, base_half, 0)),
    Vector((-base_half, base_half, 0))
]
v_iron_tip = bm_iron.verts.new(tip_local)
v_base_verts = [bm_iron.verts.new(b) for b in base_v]

for i in range(4):
    bm_iron.faces.new([v_iron_tip, v_base_verts[i], v_base_verts[(i + 1) % 4]])

collar_depth = -0.10
collar_verts = [bm_iron.verts.new(Vector((b.x * 1.06, b.y * 1.06, collar_depth))) for b in base_v]
for i in range(4):
    bm_iron.faces.new([v_base_verts[i], v_base_verts[(i + 1) % 4], collar_verts[(i + 1) % 4], collar_verts[i]])

# 4 Đinh tán sắt rèn dẹt chốt xuyên tâm
for i in range(4):
    ang = i * (math.pi / 2.0)
    p_rivet = Vector((math.cos(ang) * (base_half * 1.08), math.sin(ang) * (base_half * 1.08), collar_depth * 0.5))
    mat_rivet = Matrix.Translation(p_rivet) @ Matrix.Scale(0.6, 4, Vector((math.cos(ang), math.sin(ang), 0))) # Đinh tán dẹt
    bmesh.ops.create_icosphere(bm_iron, subdivisions=2, radius=0.022, matrix=mat_rivet)

for v in bm_iron.verts:
    if v != v_iron_tip:
        v.co += Vector((math.sin(v.co.z * 50.0) * 0.003, math.cos(v.co.x * 50.0) * 0.003, 0))

mat_iron_final = Matrix.Translation(p_junction) @ mat_rot
bmesh.ops.transform(bm_iron, matrix=mat_iron_final, verts=bm_iron.verts)

m_iron = bpy.data.meshes.new("Mesh_Dau_Bit_Sat_938")
bm_iron.to_mesh(m_iron)
bm_iron.free()

mat_iron = bpy.data.materials.new("Mat_DauBitSat_PBR_Rust")
mat_iron.use_nodes = True
in_nodes = mat_iron.node_tree.nodes
il = mat_iron.node_tree.links
i_bsdf = in_nodes.get("Principled BSDF")

tex_rust = in_nodes.new("ShaderNodeTexNoise")
tex_rust.inputs["Scale"].default_value = 28.0
tex_rust.inputs["Detail"].default_value = 10.0

ramp_rust = in_nodes.new("ShaderNodeValToRGB")
ramp_rust.color_ramp.elements[0].position = 0.30
ramp_rust.color_ramp.elements[0].color = (0.16, 0.17, 0.19, 1.0) # Thép rèn đập búa xám sẫm
ramp_rust.color_ramp.elements[1].position = 0.65
ramp_rust.color_ramp.elements[1].color = (0.45, 0.24, 0.12, 1.0) # Vệt rỉ oxy hóa nước mặn
il.new(tex_rust.outputs["Fac"], ramp_rust.inputs["Fac"])
il.new(ramp_rust.outputs["Color"], i_bsdf.inputs["Base Color"])

i_bsdf.inputs["Metallic"].default_value = 0.88
i_bsdf.inputs["Roughness"].default_value = 0.55

bump_rust = in_nodes.new("ShaderNodeBump")
bump_rust.inputs["Strength"].default_value = 0.55
bump_rust.inputs["Distance"].default_value = 0.04
il.new(tex_rust.outputs["Fac"], bump_rust.inputs["Height"])
il.new(bump_rust.outputs["Normal"], i_bsdf.inputs["Normal"])

m_iron.materials.append(mat_iron)
obj_iron = bpy.data.objects.new("Coc_Dau_Bit_Sat_938", m_iron)
scene.collection.objects.link(obj_iron)

# 5. DỰNG TẦNG BÙN SÉT ĐÁY SÔNG TỰ NHIÊN
bm_mud = bmesh.new()
grid_res = 36
bmesh.ops.create_grid(bm_mud, x_segments=grid_res, y_segments=grid_res, size=4.5)
for v in bm_mud.verts:
    v.co.z = 0.08 * math.sin(v.co.x * 1.2) * math.cos(v.co.y * 1.2) - 0.05 * (v.co.x**2 + v.co.y**2)/12.0

bmesh.ops.extrude_edge_only(bm_mud, edges=[e for e in bm_mud.edges if e.is_boundary])
for v in bm_mud.verts:
    if v.co.z < -0.15:
        v.co.z = -1.25

m_mud = bpy.data.meshes.new("Mesh_Tang_Bun_Set_DaySong")
bm_mud.to_mesh(m_mud)
bm_mud.free()

mat_mud = bpy.data.materials.new("Mat_BunSet_PhuSa_Real")
mat_mud.use_nodes = True
mn = mat_mud.node_tree.nodes
ml = mat_mud.node_tree.links
m_bsdf = mn.get("Principled BSDF")

tex_mud = mn.new("ShaderNodeTexNoise")
tex_mud.inputs["Scale"].default_value = 18.0
tex_mud.inputs["Detail"].default_value = 8.0

ramp_mud = mn.new("ShaderNodeValToRGB")
ramp_mud.color_ramp.elements[0].position = 0.25
ramp_mud.color_ramp.elements[0].color = (0.13, 0.11, 0.09, 1.0)
ramp_mud.color_ramp.elements[1].position = 0.80
ramp_mud.color_ramp.elements[1].color = (0.24, 0.20, 0.16, 1.0)

ml.new(tex_mud.outputs["Fac"], ramp_mud.inputs["Fac"])
ml.new(ramp_mud.outputs["Color"], m_bsdf.inputs["Base Color"])
m_bsdf.inputs["Roughness"].default_value = 0.90

bump_mud = mn.new("ShaderNodeBump")
bump_mud.inputs["Strength"].default_value = 0.6
ml.new(tex_mud.outputs["Fac"], bump_mud.inputs["Height"])
ml.new(bump_mud.outputs["Normal"], m_bsdf.inputs["Normal"])

m_mud.materials.append(mat_mud)
obj_mud = bpy.data.objects.new("DiaHinh_TangBun_DaySong", m_mud)
scene.collection.objects.link(obj_mud)

# 6. TẠO CÁC CỌC PHỤ TRONG TRẬN ĐỊA BÃI CỌC BẠCH ĐẰNG (STAKE FIELD)
stake_offsets = [
    (1.4, 0.8, -0.05),
    (-1.5, 0.6, -0.02),
    (0.8, -1.2, 0.03),
    (-1.1, -1.0, -0.04),
    (2.2, -0.6, 0.02)
]
field_objs = []
for idx, (ox, oy, oz) in enumerate(stake_offsets):
    # Tạo instance cọc phụ
    copy_wood = obj_wood.copy()
    copy_wood.location = Vector((ox, oy, oz))
    scene.collection.objects.link(copy_wood)
    
    copy_iron = obj_iron.copy()
    copy_iron.location = Vector((ox, oy, oz))
    scene.collection.objects.link(copy_iron)
    
    field_objs.extend([copy_wood, copy_iron])

# 7. MẶT NƯỚC SÔNG BẠCH ĐẰNG (GỢN SÓNG PHÙ SA LĂN TĂN)
bm_water = bmesh.new()
bmesh.ops.create_grid(bm_water, x_segments=24, y_segments=24, size=4.6)
for v in bm_water.verts:
    v.co.z = 1.10 + 0.025 * math.sin(v.co.x * 3.5 + v.co.y * 3.0)

m_water = bpy.data.meshes.new("Mesh_Nuoc_Song_TrieuRut")
bm_water.to_mesh(m_water)
bm_water.free()

mat_water = bpy.data.materials.new("Mat_NuocSong_BachDang_PBR")
mat_water.use_nodes = True
wnodes = mat_water.node_tree.nodes
water_bsdf = wnodes.get("Principled BSDF")
water_bsdf.inputs["Base Color"].default_value = (0.16, 0.32, 0.42, 0.45)
water_bsdf.inputs["Roughness"].default_value = 0.12
water_bsdf.inputs["Transmission Weight"].default_value = 0.85
mat_water.blend_method = 'BLEND'

m_water.materials.append(mat_water)
obj_water = bpy.data.objects.new("MatNuoc_Song_TrieuRut", m_water)
scene.collection.objects.link(obj_water)

# 8. HỆ THỐNG CHIẾU SÁNG ĐIỆN ẢNH
sun_data = bpy.data.lights.new("Sun_Light", 'SUN')
sun_data.energy = 5.0
sun_data.color = (1.0, 0.97, 0.90)
sun_obj = bpy.data.objects.new("Sun_Light", sun_data)
sun_obj.location = Vector((4.0, -5.0, 6.0))
sun_obj.rotation_euler = Euler((math.radians(45), math.radians(15), math.radians(-35)))
scene.collection.objects.link(sun_obj)

fill_data = bpy.data.lights.new("Fill_Light", 'POINT')
fill_data.energy = 220.0
fill_data.color = (0.6, 0.8, 0.95)
fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
fill_obj.location = Vector((-3.0, -3.0, 2.0))
scene.collection.objects.link(fill_obj)

rim_data = bpy.data.lights.new("Rim_Light", 'SPOT')
rim_data.energy = 450.0
rim_data.spot_size = math.radians(50)
rim_data.color = (1.0, 0.95, 0.85)
rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
rim_obj.location = Vector((1.8, 3.0, 3.5))
rim_obj.rotation_euler = (p_tip - rim_obj.location).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(rim_obj)

# 9. HÀM RENDER ĐA GÓC ĐỘ CHUẨN XÁC
def render_angle(cam_pos, look_target, filename, lens=50.0):
    cam_data = bpy.data.cameras.new("Cam_Render")
    cam_obj = bpy.data.objects.new("Cam_Render", cam_data)
    scene.collection.objects.link(cam_obj)
    
    cam_obj.location = cam_pos
    look_dir = look_target - cam_pos
    cam_obj.rotation_euler = look_dir.to_track_quat('-Z', 'Y').to_euler()
    cam_data.lens = lens
    
    scene.camera = cam_obj
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    
    out_dir = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh'
    out_path = os.path.join(out_dir, filename)
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    
    artifact_dir = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c'
    import shutil
    shutil.copyfile(out_path, os.path.join(artifact_dir, filename))
    print(f"Render thanh cong: {filename}")
    
    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.cameras.remove(cam_data)

# 1. Side View trực giao: Hiện Blueprint tham chiếu phía sau để so khớp
if bp_plane:
    bp_plane.hide_render = False
obj_water.hide_render = True # Ẩn nước để thấy rõ toàn bộ thân cọc và tầng bùn
render_angle(Vector((0.0, -4.8, 0.85)), Vector((0.4, 0.0, 0.55)), "anh_coc_goc_nhin_sideview.png", lens=48.0)

if bp_plane:
    bp_plane.hide_render = True

# 2. Cận cảnh Hero Shot: Đầu bịt sắt rèn 4 cạnh, đai sắt, đinh tán dẹt và thân gỗ lim
render_angle(Vector((0.15, -1.25, 1.45)), Vector((0.85, 0.0, 1.40)), "anh_coc_cancanh_dau_sat.png", lens=65.0)

# 3. Cận cảnh Gốc cọc cắm sâu vào bùn đáy sông
render_angle(Vector((-0.65, -1.6, 0.25)), Vector((0.1, 0.0, -0.15)), "anh_coc_cancanh_goc_cam_bun.png", lens=55.0)

# 4. Toàn cảnh Phối cảnh 3D Bãi cọc ngầm cắm xiên đón dòng nước triều rút
obj_water.hide_render = False # Hiện mặt nước sông Bạch Đằng
render_angle(Vector((-3.2, -3.8, 2.6)), Vector((0.5, 0.0, 0.5)), "anh_bai_coc_toan_canh_ngam_nuoc.png", lens=32.0)

# 10. XUẤT GLB MÔ HÌNH
bpy.ops.object.select_all(action='DESELECT')
export_list = [obj_wood, obj_iron, obj_mud] + field_objs
for o in export_list:
    o.select_set(True)
bpy.context.view_layer.objects.active = obj_wood

out_glb = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/coc_bach_dang_938.glb'
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    use_selection=True,
    export_format='GLB',
    export_apply=True,
    export_yup=True,
    export_materials='EXPORT'
)
print(f"Xuat GLB thanh cong: {out_glb} ({os.path.getsize(out_glb)/1024:.1f} KB)")
