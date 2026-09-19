const net = require('net');
const fs = require('fs');

const client = new net.Socket();
client.connect(9876, '127.0.0.1', () => {
  const code = `
import bpy, bmesh, math, os, traceback
from mathutils import Vector, Matrix, Euler

log_file = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/rebuild_rowers_blender.txt'
with open(log_file, 'w', encoding='utf-8') as f:
    f.write("=== BƯỚC 1: TÁI CẤU TRÚC LÍNH CẦM CHÈO CHUẨN LỊCH SỬ TRONG BLENDER ===\\n")

try:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    soldier_base = bpy.data.objects.get('ThuyBinh_DaiViet_Master')
    giap_base = bpy.data.objects.get('Giap_HoTam_DongSon_ThuyBinh_DaiViet_Master')
    dai_base = bpy.data.objects.get('Dai_That_Lung_ThuyBinh_DaiViet_Master')
    
    if not soldier_base:
        raise Exception("Không tìm thấy ThuyBinh_DaiViet_Master!")
        
    # Tạo hàm sinh 1 người lính hoàn chỉnh cho 1 bên mạn (Port hoặc Stbd)
    # is_stbd = False (Mạn Tả, mạn nằm ở +Y)
    # is_stbd = True (Mạn Hữu, mạn nằm ở -Y)
    def build_historical_rower(is_stbd=False):
        side_sign = -1.0 if is_stbd else 1.0
        
        # 1. Bake hình học lính, giáp, đai
        eval_soldier = soldier_base.evaluated_get(depsgraph)
        m_soldier = bpy.data.meshes.new_from_object(eval_soldier)
        o_soldier = bpy.data.objects.new("TMP_Soldier", m_soldier)
        bpy.context.scene.collection.objects.link(o_soldier)
        o_soldier.matrix_world = soldier_base.matrix_world.copy()
        
        eval_giap = giap_base.evaluated_get(depsgraph)
        m_giap = bpy.data.meshes.new_from_object(eval_giap)
        o_giap = bpy.data.objects.new("TMP_Giap", m_giap)
        bpy.context.scene.collection.objects.link(o_giap)
        o_giap.matrix_world = giap_base.matrix_world.copy()
        
        eval_dai = dai_base.evaluated_get(depsgraph)
        m_dai = bpy.data.meshes.new_from_object(eval_dai)
        o_dai = bpy.data.objects.new("TMP_Dai", m_dai)
        bpy.context.scene.collection.objects.link(o_dai)
        o_dai.matrix_world = dai_base.matrix_world.copy()
        
        # 2. Xoay lính hướng mặt về phía trước (+X):
        # Ban đầu mặt lính hướng về -Y. Quay quanh Z một góc +90 độ (pi/2) để mặt hướng về +X!
        rot_facing = Euler((0, 0, math.pi / 2.0)).to_matrix().to_4x4()
        for o in [o_soldier, o_giap, o_dai]:
            o.matrix_world = rot_facing @ o.matrix_world
            
        # 3. Tạo chiếc Mái chèo dài chuẩn lịch sử (Oar):
        # Sau khi xoay rot_facing:
        # Mặt lính hướng về +X.
        # Ngực ở X = 0, tay vươn ra phía trước theo trục +X (X ~ +0.30m).
        # Tay trái ở +Y (khoảng +0.32m), tay phải ở -Y (khoảng -0.32m).
        # Điểm giữa 2 lòng bàn tay: Vector((0.30, 0.0, 0.88)).
        #
        # Nếu là Mạn Tả (is_stbd = False):
        # Mạn thuyền ở bên trái (+Y). Chiếc mái chèo vươn từ tay lính chéo sang +Y:
        # - Đốc cán chèo (tay trong cầm): Vector((0.15, -0.20, 0.92))
        # - Vị trí tay ngoài cầm thân chèo: Vector((0.30, +0.25, 0.85))
        # - Điểm tì lên cọc mạn thuyền (Fulcrum): Vector((0.45, +0.85, 0.65))
        # - Đầu lưỡi chèo cắm sâu xuống dòng nước sông: Vector((0.65, +2.35, -0.20))
        #
        # Nếu là Mạn Hữu (is_stbd = True):
        # Mạn thuyền ở bên phải (-Y). Chiếc mái chèo vươn từ tay lính chéo sang -Y:
        # - Đốc cán chèo: Vector((0.15, +0.20, 0.92))
        # - Vị trí tay ngoài cầm thân chèo: Vector((0.30, -0.25, 0.85))
        # - Điểm tì lên cọc mạn thuyền: Vector((0.45, -0.85, 0.65))
        # - Đầu lưỡi chèo cắm sâu xuống dòng nước sông: Vector((0.65, -2.35, -0.20))
        
        p_handle = Vector((0.15, -0.20 * side_sign, 0.92))
        p_water = Vector((0.65, 2.35 * side_sign, -0.20))
        
        dir_oar = p_water - p_handle
        oar_len = dir_oar.length
        
        bm = bmesh.new()
        rot_diff = Vector((0, 0, 1)).rotation_difference(dir_oar.normalized())
        center_oar = (p_handle + p_water) * 0.5
        mat_oar = Matrix.Translation(center_oar) @ rot_diff.to_matrix().to_4x4()
        
        # Thân cán chèo bằng bmesh cone (cylinder)
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            radius1=0.032,
            radius2=0.032,
            depth=oar_len,
            matrix=mat_oar,
            segments=12
        )
        
        # Lưỡi chèo dẹt nhúng chìm trong nước sông
        blade_len = 0.95
        blade_width = 0.22
        blade_thick = 0.028
        blade_center = p_water - dir_oar.normalized() * (blade_len * 0.4)
        mat_blade = Matrix.Translation(blade_center) @ rot_diff.to_matrix().to_4x4() @ Matrix.Scale(blade_width, 4, Vector((1,0,0))) @ Matrix.Scale(blade_thick, 4, Vector((0,1,0))) @ Matrix.Scale(blade_len, 4, Vector((0,0,1)))
        
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=mat_blade
        )
        
        m_oar = bpy.data.meshes.new(f"TMP_Oar_{'Stbd' if is_stbd else 'Port'}")
        bm.to_mesh(m_oar)
        bm.free()
        
        mat_wood = bpy.data.materials.get('Mat_GoLim_ThuyenTa') or bpy.data.materials.get('Mat_GoLim')
        if mat_wood:
            m_oar.materials.append(mat_wood)
            
        o_oar = bpy.data.objects.new(f"TMP_Oar_{'Stbd' if is_stbd else 'Port'}", m_oar)
        bpy.context.scene.collection.objects.link(o_oar)
        
        # 4. Gộp 4 đối tượng thành 1 người lính duy nhất
        bpy.ops.object.select_all(action='DESELECT')
        for p in [o_soldier, o_giap, o_dai, o_oar]:
            p.select_set(True)
        bpy.context.view_layer.objects.active = o_soldier
        bpy.ops.object.join()
        
        final_rower = bpy.context.active_object
        
        # Decimate 0.65 tối ưu WebGL 60 FPS
        dec = final_rower.modifiers.new(name="DecimateWeb", type='DECIMATE')
        dec.ratio = 0.65
        bpy.ops.object.modifier_apply(modifier="DecimateWeb")
        
        final_mesh = final_rower.data.copy()
        bpy.data.objects.remove(final_rower, do_unlink=True)
        return final_mesh

    mesh_rower_port = build_historical_rower(is_stbd=False)
    mesh_rower_stbd = build_historical_rower(is_stbd=True)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Đã tạo xong Mesh Rower hoàn chỉnh: Port={len(mesh_rower_port.polygons)} polys, Stbd={len(mesh_rower_stbd.polygons)} polys\\n")

    # 5. Xuất thuyền cùng 6 Rower hoàn chỉnh
    col_name = "EXPORT_FINAL_HISTORICAL_COL"
    if col_name in bpy.data.collections:
        bpy.data.collections.remove(bpy.data.collections[col_name])
    export_col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(export_col)

    boat = bpy.data.objects.get('Thuyen_Chien_NgoQuyen_938')
    if not boat:
        raise Exception("Boat Thuyen_Chien_NgoQuyen_938 not found!")

    export_root = bpy.data.objects.new("Master_DaiViet_Ship_Root", None)
    export_col.objects.link(export_root)
    export_root.matrix_world = boat.matrix_world.copy()
    created_objs = [export_root]

    # Sao chép các mesh của thuyền (BỎ Mai_Cheo_Thuyen cũ)
    boat_mesh_names = [
        'Than_Thuyen_GoLim',
        'San_Boong_Thuyen',
        'Khung_Suon_ChiuLuc',
        'Mui_ChimLac_DongSon',
        'Khien_May_SonThen',
        'CoLenh_NguHanh_Master'
    ]
    buom_empty = bpy.data.objects.get('Buom_CanhDoi_BachDang')
    if buom_empty:
        for bc in buom_empty.children:
            if bc.type == 'MESH':
                boat_mesh_names.append(bc.name)

    for mname in boat_mesh_names:
        src = bpy.data.objects.get(mname)
        if src and src.type == 'MESH':
            eval_src = src.evaluated_get(depsgraph)
            new_mesh = bpy.data.meshes.new_from_object(eval_src)
            new_obj = bpy.data.objects.new(mname + "_Export", new_mesh)
            export_col.objects.link(new_obj)
            new_obj.matrix_world = src.matrix_world.copy()
            new_obj.parent = export_root
            new_obj.matrix_parent_inverse = export_root.matrix_world.inverted()
            created_objs.append(new_obj)

    # 6. Gắn 6 người lính vào đúng 6 vị trí trên thuyền
    soldier_empties = [c for c in boat.children if 'ThuyBinh' in c.name]
    for idx, s in enumerate(soldier_empties):
        is_stbd = 'Stbd' in s.name
        rower_mesh = mesh_rower_stbd if is_stbd else mesh_rower_port
        rower_name = f"Rower_{'Stbd' if is_stbd else 'Port'}_{idx}"
        
        rower_obj = bpy.data.objects.new(rower_name, rower_mesh)
        export_col.objects.link(rower_obj)
        rower_obj.matrix_world = s.matrix_world.copy()
        rower_obj.parent = export_root
        rower_obj.matrix_parent_inverse = export_root.matrix_world.inverted()
        created_objs.append(rower_obj)

    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"Tổng số đối tượng xuất xưởng (thuyền + 6 Rower hoàn hảo): {len(created_objs)}\\n")

    # Chọn và xuất ra GLB
    bpy.ops.object.select_all(action='DESELECT')
    for o in created_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = export_root

    out_glb = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/thuyen_daiviet_master.glb'
    bpy.ops.export_scene.gltf(
        filepath=out_glb,
        use_selection=True,
        export_format='GLB',
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT'
    )
    
    file_size = os.path.getsize(out_glb)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"XUẤT THÀNH CÔNG GLB: {out_glb} - Kích thước: {file_size} bytes ({file_size/1024/1024:.2f} MB)\\n")

    # Copy sang web3d_export
    web3d_target = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/web3d_export/thuyen_daiviet_master.glb'
    with open(out_glb, 'rb') as f_in, open(web3d_target, 'wb') as f_out:
        f_out.write(f_in.read())

    # Dọn dẹp
    for o in created_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(export_col)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("Dọn dẹp hoàn tất 100%!\\n")

except Exception as e:
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"LỖI: {traceback.format_exc()}\\n")
`;
  client.write(JSON.stringify({ type: 'execute_code', params: { code } }));
});

client.on('data', () => {
  client.destroy();
  if (fs.existsSync('rebuild_rowers_blender.txt')) {
    console.log(fs.readFileSync('rebuild_rowers_blender.txt', 'utf-8'));
  }
});
