import bpy

for ob in bpy.context.scene.objects:
    if any(k in ob.name for k in ['Nui', 'Thuyen', 'Root', 'Water', 'MatNuoc', 'tree', 'Tree', 'Cay']):
        print(f"OBJ: {ob.name:32} LOC: ({ob.location.x:6.1f}, {ob.location.y:6.1f}, {ob.location.z:6.1f}) DIM: ({ob.dimensions.x:6.1f}, {ob.dimensions.y:6.1f}, {ob.dimensions.z:6.1f}) VIS: {not ob.hide_viewport}")
