import bpy

prow = bpy.data.objects.get('Mui_ChimLac_DongSon')
if prow:
    verts = [v.co for v in prow.data.vertices]
    print(f"Prow mesh X range: {min(v.x for v in verts):.2f} to {max(v.x for v in verts):.2f}")
    print(f"Prow mesh Y range: {min(v.y for v in verts):.2f} to {max(v.y for v in verts):.2f}")
    print(f"Prow mesh Z range: {min(v.z for v in verts):.2f} to {max(v.z for v in verts):.2f}")
