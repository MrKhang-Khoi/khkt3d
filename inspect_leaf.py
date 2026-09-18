import bpy

for ob in bpy.context.scene.objects:
    if 'La_' in ob.name or 'leaves' in ob.name.lower():
        print(f"Leaf obj: {ob.name}, type: {ob.type}, mat: {[m.name for m in ob.data.materials if m]}, verts: {len(ob.data.vertices)}, scale: {ob.scale}, loc: {ob.location}")
        break
