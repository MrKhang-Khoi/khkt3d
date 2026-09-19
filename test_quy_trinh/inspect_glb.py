import json

with open('test_quy_trinh/coc_bach_dang_938.glb', 'rb') as f:
    data = f.read()

json_len = int.from_bytes(data[12:16], 'little')
gltf = json.loads(data[20:20+json_len].decode('utf-8'))
for mesh in gltf.get('meshes', []):
    name = mesh.get('name')
    for prim in mesh.get('primitives', []):
        acc_idx = prim['attributes']['POSITION']
        acc = gltf['accessors'][acc_idx]
        print(f"{name}: min={acc.get('min')} max={acc.get('max')}")
