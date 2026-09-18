import bpy
import math

# Clear test objects
for o in list(bpy.context.scene.objects):
    if 'Test' in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.mesh.landscape_add(
    ant_terrain_name='Test_Karst_TrangKenh',
    mesh_size_x=65.0,
    mesh_size_y=240.0,
    subdivision_x=100,
    subdivision_y=140,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=0.8,
    noise_depth=8,
    offset=0.85,
    gain=3.5,
    height=22.0,
    edge_falloff='1',
    falloff_x=6.0,
    falloff_y=6.0,
    smooth_mesh=True,
    refresh=True
)

ob = bpy.context.active_object
ob.location = (-55.0, 0.0, 0.0)
zs = [v.co.z for v in ob.data.vertices]
print(f"Mountain test: min_z={min(zs):.2f}, max_z={max(zs):.2f}, dim={ob.dimensions}")
