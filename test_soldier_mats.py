import bpy
import bmesh
import math
from mathutils import Vector, Matrix

print("=== [VIETNAM-SIM MASTER] THIẾT KẾ BỘ THƯ VIỆN NGUYÊN MẪU QUÂN LÍNH PBR TỐI ƯU WEBGL ===")

# Tạo collection chứa lính mẫu
col_soldier = bpy.data.collections.get("06_QuanLinh_BinhSi") or bpy.data.collections.new("06_QuanLinh_BinhSi")
if col_soldier.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col_soldier)

# 1. VẬT LIỆU CHUẨN LỊCH SỬ THẾ KỶ 10 (PBR ĐỒNG BỘ WEBGL)
def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

mat_da_viet = get_or_create_mat("Mat_DaNguoi_VietCo", (0.72, 0.48, 0.32), 0.0, 0.65) # Da rám nắng sông nước
mat_kho_cham = get_or_create_mat("Mat_KhoVai_ChamNau", (0.16, 0.11, 0.08), 0.0, 0.80) # Khố vải chàm
mat_khan_do = get_or_create_mat("Mat_KhanQuan_DoSon", (0.82, 0.12, 0.08), 0.0, 0.60) # Khăn quấn đầu đỏ
mat_giap_dong = get_or_create_mat("Mat_GiapHoTam_Dong", (0.55, 0.35, 0.14), 0.7, 0.35) # Giáp hộ tâm đồng
mat_kiem_sat = get_or_create_mat("Mat_VuKhi_SatThep", (0.35, 0.36, 0.38), 0.85, 0.25) # Gươm kiếm sắt

mat_giap_namhan = get_or_create_mat("Mat_GiapSat_NamHan", (0.22, 0.23, 0.25), 0.8, 0.30) # Giáp sắt Ngũ Đại
mat_mu_namhan = get_or_create_mat("Mat_MuTru_NamHan", (0.30, 0.31, 0.34), 0.85, 0.25) # Mũ trụ chóp sắt
mat_bao_hoangthao = get_or_create_mat("Mat_CamBao_HoangThao", (0.75, 0.58, 0.12), 0.4, 0.40) # Cẩm bào vàng tướng soái

print("-> Khởi tạo bộ vật liệu binh lính chuẩn sử hoàn tất!")