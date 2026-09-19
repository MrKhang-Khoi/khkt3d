const { chromium } = require('playwright');

(async () => {
    console.log("=== CHẠY KIỂM THỬ WEBGL GATE 4 BẰNG PLAYWRIGHT ===");
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
        await page.goto('http://localhost:8080', { waitUntil: 'networkidle', timeout: 30000 });
        console.log("Page loaded successfully.");
        
        // Đợi WebGL render ổn định 4 giây
        await page.waitForTimeout(4000);
        
        const screenshotPath = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_web3d_kiemchung_powergrip_flawless.png';
        await page.screenshot({ path: screenshotPath });
        console.log("Captured WebGL screenshot to:", screenshotPath);
        
        if (errors.length === 0) {
            console.log(">>> GATE 4 PASS: 0 lỗi Console, WebGL Three.js tải tài nguyên hoàn hảo! <<<");
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
