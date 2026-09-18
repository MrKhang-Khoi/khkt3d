import bpy

coc_objs = [o for o in bpy.context.scene.objects if 'Coc_' in o.name]
print(f"Total stakes: {len(coc_objs)}")
for c in coc_objs[:10]:
    print(f"  {c.name:24} loc: ({c.location.x:.1f}, {c.location.y:.1f}, {c.location.z:.1f}) rot: ({c.rotation_euler.x:.1f}, {c.rotation_euler.y:.1f}, {c.rotation_euler.z:.1f})")
