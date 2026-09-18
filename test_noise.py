import bpy

# Test different noise types
bpy.ops.mesh.landscape_add(
    ant_terrain_name='Test_Mount',
    mesh_size_x=20.0,
    mesh_size_y=20.0,
    subdivision_x=32,
    subdivision_y=32,
    noise_type='multi_fractal',
    basis_type='PERLIN',
    refresh=True
)
ob = bpy.context.active_object
zs = [v.co.z for v in ob.data.vertices]
print(f"Test_Mount: min_z={min(zs):.3f}, max_z={max(zs):.3f}")
bpy.data.objects.remove(ob, do_unlink=True)
