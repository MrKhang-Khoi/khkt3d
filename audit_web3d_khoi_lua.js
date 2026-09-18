const { chromium } = require('playwright');
const path = require('path');

(async () => {
    console.log('=== BẮT ĐẦU AUDIT WEB3D KHÓI LỬA BẠCH ĐẰNG 938 VỚI PLAYWRIGHT ===');
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

    const artifactDir = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c';

    for (const res of resolutions) {
        console.log(`\n--- Kiểm thử độ phân giải: ${res.name} (${res.width}x${res.height}) ---`);
        const context = await browser.newContext({
            viewport: { width: res.width, height: res.height }
        });
        const page = await context.newPage();

        const consoleErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') consoleErrors.push(msg.text());
            else if (msg.text().includes('MASTER 3D') || msg.text().includes('VIETNAM-SIM')) {
                console.log(`[Browser Console]: ${msg.text()}`);
            }
        });
        page.on('pageerror', err => consoleErrors.push(err.toString()));

        const fileUrl = 'file:///C:/Users/HPZBook/Desktop/TEST_BLENDER/mo_phong_bach_dang_938.html';
        console.log('Đang tải trang:', fileUrl);

        const startTime = Date.now();
        await page.goto(fileUrl, { waitUntil: 'load', timeout: 30000 });
        const loadTime = Date.now() - startTime;
        console.log(`-> Tải trang xong trong: ${loadTime}ms`);

        await page.waitForSelector('#canvas3d', { timeout: 10000 });
        await page.waitForTimeout(3000);

        // Kích hoạt Pha 3: Địch Mắc Cọc & Bốc Cháy
        console.log('-> Kích hoạt Pha 3: Triều rút & Tàu địch bốc cháy...');
        await page.evaluate(() => {
            if (typeof setBattlePhase === 'function') {
                setBattlePhase(3, true);
            }
        });

        // Chờ 1.5s để ngọn lửa và khói bốc lên
        await page.waitForTimeout(2000);

        // Chuyển sang góc máy Hero Shot cận cảnh cháy tàu
        console.log('-> Chuyển camera sang Hero Shot Cận Cảnh Cháy Tàu...');
        await page.evaluate(() => {
            if (camTargets && camTargets.fire_closeup) {
                currentCamTarget = camTargets.fire_closeup;
                camera.position.copy(currentCamTarget.pos);
                controls.target.copy(currentCamTarget.look);
                controls.update();
            }
        });

        await page.waitForTimeout(1500);

        // Kiểm tra hiệu năng FPS
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

        // Chụp ảnh nghiệm thu Hero Shot
        const shotHero = path.join(artifactDir, `anh_web3d_khoi_lua_hero_${res.name}.png`);
        await page.screenshot({ path: shotHero, timeout: 15000 });
        console.log(`-> Đã chụp ảnh Hero Shot: ${shotHero}`);

        // Chuyển sang toàn cảnh chiến trường
        await page.evaluate(() => {
            if (camTargets && camTargets.headon) {
                currentCamTarget = camTargets.headon;
                camera.position.copy(currentCamTarget.pos);
                controls.target.copy(currentCamTarget.look);
                controls.update();
            }
        });
        await page.waitForTimeout(1000);

        const shotToanCanh = path.join(artifactDir, `anh_web3d_khoi_lua_toancanh_${res.name}.png`);
        await page.screenshot({ path: shotToanCanh, timeout: 15000 });
        console.log(`-> Đã chụp ảnh Toàn Cảnh: ${shotToanCanh}`);

        // Kiểm tra tràn ngang
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
        console.log(`-> Bẫy tràn ngang: ${overflow ? 'CÓ LỖI TRÀN' : 'CHUẨN 0 TRÀN NGANG'}`);

        console.log(`-> Lỗi Console F12: ${consoleErrors.length}`);
        if (consoleErrors.length > 0) {
            console.log('Các lỗi console:', consoleErrors);
        }

        await context.close();
    }

    await browser.close();
    console.log('\n=== KIỂM THỬ PLAYWRIGHT WEB3D HOÀN TẤT THÀNH CÔNG! ===');
})();
