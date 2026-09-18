import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import shutil

# 1. Hạ tướng chỉ huy xuống sàn boong đuôi
cmd = bpy.data.objects.get("Crew_Cmd_DV_01_SoaiTienPhong_Ta")
if cmd:
    cmd.location = Vector((-3.6, 0.0, 0.20)) # Chân tiếp xúc hoàn hảo với sàn gỗ

# 2. Làm lại Cờ lệnh Ngũ hành chuẩn vật liệu và hình dáng
flag_obj = bpy.data.objects.get("CoLenh_NguHanh_DuoiThuyen")
if flag_obj:
    bpy.data.objects.remove(flag_obj, do_unlink=True)

mat_flag      = bpy.data.materials.get("Mat_CoLenh_DaiViet")
mat_flag_gold = bpy.data.materials.get("Mat_CoLenh_VangHaoKhi")
mat_wood      = bpy.data.materials.get("Mat_GoLim_ThuyenTa")

bm = bmesh.new()

# Cọc cờ cắm nghiêng 76 độ về sau
rot_pole = Euler((0, math.radians(-14), 0)).to_matrix().to_4x4()
mat_pole = Matrix.Translation(Vector((-4.10, 0.0, 1.45))) @ rot_pole @ Matrix.Diagonal(Vector((0.035, 0.035, 2.50, 1.0)))
bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=1.0, radius2=0.8, depth=1.0, matrix=mat_pole)

# Bệ gá cọc cờ bằng gỗ lim
mat_base = Matrix.Translation(Vector((-4.10, 0.0, 0.28))) @ Matrix.Diagonal(Vector((0.14, 0.14, 0.18, 1.0)))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_base)

# Gán toàn bộ cọc và bệ vào Slot 2 (Gỗ lim)
for f in bm.faces:
    f.material_index = 2
fc_wood = len(bm.faces)

# Thân lá cờ chữ nhật uốn lượn hình sóng
flag_w = 0.95
flag_h = 1.30
z_top = 2.65
nx = 8
nz = 8
verts_grid = []
for iz in range(nz + 1):
    row = []
    frac_z = iz / nz
    curr_z = z_top - frac_z * flag_h
    for ix in range(nx + 1):
        frac_x = ix / nx
        curr_x = -4.10 - frac_x * flag_w
        wave_y = 0.08 * math.sin(frac_x * math.pi * 2.2) * (0.2 + 0.8 * frac_x)
        v = bm.verts.new((curr_x, wave_y, curr_z))
        row.append(v)
    verts_grid.append(row)

for iz in range(nz):
    for ix in range(nx):
        f = bm.faces.new((verts_grid[iz][ix], verts_grid[iz+1][ix], verts_grid[iz+1][ix+1], verts_grid[iz][ix+1]))
        f.material_index = 0 # Đỏ son

# Viền răng cưa ngọn lửa (Slot 1: Vàng)
for iz in range(nz):
    v1 = verts_grid[iz][nx]
    v2 = verts_grid[iz+1][nx]
    v_mid_z = (v1.co.z + v2.co.z) * 0.5
    tip_x = v1.co.x - 0.16
    tip_y = (v1.co.y + v2.co.y) * 0.5
    v_tip = bm.verts.new((tip_x, tip_y, v_mid_z))
    f = bm.faces.new((v1, v2, v_tip))
    f.material_index = 1 # Vàng ngọn lửa

mesh_flag = bpy.data.meshes.new("Mesh_CoLenh_NguHanh_Fixed")
bm.to_mesh(mesh_flag)
bm.free()
for p in mesh_flag.polygons:
    p.use_smooth = True
mesh_flag.materials.append(mat_flag)      # 0
mesh_flag.materials.append(mat_flag_gold) # 1
mesh_flag.materials.append(mat_wood)      # 2

master_ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
col_ta = bpy.data.collections.get('03_HamDoi_DaiViet_TienPhong')
new_flag = bpy.data.objects.new("CoLenh_NguHanh_DuoiThuyen", mesh_flag)
new_flag.parent = master_ta_root
if col_ta:
    col_ta.objects.link(new_flag)

# 3. Chỉnh camera góc nhìn tướng chỉ huy bao quát (Hero Stern View)
cam_stern = bpy.data.objects.get("Camera_Stern_DV01")
root = bpy.data.objects.get("Root_DV_01_SoaiTienPhong_Ta")
ship_pos = root.location if root else Vector((0,0,0))

# Đặt camera lùi xa hơn một chút và cao hơn để thấy trọn vẹn tướng và cờ
cam_stern.location = ship_pos + Vector((-8.2, 4.2, 2.9))
target = ship_pos + Vector((-3.6, 0.0, 1.4))
direction = target - cam_stern.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_stern.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam_stern
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
out_path = r'c:\Users\HPZBook\Desktop\TEST_BLENDER\anh_blender_cancanh_commander.png'
scene.render.filepath = out_path
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

bpy.ops.render.render(write_still=True)
art_path = r'C:\Users\HPZBook\.gemini\antigravity\brain\ae5a66d4-efdc-45cf-bd26-8edf0045f51c\anh_blender_cancanh_commander.png'
shutil.copyfile(out_path, art_path)
print("-> Re-rendered commander shot successfully!")
