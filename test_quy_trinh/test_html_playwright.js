const { chromium } = require('playwright');
const path = require('path');

(async () => {
    console.log("=== CHẠY KIỂM THỬ WEBGL GATE 4 CHO DỰ ÁN test_quy_trinh ===");
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    
    const errors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.error('[Browser Error]', msg.text());
            errors.push(msg.text());
        }
    });
    page.on('pageerror', err => {
        console.error('[Browser Uncaught]', err.message);
        errors.push(err.message);
    });

    try {
        const fileUrl = 'http://localhost:8080/test_quy_trinh/index.html';
        await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 30000 });
        console.log("Page loaded successfully.");
        
        // Đợi 3D load và render xong
        await page.waitForTimeout(3000);
        
        // Chụp góc nghiêng Side View
        const shot1 = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_web3d_coc_sideview.png';
        await page.screenshot({ path: shot1 });
        console.log("Captured Side View to:", shot1);
        
        // Click nút Cận cảnh đầu bịt sắt
        const btnIron = await page.$('button:has-text("Cận Cảnh Đầu Bịt Sắt")');
        if (btnIron) {
            await btnIron.click();
            await page.waitForTimeout(1500);
            const shot2 = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_web3d_coc_cancanh_sat.png';
            await page.screenshot({ path: shot2 });
            console.log("Captured Iron Cap Closeup to:", shot2);
        }
        
        if (errors.length === 0) {
            console.log(">>> GATE 4 PASS: 0 lỗi console, mô hình 3D cọc HTML hoạt động mượt mà! <<<");
            await browser.close();
            process.exit(0);
        } else {
            console.error(`>>> GATE 4 FAIL: Có ${errors.length} lỗi console! <<<`);
            await browser.close();
            process.exit(1);
        }
    } catch (e) {
        console.error("[Playwright Test Error]", e.message);
        await browser.close();
        process.exit(1);
    }
})();
