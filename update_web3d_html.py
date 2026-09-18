import os
import base64
import re

glb_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\bach_dang_battle_optimized.glb'
html_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\index.html'

print("Reading GLB and converting to base64...")
with open(glb_path, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('ascii')

print(f"Base64 length: {len(glb_b64)} chars ({len(glb_b64)/(1024*1024):.2f} MB)")

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Replace window.EMBEDDED_GLB_BASE64 = "...";
pattern = r'window\.EMBEDDED_GLB_BASE64\s*=\s*\"[^\"]*\";'
replacement = f'window.EMBEDDED_GLB_BASE64 = "{glb_b64}";'

if re.search(pattern, html_content):
    new_html = re.sub(pattern, replacement, html_content)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("SUCCESS: Updated index.html with new GLB base64!")
else:
    print("WARNING: Pattern not found in index.html!")
