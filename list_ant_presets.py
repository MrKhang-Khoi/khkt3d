import os

p = r'C:\Users\HPZBook\AppData\Roaming\Blender Foundation\Blender\5.2\extensions\blender_org\antlandscape\presets\operator'
if os.path.exists(p):
    files = os.listdir(p)
    print("Preset files:", files)
