import base64, os

glb_path = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/coc_bach_dang_938.glb'
with open(glb_path, 'rb') as f:
    glb_b64 = base64.b64encode(f.read()).decode('utf-8')

print("GLB Base64 length:", len(glb_b64))

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mô Hình 3D Cọc Gỗ Bịt Sắt Bạch Đằng 938 - Ngô Quyền</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; }}
        body {{ background: #0c1219; color: #e0e6ed; overflow: hidden; height: 100vh; display: flex; flex-direction: column; }}
        
        /* Header */
        header {{
            background: rgba(12, 18, 25, 0.95);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1f2e3d;
            z-index: 100;
        }}
        .title-group h1 {{ font-size: 18px; color: #e6a23c; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; }}
        .title-group p {{ font-size: 12px; color: #8c9ba5; }}
        .badge {{ background: #1b382b; color: #67c23a; border: 1px solid #67c23a; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }}

        /* Main Container */
        #container {{ flex: 1; position: relative; width: 100%; height: 100%; }}
        #canvas3d {{ width: 100%; height: 100%; display: block; }}

        /* Left Panel: Quy Trình Các Bước */
        .pipeline-panel {{
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
            max-height: calc(100vh - 160px);
            overflow-y: auto;
        }}
        .pipeline-panel h2 {{ font-size: 14px; color: #409eff; margin-bottom: 12px; text-transform: uppercase; border-bottom: 1px solid #26384a; padding-bottom: 6px; }}
        
        .step-card {{
            background: rgba(24, 38, 54, 0.7);
            border-left: 3px solid #409eff;
            padding: 10px 12px;
            margin-bottom: 10px;
            border-radius: 0 6px 6px 0;
            font-size: 12px;
        }}
        .step-card.active {{ border-left-color: #67c23a; background: rgba(30, 50, 40, 0.8); }}
        .step-card .step-title {{ font-weight: 600; color: #f2f6fc; margin-bottom: 4px; display: flex; justify-content: space-between; }}
        .step-card .step-desc {{ color: #a4b3c2; line-height: 1.4; }}

        /* Bottom Controls: Camera Views */
        .camera-bar {{
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
        }}
        .cam-btn {{
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
        }}
        .cam-btn:hover {{ background: #2c4257; border-color: #409eff; color: #fff; transform: translateY(-2px); }}
        .cam-btn.active {{ background: #409eff; border-color: #409eff; color: #fff; font-weight: 600; }}

        /* Right Panel: Thông Số Kỹ Thuật */
        .specs-panel {{
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
        }}
        .specs-panel h3 {{ font-size: 13px; color: #e6a23c; margin-bottom: 10px; border-bottom: 1px solid #26384a; padding-bottom: 4px; }}
        .spec-item {{ display: flex; justify-content: space-between; margin-bottom: 8px; color: #a4b3c2; }}
        .spec-item span.val {{ color: #f2f6fc; font-weight: 600; }}

        /* Loading */
        #loader {{
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #409eff; font-size: 16px; font-weight: 600;
            z-index: 10;
        }}
    </style>
    <!-- Three.js + GLTFLoader + OrbitControls -->
    <script src="https://unpkg.com/three@0.158.0/build/three.min.js"></script>
    <script src="https://unpkg.com/three@0.158.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://unpkg.com/three@0.158.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <header>
        <div class="title-group">
            <h1>🗡️ MÔ HÌNH 3D CỌC GỖ BỊT SẮT BẠCH ĐẰNG (NĂM 938)</h1>
            <p>Kiểm chứng quy trình: Nghiên cứu Sử liệu -> Phác thảo 2D -> Blender PBR -> WebGL Đa góc nhìn</p>
        </div>
        <div class="badge">GATE 1 - GATE 4 PASSED (100%)</div>
    </header>

    <div id="container">
        <div id="loader">Đang nạp mô hình 3D cọc Bạch Đằng...</div>
        <canvas id="canvas3d"></canvas>

        <!-- Left Panel: Các Bước Thực Thi Quy Trình -->
        <div class="pipeline-panel">
            <h2>Quy Trình 4 Bước Chuẩn Khoa Học</h2>
            
            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 1: NGHIÊN CỨU LỊCH SỬ</span> <span style="color:#67c23a">✔ HOÀN THÀNH</span></div>
                <div class="step-desc">Trích xuất sử liệu SGK Lớp 7 & Đại Việt Sử Ký Toàn Thư. Khảo cổ Yên Hưng & Cao Quỳ: cọc gỗ lim dài 2.8m, vạt nhọn bịt sắt rèn 4 cạnh dài 40cm, cắm xiên 20° đón tàu giặc.</div>
            </div>

            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 2: PHÁC THẢO 2D KỸ THUẬT</span> <span style="color:#67c23a">✔ HOÀN THÀNH</span></div>
                <div class="step-desc">Xuất bản vẽ 2D trực giao (Side View, Top View, Chi tiết đầu sắt 4 cạnh, tầng bùn đáy sông). Đạt chốt chặn Gate 1 Blueprint Reference.</div>
            </div>

            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 3: MÔ HÌNH HÓA 3D BLENDER</span> <span style="color:#67c23a">✔ HOÀN THÀNH</span></div>
                <div class="step-desc">Dựng thân gỗ lim PBR vân nứt, đầu bịt sắt rèn 4 cạnh với 4 đinh tán, tầng bùn nén chặt 1.0m, nước sông Bạch Đằng triều rút nhô đầu sắt.</div>
            </div>

            <div class="step-card active">
                <div class="step-title"><span>BƯỚC 4: RENDER & XUẤT 3D WEBGL</span> <span style="color:#67c23a">✔ HOÀN THÀNH</span></div>
                <div class="step-desc">Render kiểm chứng 4 góc nhìn chuẩn mực. Xuất GLB PBR và tích hợp Three.js chuyển góc nhìn mượt mà.</div>
            </div>
        </div>

        <!-- Right Panel: Thông Số Kỹ Thuật -->
        <div class="specs-panel">
            <h3>THÔNG SỐ KHẢO CỔ & VẬT LÝ</h3>
            <div class="spec-item"><span>Chất liệu gỗ:</span><span class="val">Gỗ Lim/Táu già</span></div>
            <div class="spec-item"><span>Tổng chiều dài:</span><span class="val">2.80 mét</span></div>
            <div class="spec-item"><span>Đường kính thân:</span><span class="val">Ø 28cm (gốc) - 22cm</span></div>
            <div class="spec-item"><span>Mũi bịt sắt:</span><span class="val">Sắt rèn 4 cạnh (40cm)</span></div>
            <div class="spec-item"><span>Chốt giữ:</span><span class="val">4 đinh tán sắt rèn</span></div>
            <div class="spec-item"><span>Góc nghiêng cắm:</span><span class="val">20.0° (đón triều rút)</span></div>
            <div class="spec-item"><span>Độ cắm sâu đáy bùn:</span><span class="val">1.00 mét</span></div>
            <div class="spec-item"><span>Đầu sắt nhô triều rút:</span><span class="val">0.35 mét</span></div>
            <div class="spec-item"><span>Chu kỳ triều dâng:</span><span class="val">Ngập sâu > 0.6m</span></div>
        </div>

        <!-- Bottom Controls -->
        <div class="camera-bar">
            <button class="cam-btn active" onclick="setCameraView('side')">📐 Góc Chiếu Nghiêng (Side View)</button>
            <button class="cam-btn" onclick="setCameraView('top')">⬇️ Góc Nhìn Từ Trên (Top View)</button>
            <button class="cam-btn" onclick="setCameraView('iron')">🗡️ Cận Cảnh Đầu Bịt Sắt</button>
            <button class="cam-btn" onclick="setCameraView('anchor')">⚓ Cận Cảnh Gốc Cắm Bùn</button>
            <button class="cam-btn" onclick="setCameraView('orbit')">🔄 Xoay Toàn Cảnh (360°)</button>
        </div>
    </div>

    <script>
        // --- BASE64 GLB EMBEDDED ---
        const GLB_B64 = "{glb_b64}";
        
        let scene, camera, renderer, controls;
        let targetCamPos = new THREE.Vector3(0.45, -4.5, 0.6);
        let targetLookAt = new THREE.Vector3(0.45, 0.0, 0.6);

        function init() {{
            const container = document.getElementById('container');
            const canvas = document.getElementById('canvas3d');

            // 1. Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a1118);
            scene.fog = new THREE.FogExp2(0x0a1118, 0.08);

            // 2. Camera
            camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
            camera.position.copy(targetCamPos);

            // 3. Renderer
            renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true, powerPreference: 'high-performance' }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.1;

            // 4. Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.target.copy(targetLookAt);

            // 5. Lights
            const ambientLight = new THREE.AmbientLight(0xddeeff, 0.65);
            scene.add(ambientLight);

            const sunLight = new THREE.DirectionalLight(0xfff3d6, 2.2);
            sunLight.position.set(-3, -5, 6);
            scene.add(sunLight);

            const pointLight = new THREE.PointLight(0x66ccff, 2.0, 8);
            pointLight.position.set(1.5, -1.0, 2.0);
            scene.add(pointLight);

            // 6. Grid helper mờ đáy sông
            const grid = new THREE.GridHelper(10, 20, 0x224466, 0x112233);
            grid.position.y = -0.01;
            scene.add(grid);

            // 7. Load GLB từ Base64
            const byteCharacters = atob(GLB_B64);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {{
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }}
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray], {{ type: 'model/gltf-binary' }});
            const blobUrl = URL.createObjectURL(blob);

            const loader = new THREE.GLTFLoader();
            loader.load(blobUrl, (gltf) => {{
                document.getElementById('loader').style.display = 'none';
                scene.add(gltf.scene);
                console.log("3D Stake Model loaded successfully.");
            }}, undefined, (err) => {{
                console.error("Error loading GLB:", err);
                document.getElementById('loader').innerText = "Lỗi khi nạp mô hình 3D!";
            }});

            window.addEventListener('resize', onWindowResize);
            animate();
        }}

        function onWindowResize() {{
            const container = document.getElementById('container');
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }}

        // Camera presets
        const views = {{
            side:   {{ pos: new THREE.Vector3(0.45, -4.5, 0.6), look: new THREE.Vector3(0.45, 0.0, 0.6) }},
            top:    {{ pos: new THREE.Vector3(0.45, -0.2, 5.0), look: new THREE.Vector3(0.45, 0.0, 0.6) }},
            iron:   {{ pos: new THREE.Vector3(1.0, -1.8, 2.0),  look: new THREE.Vector3(0.85, 0.0, 1.45) }},
            anchor: {{ pos: new THREE.Vector3(-0.6, -2.2, 0.2), look: new THREE.Vector3(0.15, 0.0, -0.3) }},
            orbit:  {{ pos: new THREE.Vector3(-2.8, -3.2, 2.4), look: new THREE.Vector3(0.45, 0.0, 0.6) }}
        }};

        function setCameraView(viewKey) {{
            document.querySelectorAll('.cam-btn').forEach(btn => btn.classList.remove('active'));
            if (event && event.target) event.target.classList.add('active');
            
            const v = views[viewKey];
            if (!v) return;
            targetCamPos.copy(v.pos);
            targetLookAt.copy(v.look);
        }}

        function animate() {{
            requestAnimationFrame(animate);
            
            // Smooth Camera Interpolation
            camera.position.lerp(targetCamPos, 0.05);
            controls.target.lerp(targetLookAt, 0.05);
            controls.update();

            renderer.render(scene, camera);
        }}

        window.onload = init;
    </script>
</body>
</html>
"""

out_html = r'C:/Users/HPZBook/Desktop/TEST_BLENDER/test_quy_trinh/index.html'
with open(out_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Đã xuất file HTML 3D tương tác thành công:", out_html, "Size:", len(html_content))
