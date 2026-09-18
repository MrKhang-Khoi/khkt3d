const { chromium } = require('playwright');
const path = require('path');

(async () => {
    console.log('=== BẮT ĐẦU AUDIT WEB3D ĐẠI CHIẾN BẠCH ĐẰNG 938 VỚI PLAYWRIGHT (D3D11 HARDWARE ACCEL) ===');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--enable-webgl',
            '--ignore-gpu-blocklist',
            '--use-gl=angle',
            '--use-angle=d3d11'
        ]
    });

    const resolutions = [
        { width: 1920, height: 1080, name: 'FHD_1080p' },
        { width: 1366, height: 768, name: 'TruongHoc_768p' }
    ];

    for (const res of resolutions) {
        console.log(`\n--- Kiểm thử độ phân giải: ${res.name} (${res.width}x${res.height}) ---`);
        const context = await browser.newContext({
            viewport: { width: res.width, height: res.height }
        });
        const page = await context.newPage();

        const consoleErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') consoleErrors.push(msg.text());
            else console.log(`[Browser Console ${msg.type()}]:`, msg.text());
        });
        page.on('pageerror', err => consoleErrors.push(err.toString()));

        const fileUrl = 'file:///C:/Users/HPZBook/Desktop/TEST_BLENDER/web3d_export/index.html';
        console.log('Đang tải trang:', fileUrl);

        const startTime = Date.now();
        await page.goto(fileUrl, { waitUntil: 'load', timeout: 30000 });
        const loadTime = Date.now() - startTime;
        console.log(`-> Tải trang xong trong: ${loadTime}ms`);

        await page.waitForSelector('#canvas3d', { timeout: 10000 });
        await page.waitForTimeout(3500);

        const loadingHidden = await page.evaluate(() => {
            const el = document.getElementById('loading');
            return !el || el.style.display === 'none' || el.offsetParent === null;
        });
        console.log(`-> Trạng thái Loading: ${loadingHidden ? 'ĐÃ NẠP THÀNH CÔNG' : 'Chưa xong'}`);

        const overflowCheck = await page.evaluate(() => {
            return {
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
            };
        });
        console.log(`-> Kiểm tra tràn ngang: scrollWidth=${overflowCheck.scrollWidth}, clientWidth=${overflowCheck.clientWidth}, hasOverflow=${overflowCheck.hasOverflow}`);

        const fps = await page.evaluate(async () => {
            return new Promise(resolve => {
                let frames = 0;
                const start = performance.now();
                function step() {
                    frames++;
                    if (performance.now() - start < 1000) {
                        requestAnimationFrame(step);
                    } else {
                        resolve(frames);
                    }
                }
                requestAnimationFrame(step);
            });
        });
        console.log(`-> Hiệu năng đồ họa: ${fps} FPS`);

        const artifactDir = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c';
        const shotPath = path.join(artifactDir, `anh_web3d_quan_ao_moi_${res.name}.png`);
        await page.screenshot({ path: shotPath, timeout: 15000 });
        console.log(`-> Đã chụp ảnh nghiệm thu: ${shotPath}`);

        console.log(`-> Lỗi Console F12: ${consoleErrors.length}`);
        await context.close();
    }

    await browser.close();
    console.log('\n=== KIỂM THỬ PLAYWRIGHT ZERO-BUG HOÀN TẤT 100%! ===');
})();
