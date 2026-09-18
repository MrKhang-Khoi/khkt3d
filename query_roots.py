import bpy

for o in bpy.data.objects:
    if o.parent is None and ('Ta_' in o.name or 'Han_' in o.name or 'DV' in o.name or 'NH' in o.name or 'Boat' in o.name or 'Ship' in o.name):
        print('Root:', o.name, o.location)
