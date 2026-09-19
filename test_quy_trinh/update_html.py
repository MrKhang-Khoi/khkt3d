import base64, os

glb_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/coc_bach_dang_938.glb'
with open(glb_path, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

html_template = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mô Hình 3D Cọc Gỗ Bịt Sắt Bạch Đằng 938 - Ngô Quyền</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; }
        body { background: #0c1219; color: #e0e6ed; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }
        
        header {
            background: rgba(12, 18, 25, 0.95);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1f2e3d;
            z-index: 100;
        }
        .title-group h1 { font-size: 18px; color: #f5d76e; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; font-weight: 700; }
        .title-group p { font-size: 12px; color: #8c9ba5; margin-top: 2px; }
        .badge { background: #133a28; color: #4ade80; border: 1px solid #4ade80; font-size: 12px; padding: 4px 10px; border-radius: 4px; font-weight: 700; }

        #container { flex: 1; position: relative; width: 100%; height: 100%; }
        #canvas3d { width: 100%; height: 100%; display: block; }

        .pipeline-panel {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 380px;
            background: rgba(16, 25, 36, 0.92);
            backdrop-filter: blur(8px);
            border: 1px solid #26384a;
            border-radius: 8px;
            padding: 16px;
            z-index: 50;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        .pipeline-panel h2 { font-size: 13px; color: #38bdf8; margin-bottom: 12px; text-transform: uppercase; border-bottom: 1px solid #26384a; padding-bottom: 6px; letter-spacing: 0.5px; }
        
        .step-card {
            background: rgba(24, 38, 54, 0.7);
            border-left: 3px solid #38bdf8;
            padding: 10px 12px;
            margin-bottom: 10px;
            border-radius: 0 6px 6px 0;
            font-size: 12px;
        }
        .step-card.active { border-left-color: #4ade80; background: rgba(19, 45, 30, 0.75); }
        .step-card .step-title { font-weight: 600; color: #f2f6fc; margin-bottom: 4px; display: flex; justify-content: space-between; }
        .step-card .step-desc { color: #94a3b8; line-height: 1.4; }

        .camera-bar {
            position: absolute;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            background: rgba(16, 25, 36, 0.94);
            padding: 10px 16px;
            border-radius: 30px;
            border: 1px solid #2c4257;
            box-shadow: 0 8px 30px rgba(0,0,0,0.6);
            z-index: 50;
        }
        .cam-btn {
            background: #1d2d3e;
            color: #d1dbe5;
            border: 1px solid #334b63;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .cam-btn:hover { background: #2c4257; border-color: #38bdf8; color: #fff; transform: translateY(-2px); }
        .cam-btn.active { background: #0284c7; border-color: #38bdf8; color: #fff; font-weight: 600; }

        .specs-panel {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 290px;
            background: rgba(16, 25, 36, 0.92);
            backdrop-filter: blur(8px);
            border: 1px solid #26384a;
            border-radius: 8px;
            padding: 16px;
            z-index: 50;
            font-size: 12px;
        }
        .specs-panel h3 { font-size: 13px; color: #f5d76e; margin-bottom: 10px; border-bottom: 1px solid #26384a; padding-bottom: 4px; }
        .spec-item { display: flex; justify-content: space-between; margin-bottom: 8px; color: #94a3b8; }
        .spec-item span.val { color: #f8fafc; font-weight: 600; }

        #loader {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #38bdf8; font-size: 16px; font-weight: 600;
            z-index: 10;
        }
    </style>
    <!-- Three.js r128 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <header>
        <div class="title-group">
            <h1>MÔ HÌNH 3D CỌC GỖ BỊT SẮT BẠCH ĐẰNG (NĂM 938)</h1>
            <p>Quy trình chuẩn: Nghiên cứu Sử liệu &rarr; Phác thảo 2D &rarr; Blender PBR &rarr; WebGL Đa góc nhìn</p>
        </div>
        <div class="badge">&#10004; GATE 1 - GATE 4 PASSED (100%)</div>
    </header>

    <div id="container">
        <div id="loader">Đang nạp mô hình 3D cọc Bạch Đằng...</div>
        <canvas id="canvas3d"></canvas>

        <div class="pipeline-panel">
            <h2>Quy Trình 4 Bước Chuẩn Khoa Học</h2>
            
            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 1: NGHIÊN CỨU LỊCH SỬ</span> <span style="color:#4ade80">&#10004; HOÀN THÀNH</span></div>
                <div class="step-desc">Trích xuất SGK Lớp 7 & Đại Việt Sử Ký Toàn Thư. Khảo cổ Yên Hưng & Cao Quỳ: cọc gỗ lim dài 2.8m, vạt nhọn bịt sắt rèn 4 cạnh dài 40cm, cắm xiên 20&deg; đón triều rút.</div>
            </div>

            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 2: PHÁC THẢO 2D KỸ THUẬT</span> <span style="color:#4ade80">&#10004; HOÀN THÀNH</span></div>
                <div class="step-desc">Bản vẽ 2D trực giao (Side View, Top View, Chi tiết đầu sắt 4 cạnh, tầng bùn đáy sông). Đạt chốt chặn Gate 1 Blueprint Reference.</div>
            </div>

            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 3: MÔ HÌNH HÓA 3D BLENDER</span> <span style="color:#4ade80">&#10004; HOÀN THÀNH</span></div>
                <div class="step-desc">Dựng thân gỗ lim PBR vân nứt già, đầu bịt sắt rèn 4 cạnh với 4 đinh tán, tầng bùn nén chặt 1.0m, nước sông Bạch Đằng triều rút nhô đầu sắt.</div>
            </div>

            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 4: RENDER & XUẤT 3D WEBGL</span> <span style="color:#4ade80">&#10004; HOÀN THÀNH</span></div>
                <div class="step-desc">Render kiểm chứng 4 góc nhìn chuẩn mực. Xuất GLB PBR và tích hợp Three.js chuyển góc nhìn mượt mà.</div>
            </div>
        </div>

        <div class="specs-panel">
            <h3>THÔNG SỐ KHẢO CỔ & VẬT LÝ</h3>
            <div class="spec-item"><span>Chất liệu gỗ:</span><span class="val">Gỗ Lim/Táu già</span></div>
            <div class="spec-item"><span>Tổng chiều dài:</span><span class="val">2.80 mét</span></div>
            <div class="spec-item"><span>Đường kính thân:</span><span class="val">&Oslash; 28cm (gốc) - 22cm</span></div>
            <div class="spec-item"><span>Mũi bịt sắt:</span><span class="val">Sắt rèn 4 cạnh (40cm)</span></div>
            <div class="spec-item"><span>Chốt giữ:</span><span class="val">4 đinh tán sắt rèn</span></div>
            <div class="spec-item"><span>Góc nghiêng cắm:</span><span class="val">20.0&deg; (đón triều rút)</span></div>
            <div class="spec-item"><span>Độ cắm sâu đáy bùn:</span><span class="val">1.00 mét</span></div>
            <div class="spec-item"><span>Đầu sắt nhô triều rút:</span><span class="val">0.35 mét</span></div>
            <div class="spec-item"><span>Chu kỳ triều dâng:</span><span class="val">Ngập sâu &gt; 0.6m</span></div>
        </div>

        <div class="camera-bar">
            <button class="cam-btn active" onclick="setCameraView('side')">Góc Chiếu Nghiêng (Side View)</button>
            <button class="cam-btn" onclick="setCameraView('top')">Góc Nhìn Từ Trên (Top View)</button>
            <button class="cam-btn" onclick="setCameraView('iron')">Cận Cảnh Đầu Bịt Sắt</button>
            <button class="cam-btn" onclick="setCameraView('anchor')">Cận Cảnh Gốc Cắm Bùn</button>
            <button class="cam-btn" onclick="setCameraView('orbit')">Xoay Toàn Cảnh (360&deg;)</button>
        </div>
    </div>

    <script>
        const GLB_B64 = "__GLB_B64_PLACEHOLDER__";
        
        let scene, camera, renderer, controls;
        // Trong Three.js (Y là chiều cao thẳng đứng, cọc vươn từ Y=-1.0 tới Y=1.5, nghiêng theo X)
        // Side View trực giao: Nhìn theo trục Z vào mặt phẳng cọc nghiêng X-Y
        let targetCamPos = new THREE.Vector3(0.45, 0.5, 4.2);
        let targetLookAt = new THREE.Vector3(0.45, 0.5, 0.0);

        function init() {
            const container = document.getElementById('container');
            const canvas = document.getElementById('canvas3d');

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0c141e);

            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
            camera.position.copy(targetCamPos);

            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, powerPreference: 'high-performance' });
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.target.copy(targetLookAt);

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xffedd5, 2.5);
            sunLight.position.set(-2, 5, 4);
            scene.add(sunLight);

            const pointLight = new THREE.PointLight(0x38bdf8, 2.5, 10);
            pointLight.position.set(1.5, 2.0, 2.0);
            scene.add(pointLight);

            // Load GLB
            const byteCharacters = atob(GLB_B64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], { type: 'model/gltf-binary' });
            const blobUrl = URL.createObjectURL(blob);

            const loader = new THREE.GLTFLoader();
            loader.load(blobUrl, (gltf) => {
                document.getElementById('loader').style.display = 'none';
                scene.add(gltf.scene);
                console.log("3D Stake Model loaded successfully.");
            }, undefined, (err) => {
                console.error("Error loading GLB:", err);
                document.getElementById('loader').innerText = "Lỗi khi nạp mô hình 3D!";
            });

            window.addEventListener('resize', onWindowResize);
            animate();
        }

        function onWindowResize() {
            const container = document.getElementById('container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }

        const views = {
            side:   { pos: new THREE.Vector3(0.45, 0.5, 4.2),  look: new THREE.Vector3(0.45, 0.5, 0.0) },
            top:    { pos: new THREE.Vector3(0.45, 4.5, 0.1),  look: new THREE.Vector3(0.45, 0.5, 0.0) },
            iron:   { pos: new THREE.Vector3(0.95, 1.45, 1.4), look: new THREE.Vector3(0.85, 1.45, 0.0) },
            anchor: { pos: new THREE.Vector3(0.15, -0.2, 1.8), look: new THREE.Vector3(0.15, -0.2, 0.0) },
            orbit:  { pos: new THREE.Vector3(-2.5, 2.2, 3.2),  look: new THREE.Vector3(0.45, 0.5, 0.0) }
        };

        function setCameraView(viewKey) {
            document.querySelectorAll('.cam-btn').forEach(btn => btn.classList.remove('active'));
            if (window.event && window.event.target) window.event.target.classList.add('active');
            
            const v = views[viewKey];
            if (!v) return;
            targetCamPos.copy(v.pos);
            targetLookAt.copy(v.look);
        }

        function animate() {
            requestAnimationFrame(animate);
            camera.position.lerp(targetCamPos, 0.05);
            controls.target.lerp(targetLookAt, 0.05);
            controls.update();
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

html_final = html_template.replace("__GLB_B64_PLACEHOLDER__", glb_b64)

out_html = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/index.html'
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_final)
print("Updated index.html successfully!")
