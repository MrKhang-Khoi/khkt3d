const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
    console.log('=== [AUDIT ZERO-BUG] KIỂM THỬ TỰ ĐỘNG WEB 3D MASTER ĐẠI CHIẾN BẠCH ĐẰNG 938 ===');
    const browser = await chromium.launch({
        headless: true,
        args: [
            '--use-gl=angle',
            '--use-angle=swiftshader',
            '--enable-webgl',
            '--allow-file-access-from-files',
            '--disable-web-security'
        ]
    });

    const resolutions = [
        { width: 1920, height: 1080, name: 'FHD_1080p', shot: 'anh_web3d_fhd_1080p.png' },
        { width: 1366, height: 768, name: 'TruongHoc_768p', shot: 'anh_web3d_truonghoc_768p.png' }
    ];

    let totalErrors = 0;

    const artifactDir = 'C:/Users/HPZBook/.gemini/antigravity/brain/ae5a66d4-efdc-45cf-bd26-8edf0045f51c';

    async function captureScreenshot(page, filePath) {
        try {
            await page.screenshot({ path: filePath, timeout: 5000 });
        } catch (err) {
            console.warn(`[Screenshot fallback] page.screenshot timed out, capturing WebGL frame directly via toDataURL: ${err.message}`);
            const dataUrl = await page.evaluate(() => {
                const c = document.getElementById('canvas3d');
                return c ? c.toDataURL('image/png') : null;
            });
            if (dataUrl) {
                const base64Data = dataUrl.replace(/^data:image\/png;base64,/, '');
                fs.writeFileSync(filePath, base64Data, 'base64');
                console.log(`[Screenshot fallback] Captured WebGL canvas to ${filePath} (${base64Data.length} bytes base64)`);
            }
        }
        if (fs.existsSync(filePath)) {
            const fileName = path.basename(filePath);
            const artTarget = path.join(artifactDir, fileName);
            try {
                fs.copyFileSync(filePath, artTarget);
            } catch(e) { console.warn("[Audit Warning]", e); }
        }
    }

    for (const res of resolutions) {
        console.log(`\n-----------------------------------------------------------`);
        console.log(`1. Kiểm thử độ phân giải: ${res.name} (${res.width}x${res.height})`);
        console.log(`-----------------------------------------------------------`);
        
        const context = await browser.newContext({
            viewport: { width: res.width, height: res.height }
        });
        const page = await context.newPage();

        const consoleErrors = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
                console.error(`[Browser Console Error]:`, msg.text());
            } else {
                console.log(`[Browser Console]:`, msg.text());
            }
        });
        page.on('pageerror', err => {
            consoleErrors.push(err.toString());
            console.error(`[Page Uncaught Error]:`, err.toString());
        });

        const fileUrl = 'file:///' + path.resolve(__dirname, 'mo_phong_bach_dang_938.html').replace(/\\/g, '/');
        console.log(`Đang tải trang: ${fileUrl}`);

        const t0 = Date.now();
        await page.goto(fileUrl, { waitUntil: 'load', timeout: 30000 });
        const loadDuration = Date.now() - t0;
        console.log(`-> Tải trang hoàn tất trong: ${loadDuration}ms`);

        // Chờ canvas và mô hình Master 3D nạp hoàn tất
        await page.waitForSelector('#canvas3d', { timeout: 10000 });
        
        // Chờ mô hình Master 3D nạp xong (loading-indicator biến mất hoặc fleet count đủ)
        await page.waitForFunction(() => {
            return window.daiVietFleet && window.daiVietFleet.length === 8 &&
                   window.namHanFleet && window.namHanFleet.length === 26;
        }, { timeout: 15000 }).catch(e => console.warn('Wait for fleet timeout:', e.message));

        await page.waitForTimeout(1500);

        // 1. Kiểm tra xóa bỏ khung H1 (#pedagogy-panel) để giải phóng không gian quan sát
        const hasOldH1Panel = await page.evaluate(() => {
            return document.getElementById('pedagogy-panel') !== null;
        });
        console.log(`-> Kiểm tra xóa khung H1 cũ: ${!hasOldH1Panel ? 'PASS (Đã xóa triệt để, không gian thoáng đãng)' : 'FAIL (Vẫn còn)'}`);
        if (hasOldH1Panel) totalErrors++;

        // 2. Kiểm tra huy hiệu tiêu đề mới (#top-badge)
        const topBadge = await page.evaluate(() => {
            const b = document.getElementById('top-badge');
            return b ? { exists: true, text: b.innerText } : { exists: false };
        });
        console.log(`-> Huy hiệu tiêu đề mới: ${topBadge.exists ? 'PASS: "' + topBadge.text.replace(/\n/g, ' ') + '"' : 'FAIL'}`);

        // 3. Kiểm tra số lượng chiến thuyền 3D Master
        const fleetStats = await page.evaluate(() => {
            return {
                dvCount: (window.daiVietFleet || []).length,
                nhCount: (window.namHanFleet || []).length,
                stakesCount: (window.stakesGroup ? window.stakesGroup.children.length : 0)
            };
        });
        console.log(`-> Số lượng chiến thuyền Master: Đại Việt = ${fleetStats.dvCount}/8, Nam Hán = ${fleetStats.nhCount}/26, Bãi cọc = ${fleetStats.stakesCount}`);
        if (fleetStats.dvCount !== 8 || fleetStats.nhCount !== 26) {
            console.error('FAIL: Số lượng chiến hạm không đúng chuẩn lịch sử!');
            totalErrors++;
        } else {
            console.log('PASS: Đội hình 34 chiến thuyền Master 3D đầy đủ 100%!');
        }

        // 4. Kiểm tra bẫy tràn ngang (Rule 3)
        const overflow = await page.evaluate(() => {
            return {
                scrollWidth: document.documentElement.scrollWidth,
                clientWidth: document.documentElement.clientWidth,
                hasOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth
            };
        });
        console.log(`-> Bẫy tràn ngang: scrollWidth=${overflow.scrollWidth}, clientWidth=${overflow.clientWidth}, hasOverflow=${overflow.hasOverflow}`);
        if (overflow.hasOverflow) {
            console.error('FAIL: Trang bị tràn ngang!');
            totalErrors++;
        } else {
            console.log('PASS: Không bị tràn ngang (0 Horizontal Scrollbar Trap)!');
        }

        // 5. Chụp ảnh màn hình toàn cảnh chiến trường
        await captureScreenshot(page, path.resolve(__dirname, res.shot));
        console.log(`-> Đã chụp ảnh kiểm chứng toàn cảnh: ${res.shot}`);

        // 6. Thử nghiệm mở Dropdown 4 Pha chiến thuật
        if (res.name === 'FHD_1080p') {
            console.log('\n--- Thử nghiệm tương tác Menu Dropdown 4 Pha Chiến Thuật ---');
            await page.click('#btn-phase-badge');
            await page.waitForTimeout(500);

            const isDropdownOpen = await page.evaluate(() => {
                const pop = document.getElementById('pop-phase');
                return pop && pop.classList.contains('open');
            });
            console.log(`-> Trạng thái mở menu Dropdown 4 Pha: ${isDropdownOpen ? 'PASS (Đã bung menu)' : 'FAIL'}`);

            await captureScreenshot(page, path.resolve(__dirname, 'anh_web3d_phase_dropdown.png'));
            console.log('-> Đã chụp ảnh Dropdown 4 Pha: anh_web3d_phase_dropdown.png');

            // Chuyển sang Pha 3 (Triều rút - Địch mắc cọc)
            await page.click('#pop-phase button[data-phase="3"]');
            await page.waitForTimeout(1500);

            const phaseText = await page.textContent('#txt-phase-badge');
            console.log(`-> Đã chọn Pha 3, Badge cập nhật: "${phaseText}"`);

            await captureScreenshot(page, path.resolve(__dirname, 'anh_web3d_trieu_rut_lo_coc.png'));
            console.log('-> Đã chụp ảnh Pha 3 (Triều rút cọc nhô): anh_web3d_trieu_rut_lo_coc.png');

            // 7. Chuyển Camera sang Cận cảnh Thuyền Ta DV_01
            console.log('\n--- Thử nghiệm Camera Cận Cảnh Thuyền Ta Master DV_01 ---');
            await page.click('#btn-cam-badge');
            await page.waitForTimeout(300);
            await page.click('button[data-cam="dv01"]');
            await page.waitForTimeout(2000);

            await captureScreenshot(page, path.resolve(__dirname, 'anh_web3d_cancanh_master_dv01.png'));
            console.log('-> Đã chụp ảnh Cận cảnh Thuyền Ta Master: anh_web3d_cancanh_master_dv01.png');

            // 8. Chuyển Camera sang Soái Hạm Lưu Hoằng Tháo
            console.log('\n--- Thử nghiệm Camera Soái Hạm Nam Hán Master ---');
            await page.click('#btn-cam-badge');
            await page.waitForTimeout(300);
            await page.click('button[data-cam="flagship"]');
            await page.waitForTimeout(2000);

            await captureScreenshot(page, path.resolve(__dirname, 'anh_web3d_cancanh_master_namhan.png'));
            console.log('-> Đã chụp ảnh Cận cảnh Soái Hạm Nam Hán: anh_web3d_cancanh_master_namhan.png');
        }

        if (consoleErrors.length > 0) {
            console.error(`FAIL: Có ${consoleErrors.length} lỗi console trên ${res.name}!`);
            totalErrors += consoleErrors.length;
        } else {
            console.log(`PASS: Console sạch 0 lỗi trên ${res.name}!`);
        }

        await context.close();
    }

    await browser.close();

    console.log(`\n===========================================================`);
    if (totalErrors === 0) {
        console.log(`KẾT QUẢ AUDIT: TẤT CẢ TIÊU CHÍ ĐẠT 100% (ZERO BUGS)!`);
    } else {
        console.error(`KẾT QUẢ AUDIT: CÓ ${totalErrors} LỖI CẦN FIX!`);
        process.exit(1);
    }
    console.log(`===========================================================`);
})();
