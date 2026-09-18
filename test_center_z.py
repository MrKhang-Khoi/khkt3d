import bpy

for o in list(bpy.context.scene.objects):
    if 'Test' in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

# Generate with height_invert = False vs True
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Test_Norm',
    mesh_size_x=20.0,
    mesh_size_y=20.0,
    subdivision_x=32,
    subdivision_y=32,
    noise_type='ridged_multi_fractal',
    basis_type='BLENDER',
    vl_basis_type='VORONOI_F2F1',
    distortion=1.0,
    noise_depth=8,
    offset=0.88,
    gain=4.2,
    height=0.5,
    height_invert=False,
    edge_falloff='3',
    falloff_x=4.0,
    falloff_y=4.0,
    refresh=True
)
ob = bpy.context.active_object
zs = [v.co.z for v in ob.data.vertices]
center_v = min(ob.data.vertices, key=lambda v: v.co.x**2 + v.co.y**2)
edge_v = max(ob.data.vertices, key=lambda v: v.co.x**2 + v.co.y**2)
print(f"Center Z: {center_v.co.z:.3f}, Edge Z: {edge_v.co.z:.3f}, Min Z: {min(zs):.3f}, Max Z: {max(zs):.3f}")
