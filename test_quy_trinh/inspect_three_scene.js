const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    
    page.on('console', msg => console.log('[Console]', msg.text()));

    await page.goto('http://localhost:8080/test_quy_trinh/index.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);
    
    const info = await page.evaluate(() => {
        if (!window.scene) return "No window.scene";
        let objects = [];
        window.scene.traverse(o => {
            if (o.isMesh) {
                o.geometry.computeBoundingBox();
                const bb = o.geometry.boundingBox;
                objects.push({ name: o.name, min: bb.min, max: bb.max, pos: o.position });
            }
        });
        return objects;
    });
    console.log("Meshes in Three.js Scene:", JSON.stringify(info, null, 2));
    await browser.close();
})();
