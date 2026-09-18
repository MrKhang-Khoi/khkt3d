import bpy

for mat in bpy.data.materials:
    if any(k in mat.name.lower() for k in ['buom', 'sail', 'nan', 'vai']):
        print(f"Material: {mat.name}")
        if mat.use_nodes:
            for n in mat.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED':
                    print(f"  Base Color: {n.inputs['Base Color'].default_value[:]}")