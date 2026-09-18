import bpy
import time

def init_mcp():
    print('[BLENDER-LIVE] Initializing Blender MCP Server...')
    if 'blender_mcp' not in bpy.context.preferences.addons:
        try:
            bpy.ops.preferences.addon_enable(module='blender_mcp')
            print('[BLENDER-LIVE] Enabled blender_mcp addon.')
        except Exception as e:
            print('[BLENDER-LIVE] Could not enable addon:', e)
    
    try:
        bpy.ops.blendermcp.start_server()
        print('[BLENDER-LIVE] bpy.ops.blendermcp.start_server() succeeded!')
    except Exception as e:
        print('[BLENDER-LIVE] Operator failed, trying direct start:', e)
        try:
            import blender_mcp
            server = getattr(bpy.types, 'blendermcp_server', None)
            if server is None:
                server = blender_mcp.BlenderMCPServer(port=9876)
                bpy.types.blendermcp_server = server
            if not server.running:
                server.start()
            print('[BLENDER-LIVE] Direct server start succeeded on port 9876!')
        except Exception as err2:
            print('[BLENDER-LIVE] Direct server start failed:', err2)

bpy.app.timers.register(init_mcp, first_interval=1.0)
