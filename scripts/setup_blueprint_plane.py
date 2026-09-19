import bpy, math, os
from mathutils import Vector, Euler

# 1. Đường dẫn file ảnh phác thảo
img_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/references/phac_thao_thuy_binh_dai_viet_938.jpg'
if not os.path.exists(img_path):
    # Copy từ uploaded media nếu cần
    uploaded = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/.user_uploaded/media_1789787615585.png'
    if os.path.exists(uploaded):
        import shutil
        os.makedirs(os.path.dirname(img_path), exist_ok=True)
        shutil.copyfile(uploaded, img_path)

if not os.path.exists(img_path):
    raise Exception(f'Không tìm thấy ảnh phác thảo 2D tại {img_path}')

# 2. Xóa mặt phẳng cũ nếu có
plane_name = 'REFERENCE_BLUEPRINT_PLANE'
old_p = bpy.data.objects.get(plane_name)
if old_p:
    bpy.data.objects.remove(old_p, do_unlink=True)

# 3. Tạo mặt phẳng Mesh Plane tỉ lệ thực 3.2m x 1.8m
img = bpy.data.images.load(img_path, check_existing=True)
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-6.27, -44.34, 0.53))
plane = bpy.context.active_object
plane.name = plane_name
plane.scale = Vector((3.4, 1.9, 1.0))
# Xoay đứng theo góc chiếu Side View
plane.rotation_euler = Euler((math.pi / 2.0, 0, math.pi / 2.0))

# 4. Gán vật liệu bán trong suốt
mat = bpy.data.materials.new(name='Mat_Blueprint_Transparent')
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

bsdf = nodes.get('Principled BSDF')
tex_node = nodes.new('ShaderNodeTexImage')
tex_node.image = img

links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
mat.blend_method = 'BLEND'
plane.data.materials.append(mat)

# 5. Đưa vào collection của thuyền
col = bpy.data.collections.get('Export_DaiViet_Master_Full')
if col:
    if plane.name not in col.objects:
        col.objects.link(plane)
    for c in list(plane.users_collection):
        if c != col:
            c.objects.unlink(plane)

print('SUCCESS: Đã nạp REFERENCE_BLUEPRINT_PLANE vào Blender thành công!')
