const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    
    await page.goto('http://localhost:8080', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Tìm các nút camera hoặc chọn góc nhìn
    const viewBtn = await page.$('button:has-text("GÓC NHÌN")') || await page.$('[id*="camera"]') || await page.$('.control-btn');
    if (viewBtn) {
        await viewBtn.click();
        await page.waitForTimeout(1000);
    }
    
    // Chụp cận cảnh
    const closeupPath = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c/anh_web3d_cancanh_powergrip_flawless.png';
    await page.screenshot({ path: closeupPath });
    console.log("Captured closeup to:", closeupPath);
    await browser.close();
})();
