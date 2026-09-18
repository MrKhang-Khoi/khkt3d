import bpy

print("Testing landscape operator...")
try:
    bpy.ops.mesh.landscape_add(
        ant_terrain_name="Test_Landscape",
        mesh_size_x=20.0,
        mesh_size_y=20.0,
        subdivision_x=32,
        subdivision_y=32,
        refresh=True
    )
    print("SUCCESS: landscape_add works!")
    ob = bpy.context.active_object
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)
except Exception as e:
    print("ERROR landscape_add:", e)

print("Testing tree operator...")
try:
    bpy.ops.curve.tree_add(
        do_update=True,
        bevel=True,
        showLeaves=True,
        levels=2,
        scale=1.5
    )
    print("SUCCESS: tree_add works!")
    for name in ['tree', 'leaves']:
        ob = bpy.data.objects.get(name)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
except Exception as e:
    print("ERROR tree_add:", e)
