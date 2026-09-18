import bpy

print("=== THUYEN TA HIERARCHY ===")
for ob in bpy.context.scene.objects:
    if 'Thuyen' in ob.name or 'Than_' in ob.name or 'San_' in ob.name or 'Buom' in ob.name:
        print(f"  {ob.name:32} parent: {ob.parent.name if ob.parent else 'NONE'} world_loc: ({ob.matrix_world.translation.x:.1f}, {ob.matrix_world.translation.y:.1f}, {ob.matrix_world.translation.z:.1f})")

print("=== LAU THUYEN HIERARCHY ===")
for ob in bpy.context.scene.objects:
    if 'NamHan' in ob.name or 'LauThuyen' in ob.name:
        print(f"  {ob.name:32} parent: {ob.parent.name if ob.parent else 'NONE'} world_loc: ({ob.matrix_world.translation.x:.1f}, {ob.matrix_world.translation.y:.1f}, {ob.matrix_world.translation.z:.1f})")
