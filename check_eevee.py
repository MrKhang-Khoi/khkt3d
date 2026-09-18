import bpy

eevee = bpy.context.scene.eevee
print("EEVEE attributes:")
for attr in dir(eevee):
    if not attr.startswith("__"):
        try:
            val = getattr(eevee, attr)
            if not callable(val):
                print(f"  {attr}: {val}")
        except Exception:
            pass

print("View Settings Look:", bpy.context.scene.view_settings.look)