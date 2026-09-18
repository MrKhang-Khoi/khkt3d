@echo off
chcp 65001 > nul
echo ============================================================
echo   MÔ PHỎNG 3D ĐẠI CHIẾN BẠCH ĐẰNG 938 - THREE.JS WEB3D
echo ============================================================
echo.
echo [1] Đang khởi động sa bàn 3D trên trình duyệt mặc định...
cd /d "%~dp0"
start "" "index.html"
echo.
echo [OK] Đã mở sa bàn 3D thành công!
echo Bạn có thể xoay 360 độ, kéo thanh trượt thời gian và đổi góc quay.
echo.
pause
