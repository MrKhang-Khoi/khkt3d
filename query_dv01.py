import bpy

dv01 = bpy.data.objects.get('Boat_DV_01')
if dv01:
    print('DV01 loc:', dv01.location, 'rot:', dv01.rotation_euler)
    for c in dv01.children:
        print(' - child:', c.name, 'type:', c.type)
else:
    print('Boat_DV_01 not found, listing all objects:')
    for o in bpy.data.objects:
        if 'DV' in o.name or 'Ta' in o.name:
            print(' ', o.name, o.location)
