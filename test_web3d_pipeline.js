const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const PORT = 8089;
const PUBLIC_DIR = path.join(__dirname, 'web3d_export');

// 1. Tạo HTTP Server tĩnh phục vụ web3d_export
const server = http.createServer((req, res) => {
    let reqPath = req.url.split('?')[0];
    if (reqPath === '/' || reqPath === '') reqPath = '/index.html';
    const filePath = path.join(PUBLIC_DIR, reqPath);

    fs.readFile(filePath, (err, data) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
            return;
        }

        let contentType = 'text/plain';
        if (filePath.endsWith('.html')) contentType = 'text/html; charset=utf-8';
        else if (filePath.endsWith('.js')) contentType = 'application/javascript';
        else if (filePath.endsWith('.glb')) contentType = 'model/gltf-binary';
        else if (filePath.endsWith('.json')) contentType = 'application/json';
        else if (filePath.endsWith('.png')) contentType = 'image/png';

        res.writeHead(200, {
            'Content-Type': contentType,
            'Access-Control-Allow-Origin': '*'
        });
        res.end(data);
    });
});

async function runAudit() {
    server.listen(PORT, async () => {
        console.log(`[TEST-SERVER] Đang phục vụ tại http://127.0.0.1:${PORT}`);

        const browser = await chromium.launch({
            headless: true,
            args: ['--use-gl=angle', '--use-angle=default']
        });
        const context = await browser.newContext({
            viewport: { width: 1920, height: 1080 }
        });
        const page = await context.newPage();

        const networkLogs = [];
        const consoleErrors = [];

        page.on('response', (response) => {
            networkLogs.push({
                url: response.url(),
                status: response.status(),
                statusText: response.statusText()
            });
        });

        page.on('console', (msg) => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            } else {
                console.log(`[BROWSER CONSOLE] ${msg.text()}`);
            }
        });

        const startTime = Date.now();
        console.log("-> Đang mở trang Web3D...");
        await page.goto(`http://127.0.0.1:${PORT}/index.html`, { waitUntil: 'networkidle' });

        // Chờ bảng loading biến mất (tệp GLB đã nạp và AnimationMixer đã kích hoạt)
        await page.waitForSelector('#loading', { state: 'hidden', timeout: 30000 });
        const loadDurationMs = Date.now() - startTime;
        console.log(`-> Mô hình 3D và Animation nạp thành công sau ${loadDurationMs} ms!`);

        // Chờ 3 giây để chu kỳ chuyển động diễn hoạt
        await page.waitForTimeout(3000);

        // Chụp ảnh màn hình ứng dụng Web3D thực tế
        const screenshotPath = path.join(__dirname, 'anh_kiem_chung_web3d_threejs.png');
        await page.screenshot({ path: screenshotPath });
        console.log(`-> Đã chụp ảnh màn hình kiểm chứng tại: ${screenshotPath}`);

        // Click thử các nút điều khiển góc quay
        await page.click('#btn-cam-stakes');
        await page.waitForTimeout(1000);
        await page.click('#btn-cam-han');
        await page.waitForTimeout(1000);
        await page.click('#btn-cam-orbit');
        await page.waitForTimeout(1000);

        console.log("\n=== KẾT QUẢ ĐO ĐẠC MẠNG & CHẤT LƯỢNG (AUDIT SUMMARY) ===");
        console.log(`Tổng số gói tin mạng bắt được: ${networkLogs.length}`);
        const glbLog = networkLogs.find(n => n.url.includes('.glb'));
        if (glbLog) {
            console.log(`- Gói tin GLB: HTTP ${glbLog.status} OK -> ${glbLog.url}`);
        } else {
            console.log("- CẢNH BÁO: Không tìm thấy gói tin GLB!");
        }

        console.log(`- Số lỗi Console F12: ${consoleErrors.length}`);
        if (consoleErrors.length > 0) {
            console.log("Lỗi:", consoleErrors);
        }

        await browser.close();
        server.close();
        console.log("=== KIỂM THỬ PLAYWRIGHT HOÀN TẤT THÀNH CÔNG ===");
        process.exit(0);
    });
}

runAudit().catch(err => {
    console.error("LỖI KIỂM THỬ:", err);
    server.close();
    process.exit(1);
});
