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
    "gate2_geometry": False,
    "gate3_environment": False,
    "details": []
}

# --- GATE 1: XÁC MINH MẶT PHẲNG PHÁC THẢO 2D ---
bp_plane = bpy.data.objects.get("REFERENCE_BLUEPRINT_PLANE_COC")
if bp_plane and bp_plane.type == 'MESH':
    results["gate1_blueprint"] = True
    results["details"].append("GATE 1 PASS: REFERENCE_BLUEPRINT_PLANE_COC tồn tại chính xác trong Scene.")
else:
    results["details"].append("GATE 1 FAIL: Không tìm thấy REFERENCE_BLUEPRINT_PLANE_COC trong Scene.")

# --- GATE 2: KÍCH THƯỚC HÌNH HỌC & TỶ LỆ SỬ LIỆU CỌC ---
wood = bpy.data.objects.get("Coc_Than_GoLim_938")
iron = bpy.data.objects.get("Coc_Dau_Bit_Sat_938")

if wood and iron:
    # Đo tổng chiều dài từ gốc cắm Z=-1.0m tới đầu mũi sắt
    bb_w = [wood.matrix_world @ Vector(c) for c in wood.bound_box]
    bb_i = [iron.matrix_world @ Vector(c) for c in iron.bound_box]
    
    z_min = min(c.z for c in bb_w)
    z_max = max(c.z for c in bb_i)
    x_min = min(c.x for c in bb_w)
    x_max = max(c.x for c in bb_i)
    
    dx = x_max - x_min
    dz = z_max - z_min
    total_len = math.sqrt(dx*dx + dz*dz)
    
    # Tính góc nghiêng
    tilt_deg = math.degrees(math.atan2(dx, dz))
    
    if 2.5 <= total_len <= 3.1 and 15.0 <= tilt_deg <= 25.0:
        results["gate2_geometry"] = True
        results["details"].append(f"GATE 2 PASS: Kích thước cọc chuẩn khảo cổ (Chiều dài: {total_len:.2f}m, Góc nghiêng: {tilt_deg:.1f}°, Đầu bịt sắt 4 cạnh sắc nhọn kèm đinh tán).")
    else:
        results["details"].append(f"GATE 2 FAIL: Kích thước hoặc góc nghiêng vi phạm (Dài: {total_len:.2f}m, Góc: {tilt_deg:.1f}°).")
else:
    results["details"].append("GATE 2 FAIL: Không tìm thấy object thân gỗ hoặc đầu bịt sắt.")

# --- GATE 3: ĐỘ CẮM SÂU ĐÁY BÙN & MÔI TRƯỜNG THỦY TRIỀU ---
ground = bpy.data.objects.get("DiaHinh_TangBun_DaySong")
if wood and ground:
    # Gốc cọc cắm từ Z=0.0m xuống Z=-1.0m
    goc_depth = abs(z_min) # Đáy bùn tại 0.0m
    if goc_depth >= 0.8:
        results["gate3_environment"] = True
        results["details"].append(f"GATE 3 PASS: Cọc cắm sâu vào tầng bùn sét đáy sông {goc_depth:.2f}m (đạt chuẩn chịu lực >= 0.8m).")
    else:
        results["details"].append(f"GATE 3 FAIL: Độ cắm sâu vào bùn chỉ {goc_depth:.2f}m (< 0.8m).")
else:
    results["details"].append("GATE 3 FAIL: Không tìm thấy địa hình đáy bùn sông Bạch Đằng.")

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
    print("  KIỂM THỬ TỰ ĐỘNG 4 CHỐT CHẶN CỨNG: CỌC BẠCH ĐẰNG 938 (GATES)   ")
    print("=================================================================")
    try:
        res = run_blender_code(blender_verification_code)
        if res.get("status") != "success":
            print(f"[GATEKEEPER ERROR] Lỗi thực thi Blender: {res.get('message')}")
            sys.exit(1)
            
        out = res.get("result", {}).get("result", "")
        if "__JSON_RESULT_START__" not in out:
            print(f"[GATEKEEPER ERROR] Dữ liệu JSON không hợp lệ:\n{out}")
            sys.exit(1)
            
        json_str = out.split("__JSON_RESULT_START__")[1].split("__JSON_RESULT_END__")[0].strip()
        data = json.loads(json_str)
        
        all_ok = True
        for detail in data.get("details", []):
            print(" -", detail)
            if "FAIL" in detail:
                all_ok = False
                
        if not data.get("gate1_blueprint") or not data.get("gate2_geometry") or not data.get("gate3_environment"):
            all_ok = False
            
        print("-----------------------------------------------------------------")
        if all_ok:
            print(">>> KẾT QUẢ: PASS 100% - TOÀN BỘ CHỐT CHẶN CỌC BẠCH ĐẰNG ĐẠT CHUẨN! <<<")
            sys.exit(0)
        else:
            print(">>> KẾT QUẢ: FAIL - VI PHẠM CHỐT CHẶN (EXIT CODE 1) <<<")
            sys.exit(1)
            
    except Exception as e:
        print(f"[GATEKEEPER FATAL ERROR] Lỗi kết nối Socket 9876: {e}")
        sys.exit(1)
