const fs = require('fs');
const path = require('path');

const glbPath = path.join(__dirname, 'web3d_export', 'bach_dang_battle_optimized.glb');
const htmlTemplatePath = path.join(__dirname, 'web3d_export', 'index.html');

console.log("Đang đọc file GLB:", glbPath);
const glbBuffer = fs.readFileSync(glbPath);
const glbBase64 = glbBuffer.toString('base64');
console.log(`Đã chuyển đổi GLB sang Base64 (${glbBase64.length} ký tự, ~${(glbBase64.length / 1024).toFixed(1)} KB)`);

const htmlContent = `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mô Phỏng 3D Đại Chiến Bạch Đằng 938 - Three.js WebGL</title>
    <style>
        * { box-sizing: border-box; }
        body { margin: 0; overflow: hidden; background: #0c1017; font-family: 'Segoe UI', Arial, sans-serif; color: #fff; }
        #canvas3d { width: 100vw; height: 100vh; display: block; }
        
        #loading {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: #f5d76e; font-size: 20px; font-weight: bold;
            background: rgba(12, 16, 23, 0.95); padding: 22px 32px; border-radius: 12px; border: 1px solid #c5a059;
            text-align: center; z-index: 100; box-shadow: 0 10px 40px rgba(0,0,0,0.8);
        }

        #ui-header {
            position: absolute; top: 20px; left: 25px;
            background: linear-gradient(135deg, rgba(20, 26, 36, 0.95), rgba(12, 16, 23, 0.85));
            padding: 16px 22px; border-radius: 10px; border-left: 4px solid #f5d76e;
            box-shadow: 0 8px 32px rgba(0,0,0,0.7); pointer-events: auto; max-width: 440px;
        }
        #ui-header h2 { margin: 0 0 6px 0; color: #f5d76e; font-size: 20px; text-transform: uppercase; letter-spacing: 1px; }
        #ui-header p { margin: 4px 0; font-size: 13px; color: #cbd5e1; line-height: 1.4; }
        
        #ui-controls {
            position: absolute; bottom: 25px; left: 50%; transform: translateX(-50%);
            background: rgba(16, 22, 32, 0.95); padding: 12px 24px; border-radius: 30px;
            border: 1px solid rgba(197, 160, 89, 0.5); box-shadow: 0 10px 40px rgba(0,0,0,0.8);
            display: flex; align-items: center; gap: 16px; z-index: 10;
        }
        .btn {
            background: #232d3d; border: 1px solid #c5a059; color: #f5d76e; padding: 8px 16px;
            border-radius: 20px; cursor: pointer; font-size: 13px; font-weight: 600;
            transition: all 0.2s ease;
        }
        .btn:hover { background: #c5a059; color: #0c1017; transform: translateY(-1px); }
        .btn.active { background: #f5d76e; color: #0c1017; }

        .slider-box { display: flex; align-items: center; gap: 10px; }
        .slider-box label { font-size: 13px; color: #f5d76e; font-weight: bold; min-width: 100px; }
        input[type="range"] {
            width: 250px; accent-color: #f5d76e; cursor: pointer;
        }

        #cam-views {
            position: absolute; top: 20px; right: 25px; display: flex; flex-direction: column; gap: 8px;
        }

        #fps-box {
            position: absolute; bottom: 15px; right: 20px; font-size: 12px; color: #94a3b8;
            background: rgba(0,0,0,0.6); padding: 5px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.1);
        }
    </style>
    <script type="importmap">
    {
        "imports": {
            "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
            "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
        }
    }
    </script>
</head>
<body>
    <div id="loading">Đang tải sa bàn 3D Đại Chiến Bạch Đằng 938...</div>

    <div id="ui-header">
        <h2>Đại Chiến Bạch Đằng 938</h2>
        <p><b>Thời khắc:</b> Mùa đông năm 938 - Ngô Quyền đại phá quân Nam Hán.</p>
        <p><b>Cơ chế mô phỏng:</b> Thủy triều rút để lộ bãi cọc gỗ Lim bịt sắt $\\to$ Lâu thuyền Lưu Hoằng Tháo đâm cọc hãm tốc, vỡ mạn nghiêng $25^\\circ$ và chìm dần.</p>
    </div>

    <div id="cam-views">
        <button class="btn active" id="btn-cam-orbit">🔭 Toàn Cảnh Chiến Trường</button>
        <button class="btn" id="btn-cam-stakes">🪵 Cận Cảnh Bãi Cọc</button>
        <button class="btn" id="btn-cam-han">🚢 Góc Nhìn Lâu Thuyền Địch</button>
        <button class="btn" id="btn-cam-viet">⛵ Góc Nhìn Thuyền Đại Việt</button>
    </div>

    <div id="ui-controls">
        <button class="btn" id="btn-play-pause">⏸ Tạm Dừng</button>
        <div class="slider-box">
            <label id="lbl-timeline">Tiến Trình: 0%</label>
            <input type="range" id="timeline-slider" min="0" max="1" step="0.002" value="0">
        </div>
        <button class="btn" id="btn-speed">Tốc độ: 1x</button>
    </div>

    <div id="fps-box">60 FPS | Three.js WebGL ACES Filmic</div>
    <canvas id="canvas3d"></canvas>

    <script>
        // Dữ liệu mô hình GLB nhúng trực tiếp dạng Base64 (Hỗ trợ mở file:// trực tiếp mà KHÔNG bị lỗi CORS trình duyệt)
        window.EMBEDDED_GLB_BASE64 = "${glbBase64}";
    </script>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

        // 1. Khởi tạo Scene, Camera & WebGL Renderer
        const canvas = document.getElementById('canvas3d');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x11161f);
        scene.fog = new THREE.FogExp2(0x11161f, 0.009);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 500);
        camera.position.set(16, 12, 16);

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // 2. Camera Controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.02;
        controls.target.set(0, 0, 0);

        // 3. Ánh sáng
        const hemiLight = new THREE.HemisphereLight(0xa0b4c8, 0x181c24, 0.85);
        scene.add(hemiLight);

        const sunLight = new THREE.DirectionalLight(0xffecd0, 2.2);
        sunLight.position.set(25, 40, 20);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 1;
        sunLight.shadow.camera.far = 120;
        sunLight.shadow.camera.left = -25;
        sunLight.shadow.camera.right = 25;
        sunLight.shadow.camera.top = 25;
        sunLight.shadow.camera.bottom = -25;
        scene.add(sunLight);

        const fireLight = new THREE.PointLight(0xff5511, 2.5, 40, 1.2);
        fireLight.position.set(-1.0, 4.0, 4.0);
        scene.add(fireLight);

        // 4. Vật liệu PBR Lịch sử cho WebGL
        const matLimWood = new THREE.MeshStandardMaterial({
            color: 0x221a14, roughness: 0.82, metalness: 0.08
        });
        const matCarvedWood = new THREE.MeshStandardMaterial({
            color: 0x483e32, roughness: 0.70, metalness: 0.05
        });
        const matIronCap = new THREE.MeshStandardMaterial({
            color: 0x42464d, roughness: 0.40, metalness: 0.88
        });
        const matVietHull = new THREE.MeshStandardMaterial({
            color: 0x2e1f14, roughness: 0.68, metalness: 0.05
        });
        const matBatwingSail = new THREE.MeshStandardMaterial({
            color: 0x7c5432, roughness: 0.85, metalness: 0.02, side: THREE.DoubleSide
        });
        const matHanHull = new THREE.MeshStandardMaterial({
            color: 0x3d2417, roughness: 0.62, metalness: 0.08
        });
        const matRoofTiles = new THREE.MeshStandardMaterial({
            color: 0x2a2d33, roughness: 0.52, metalness: 0.15
        });
        const matRiverWater = new THREE.MeshStandardMaterial({
            color: 0x092226, roughness: 0.10, metalness: 0.12, transparent: true, opacity: 0.92
        });

        // 5. Nạp tệp mô hình GLB (Tự động thích ứng cả file:// và http://)
        let mixer = null;
        let actions = [];
        let totalDuration = 12.5;
        let isPlaying = true;
        let timeScale = 1.0;

        function base64ToArrayBuffer(base64) {
            const binary_string = window.atob(base64);
            const len = binary_string.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binary_string.charCodeAt(i);
            }
            return bytes.buffer;
        }

        function initSceneWithModel(gltf) {
            document.getElementById('loading').style.display = 'none';
            const model = gltf.scene;

            model.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;

                    const name = child.name.toLowerCase();
                    if (name.includes('coc') || name.includes('stake')) {
                        if (name.includes('sat') || name.includes('iron')) child.material = matIronCap;
                        else if (name.includes('deo') || name.includes('carve')) child.material = matCarvedWood;
                        else child.material = matLimWood;
                    } else if (name.includes('river') || name.includes('water')) {
                        child.material = matRiverWater;
                    } else if (name.includes('buom') || name.includes('sail')) {
                        child.material = matBatwingSail;
                    } else if (name.includes('roof') || name.includes('tile')) {
                        child.material = matRoofTiles;
                    } else if (name.includes('namhan') || name.includes('han')) {
                        child.material = matHanHull;
                    } else if (name.includes('hull') || name.includes('thuyen')) {
                        child.material = matVietHull;
                    }
                }
            });

            scene.add(model);

            if (gltf.animations && gltf.animations.length > 0) {
                mixer = new THREE.AnimationMixer(model);
                totalDuration = 0;
                gltf.animations.forEach((clip) => {
                    const act = mixer.clipAction(clip);
                    act.play();
                    actions.push(act);
                    if (clip.duration > totalDuration) totalDuration = clip.duration;
                });
                console.log("Đã kích hoạt " + actions.length + " luồng chuyển động! Thời lượng: " + totalDuration.toFixed(2) + "s");
            }
        }

        const loader = new GLTFLoader();

        // Kiểm tra phương thức tải an toàn tuyệt đối
        if (window.EMBEDDED_GLB_BASE64 && (window.location.protocol === 'file:' || !window.location.protocol.startsWith('http'))) {
            console.log("Đang nạp mô hình từ bộ nhớ nhúng (An toàn cho giao thức file://)...");
            try {
                const buffer = base64ToArrayBuffer(window.EMBEDDED_GLB_BASE64);
                loader.parse(buffer, '', (gltf) => {
                    initSceneWithModel(gltf);
                }, (err) => {
                    console.error("Lỗi parse GLB:", err);
                    document.getElementById('loading').innerText = 'Lỗi giải mã file 3D!';
                });
            } catch (e) {
                console.error("Lỗi base64:", e);
                document.getElementById('loading').innerText = 'Lỗi chuyển đổi dữ liệu 3D!';
            }
        } else {
            // Đang chạy trên HTTP Web Server
            loader.load('bach_dang_battle_optimized.glb', (gltf) => {
                initSceneWithModel(gltf);
            }, 
            (xhr) => {
                const percent = Math.round((xhr.loaded / (xhr.total || 680000)) * 100);
                document.getElementById('loading').innerText = 'Đang tải: ' + percent + '%';
            }, 
            (err) => {
                console.warn("Fetch HTTP thất bại, chuyển sang nạp Base64 dự phòng...", err);
                if (window.EMBEDDED_GLB_BASE64) {
                    const buffer = base64ToArrayBuffer(window.EMBEDDED_GLB_BASE64);
                    loader.parse(buffer, '', (gltf) => {
                        initSceneWithModel(gltf);
                    });
                } else {
                    document.getElementById('loading').innerText = 'Lỗi khi nạp file 3D!';
                }
            });
        }

        // 6. Camera Presets
        function setCameraView(pos, target) {
            camera.position.set(pos.x, pos.y, pos.z);
            controls.target.set(target.x, target.y, target.z);
            controls.update();
        }

        const btnOrbit = document.getElementById('btn-cam-orbit');
        const btnStakes = document.getElementById('btn-cam-stakes');
        const btnHan = document.getElementById('btn-cam-han');
        const btnViet = document.getElementById('btn-cam-viet');

        function setActiveBtn(btn) {
            [btnOrbit, btnStakes, btnHan, btnViet].forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        btnOrbit.onclick = () => { setActiveBtn(btnOrbit); setCameraView({x: 16, y: 12, z: 16}, {x: 0, y: 0, z: 0}); };
        btnStakes.onclick = () => { setActiveBtn(btnStakes); setCameraView({x: 2.2, y: 1.6, z: 5.5}, {x: 0, y: 0, z: -0.5}); };
        btnHan.onclick = () => { setActiveBtn(btnHan); setCameraView({x: -4.5, y: 6.0, z: 10.0}, {x: -1.0, y: 2.5, z: 0.5}); };
        btnViet.onclick = () => { setActiveBtn(btnViet); setCameraView({x: 3.5, y: 3.5, z: -16.0}, {x: 0.5, y: 0.0, z: -10.0}); };

        // 7. Timeline & Playback UI
        const btnPlay = document.getElementById('btn-play-pause');
        const slider = document.getElementById('timeline-slider');
        const lblTime = document.getElementById('lbl-timeline');
        const btnSpeed = document.getElementById('btn-speed');

        btnPlay.onclick = () => {
            isPlaying = !isPlaying;
            btnPlay.innerText = isPlaying ? "⏸ Tạm Dừng" : "▶ Tiếp Tục";
        };

        const speeds = [1.0, 1.5, 2.0, 0.5];
        let speedIdx = 0;
        btnSpeed.onclick = () => {
            speedIdx = (speedIdx + 1) % speeds.length;
            timeScale = speeds[speedIdx];
            btnSpeed.innerText = "Tốc độ: " + timeScale + "x";
            if (mixer) mixer.timeScale = timeScale;
        };

        slider.oninput = () => {
            if (mixer && totalDuration > 0) {
                const targetTime = slider.value * totalDuration;
                mixer.setTime(targetTime);
                lblTime.innerText = "Tiến Trình: " + Math.round(slider.value * 100) + "%";
            }
        };

        // 8. Render Loop 60 FPS
        const clock = new THREE.Clock();
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        function animate() {
            requestAnimationFrame(animate);
            const delta = clock.getDelta();

            if (mixer && isPlaying) {
                mixer.update(delta * timeScale);
                const progress = (mixer.time % totalDuration) / totalDuration;
                slider.value = progress;
                lblTime.innerText = "Tiến Trình: " + Math.round(progress * 100) + "%";
            }

            fireLight.intensity = 2.2 + Math.sin(clock.getElapsedTime() * 7.0) * 0.6;
            controls.update();
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
`;

fs.writeFileSync(htmlTemplatePath, htmlContent, 'utf8');
console.log("=== ĐÃ CẬP NHẬT THÀNH CÔNG INDEX.HTML VỚI BASE64 DỰ PHÒNG CHỐNG LỖI CORS ===");
