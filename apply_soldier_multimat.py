import bpy
import bmesh
import math
from mathutils import Vector, Matrix

print("=== GÁN MULTI-MATERIAL CHO QUÂN LÍNH ĐẠI VIỆT VÀ NAM HÁN ===")

# 1. BẢNG VẬT LIỆU
def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.6):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

mat_da = get_or_create_mat("Mat_DaNguoi_VietCo", (0.58, 0.36, 0.22), 0.0, 0.65) # Da rám nắng đậm
mat_kho = get_or_create_mat("Mat_KhoVai_ChamNau", (0.10, 0.07, 0.05), 0.0, 0.85) # Khố vải nâu sẫm
mat_khan = get_or_create_mat("Mat_KhanQuan_DoSon", (0.85, 0.12, 0.08), 0.0, 0.50) # Khăn đỏ rực
mat_giap = get_or_create_mat("Mat_GiapHoTam_Dong", (0.65, 0.38, 0.12), 0.75, 0.30) # Giáp đồng vàng ánh đỏ
mat_kiem = get_or_create_mat("Mat_VuKhi_SatThep", (0.35, 0.36, 0.38), 0.90, 0.20) # Gươm sắt sáng

mesh_rower = bpy.data.meshes.get("Mesh_Archetype_Rower_DaiViet")
if mesh_rower:
    # Xóa materials cũ
    mesh_rower.materials.clear()
    mesh_rower.materials.append(mat_da)   # Index 0: Da người
    mesh_rower.materials.append(mat_khan) # Index 1: Khăn đỏ
    mesh_rower.materials.append(mat_kho)  # Index 2: Khố nâu
    
    # Gán material index theo cao độ Z của từng mặt (face)
    for poly in mesh_rower.polygons:
        z_center = sum((mesh_rower.vertices[v].co.z for v in poly.vertices)) / len(poly.vertices)
        if z_center >= 0.89:
            poly.material_index = 1 # Khăn đỏ
        elif z_center <= 0.32:
            poly.material_index = 2 # Khố vải nâu
        else:
            poly.material_index = 0 # Da mình trần

mesh_cmd = bpy.data.meshes.get("Mesh_Archetype_Commander_DaiViet")
if mesh_cmd:
    mesh_cmd.materials.clear()
    mesh_cmd.materials.append(mat_giap)  # Index 0: Giáp đồng
    mesh_cmd.materials.append(mat_khan)  # Index 1: Khăn & đai đỏ
    mesh_cmd.materials.append(mat_kiem)  # Index 2: Gươm sắt
    mesh_cmd.materials.append(mat_da)    # Index 3: Da mặt
    
    for poly in mesh_cmd.polygons:
        zc = sum((mesh_cmd.vertices[v].co.z for v in poly.vertices)) / len(poly.vertices)
        xc = sum((mesh_cmd.vertices[v].co.x for v in poly.vertices)) / len(poly.vertices)
        if zc >= 1.50:
            poly.material_index = 3 # Mặt
        elif xc >= 0.40 and zc >= 1.40:
            poly.material_index = 2 # Lưỡi gươm sắt
        elif zc <= 0.95 and zc >= 0.82:
            poly.material_index = 1 # Đai đỏ
        else:
            poly.material_index = 0 # Giáp đồng

print("-> Gán Multi-Material thành công!")