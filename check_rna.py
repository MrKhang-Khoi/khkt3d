import bpy

rna = bpy.ops.mesh.landscape_add.get_rna_type()
for prop in rna.properties:
    if prop.identifier in ['edge_falloff', 'falloff_x', 'falloff_y', 'strata_type', 'noise_type']:
        print(f"PROP {prop.identifier}: default={prop.default}, enum_items={[it.identifier for it in getattr(prop, 'enum_items', [])]}")
