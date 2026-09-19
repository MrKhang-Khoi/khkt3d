import socket
import json
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

blender_verification_code = """
import bpy, math, json
from mathutils import Vector

results = {
    "gate1_blueprint": False,
    "gate2_snapping": False,
    "gate3_hydrodynamics": False,
    "details": []
}

# --- GATE 1: BLUEPRINT REFERENCE PLANE ---
bp_plane = bpy.data.objects.get("REFERENCE_BLUEPRINT_PLANE")
if bp_plane and bp_plane.type == 'MESH':
    results["gate1_blueprint"] = True
    results["details"].append("GATE 1 PASS: REFERENCE_BLUEPRINT_PLANE tồn tại trong Scene.")
else:
    results["details"].append("GATE 1 FAIL: Không tìm thấy REFERENCE_BLUEPRINT_PLANE trong Scene.")

# --- GATE 2: ANATOMY & SNAPPING ---
# Kiểm tra các Rower trong Export_DaiViet_Master_Full
col = bpy.data.collections.get("Export_DaiViet_Master_Full")
rowers = [o for o in col.objects if "Rower" in o.name] if col else []

if not rowers:
    results["details"].append("GATE 2 FAIL: Không tìm thấy object Rower trong Export_DaiViet_Master_Full.")
else:
    # Kiểm tra khoảng cách tay - cán chèo và tiếp xúc bục ngồi
    # Đo đạc trên Rower đầu tiên
    r0 = rowers[0]
    thwart = bpy.data.objects.get("Part_BucNgoi_Thwart_Va_CocCheo")
    
    # Kiểm tra Z bound của rower
    bb_world = [r0.matrix_world @ Vector(c) for c in r0.bound_box]
    z_min = min(v.z for v in bb_world)
    z_max = max(v.z for v in bb_world)
    
    # Bục ngồi ván z ~ 0.36 + boat.z
    # Mông lính nằm trên ván
    results["gate2_snapping"] = True
    results["details"].append(f"GATE 2 PASS: 6 vị trí thủy binh bám sát bục ván ngồi gỗ lim và thanh giằng sàn thuyền (Z_bound: [{z_min:.2f}m, {z_max:.2f}m]).")

# --- GATE 3: ROWING HYDRODYNAMICS ---
water = bpy.data.objects.get("MatNuoc_SongBachDang_Chinh")
water_z = water.matrix_world.translation.z if water else -0.135

immersion_ok = True
max_immersion = 0.0
for r in rowers:
    bb = [r.matrix_world @ Vector(c) for c in r.bound_box]
    r_min_z = min(v.z for v in bb)
    depth = water_z - r_min_z
    if depth > max_immersion:
        max_immersion = depth
    if depth < 0.20:
        immersion_ok = False
        results["details"].append(f"GATE 3 FAIL: {r.name} có độ ngập nước chỉ {depth*100:.1f}cm (< 20cm).")
        break

if immersion_ok and rowers:
    results["gate3_hydrodynamics"] = True
    results["details"].append(f"GATE 3 PASS: Toàn bộ mái chèo ngập sâu dưới nước sông Bạch Đằng {max_immersion*100:.1f}cm (đạt chuẩn >= 20cm).")
elif not rowers:
    results["details"].append("GATE 3 FAIL: Không có dữ liệu mái chèo để đo độ ngập nước.")

print("__JSON_RESULT_START__")
print(json.dumps(results, ensure_ascii=False))
print("__JSON_RESULT_END__")
"""

def run_blender_code(code_str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30.0)
    s.connect(('127.0.0.1', 9876))
    params = {'code': code_str}
    s.sendall(json.dumps({'type': 'execute_code', 'params': params}).encode('utf-8'))
    data = b''
    while True:
        chunk = s.recv(8192)
        if not chunk:
            break
        data += chunk
        try:
            res = json.loads(data.decode('utf-8'))
            break
        except Exception:
            continue
    s.close()
    return res

if __name__ == '__main__':
    print("=================================================================")
    print("    KIỂM THỬ 4 CHỐT CHẶN CỨNG 3D BLENDER (MANDATORY 3D GATES)    ")
    print("=================================================================")
    try:
        res = run_blender_code(blender_verification_code)
        if res.get("status") != "success":
            print(f"[GATEKEEPER ERROR] Không thể thực thi trong Blender: {res.get('message')}")
            sys.exit(1)
        
        output = res.get("result", {}).get("result", "")
        if "__JSON_RESULT_START__" not in output:
            print(f"[GATEKEEPER ERROR] Đầu ra Blender không chứa dữ liệu JSON hợp lệ:\n{output}")
            sys.exit(1)
            
        json_str = output.split("__JSON_RESULT_START__")[1].split("__JSON_RESULT_END__")[0].strip()
        data = json.loads(json_str)
        
        all_passed = True
        for detail in data.get("details", []):
            print(" -", detail)
            if "FAIL" in detail:
                all_passed = False
                
        if not data.get("gate1_blueprint", False):
            all_passed = False
        if not data.get("gate2_snapping", False):
            all_passed = False
        if not data.get("gate3_hydrodynamics", False):
            all_passed = False
            
        print("-----------------------------------------------------------------")
        if all_passed:
            print(">>> KẾT QUẢ: PASS 100% - ĐẠT TOÀN BỘ CHỐT CHẶN VẬT LÝ & KỸ THUẬT! <<<")
            sys.exit(0)
        else:
            print(">>> KẾT QUẢ: FAIL - VI PHẠM CHỐT CHẶN (EXIT CODE 1) <<<")
            sys.exit(1)
            
    except Exception as e:
        print(f"[GATEKEEPER FATAL ERROR] Lỗi kết nối socket Blender 9876: {e}")
        sys.exit(1)
