import bpy

hull = bpy.data.objects.get('NamHan_Hull')
if hull:
    verts = [v.co for v in hull.data.vertices]
    print(f"NamHan Hull X range: {min(v.x for v in verts):.2f} to {max(v.x for v in verts):.2f}")
    print(f"NamHan Hull Y range: {min(v.y for v in verts):.2f} to {max(v.y for v in verts):.2f}")
    print(f"NamHan Hull Z range: {min(v.z for v in verts):.2f} to {max(v.z for v in verts):.2f}")

flag = bpy.data.objects.get('NamHan_CoSoai_VaiSong')
if flag:
    print(f"NamHan Flag loc: {flag.location}")

ch_nu = bpy.data.objects.get('NamHan_SangNo_ChuangNu')
if ch_nu:
    print(f"NamHan ChuangNu (crossbow) loc: {ch_nu.location}")
