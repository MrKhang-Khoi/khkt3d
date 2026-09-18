import bpy

leaves = bpy.data.objects.get('Cay_SuVet_Leaves_1')
if leaves:
    print("Leaves type:", leaves.type)
    print("Leaves materials:", [m.name for m in leaves.data.materials if m])
    print("Leaves hide_viewport:", leaves.hide_viewport)
    print("Leaves hide_render:", leaves.hide_render)
    if leaves.type == 'CURVE':
        print("Curve bevel_depth:", leaves.data.bevel_depth)
        print("Curve dimensions:", leaves.data.dimensions)
    elif leaves.type == 'MESH':
        print("Mesh verts:", len(leaves.data.vertices), "polys:", len(leaves.data.polygons))

mount = bpy.data.objects.get('DayNui_Karst_TrangKenh_Chinh')
if mount:
    print("Mount bbox Z range:", [v[2] for v in mount.bound_box])
    print("Mount scale:", mount.scale)
    print("Mount loc:", mount.location)
