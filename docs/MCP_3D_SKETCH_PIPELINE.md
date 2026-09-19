# QUY TRÌNH CHUẨN CÔNG NGHIỆP: TỪ PHÁC THẢO KỸ THUẬT 2D SANG 3D BLENDER & WEBGL THREE.JS
## (MCP 3D SKETCH-TO-MODEL INDUSTRIAL PIPELINE & 4 HARD GATEKEEPERS)

---

## 1. TỔNG QUAN & NGUYÊN TẮC CỐT LÕI (OVERVIEW)

Quy trình này giải quyết triệt để vấn đề "Làm ẩu, làm tắt, đoán mò thông số toán học" dẫn đến mô hình 3D sai lệch thực tế vật lý và giải phẫu học (ví dụ: tay lơ lửng không cầm mái chèo, chân không đạp sàn, mái chèo không chạm nước, không có điểm tựa đòn bẩy).

### Nguyên Tắc Bất Di Bất Dịch:
1. **"No Sketch, No 3D" (Không phác thảo kỹ thuật 2D - Cấm tuyệt đối mở 3D Blender)**: Mọi mô hình nhân vật, phương tiện chiến đấu bắt buộc phải có bản vẽ trực giao kỹ thuật 4 góc nhìn chuẩn mực trước khi tạo mesh hoặc dựng xương.
2. **Khóa Lỗi Tự Động Chuẩn Alibaba Open-Code-Review (Hard Gatekeepers)**: Tương tự cơ chế Git Pre-Commit khóa chặt lỗi code bằng `Exit Code 1`, quy trình 3D áp dụng 4 tầng chốt chặn bắt buộc đo đạc hình học và vật lý thực. Nếu sai bất kỳ chỉ số nào $\to$ **DỪNG TOÀN BỘ TIẾN TRÌNH (ABORT / EXIT CODE 1)** và kích hoạt Vòng lặp Tự vá lỗi (Self-Healing Loop).

---

## 2. KIẾN TRÚC CÁC CÔNG CỤ & MCP SERVER THỰC TẾ

| Thành phần | Công nghệ / Gói mã nguồn | Vai trò & Trách nhiệm |
| :--- | :--- | :--- |
| **Bản vẽ Phác thảo 2D** | 2D Orthographic Technical Sheet (PNG/JPG) | Định nghĩa góc nhìn nghiêng (Side View Profile), từ trên xuống (Top View), cơ cấu bóp tay (Hand Power Grip), điểm tì đòn bẩy (Fulcrum). |
| **Blender MCP Server** | `mcp-for-blender` (`ahujasid/mcp-for-blender` v0.1.0) | Cổng giao tiếp JSON-RPC Socket (Port 9876) cho phép AI điều khiển trực tiếp Blender: nạp mesh, gắn vật liệu, điều khiển pose bones, render và xuất GLTF/GLB. |
| **Khớp Camera Trực Giao** | Addon `fSpy` + `fSpy-Blender` | Tự động tính toán tiêu cự (Focal Length), độ nghiêng góc nhìn (Vanishing Points) từ ảnh 2D vào Blender Camera. |
| **Nhân trắc học & Giải phẫu** | `MB-Lab` (Manuel Bastioni Lab) / MakeHuman | Sinh khung cơ thể người trưởng thành chuẩn nhân trắc học Việt Nam cổ (cao 1m58 - 1m62, cơ bắp cuồn cuộn, da rám nắng). |
| **Dựng Xương & IK** | `Rigify` / `Auto-Rig Pro` / FK Bone Constraints | Tạo hệ thống xương có IK Constraints giúp bàn tay tự động khóa chặt vào cán chèo và bàn chân khóa chặt vào thanh giằng sàn thuyền. |
| **Bộ Kiểm Tra Khóa Lỗi** | `scripts/verify_all_3d_gates.py` | Đo đạc sai số hình học bằng Python BMesh/Vector math, trả về `Exit Code 0` (PASS) hoặc `Exit Code 1` (FAIL). |
| **Hiển thị Thời Gian Thực** | Three.js WebGL (WebAssembly PBR Renderer) | Tải mô hình GLB nén Draco, áp dụng shader PBR, mô phỏng sóng nước và kiểm thử giao diện bằng Playwright. |

---

## 3. CHI TIẾT 4 CHỐT CHẶN CỨNG BẰNG MÃ NGUỒN (4 HARD GATEKEEPERS)

```
       [BẢN VẼ PHÁC THẢO 2D]
                │
                ▼
   ┌───────────────────────────┐
   │ GATE 1: Blueprint Plane   │ ──(FAIL: Thiếu ảnh/Plane)──> [ABORT / EXIT 1]
   └───────────────────────────┘
                │ PASS
                ▼
   ┌───────────────────────────┐
   │ GATE 2: Anatomy & Snapping│ ──(FAIL: Tay hở > 3.5cm / Mông hở > 4cm)──> [ABORT / EXIT 1]
   └───────────────────────────┘
                │ PASS
                ▼
   ┌───────────────────────────┐
   │ GATE 3: Hydrodynamics     │ ──(FAIL: Chìm nước < 20cm / Lệch cọc)──> [ABORT / EXIT 1]
   └───────────────────────────┘
                │ PASS
                ▼
   ┌───────────────────────────┐
   │ GATE 4: Visual IoU & WebGL│ ──(FAIL: Console Error / FPS < 30)──> [ABORT / EXIT 1]
   └───────────────────────────┘
                │ PASS
                ▼
       [XUẤT GLB & COMMIT GIT]
```

### Gate 1: Blueprint Reference Verification (Xác minh Mặt phẳng Tham chiếu 2D)
- **Cơ chế**: Quét cây phân cấp Scene trong Blender. Bắt buộc phải tồn tại Object Mesh `REFERENCE_BLUEPRINT_PLANE` có chứa hình ảnh phác thảo kỹ thuật 2D gốc với tỷ lệ chuẩn ($3.4\text{m} \times 1.9\text{m}$) và vật liệu bán trong suốt (`Alpha = 0.5`).
- **Khóa lỗi**: Nếu thiếu file ảnh hoặc thiếu object plane $\to$ `raise GateViolationError("GATE 1 FAILED: Không tìm thấy Blueprint Reference Plane trong Scene!")` $\to$ Exit Code 1.

### Gate 2: Anatomy & Mechanics Snapping Gatekeeper (Bắt điểm Giải phẫu & Tiếp xúc Cơ học)
- **Tiêu chuẩn đo đạc**:
  1. **Bàn tay cuộn tròn ôm trọn cán chèo (Power Grip)**:
     - Đo khoảng cách Euclid giữa điểm tâm bàn tay (`hand.L`, `hand.R`) tới trục cán chèo gỗ:
       $$\text{Distance}(\mathbf{P}_{\text{hand}}, \text{Axis}_{\text{oar}}) \le 0.035\text{m} \quad (3.5\text{cm})$$
     - Triệt tiêu 100% tình trạng bàn tay xòe thẳng đơ lơ lửng không chạm chèo.
  2. **Tiếp xúc bục ván ngồi (Thwart Snapping)**:
     - Đáy xương chậu/mông (`pelvis`) và đùi (`thigh`) dán phẳng vào mặt phẳng trên của ván ngồi:
       $$|\mathbf{Z}_{\text{pelvis\_bottom}} - \mathbf{Z}_{\text{thwart\_top}}| \le 0.04\text{m} \quad (4.0\text{cm})$$
  3. **Bàn chân đạp thanh giằng (Footrest Brace)**:
     - Bàn chân duỗi đạp trực tiếp lên nẹp gỗ sàn thuyền, cấm lơ lửng trong không khí.
- **Khóa lỗi**: Nếu bất kỳ chỉ số nào vượt ngưỡng cho phép $\to$ Exit Code 1.

### Gate 3: Rowing Hydrodynamics Gatekeeper (Động lực học & Thủy lực Chèo Thuyền)
- **Tiêu chuẩn vật lý**:
  1. **Độ ngập nước của lưỡi chèo (Water Immersion)**:
     - Lưỡi chèo bắt buộc phải cắm chìm sâu hoàn toàn dưới mực nước sông Bạch Đằng tối thiểu $20\text{cm}$:
       $$\mathbf{Z}_{\text{blade\_tip}} \le \mathbf{Z}_{\text{water\_level}} - 0.20\text{m}$$
  2. **Góc nghiêng cán chèo (Oar Incline Angle)**:
     - Cán chèo dốc xuống mặt nước một góc từ $25^\circ$ đến $35^\circ$.
  3. **Điểm tựa đòn bẩy cọc chèo (Fulcrum Contact)**:
     - Cán chèo phải tựa tì khít vào cọc chèo gỗ (`Thole Pin`) trên mạn thuyền:
       $$\text{Distance}(\mathbf{P}_{\text{oar}}, \mathbf{P}_{\text{thole\_pin}}) \le 0.04\text{m}$$
- **Khóa lỗi**: Nếu mái chèo quạt trên không hoặc lơ lửng trên mặt nước $\to$ Exit Code 1.

### Gate 4: Visual IoU & WebGL Real-Performance Gatekeeper (Nghiệm thu WebGL)
- **Tiêu chuẩn kiểm thử**:
  1. Chụp render trực giao Side View từ Blender đối chiếu với bản phác thảo 2D gốc (đảm bảo độ trùng khớp tư thế đạt tương quan $\ge 90\%$).
  2. Xuất file GLB chuẩn Web, tải vào Three.js và chạy kiểm thử tự động Playwright:
     - Số lỗi F12 Console: Bắt buộc bằng $0$.
     - Tốc độ khung hình: Duy trì $\ge 30\text{ FPS}$ (khuyến nghị $\ge 60\text{ FPS}$).
- **Khóa lỗi**: Nếu console có lỗi nạp tài nguyên hoặc vỡ mô hình $\to$ Exit Code 1.

---

## 4. VÒNG LẶP TỰ VÁ LỖI TỰ ĐỘNG (SELF-HEALING LOOP)

Khi script `scripts/verify_all_3d_gates.py` trả về `Exit Code 1`:
1. Trợ lý AI đọc chính xác dòng thông báo lỗi và giá trị đo đạc vi phạm (ví dụ: `hand.L distance = 0.082m > 0.035m`).
2. Tự động gọi Blender MCP gửi script nắn lại góc quay của Pose Bones hoặc di chuyển tọa độ mesh cho tới khi lọt vào khoảng dung sai cho phép.
3. Chạy lại `scripts/verify_all_3d_gates.py`.
4. Chỉ khi toàn bộ 4 Gates đều trả về **`ALL GATES PASSED (100%)`** thì mới được phép bàn giao sản phẩm hoặc tạo Git commit.
