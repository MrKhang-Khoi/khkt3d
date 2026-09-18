import base64

glb_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\bach_dang_battle_optimized.glb'
html_path = r'C:\Users\HPZBook\Desktop\TEST_BLENDER\web3d_export\index.html'

with open(glb_path, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('ascii')

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

prefix = 'const embeddedGlbBase64 = '
suffix = ';'
start = html.find(prefix)
if start != -1:
    end = html.find(suffix, start + len(prefix))
    html = html[:start + len(prefix)] + glb_b64 + html[end:]
    print('Replaced base64 string successfully!')
else:
    print('Prefix not found!')

# Replace LaTeX
html = html.replace(r'$\to$', '->').replace(r'^\circ$', '25 độ')

# Enhance lighting
html = html.replace('scene.background = new THREE.Color(0x11161f);', 'scene.background = new THREE.Color(0x1a2634);')
html = html.replace('scene.fog = new THREE.FogExp2(0x11161f, 0.009);', 'scene.fog = new THREE.FogExp2(0x1a2634, 0.006);')
html = html.replace('const hemiLight = new THREE.HemisphereLight(0xa0b4c8, 0x181c24, 0.85);', 'const hemiLight = new THREE.HemisphereLight(0xdde8f5, 0x243242, 1.5);')
html = html.replace('const sunLight = new THREE.DirectionalLight(0xffecd0, 2.2);', 'const sunLight = new THREE.DirectionalLight(0xfffaed, 2.8);')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print('SUCCESS: patch_web3d_html finished!')
