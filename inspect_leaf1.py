import bpy

leaf1 = bpy.data.objects.get('Cay_SuVet_La_1')
if leaf1:
    print("Leaf1 type:", leaf1.type)
    print("Leaf1 loc:", leaf1.location)
    print("Leaf1 scale:", leaf1.scale)
    print("Leaf1 mat:", [m.name for m in leaf1.data.materials if m])
    if leaf1.type == 'MESH':
        print("Leaf1 verts:", len(leaf1.data.vertices), "polys:", len(leaf1.data.polygons))
        # check vertex positions
        zs = [v.co.z for v in leaf1.data.vertices]
        print(f"Leaf1 local Z range: {min(zs):.2f} to {max(zs):.2f}")
