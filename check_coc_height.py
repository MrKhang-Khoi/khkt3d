import bpy

print("--- KIEM TRA DO CAO COC TRONG CANH ---")
z_max = -999
highest_coc = None
for ob in bpy.data.objects:
    if 'Coc' in ob.name and ob.type == 'MESH':
        bb = [ob.matrix_world @ v.co for v in ob.data.vertices]
        if bb:
            top_z = max(v.z for v in bb)
            if top_z > z_max:
                z_max = top_z
                highest_coc = ob.name
print(f"Dinh coc cao nhat: {highest_coc} o do cao Z = {z_max:.2f} m")
print(f"Mat nuoc o do cao Z = {bpy.data.objects['MatNuoc_SongBachDang_Chinh'].location.z:.2f} m")