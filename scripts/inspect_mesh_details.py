import bpy
obj = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
if obj:
    print("Mesh modifiers:", [m.name for m in obj.modifiers])
    print("Vertex groups:", len(obj.vertex_groups))
    bb = [tuple(round(v, 2) for v in c) for c in obj.bound_box]
    print("Bound box:", bb)
