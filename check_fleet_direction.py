import bpy
from mathutils import Vector

print("=== KIEM TRA DINH HUONG CHI TIET HAM DOI ===")

scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()

# 1. KIEM TRA THUYEN DAI VIET
print("\n--- 1. DAI VIET LEAD SHIP (Thuyen_Chien_NgoQuyen_938) ---")
ta_root = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
if ta_root:
    print(f"Parent Root: {ta_root.parent.name if ta_root.parent else 'None'}, Loc: {ta_root.parent.location if ta_root.parent else ta_root.location}")
    for child in ta_root.children:
        if any(k in child.name for k in ['Mui', 'Duoi', 'Lai', 'Than']):
            mw = child.matrix_world.translation
            print(f"  Child: {child.name} -> World Pos: ({mw.x:.2f}, {mw.y:.2f}, {mw.z:.2f})")

# 2. KIEM TRA THUYEN NAM HAN
print("\n--- 2. NAM HAN LEAD SHIP & SOAI HAM ---")
soai_ham = bpy.data.objects.get('LauThuyen_NamHan_HoangThao_Master')
if soai_ham:
    print(f"Soai Ham Root: {soai_ham.parent.name if soai_ham.parent else 'None'}, Loc: {soai_ham.parent.location if soai_ham.parent else soai_ham.location}")
    for child in soai_ham.children:
        if any(k in child.name for k in ['Mui', 'Duoi', 'Cot', 'Lau']):
            mw = child.matrix_world.translation
            print(f"  Child: {child.name} -> World Pos: ({mw.x:.2f}, {mw.y:.2f}, {mw.z:.2f})")

# 3. KIEM TRA TOAN BO DANH SACH THUYEN & ROLL ANGLE
print("\n--- 3. DANH SACH 8 THUYEN DAI VIET ---")
for ob in bpy.data.objects:
    if ob.name.startswith("Root_DV_"):
        print(f"  {ob.name}: Loc = ({ob.location.x:.1f}, {ob.location.y:.1f}, {ob.location.z:.2f}), Rot = ({ob.rotation_euler.x:.2f}, {ob.rotation_euler.y:.2f}, {ob.rotation_euler.z:.2f})")

print("\n--- 4. DANH SACH CHIEN HAM NAM HAN ---")
han_count = 0
for ob in bpy.data.objects:
    if ob.name.startswith("Root_NH_"):
        han_count += 1
        if han_count <= 4 or han_count >= 25 or "SoaiHam" in ob.name:
            print(f"  {ob.name}: Loc = ({ob.location.x:.1f}, {ob.location.y:.1f}, {ob.location.z:.2f}), Rot = ({ob.rotation_euler.x:.2f}, {ob.rotation_euler.y:.2f}, {ob.rotation_euler.z:.2f})")
print(f"Tong so chien ham Nam Han: {han_count}")