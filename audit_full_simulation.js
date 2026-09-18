const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function audit() {
    console.log("=== BẮT ĐẦU KIỂM THỬ TOÀN DIỆN WEB3D PLAYWRIGHT (ZERO-BUG PIPELINE) ===");

    const browser = await chromium.launch({
        headless: true,
        args: ['--use-gl=angle', '--use-angle=default']
    });

    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    const page = await context.newPage();

    const consoleLogs = [];
    const consoleErrors = [];

    page.on('console', (msg) => {
        if (msg.type() === 'error') {
            consoleErrors.push(msg.text());
        } else {
            consoleLogs.push({ type: msg.type(), text: msg.text() });
        }
    });

    page.on('pageerror', (err) => {
        consoleErrors.push(err.message);
    });

    const fileUrl = 'file:///' + path.resolve(__dirname, 'web3d_export', 'index.html').replace(/\\/g, '/');
    console.log(`-> Mở tệp trực tiếp qua giao thức file://: ${fileUrl}`);

    const tStart = Date.now();
    await page.goto(fileUrl, { waitUntil: 'load', timeout: 30000 });

    // 1. Chờ nạp mô hình Base64
    await page.waitForSelector('#loading', { state: 'hidden', timeout: 20000 });
    const loadTime = Date.now() - tStart;
    console.log(`-> Nạp và khởi tạo WebGL thành công trong ${loadTime} ms!`);

    // 2. Chụp ảnh Pha 1 (Triều dâng)
    await page.waitForTimeout(1500);
    const shotPha1 = path.join(__dirname, 'audit_pha1_trieu_dang.png');
    await page.screenshot({ path: shotPha1 });
    console.log(`-> Đã chụp ảnh Pha 1: ${shotPha1}`);

    // 3. Tua đến Pha 2 (Frame 125 ~ 42% - Lâu thuyền đâm cọc)
    await page.evaluate(() => {
        const slider = document.getElementById('timeline-slider');
        slider.value = '0.42';
        slider.dispatchEvent(new Event('input'));
    });
    await page.waitForTimeout(1000);
    const shotPha2 = path.join(__dirname, 'audit_pha2_dam_coc.png');
    await page.screenshot({ path: shotPha2 });
    console.log(`-> Đã chụp ảnh Pha 2 (Đâm cọc): ${shotPha2}`);

    // 4. Đổi sang góc máy Cận Cảnh Bãi Cọc
    await page.click('#btn-cam-stakes');
    await page.waitForTimeout(800);
    const shotCoc = path.join(__dirname, 'audit_pha2_can_canh_coc.png');
    await page.screenshot({ path: shotCoc });
    console.log(`-> Đã chụp ảnh Cận Cảnh Bãi Cọc: ${shotCoc}`);

    // 5. Đổi sang góc máy Lâu Thuyền Địch
    await page.click('#btn-cam-han');
    await page.waitForTimeout(800);
    const shotHan = path.join(__dirname, 'audit_pha2_lau_thuyen_nghieng.png');
    await page.screenshot({ path: shotHan });
    console.log(`-> Đã chụp ảnh Lâu Thuyền Nghiêng: ${shotHan}`);

    // 6. Tua đến Pha 3 (Frame 240 ~ 80% - Triều kiệt, Đại Việt phản công)
    await page.evaluate(() => {
        const slider = document.getElementById('timeline-slider');
        slider.value = '0.80';
        slider.dispatchEvent(new Event('input'));
    });
    await page.click('#btn-cam-viet');
    await page.waitForTimeout(1000);
    const shotPha3 = path.join(__dirname, 'audit_pha3_phan_cong.png');
    await page.screenshot({ path: shotPha3 });
    console.log(`-> Đã chụp ảnh Pha 3 (Đại Việt phản công): ${shotPha3}`);

    // 7. Kiểm thử độ phân giải trường học 1366 x 768 (Rule 3)
    await page.setViewportSize({ width: 1366, height: 768 });
    await page.waitForTimeout(500);
    const overflowTrap = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    console.log(`-> Kiểm tra tràn ngang tại 1366x768 (scrollWidth > clientWidth): ${overflowTrap}`);

    // 8. Đọc nhãn trạng thái và tiến độ triều
    const bannerText = await page.textContent('#stage-banner');
    const tideText = await page.textContent('#tide-meter');
    console.log(`-> Trạng thái sân khấu hiện tại: "${bannerText}"`);
    console.log(`-> Mực nước triều đo đạc: "${tideText}"`);

    console.log(`\n=== TỔNG KẾT KIỂM ĐỊNH CHẤT LƯỢNG (AUDIT RESULT) ===`);
    console.log(`- Số lỗi Console F12: ${consoleErrors.length}`);
    if (consoleErrors.length > 0) {
        console.error("Lỗi:", consoleErrors);
    }
    console.log(`- Tràn khung ngang: ${overflowTrap ? "FAIL" : "PASS (0 bẫy tràn)"}`);
    console.log(`- Nạp mô hình file://: PASS`);

    await browser.close();

    if (consoleErrors.length === 0 && !overflowTrap) {
        console.log("=== TOÀN BỘ BÀI TEST ĐẠT CHUẨN 100% PASS ===");
        process.exit(0);
    } else {
        console.error("=== TEST THẤT BẠI ===");
        process.exit(1);
    }
}

audit().catch(err => {
    console.error("LỖI AUDIT:", err);
    process.exit(1);
});
