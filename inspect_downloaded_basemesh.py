import execute_in_blender

res = execute_in_blender.run_code_in_blender("""
import bpy

# Tạo một scene mới tạm thời để inspect
test_scene = bpy.data.scenes.new("Scene_Inspect_BaseMesh")
old_scene = bpy.context.window.scene
bpy.context.window.scene = test_scene

glb_path = r"c:\\Users\\HPZBook\\Desktop\\TEST_BLENDER\\assets\\characters\\male_base_mesh.glb"
bpy.ops.import_scene.gltf(filepath=glb_path)

print("=== INSPECT MALE BASE MESH ===")
armatures = [o for o in test_scene.objects if o.type == 'ARMATURE']
meshes = [o for o in test_scene.objects if o.type == 'MESH']
print("Armatures count:", len(armatures))
for a in armatures:
    print(f"  Armature: {a.name}, Bones count: {len(a.data.bones)}")
    bone_names = [b.name for b in a.data.bones]
    print(f"  Bones sample: {bone_names[:15]}")
    # Kiểm tra xương ngón tay
    finger_bones = [b for b in bone_names if any(k in b.lower() for k in ['finger', 'thumb', 'index', 'hand', 'arm'])]
    print(f"  Hand/Arm bones: {finger_bones}")

print("Meshes count:", len(meshes))
for m in meshes:
    verts = len(m.data.vertices)
    polys = len(m.data.polygons)
    print(f"  Mesh: {m.name}, Verts: {verts}, Polys: {polys}")
    # Kích thước
    dim = m.dimensions
    print(f"  Dimensions: X={dim.x:.2f}m, Y={dim.y:.2f}m, Z={dim.z:.2f}m")

# Quay lại scene cũ và xóa test scene
bpy.context.window.scene = old_scene
bpy.data.scenes.remove(test_scene)
""")

print("STATUS:", res.get("status"))
print("OUTPUT:\n", res.get("result", {}).get("result"))
print("ERROR:\n", res.get("message"))
