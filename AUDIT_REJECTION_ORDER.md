# 🛑 LỆNH ĐÌNH CHỈ & BÁC BỎ TÀI NGUYÊN (AUDIT REJECTION NOTICE)
**Người ban hành:** Antigravity Independent Quality Gatekeeper (qa-educator & po-historian)
**Thời gian:** 2026-09-17 22:18:00
**Đối tượng kiểm tra:** 
1. `assets/props/coc_bach_dang_master.blend`
2. `assets/ships/thuyen_ta_ngoquyen_master.blend`

---

### I. CÁC VI PHẠM ĐƯỢC PHÁT HIỆN QUA PHÂN TÍCH TỰ ĐỘNG:

#### 1. Vi phạm tại `thuyen_ta_ngoquyen_master.blend`:
- 🔴 **Lỗi Hình học (Extreme Low-Poly / Slop)**: Vỏ thân thuyền (`Than_Thuyen_GoLim`) chỉ có vỏn vẹn **48 đa giác (polygons)**! Đây là mô hình hình hộp thô thiển, mất hoàn toàn độ uốn lượn khí động học của thuyền buồm Vịnh Bắc Bộ.
- 🔴 **Thiếu các chi tiết lịch sử cốt lõi**:
  * Đã bỏ quên toàn bộ hàng khiên mây đan sơn then (sơn mài đen đỏ) treo dọc hai bên be thuyền.
  * Đã bỏ quên hàng cọc chèo và bệ tì chèo của thủy binh.
  * Thuyền rỗng, không có nhân vật lính chèo thuyền.
- 🔴 **Lỗi LookDev / Render**: File không lưu Camera và hệ thống chiếu sáng chuẩn LookDev. Khi chạy render tự động, màn hình đen ngòm 95% (`audit_render_thuyen_ta.png`).

#### 2. Vi phạm tại `coc_bach_dang_master.blend`:
- 🔴 **Lỗi Cấu trúc Asset**: Gom gộp toàn bộ 21 cọc vào một khối Mesh duy nhất (`Coc_BachDang_Master_Group`). Điều này làm mất khả năng tái sử dụng (không thể dùng Geometry Nodes để rải từng cây cọc ngẫu nhiên theo lòng sông).
- 🔴 **Lỗi Topology**: Chứa 130 mặt N-gons (> 4 cạnh) trên đỉnh chóp cọc.

---

### II. YÊU CẦU BẮT BUỘC ĐỐI VỚI WORKER AI:
1. **ĐÌNH CHỈ NGAY LẬP TỨC** việc tạo file cảnh tổng thể `scenes/dai_chien_bach_dang_assembly.blend`.
2. **LÀM LẠI `thuyen_ta_ngoquyen_master.blend`**:
   - Sử dụng lại code lofting chất lượng cao từ `tao_thuyen_chi_tiet_cao.py` (tối thiểu 800–1200 đa giác mượt mà).
   - Dựng đầy đủ: Hàng khiên mây sơn ta hai bên mạn, hệ thống cọc chèo, sàn thao diễn, buồm cánh dơi nan tre.
   - Bố trí Camera Turnaround 360° và ánh sáng 3 điểm trung tính chuẩn LookDev trong file.
3. **LÀM LẠI `coc_bach_dang_master.blend`**:
   - Tách thành 3 vật thể Master độc lập: `Coc_Chinh_BitSat`, `Coc_Nghieng_GoLim`, `Coc_Gay_MuiSat` để làm nguồn rải bãi cọc.

**KÝ DUYỆT:** GATEKEEPER AUDITOR - STATUS: REJECTED (FAIL)
