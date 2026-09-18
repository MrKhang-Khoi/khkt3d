import base64
import os

glb_path = r"c:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\thuyen_daiviet_master.glb"
with open(glb_path, "rb") as f:
    dv_b64 = base64.b64encode(f.read()).decode('utf-8')

print("Encoded Dai Viet Master GLB to base64, length:", len(dv_b64))

def update_assets_file(filepath):
    if not os.path.exists(filepath):
        print("File not found:", filepath)
        return
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith("window.ASSETS_DAIVIET_B64"):
            new_lines.append(f'window.ASSETS_DAIVIET_B64 = "{dv_b64}";\n')
        else:
            new_lines.append(line)
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Updated:", filepath, "New size:", os.path.getsize(filepath))

update_assets_file(r"c:\Users\HPZBook\Desktop\TEST_BLENDER\ships_assets_data.js")
update_assets_file(r"c:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\ships_assets_data.js")
