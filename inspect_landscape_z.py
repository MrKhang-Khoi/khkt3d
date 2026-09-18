import bpy

m1 = bpy.data.objects.get('DayNui_Karst_TrangKenh_Chinh')
m2 = bpy.data.objects.get('DayNui_Karst_HauCanh_Bac')

for m in [m1, m2]:
    if m:
        mesh = m.data
        zs = [v.co.z for v in mesh.vertices]
        print(f"{m.name}: min_z={min(zs):.3f}, max_z={max(zs):.3f}, scale={m.scale}, rot={m.rotation_euler}")
