import bpy
import math

for ob in bpy.context.scene.objects:
    if 'Root_DaiViet' in ob.name or 'Root_NamHan' in ob.name:
        rot_deg = [math.degrees(a) for a in ob.rotation_euler]
        print(f"{ob.name:32} rot: ({rot_deg[0]:.1f}, {rot_deg[1]:.1f}, {rot_deg[2]:.1f}) loc: ({ob.location.x:.1f}, {ob.location.y:.1f}, {ob.location.z:.1f})")
        if ob.children:
            ch = ob.children[0]
            ch_rot = [math.degrees(a) for a in ch.rotation_euler]
            print(f"   -> child {ch.name:28} rot: ({ch_rot[0]:.1f}, {ch_rot[1]:.1f}, {ch_rot[2]:.1f})")
        break
