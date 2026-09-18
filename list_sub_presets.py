import os

p = r'C:\Users\HPZBook\AppData\Roaming\Blender Foundation\Blender\5.2\extensions\blender_org\antlandscape\presets\operator\mesh.landscape_add'
if os.path.exists(p):
    files = os.listdir(p)
    print("Presets in mesh.landscape_add:", files)
