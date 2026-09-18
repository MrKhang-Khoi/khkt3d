import bpy

print("--- DANH SACH MAI CHEO THUYEN TA ---")
for ob in bpy.data.objects:
    if "Ta" in ob.name and ("Cheo" in ob.name or "Mai" in ob.name or "Oar" in ob.name):
        print(f"Ta Oar: {ob.name}, Type: {ob.type}")
    if "Thuyen_Chien_NgoQuyen" in ob.name:
        for c in ob.children_recursive:
            if "Cheo" in c.name or "Mai" in c.name or "Oar" in c.name:
                print(f"Master Ta Oar: {c.name}")

print("--- DANH SACH MAI CHEO THUYEN NAM HAN ---")
for ob in bpy.data.objects:
    if ("LauThuyen" in ob.name or "NamHan" in ob.name or "Dich" in ob.name) and ("Cheo" in ob.name or "Mai" in ob.name or "Oar" in ob.name):
        print(f"Dich Oar: {ob.name}, Type: {ob.type}")
    if "LauThuyen_NamHan_HoangThao_Master" in ob.name:
        for c in ob.children_recursive:
            if "Cheo" in c.name or "Mai" in c.name or "Oar" in c.name:
                print(f"Master Dich Oar: {c.name}")