import bpy

scene = bpy.context.scene
print("Render Engine:", scene.render.engine)
print("Camera:", scene.camera.name if scene.camera else "None")
print("Resolution:", scene.render.resolution_x, "x", scene.render.resolution_y)