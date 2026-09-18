import bpy, os

# Look for ant_landscape presets in blender addons
import addon_utils
for mod in addon_utils.modules():
    if 'antlandscape' in mod.__name__.lower():
        p = os.path.dirname(mod.__file__)
        presets_dir = os.path.join(p, 'presets')
        print("ANT dir:", p)
        if os.path.exists(presets_dir):
            print("Presets:", os.listdir(presets_dir))
