import bpy
from mathutils import Vector

scene = bpy.context.scene
scene.frame_set(1)
bpy.context.view_layer.update()

def get_bbox_center_world(obj):
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return sum(bbox_corners, Vector()) / 8.0

print("--- VERTEX / BOUNDING BOX WORLD POSITIONS ---")

ta_mui = bpy.data.objects.get('Mui_ChimLac_DongSon')
if ta_mui:
    c = get_bbox_center_world(ta_mui)
    print(f"Dai Viet Mui_ChimLac BBox Center: X={c.x:.2f}, Y={c.y:.2f}, Z={c.z:.2f}")

ta_than = bpy.data.objects.get('Than_Thuyen_GoLim')
if ta_than:
    c = get_bbox_center_world(ta_than)
    print(f"Dai Viet Than_Thuyen BBox Center: X={c.x:.2f}, Y={c.y:.2f}, Z={c.z:.2f}")

nh_cot_mui = bpy.data.objects.get('NamHan_Cot_Mui')
if nh_cot_mui:
    c = get_bbox_center_world(nh_cot_mui)
    print(f"Nam Han Cot_Mui BBox Center: X={c.x:.2f}, Y={c.y:.2f}, Z={c.z:.2f}")

nh_cot_chinh = bpy.data.objects.get('NamHan_Cot_Chinh')
if nh_cot_chinh:
    c = get_bbox_center_world(nh_cot_chinh)
    print(f"Nam Han Cot_Chinh BBox Center: X={c.x:.2f}, Y={c.y:.2f}, Z={c.z:.2f}")

nh_than = bpy.data.objects.get('NamHan_ThanTau_GoThong')
if nh_than:
    c = get_bbox_center_world(nh_than)
    print(f"Nam Han ThanTau BBox Center: X={c.x:.2f}, Y={c.y:.2f}, Z={c.z:.2f}")