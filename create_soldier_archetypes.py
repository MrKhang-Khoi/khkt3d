import bpy
import bmesh
import math
from mathutils import Vector, Matrix

print("=== [VIETNAM-SIM MASTER] TẠO NGUYÊN MẪU QUÂN LÍNH 3D CHUẨN SỬ TỐI ƯU WEBGL ===")

# Xóa các mesh lính cũ nếu có
for ob in list(bpy.data.objects):
    if ob.name.startswith("Archetype_") or ob.name.startswith("Crew_"):
        bpy.data.objects.remove(ob, do_unlink=True)

col_ta = bpy.data.collections.get('03_HamDoi_DaiViet_TienPhong')
col_dich = bpy.data.collections.get('04_HamDoi_NamHan_DaiHamDoi')

# 1. NGUYÊN MẪU 1: TAY CHÈO ĐẠI VIỆT (SEATED ROWER)
# Chiều cao ngồi ~0.95m (người thật 1.65m), đầu quấn khăn đỏ, mình trần đóng khố
bm = bmesh.new()
# Đầu
mat_head = Matrix.Translation(Vector((0.0, 0.0, 0.85))) @ Matrix.Diagonal(Vector((0.13, 0.12, 0.14, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_head)
# Khăn quấn đầu đỏ
mat_band = Matrix.Translation(Vector((0.0, 0.0, 0.90))) @ Matrix.Diagonal(Vector((0.14, 0.13, 0.06, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_band)
# Thân mình trần
mat_torso = Matrix.Translation(Vector((0.0, 0.0, 0.55))) @ Matrix.Diagonal(Vector((0.26, 0.18, 0.38, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_torso)
# Khố vải chàm
mat_loincl = Matrix.Translation(Vector((0.0, 0.0, 0.28))) @ Matrix.Diagonal(Vector((0.28, 0.20, 0.20, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_loincl)
# Hai tay vươn ra cầm chèo
mat_arm_l = Matrix.Translation(Vector((0.15, -0.16, 0.45))) @ Matrix.Diagonal(Vector((0.28, 0.08, 0.08, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_arm_l)
mat_arm_r = Matrix.Translation(Vector((0.15, 0.16, 0.45))) @ Matrix.Diagonal(Vector((0.28, 0.08, 0.08, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_arm_r)
# Đùi ngồi gập
mat_leg_l = Matrix.Translation(Vector((0.16, -0.10, 0.18))) @ Matrix.Diagonal(Vector((0.26, 0.10, 0.12, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_leg_l)
mat_leg_r = Matrix.Translation(Vector((0.16, 0.10, 0.18))) @ Matrix.Diagonal(Vector((0.26, 0.10, 0.12, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_leg_r)

mesh_rower = bpy.data.meshes.new("Mesh_Archetype_Rower_DaiViet")
bm.to_mesh(mesh_rower)
bm.free()

# 2. NGUYÊN MẪU 2: TƯỚNG CHỈ HUY ĐẠI VIỆT (STANDING COMMANDER)
# Đứng thẳng 1.68m, giáp hộ tâm đồng, áo chẽn, tay vung kiếm chỉ huy
bm = bmesh.new()
# Đầu & búi tó
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.58))) @ Matrix.Diagonal(Vector((0.14, 0.13, 0.15, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_topknot = Matrix.Translation(Vector((-0.04, 0.0, 1.68))) @ Matrix.Diagonal(Vector((0.08, 0.08, 0.09, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_topknot)
# Thân & Giáp hộ tâm đồng
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.32, 0.22, 0.50, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
# Tấm gương tròn hộ tâm trước ngực
mat_mirror = Matrix.Translation(Vector((0.17, 0.0, 1.25))) @ Matrix.Diagonal(Vector((0.04, 0.16, 0.16, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_mirror)
# Đai thắt lưng đỏ
mat_belt = Matrix.Translation(Vector((0.0, 0.0, 0.88))) @ Matrix.Diagonal(Vector((0.34, 0.24, 0.10, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_belt)
# Chân đứng vững chãi
mat_ll = Matrix.Translation(Vector((0.0, -0.12, 0.44))) @ Matrix.Diagonal(Vector((0.14, 0.14, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.12, 0.44))) @ Matrix.Diagonal(Vector((0.14, 0.14, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
# Tay phải giơ kiếm chỉ huy
mat_arm = Matrix.Translation(Vector((0.30, 0.18, 1.40))) @ Matrix.Diagonal(Vector((0.45, 0.09, 0.09, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_arm)
# Lưỡi kiếm sắt
mat_blade = Matrix.Translation(Vector((0.65, 0.18, 1.55))) @ Matrix.Diagonal(Vector((0.55, 0.04, 0.08, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_blade)

mesh_cmd = bpy.data.meshes.new("Mesh_Archetype_Commander_DaiViet")
bm.to_mesh(mesh_cmd)
bm.free()

# 3. NGUYÊN MẪU 3: LÍNH ĐÁNH TRỐNG ĐẠI VIỆT (DRUMMER)
bm = bmesh.new()
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.55))) @ Matrix.Diagonal(Vector((0.13, 0.12, 0.14, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.28, 0.20, 0.48, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
mat_ll = Matrix.Translation(Vector((0.0, -0.11, 0.44))) @ Matrix.Diagonal(Vector((0.13, 0.13, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.11, 0.44))) @ Matrix.Diagonal(Vector((0.13, 0.13, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
# Hai tay cầm dùi gióng trống
mat_d_l = Matrix.Translation(Vector((0.22, -0.15, 1.25))) @ Matrix.Diagonal(Vector((0.25, 0.07, 0.07, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_d_l)
mat_d_r = Matrix.Translation(Vector((0.22, 0.15, 1.25))) @ Matrix.Diagonal(Vector((0.25, 0.07, 0.07, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_d_r)

mesh_drummer = bpy.data.meshes.new("Mesh_Archetype_Drummer_DaiViet")
bm.to_mesh(mesh_drummer)
bm.free()

# 4. NGUYÊN MẪU 4: LÍNH THỦY NAM HÁN GIÁP SẮT (ARMORED HAN SOLDIER)
# Mũ trụ sắt có chóp, áo giáp vảy cá Ngũ Đại, tay cầm kích dài 2.2m
bm = bmesh.new()
# Mũ trụ có chóp
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.62))) @ Matrix.Diagonal(Vector((0.15, 0.15, 0.16, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_spike = Matrix.Translation(Vector((0.0, 0.0, 1.76))) @ Matrix.Diagonal(Vector((0.04, 0.04, 0.14, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_spike)
# Giáp sắt thời Ngũ Đại
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.34, 0.24, 0.55, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
mat_ll = Matrix.Translation(Vector((0.0, -0.12, 0.44))) @ Matrix.Diagonal(Vector((0.15, 0.15, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.12, 0.44))) @ Matrix.Diagonal(Vector((0.15, 0.15, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
# Cầm cây kích dài (thương 3 ngạnh)
mat_spear = Matrix.Translation(Vector((0.25, 0.18, 1.10))) @ Matrix.Diagonal(Vector((0.04, 0.04, 2.20, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_spear)
mat_tip = Matrix.Translation(Vector((0.25, 0.18, 2.25))) @ Matrix.Diagonal(Vector((0.08, 0.02, 0.30, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_tip)

mesh_han_soldier = bpy.data.meshes.new("Mesh_Archetype_Soldier_NamHan")
bm.to_mesh(mesh_han_soldier)
bm.free()

# 5. NGUYÊN MẪU 5: TƯỚNG QUÂN LƯU HOẰNG THÁO (GRAND COMMANDER HOANG THAO)
bm = bmesh.new()
# Mũ trụ tướng quân có lông vũ đỏ
mat_h = Matrix.Translation(Vector((0.0, 0.0, 1.65))) @ Matrix.Diagonal(Vector((0.16, 0.16, 0.18, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_h)
mat_plume = Matrix.Translation(Vector((-0.05, 0.0, 1.82))) @ Matrix.Diagonal(Vector((0.06, 0.06, 0.18, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_plume)
# Cẩm bào hoàng kim & giáp tướng
mat_t = Matrix.Translation(Vector((0.0, 0.0, 1.15))) @ Matrix.Diagonal(Vector((0.36, 0.26, 0.60, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_t)
# Áo choàng đỏ sau lưng
mat_cape = Matrix.Translation(Vector((-0.18, 0.0, 0.95))) @ Matrix.Diagonal(Vector((0.05, 0.35, 0.85, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_cape)
mat_ll = Matrix.Translation(Vector((0.0, -0.14, 0.44))) @ Matrix.Diagonal(Vector((0.16, 0.16, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_ll)
mat_lr = Matrix.Translation(Vector((0.0, 0.14, 0.44))) @ Matrix.Diagonal(Vector((0.16, 0.16, 0.82, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_lr)
# Hai tay chống trường kiếm uy phong
mat_sword = Matrix.Translation(Vector((0.28, 0.0, 0.65))) @ Matrix.Diagonal(Vector((0.05, 0.05, 1.30, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_sword)

mesh_hoangthao = bpy.data.meshes.new("Mesh_Archetype_LuuHoangThao")
bm.to_mesh(mesh_hoangthao)
bm.free()

# GÁN VẬT LIỆU CHO CÁC MESH
mat_da = bpy.data.materials.get("Mat_DaNguoi_VietCo")
mat_giap = bpy.data.materials.get("Mat_GiapHoTam_Dong")
mat_han = bpy.data.materials.get("Mat_GiapSat_NamHan")
mat_ht = bpy.data.materials.get("Mat_CamBao_HoangThao")

mesh_rower.materials.append(mat_da)
mesh_cmd.materials.append(mat_giap)
mesh_drummer.materials.append(mat_da)
mesh_han_soldier.materials.append(mat_han)
mesh_hoangthao.materials.append(mat_ht)

print("-> Tạo xong 5 bộ Mesh Archetype chuẩn sử và tối ưu hóa WebGL!")