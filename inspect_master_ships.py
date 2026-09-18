import bpy

with bpy.data.libraries.load(r'c:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships\lau_thuyen_namhan_master.blend') as (data_from, data_to):
    print('Nam Han collections:', data_from.collections)
    print('Nam Han objects:', data_from.objects)

with bpy.data.libraries.load(r'c:\Users\HPZBook\Desktop\TEST_BLENDER\assets\ships\thuyen_ta_ngoquyen_master.blend') as (data_from, data_to):
    print('Dai Viet collections:', data_from.collections)
    print('Dai Viet objects:', data_from.objects)
