import bpy

ta_cheo = bpy.data.objects.get("Mai_Cheo_Thuyen")
if ta_cheo:
    print(f"Ta Cheo Loc: {ta_cheo.location}, Rot: {ta_cheo.rotation_euler}, Scale: {ta_cheo.scale}")

han_cheo = bpy.data.objects.get("NamHan_24MaiCheo_HangNang")
if han_cheo:
    print(f"Han Cheo Loc: {han_cheo.location}, Rot: {han_cheo.rotation_euler}, Scale: {han_cheo.scale}")