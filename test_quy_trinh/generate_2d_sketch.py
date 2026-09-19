import os, sys, math
from PIL import Image, ImageDraw

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

W, H = 1920, 1080
img = Image.new("RGB", (W, H), (246, 243, 235))
draw = ImageDraw.Draw(img)

# 1. Lưới kỹ thuật
grid_color = (230, 225, 212)
for x in range(0, W, 40):
    draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
for y in range(0, H, 40):
    draw.line([(y, 0), (y, W)], fill=grid_color, width=1)

# 2. Khung viền
draw.rectangle([(30, 30), (W - 30, H - 30)], outline=(80, 70, 60), width=3)
draw.rectangle([(38, 38), (W - 38, H - 38)], outline=(120, 110, 100), width=1)

# 3. Tiêu đề
draw.text((70, 55), "BAN VE PHAC THAO KY THUAT 2D: COC GO BIT SAT BACH DANG (NAM 938)", fill=(40, 30, 20))
draw.text((70, 85), "TIEU CHUAN KHAO CO HOC QUOC GIA - CHIEN THANG BACH DANG NGO QUYEN | TY LE 1:15", fill=(100, 80, 60))
draw.line([(70, 115), (1100, 115)], fill=(120, 100, 80), width=2)

# --- KHUNG 1: SIDE VIEW PROFILE ---
draw.text((120, 140), "GOC CHIEU NGHIENG TRUC GIAO (SIDE VIEW PROFILE)", fill=(40, 35, 30))

# Tầng bùn cát
draw.rectangle([(80, 720), (1050, 980)], fill=(225, 215, 195), outline=(140, 120, 100), width=2)
draw.text((100, 735), "TANG BUN SET DAY SONG BACH DANG (CAM SAU >= 1.0m)", fill=(100, 80, 60))
for sx in range(100, 1030, 35):
    draw.line([(sx, 760), (sx + 20, 780)], fill=(180, 160, 140), width=1)

# Mực nước
draw.line([(80, 360), (1050, 360)], fill=(70, 130, 180), width=2)
draw.text((100, 335), "MUC NUOC THUY TRIEU DANG CAO (+2.4m) -> CHE KHUAT HOAN TOAN COC SAT", fill=(50, 100, 150))

draw.line([(80, 490), (1050, 490)], fill=(200, 90, 60), width=2)
draw.text((100, 465), "MUC NUOC THUY TRIEU RUT (+1.5m) -> MUI SAT NHO LEN DAM LUON THUYEN GIAC", fill=(180, 60, 30))

c_wood_dark = (100, 65, 35)
c_wood_light = (160, 120, 75)
c_iron = (60, 65, 75)

# Thân gỗ
p_goc_L = (480, 900)
p_goc_R = (550, 900)
p_top_L = (645, 410)
p_top_R = (700, 410)
draw.polygon([p_goc_L, p_goc_R, p_top_R, p_top_L], fill=c_wood_light, outline=c_wood_dark, width=3)

for offset in [-15, 0, 15]:
    draw.line([(515 + offset, 890), (672 + offset, 420)], fill=(120, 80, 45), width=2)

for ry in range(430, 710, 20):
    draw.arc([(640 + (ry-400)*0.18, ry), (670 + (ry-400)*0.18, ry+12)], 0, 180, fill=(70, 110, 60), width=2)

# Đầu bịt sắt
p_iron_tip = (715, 270)
draw.polygon([p_top_L, p_top_R, p_iron_tip], fill=c_iron, outline=(30, 35, 40), width=3)
draw.line([(672, 410), p_iron_tip], fill=(100, 105, 115), width=2)

# Đai sắt
draw.polygon([(640, 410), (705, 410), (708, 435), (637, 435)], fill=(45, 50, 55), outline=(20, 25, 30), width=2)
for rx in [652, 672, 692]:
    draw.ellipse([(rx - 4, 422 - 4), (rx + 4, 422 + 4)], fill=(180, 160, 120), outline=(20, 20, 20))

# Kích thước
draw.line([(760, 270), (790, 270)], fill=(80, 80, 80), width=1)
draw.line([(760, 900), (790, 900)], fill=(80, 80, 80), width=1)
draw.line([(775, 270), (775, 900)], fill=(140, 40, 30), width=2)
draw.text((790, 560), "TONG CHIEU DAI: 2.80m", fill=(140, 40, 30))

draw.line([(740, 270), (740, 410)], fill=(30, 60, 140), width=2)
draw.text((750, 330), "MUI SAT: 0.40m", fill=(30, 60, 140))

draw.arc([(540, 650), (620, 730)], 250, 290, fill=(180, 60, 30), width=2)
draw.text((610, 660), "Goc cam: 20 deg", fill=(180, 60, 30))

# --- KHUNG 2: CHI TIẾT ĐẦU BỊT SẮT ---
box2_x = 1120
draw.rectangle([(box2_x, 140), (W - 50, 520)], outline=(100, 90, 80), width=2)
draw.text((box2_x + 20, 155), "CHI TIET DAU COC BIT SAT (IRON CAP 4-FACET DETAIL)", fill=(40, 35, 30))

tip_x = box2_x + 250
tip_y = 230
draw.polygon([(tip_x - 90, 420), (tip_x + 90, 420), (tip_x, tip_y)], fill=(70, 75, 85), outline=(20, 25, 30), width=3)
draw.polygon([(tip_x, 420), (tip_x + 90, 420), (tip_x, tip_y)], fill=(50, 55, 65))
draw.line([(tip_x, 420), (tip_x, tip_y)], fill=(130, 135, 145), width=3)

draw.rectangle([(tip_x - 96, 420), (tip_x + 96, 455)], fill=(40, 45, 50), outline=(15, 20, 25), width=2)
for d_x in [tip_x - 65, tip_x - 20, tip_x + 25, tip_x + 70]:
    draw.ellipse([(d_x - 6, 437 - 6), (d_x + 6, 437 + 6)], fill=(190, 150, 100), outline=(20, 20, 20), width=2)
draw.text((box2_x + 40, 470), "- Sat ren nguoi 4 canh sac ben (dai 40cm, rong 18cm)", fill=(60, 50, 40))
draw.text((box2_x + 40, 492), "- 4 dinh tan sat xuyen than go chong tuot khi va dap", fill=(60, 50, 40))

# --- KHUNG 3: TOP VIEW & THÔNG SỐ PBR ---
draw.rectangle([(box2_x, 540), (W - 50, 980)], outline=(100, 90, 80), width=2)
draw.text((box2_x + 20, 555), "GOC CHIEU TU TREN XUONG (TOP VIEW) & DAC TA KY THUAT", fill=(40, 35, 30))

cx, cy = box2_x + 140, 680
draw.ellipse([(cx - 70, cy - 70), (cx + 70, cy + 70)], fill=c_wood_light, outline=c_wood_dark, width=3)
draw.polygon([(cx - 45, cy), (cx, cy - 45), (cx + 45, cy), (cx, cy + 45)], fill=c_iron, outline=(20, 25, 30), width=2)
draw.line([(cx - 45, cy), (cx + 45, cy)], fill=(120, 125, 135), width=2)
draw.line([(cx, cy - 45), (cx, cy + 45)], fill=(120, 125, 135), width=2)
draw.ellipse([(cx - 4, cy - 4), (cx + 4, cy + 4)], fill=(240, 240, 255))
draw.text((cx - 55, cy + 85), "Thiet dien: D = 28cm", fill=(60, 50, 40))

draw.text((box2_x + 280, 610), "[THONG SO VAT LIEU PBR CHUAN XAC]", fill=(120, 40, 30))
draw.text((box2_x + 280, 645), "1. Than coc: Go Lim/Tau nguyen than ngam nuoc man", fill=(50, 45, 40))
draw.text((box2_x + 280, 675), "   - Roughness: 0.85, Bump: Vet tho nut go gia", fill=(80, 75, 70))
draw.text((box2_x + 280, 705), "   - Albedo: Nau den sam pha reu xanh day song", fill=(80, 75, 70))
draw.text((box2_x + 280, 740), "2. Dau bit sat: Sat ren tho the ky X (Wrought Iron)", fill=(50, 45, 40))
draw.text((box2_x + 280, 770), "   - Metalness: 0.90, Roughness: 0.55", fill=(80, 75, 70))
draw.text((box2_x + 280, 800), "   - Hieu ung ri set oxy hoa nuoc lo (Iron Oxide)", fill=(80, 75, 70))
draw.text((box2_x + 280, 835), "3. Tang nen: Bun set Bach Dang nen chat neo coc", fill=(50, 45, 40))
draw.text((box2_x + 280, 865), "   - Do sau chim trong bun: 1.00m (chiu xung luc tau)", fill=(80, 75, 70))

draw.rectangle([(box2_x + 280, 905), (W - 80, 960)], fill=(230, 240, 230), outline=(60, 130, 60), width=2)
draw.text((box2_x + 300, 922), "GATE 1 APPROVED: BAN PHAC THAO DAT CHUAN KHAO CO & VAT LY", fill=(30, 100, 30))

out_sketch_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/references/phac_thao_coc_bach_dang_2d.png'
img.save(out_sketch_path, quality=95)
print("Xuat phac thao 2D thanh cong:", out_sketch_path)

artifact_dir = r'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c'
artifact_copy = os.path.join(artifact_dir, 'phac_thao_coc_bach_dang_2d.png')
img.save(artifact_copy, quality=95)
print("Copy sang artifact thanh cong:", artifact_copy)
