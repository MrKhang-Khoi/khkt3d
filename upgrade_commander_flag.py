import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

print("=== [VIETNAM-SIM 3D] UPGRADING COMMANDER, DRUMMER, DRUM & STERN BANNER ===")

def get_or_create_pbr_mat(name, base_color, roughness=0.5, metallic=0.0, sss=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if sss > 0:
            if 'Subsurface Weight' in bsdf.inputs:
                bsdf.inputs['Subsurface Weight'].default_value = sss
            elif 'Subsurface' in bsdf.inputs:
                bsdf.inputs['Subsurface'].default_value = sss
    return mat

mat_skin   = get_or_create_pbr_mat("Mat_DaNguoi_VietCo", (0.58, 0.35, 0.22), roughness=0.45, sss=0.15)
mat_loin   = get_or_create_pbr_mat("Mat_Kho_VaiCham", (0.22, 0.16, 0.12), roughness=0.85)
mat_hair   = get_or_create_pbr_mat("Mat_Toc_Den", (0.05, 0.04, 0.04), roughness=0.7)
mat_band   = get_or_create_pbr_mat("Mat_Khan_DauRiu", (0.68, 0.12, 0.08), roughness=0.6)
mat_tunic  = get_or_create_pbr_mat("Mat_AoChen_ChiHuy", (0.18, 0.14, 0.11), roughness=0.75)
mat_bronze = get_or_create_pbr_mat("Mat_GiapHoTam_Dong", (0.75, 0.48, 0.20), roughness=0.28, metallic=0.85)
mat_sword  = get_or_create_pbr_mat("Mat_Kiem_KimLoai", (0.65, 0.68, 0.70), roughness=0.25, metallic=0.92)
mat_drum   = get_or_create_pbr_mat("Mat_TrongDong_DongSon", (0.45, 0.38, 0.24), roughness=0.35, metallic=0.78)
mat_flag   = get_or_create_pbr_mat("Mat_CoLenh_DaiViet", (0.85, 0.14, 0.08), roughness=0.6)
mat_flag_gold = get_or_create_pbr_mat("Mat_CoLenh_VangHaoKhi", (0.88, 0.68, 0.12), roughness=0.55)
mat_wood   = get_or_create_pbr_mat("Mat_GoLim_ThuyenTa", (0.16, 0.10, 0.07), roughness=0.65)

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
col_ta = bpy.data.collections.get('03_HamDoi_DaiViet_TienPhong')

# =============================================================================
# 1. TƯỚNG CHỈ HUY ĐẠI VIỆT (ATHLETIC COMMANDER)
# =============================================================================
def build_commander_mesh():
    bm = bmesh.new()
    # Slot 0: Da người (mat_skin)
    # Slot 1: Áo chẽn thắt đai (mat_tunic)
    # Slot 2: Tóc đen (mat_hair)
    # Slot 3: Khăn đỏ / Thắt lưng (mat_band)
    # Slot 4: Giáp hộ tâm đồng (mat_bronze)
    # Slot 5: Kiếm kim loại (mat_sword)
    
    # A. ĐẦU, BÚI TÓC & KHĂN ĐỎ ĐẦU RÌU (cao 1.55m - 1.70m)
    mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.58))) @ Matrix.Diagonal(Vector((0.095, 0.09, 0.115, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=1.0, matrix=mat_h)
    for f in bm.faces: f.material_index = 0
    fc = len(bm.faces)
    
    # Búi tóc củ hành phía sau gáy
    mat_hair_m = Matrix.Translation(Vector((-0.095, 0.0, 1.62))) @ Matrix.Diagonal(Vector((0.05, 0.05, 0.055, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=1.0, matrix=mat_hair_m)
    for f in bm.faces[fc:]: f.material_index = 2
    fc = len(bm.faces)
    
    # Khăn đầu rìu đỏ quấn trán
    mat_band_m = Matrix.Translation(Vector((0.0, 0.0, 1.62))) @ Matrix.Diagonal(Vector((0.105, 0.10, 0.038, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=6, radius=1.0, matrix=mat_band_m)
    for f in bm.faces[fc:]: f.material_index = 3
    fc = len(bm.faces)
    
    # Cổ
    mat_neck = Matrix.Translation(Vector((0.0, 0.0, 1.46))) @ Matrix.Diagonal(Vector((0.055, 0.055, 0.10, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=1.0, depth=1.0, matrix=mat_neck)
    for f in bm.faces[fc:]: f.material_index = 0
    fc = len(bm.faces)
    
    # B. THÂN ÁO CHẼN & GIÁP HỘ TÂM ĐỒNG TRÒN
    # Thân trên (Lồng ngực nở, áo chẽn)
    mat_chest = Matrix.Translation(Vector((0.0, 0.0, 1.25))) @ Matrix.Diagonal(Vector((0.16, 0.22, 0.32, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=1.0, matrix=mat_chest)
    for f in bm.faces[fc:]: f.material_index = 1
    fc = len(bm.faces)
    
    # Gương tròn hộ tâm đồng (Tấm đồng trước ngực)
    mat_mirror = Matrix.Translation(Vector((0.155, 0.0, 1.28))) @ Matrix.Diagonal(Vector((0.02, 0.11, 0.11, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=mat_mirror)
    for f in bm.faces[fc:]: f.material_index = 4
    fc = len(bm.faces)
    
    # Đai thắt lưng đỏ
    mat_belt = Matrix.Translation(Vector((0.0, 0.0, 1.02))) @ Matrix.Diagonal(Vector((0.165, 0.21, 0.07, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=1.0, radius2=1.0, depth=1.0, matrix=mat_belt)
    for f in bm.faces[fc:]: f.material_index = 3
    fc = len(bm.faces)
    
    # Hông và vạt áo ngắn
    mat_hips = Matrix.Translation(Vector((0.0, 0.0, 0.88))) @ Matrix.Diagonal(Vector((0.15, 0.19, 0.22, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=1.0, matrix=mat_hips)
    for f in bm.faces[fc:]: f.material_index = 1
    fc = len(bm.faces)
    
    # C. HAI CHÂN ĐỨNG VỮNG CHÃI TRÊN BOONG ĐUÔI
    for s in [-1.0, 1.0]:
        y_leg = s * 0.13
        # Đùi
        mat_thigh = Matrix.Translation(Vector((0.0, y_leg, 0.68))) @ Matrix.Diagonal(Vector((0.08, 0.08, 0.28, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.85, depth=1.0, matrix=mat_thigh)
        # Cẳng chân (quấn xà cạp nâu)
        mat_calf = Matrix.Translation(Vector((0.0, y_leg, 0.35))) @ Matrix.Diagonal(Vector((0.065, 0.065, 0.38, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.85, radius2=0.75, depth=1.0, matrix=mat_calf)
        # Bàn chân
        mat_foot = Matrix.Translation(Vector((0.04, y_leg, 0.06))) @ Matrix.Diagonal(Vector((0.11, 0.055, 0.06, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=mat_foot)
    for f in bm.faces[fc:]: f.material_index = 1
    fc = len(bm.faces)
    
    # D. TAY TRÁI CHỐNG HÔNG OAI PHONG
    mat_larm = Matrix.Translation(Vector((-0.02, -0.22, 1.22))) @ Matrix.Diagonal(Vector((0.06, 0.06, 0.22, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.85, depth=1.0, matrix=mat_larm)
    mat_lfore = Matrix.Translation(Vector((0.05, -0.20, 1.06))) @ Matrix.Diagonal(Vector((0.05, 0.14, 0.05, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.85, radius2=0.75, depth=1.0, matrix=mat_lfore)
    mat_lhand = Matrix.Translation(Vector((0.08, -0.15, 1.04))) @ Matrix.Diagonal(Vector((0.045, 0.045, 0.045, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=6, radius=1.0, matrix=mat_lhand)
    for f in bm.faces[fc:]: f.material_index = 0
    fc = len(bm.faces)
    
    # E. TAY PHẢI VUNG KIẾM CHỈ HUY HƯỚNG TIẾN CÔNG (HƯỚNG TRƯỚC +X)
    mat_rarm = Matrix.Translation(Vector((0.18, 0.18, 1.34))) @ Euler((0, math.radians(-35), math.radians(15))).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.06, 0.06, 0.25, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.85, depth=1.0, matrix=mat_rarm)
    mat_rfore = Matrix.Translation(Vector((0.36, 0.22, 1.45))) @ Euler((0, math.radians(-65), 0)).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.05, 0.05, 0.24, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.85, radius2=0.75, depth=1.0, matrix=mat_rfore)
    mat_rhand = Matrix.Translation(Vector((0.50, 0.22, 1.52))) @ Matrix.Diagonal(Vector((0.05, 0.05, 0.05, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=6, radius=1.0, matrix=mat_rhand)
    for f in bm.faces[fc:]: f.material_index = 0
    fc = len(bm.faces)
    
    # F. THANH KIẾM CHỈ HUY (Chuôi kiếm trong tay, lưỡi kiếm vươn về trước chỉ trận địa)
    # Chuôi kiếm
    mat_hilt = Matrix.Translation(Vector((0.50, 0.22, 1.50))) @ Euler((0, math.radians(-65), 0)).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.025, 0.025, 0.18, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=1.0, radius2=1.0, depth=1.0, matrix=mat_hilt)
    # Chắn tay kiếm (Crossguard)
    mat_guard = Matrix.Translation(Vector((0.56, 0.22, 1.56))) @ Euler((0, math.radians(-65), 0)).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.03, 0.12, 0.02, 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_guard)
    for f in bm.faces[fc:]: f.material_index = 4 # Đồng
    fc = len(bm.faces)
    
    # Lưỡi kiếm sắt/đồng dài 65cm sáng quắc
    mat_blade = Matrix.Translation(Vector((0.85, 0.22, 1.76))) @ Euler((0, math.radians(-65), 0)).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.02, 0.045, 0.65, 1.0)))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_blade)
    for f in bm.faces[fc:]: f.material_index = 5 # Kim loại
    
    mesh = bpy.data.meshes.new("Mesh_Archetype_Commander_Organic")
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons: p.use_smooth = True
    
    mesh.materials.append(mat_skin)   # 0
    mesh.materials.append(mat_tunic)  # 1
    mesh.materials.append(mat_hair)   # 2
    mesh.materials.append(mat_band)   # 3
    mesh.materials.append(mat_bronze) # 4
    mesh.materials.append(mat_sword)  # 5
    return mesh

# Gán cho Commander
cmd_obj = bpy.data.objects.get("Crew_Cmd_DV_01_SoaiTienPhong_Ta")
if cmd_obj:
    cmd_obj.data = build_commander_mesh()
    print("-> Đã nâng cấp Tướng chỉ huy Đại Việt sang Mesh Organic Chuẩn Sử & Multi-material!")

# =============================================================================
# 2. TRỐNG ĐỒNG ĐÔNG SƠN DÁNG THẮT LƯNG (BRONZE WAR DRUM)
# =============================================================================
def build_dongson_drum_mesh():
    bm = bmesh.new()
    # Slot 0: Đồng Đông Sơn (mat_drum)
    # Mặt trống phẳng rộng
    mat_head = Matrix.Translation(Vector((0, 0, 0.42))) @ Matrix.Diagonal(Vector((0.36, 0.36, 0.04, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=1.0, radius2=0.95, depth=1.0, matrix=mat_head)
    # Tang trên nở
    mat_upper = Matrix.Translation(Vector((0, 0, 0.32))) @ Matrix.Diagonal(Vector((0.35, 0.35, 0.16, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=16, radius1=1.0, radius2=0.82, depth=1.0, matrix=mat_upper)
    # Lưng trống thắt eo hình trụ
    mat_waist = Matrix.Translation(Vector((0, 0, 0.16))) @ Matrix.Diagonal(Vector((0.26, 0.26, 0.16, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=False, cap_tris=False, segments=16, radius1=1.0, radius2=1.0, depth=1.0, matrix=mat_waist)
    # Chân trống choãi
    mat_base = Matrix.Translation(Vector((0, 0, 0.04))) @ Matrix.Diagonal(Vector((0.33, 0.33, 0.12, 1.0)))
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.80, radius2=1.0, depth=1.0, matrix=mat_base)
    # 4 Quai trống kép (đặc trưng Đông Sơn)
    for angle in [45, 135, 225, 315]:
        rot_q = Euler((0, 0, math.radians(angle))).to_matrix().to_4x4()
        mat_handle = rot_q @ Matrix.Translation(Vector((0.30, 0, 0.26))) @ Matrix.Diagonal(Vector((0.025, 0.04, 0.14, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=mat_handle)
        
    mesh = bpy.data.meshes.new("Mesh_TrongDong_DongSon_Final")
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons: p.use_smooth = True
    mesh.materials.append(mat_drum)
    return mesh

drum_obj = bpy.data.objects.get("TrongTran_KhieuChien")
if drum_obj:
    drum_obj.data = build_dongson_drum_mesh()
    drum_obj.location = Vector((0.50, 0.0, 0.22)) # Hạ xuống ngang mặt sàn
    print("-> Đã nâng cấp Trống trận sang Trống đồng Đông Sơn dáng thắt eo chân thực!")

# =============================================================================
# 3. LÍNH ĐÁNH TRỐNG HÀO HÙNG (ATHLETIC DRUMMER)
# =============================================================================
def build_drummer_mesh():
    bm = bmesh.new()
    # Slot 0: Da người (mat_skin)
    # Slot 1: Khố vải chàm (mat_loin)
    # Slot 2: Tóc đen (mat_hair)
    # Slot 3: Khăn đỏ (mat_band)
    # Slot 4: Gỗ dùi trống (mat_wood)
    
    # Đầu & Khăn đỏ
    mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.35))) @ Matrix.Diagonal(Vector((0.09, 0.085, 0.11, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=1.0, matrix=mat_h)
    for f in bm.faces: f.material_index = 0
    fc = len(bm.faces)
    
    mat_hair_m = Matrix.Translation(Vector((-0.09, 0.0, 1.38))) @ Matrix.Diagonal(Vector((0.045, 0.045, 0.05, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=1.0, matrix=mat_hair_m)
    for f in bm.faces[fc:]: f.material_index = 2
    fc = len(bm.faces)
    
    mat_band_m = Matrix.Translation(Vector((0.0, 0.0, 1.38))) @ Matrix.Diagonal(Vector((0.10, 0.095, 0.035, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=1.0, matrix=mat_band_m)
    for f in bm.faces[fc:]: f.material_index = 3
    fc = len(bm.faces)
    
    # Thân mình trần cuồn cuộn cơ bắp
    mat_torso = Matrix.Translation(Vector((0.0, 0.0, 1.05))) @ Matrix.Diagonal(Vector((0.14, 0.20, 0.26, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=1.0, matrix=mat_torso)
    for f in bm.faces[fc:]: f.material_index = 0
    fc = len(bm.faces)
    
    # Đóng khố vải chàm
    mat_loin_m = Matrix.Translation(Vector((0.0, 0.0, 0.82))) @ Matrix.Diagonal(Vector((0.145, 0.18, 0.20, 1.0)))
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=1.0, matrix=mat_loin_m)
    for f in bm.faces[fc:]: f.material_index = 1
    fc = len(bm.faces)
    
    # Hai chân đứng tấn
    for s in [-1.0, 1.0]:
        y_leg = s * 0.14
        mat_thigh = Matrix.Translation(Vector((0.0, y_leg, 0.62))) @ Matrix.Diagonal(Vector((0.075, 0.075, 0.25, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.85, depth=1.0, matrix=mat_thigh)
        mat_calf = Matrix.Translation(Vector((0.0, y_leg, 0.32))) @ Matrix.Diagonal(Vector((0.06, 0.06, 0.32, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.85, radius2=0.75, depth=1.0, matrix=mat_calf)
        mat_foot = Matrix.Translation(Vector((0.03, y_leg, 0.06))) @ Matrix.Diagonal(Vector((0.10, 0.05, 0.06, 1.0)))
        bmesh.ops.create_cube(bm, size=1.0, matrix=mat_foot)
    for f in bm.faces[fc:]: f.material_index = 0
    fc = len(bm.faces)
    
    # Hai cánh tay vung lên giáng dùi trống xuống mặt trống
    for s in [-1.0, 1.0]:
        y_arm = s * 0.16
        # Cánh tay
        mat_uarm = Matrix.Translation(Vector((0.12, y_arm, 1.15))) @ Euler((0, math.radians(-30), math.radians(s * 15))).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.05, 0.05, 0.20, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.85, depth=1.0, matrix=mat_uarm)
        # Cẳng tay hướng xuống mặt trống
        mat_farm = Matrix.Translation(Vector((0.26, s * 0.10, 1.02))) @ Euler((0, math.radians(25), 0)).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.045, 0.045, 0.20, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.85, radius2=0.75, depth=1.0, matrix=mat_farm)
        # Bàn tay
        mat_hand = Matrix.Translation(Vector((0.34, s * 0.08, 0.88))) @ Matrix.Diagonal(Vector((0.04, 0.04, 0.04, 1.0)))
        bmesh.ops.create_uvsphere(bm, u_segments=6, v_segments=6, radius=1.0, matrix=mat_hand)
        for f in bm.faces[fc:]: f.material_index = 0
        fc = len(bm.faces)
        # Dùi trống gỗ
        mat_stick = Matrix.Translation(Vector((0.38, s * 0.08, 0.78))) @ Euler((0, math.radians(40), 0)).to_matrix().to_4x4() @ Matrix.Diagonal(Vector((0.02, 0.02, 0.26, 1.0)))
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=1.0, radius2=1.0, depth=1.0, matrix=mat_stick)
        for f in bm.faces[fc:]: f.material_index = 4 # Gỗ
        fc = len(bm.faces)
        
    mesh = bpy.data.meshes.new("Mesh_Archetype_Drummer_Organic")
    bm.to_mesh(mesh)
    bm.free()
    for p in mesh.polygons: p.use_smooth = True
    mesh.materials.append(mat_skin) # 0
    mesh.materials.append(mat_loin) # 1
    mesh.materials.append(mat_hair) # 2
    mesh.materials.append(mat_band) # 3
    mesh.materials.append(mat_wood) # 4
    return mesh

drummer_obj = bpy.data.objects.get("Linh_DanhTrong_DV01")
if drummer_obj:
    drummer_obj.data = build_drummer_mesh()
    drummer_obj.location = Vector((0.05, 0.0, 0.22)) # Đứng ngay sau trống
    print("-> Đã nâng cấp Lính đánh trống sang Nhân trắc học cơ bắp & Multi-material!")

# =============================================================================
# 4. CỜ LỆNH NGŨ HÀNH VIỀN LỬA ĐUÔI THUYỀN (STERN COMMAND BANNER)
# =============================================================================
old_stern_flag = bpy.data.objects.get("CoLenh_NguHanh_DuoiThuyen")
if old_stern_flag:
    bpy.data.objects.remove(old_stern_flag, do_unlink=True)

bm_flag = bmesh.new()
# Slot 0: Vải cờ đỏ son (mat_flag)
# Slot 1: Viền ngọn lửa vàng hào khí (mat_flag_gold)
# Slot 2: Cán cờ tre/gỗ lim (mat_wood)

# Cọc cờ cắm nghiêng 78 độ về phía sau đuôi tàu
rot_pole = Euler((0, math.radians(-12), 0)).to_matrix().to_4x4()
mat_pole = Matrix.Translation(Vector((-4.05, 0.0, 1.60))) @ rot_pole @ Matrix.Diagonal(Vector((0.04, 0.04, 2.60, 1.0)))
bmesh.ops.create_cone(bm_flag, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.8, depth=1.0, matrix=mat_pole)
for f in bm_flag.faces: f.material_index = 2
fc = len(bm_flag.faces)

# Bệ gá cọc cờ bằng gỗ lim trên sàn đuôi
mat_base = Matrix.Translation(Vector((-4.05, 0.0, 0.35))) @ Matrix.Diagonal(Vector((0.15, 0.15, 0.25, 1.0)))
bmesh.ops.create_cube(bm_flag, size=1.0, matrix=mat_base)
for f in bm_flag.faces[fc:]: f.material_index = 2
fc = len(bm_flag.faces)

# Thân lá cờ chữ nhật uốn lượn hình sóng gió (Wave displacement)
flag_w = 0.90 # Dài 90cm
flag_h = 1.25 # Cao 125cm
z_top = 2.70
nx = 8
nz = 8
verts_grid = []
for iz in range(nz + 1):
    row = []
    frac_z = iz / nz
    curr_z = z_top - frac_z * flag_h
    for ix in range(nx + 1):
        frac_x = ix / nx
        # Bay về phía sau (-X) theo hướng gió
        curr_x = -4.05 - frac_x * flag_w
        # Độ lượn sóng Y
        wave_y = 0.06 * math.sin(frac_x * math.pi * 2.5) * (0.2 + 0.8 * frac_x)
        v = bm_flag.verts.new((curr_x, wave_y, curr_z))
        row.append(v)
    verts_grid.append(row)

for iz in range(nz):
    for ix in range(nx):
        f = bm_flag.faces.new((verts_grid[iz][ix], verts_grid[iz+1][ix], verts_grid[iz+1][ix+1], verts_grid[iz][ix+1]))
        f.material_index = 0 # Đỏ son
fc = len(bm_flag.faces)

# Viền răng cưa ngọn lửa (Flaming teeth) ở 3 mép ngoài (trên, dưới, mép sau)
# Răng cưa mép sau
for iz in range(nz):
    v1 = verts_grid[iz][nx]
    v2 = verts_grid[iz+1][nx]
    v_mid_z = (v1.co.z + v2.co.z) * 0.5
    # Đỉnh răng cưa nhọn thò ra ngoài 15cm
    tip_x = v1.co.x - 0.15
    tip_y = (v1.co.y + v2.co.y) * 0.5
    v_tip = bm_flag.verts.new((tip_x, tip_y, v_mid_z))
    f = bm_flag.faces.new((v1, v2, v_tip))
    f.material_index = 1 # Vàng ngọn lửa

mesh_flag_final = bpy.data.meshes.new("Mesh_CoLenh_NguHanh_DuoiThuyen")
bm_flag.to_mesh(mesh_flag_final)
bm_flag.free()
for p in mesh_flag_final.polygons: p.use_smooth = True
mesh_flag_final.materials.append(mat_flag)      # 0: Đỏ son
mesh_flag_final.materials.append(mat_flag_gold) # 1: Viền lửa vàng
mesh_flag_final.materials.append(mat_wood)      # 2: Cán tre

obj_flag = bpy.data.objects.new("CoLenh_NguHanh_DuoiThuyen", mesh_flag_final)
obj_flag.parent = master_ta_root
if col_ta:
    col_ta.objects.link(obj_flag)
print("-> Đã dựng Cờ lệnh Ngũ Hành viền ngọn lửa cắm vững chãi ở đuôi thuyền!")

print("=== [VIETNAM-SIM 3D] HOÀN TẤT NÂNG CẤP TOÀN BỘ 4 THÀNH PHẦN! ===")
