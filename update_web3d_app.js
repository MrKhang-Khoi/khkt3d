const fs = require('fs');
const path = require('path');

const glbPath = path.join(__dirname, 'web3d_export', 'bach_dang_battle_optimized.glb');
const htmlPath = path.join(__dirname, 'web3d_export', 'index.html');

console.log('Đang đọc file GLB mới:', glbPath);
const glbBuffer = fs.readFileSync(glbPath);
const glbBase64 = glbBuffer.toString('base64');
console.log(`Đã chuyển đổi GLB sang Base64 (${glbBase64.length} ký tự, ${(glbBase64.length / 1024 / 1024).toFixed(2)} MB)`);

const htmlContent = `<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mô Phỏng 3D Đại Chiến Bạch Đằng 938 - Three.js WebGL</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { overflow: hidden; background: #080c14; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; color: #fff; }
        #canvas3d { width: 100vw; height: 100vh; display: block; }
        
        #loading {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: #f5d76e; font-size: 20px; font-weight: bold;
            background: rgba(12, 18, 28, 0.95); padding: 24px 36px; border-radius: 14px;
            border: 1px solid rgba(197, 160, 89, 0.6); text-align: center; z-index: 100;
            box-shadow: 0 12px 48px rgba(0,0,0,0.85); backdrop-filter: blur(8px);
        }

        #ui-header {
            position: absolute; top: 20px; left: 24px;
            background: linear-gradient(135deg, rgba(16, 24, 38, 0.92), rgba(10, 15, 24, 0.88));
            padding: 18px 24px; border-radius: 12px; border-left: 4px solid #f5d76e;
            box-shadow: 0 8px 32px rgba(0,0,0,0.75); pointer-events: auto; max-width: 480px;
            backdrop-filter: blur(8px); border-top: 1px solid rgba(255,255,255,0.06);
        }
        #ui-header h1 { margin: 0 0 6px 0; color: #f5d76e; font-size: 21px; text-transform: uppercase; letter-spacing: 1.2px; }
        #ui-header .meta { font-size: 13px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }
        #ui-header .stage-banner {
            background: rgba(245, 215, 110, 0.12); border: 1px solid rgba(245, 215, 110, 0.35);
            padding: 8px 12px; border-radius: 6px; font-size: 13px; color: #fde047; font-weight: 600;
            line-height: 1.4; transition: all 0.3s ease;
        }

        #cam-views {
            position: absolute; top: 20px; right: 24px; display: flex; flex-direction: column; gap: 9px; z-index: 10;
        }
        .btn-cam {
            background: rgba(18, 26, 40, 0.88); border: 1px solid rgba(197, 160, 89, 0.45);
            color: #e2e8f0; padding: 10px 18px; border-radius: 8px; cursor: pointer;
            font-size: 13px; font-weight: 600; transition: all 0.25s ease; text-align: left;
            backdrop-filter: blur(6px); display: flex; align-items: center; gap: 8px;
        }
        .btn-cam:hover { background: rgba(197, 160, 89, 0.25); color: #f5d76e; border-color: #f5d76e; transform: translateX(-3px); }
        .btn-cam.active { background: #f5d76e; color: #0a0f18; border-color: #f5d76e; font-weight: 700; box-shadow: 0 0 16px rgba(245, 215, 110, 0.4); }

        #ui-controls {
            position: absolute; bottom: 26px; left: 50%; transform: translateX(-50%);
            background: rgba(14, 20, 32, 0.94); padding: 12px 28px; border-radius: 36px;
            border: 1px solid rgba(197, 160, 89, 0.45); box-shadow: 0 12px 40px rgba(0,0,0,0.85);
            display: flex; align-items: center; gap: 18px; z-index: 10; backdrop-filter: blur(10px);
        }
        .ctrl-btn {
            background: #1e293b; border: 1px solid rgba(197, 160, 89, 0.5); color: #f5d76e;
            padding: 8px 18px; border-radius: 20px; cursor: pointer; font-size: 13px;
            font-weight: 600; transition: all 0.2s ease;
        }
        .ctrl-btn:hover { background: #f5d76e; color: #0a0f18; }

        .slider-box { display: flex; align-items: center; gap: 12px; }
        .slider-box label { font-size: 13px; color: #f5d76e; font-weight: 600; min-width: 110px; }
        input[type="range"] {
            width: 280px; accent-color: #f5d76e; cursor: pointer; height: 6px;
        }

        #tide-meter {
            display: flex; align-items: center; gap: 6px; font-size: 13px; color: #38bdf8;
            background: rgba(56, 189, 248, 0.12); padding: 5px 12px; border-radius: 14px;
            border: 1px solid rgba(56, 189, 248, 0.3); font-weight: 600; min-width: 125px;
        }

        #fps-box {
            position: absolute; bottom: 15px; right: 24px; font-size: 12px; color: #64748b;
            background: rgba(0,0,0,0.6); padding: 5px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);
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
    <div id="loading">Đang khởi tạo sa bàn 3D Đại Chiến Bạch Đằng 938...</div>

    <div id="ui-header">
        <h1>Đại Chiến Bạch Đằng 938</h1>
        <div class="meta">Mùa đông năm 938 | Ngô Quyền đại phá Hoằng Tháo</div>
        <div class="stage-banner" id="stage-banner">Pha 1: Triều cường (+1.4m) - Thuyền Đại Việt nhử giặc qua bãi cọc</div>
    </div>

    <div id="cam-views">
        <button class="btn-cam active" id="btn-cam-orbit">🔭 Toàn Cảnh Chiến Trường</button>
        <button class="btn-cam" id="btn-cam-stakes">🪵 Cận Cảnh Bãi Cọc Ngầm</button>
        <button class="btn-cam" id="btn-cam-han">🚢 Lâu Thuyền Địch Va Cọc</button>
        <button class="btn-cam" id="btn-cam-viet">⛵ Thuyền Đại Việt Phản Công</button>
    </div>

    <div id="ui-controls">
        <button class="ctrl-btn" id="btn-play-pause">⏸ Tạm Dừng</button>
        <div class="slider-box">
            <label id="lbl-timeline">Tiến Trình: 0%</label>
            <input type="range" id="timeline-slider" min="0" max="1" step="0.002" value="0">
        </div>
        <div id="tide-meter">🌊 Triều: +1.4m</div>
        <button class="ctrl-btn" id="btn-speed">Tốc độ: 1x</button>
    </div>

    <div id="fps-box">60 FPS | Three.js WebGL ACES Filmic</div>
    <canvas id="canvas3d"></canvas>

    <script>
        // Dữ liệu mô hình nhúng trực tiếp Base64 hỗ trợ mở qua giao thức file:// không bị CORS
        window.EMBEDDED_GLB_BASE64 = "${glbBase64}";
    </script>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

        // 1. Khởi tạo Scene, Camera & WebGL Renderer
        const canvas = document.getElementById('canvas3d');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a1017);
        scene.fog = new THREE.FogExp2(0x0a1017, 0.008);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 600);
        camera.position.set(24, 15, 20);

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.15;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // 2. Camera Controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.02;
        controls.target.set(0, 0, 0);

        // 3. Ánh sáng Điện ảnh Chiến trường
        const hemiLight = new THREE.HemisphereLight(0x8fa3ad, 0x141820, 0.95);
        scene.add(hemiLight);

        const sunLight = new THREE.DirectionalLight(0xffeed6, 2.6);
        sunLight.position.set(30, 45, 25);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.near = 1;
        sunLight.shadow.camera.far = 150;
        sunLight.shadow.camera.left = -30;
        sunLight.shadow.camera.right = 30;
        sunLight.shadow.camera.top = 30;
        sunLight.shadow.camera.bottom = -30;
        scene.add(sunLight);

        // Ánh sáng bù trời xanh sông nước tránh tối cục bộ
        const fillLight = new THREE.DirectionalLight(0x7ea6cc, 1.4);
        fillLight.position.set(-25, 20, -25);
        scene.add(fillLight);

        const fireLight = new THREE.PointLight(0xff6611, 3.2, 50, 1.2);
        fireLight.position.set(-1.0, 3.5, 4.0);
        scene.add(fireLight);

        // 4. Vật liệu PBR Lịch sử cho Three.js
        const matLimWood = new THREE.MeshStandardMaterial({
            color: 0x221a14, roughness: 0.82, metalness: 0.08
        });
        const matCarvedWood = new THREE.MeshStandardMaterial({
            color: 0x483e32, roughness: 0.70, metalness: 0.05
        });
        const matIronCap = new THREE.MeshStandardMaterial({
            color: 0x4a4e57, roughness: 0.38, metalness: 0.90
        });
        const matVietHull = new THREE.MeshStandardMaterial({
            color: 0x302116, roughness: 0.68, metalness: 0.05
        });
        const matBatwingSail = new THREE.MeshStandardMaterial({
            color: 0x7c5230, roughness: 0.82, metalness: 0.02, side: THREE.DoubleSide
        });
        const matHanHull = new THREE.MeshStandardMaterial({
            color: 0x3d2315, roughness: 0.62, metalness: 0.08
        });
        const matRoofTiles = new THREE.MeshStandardMaterial({
            color: 0x272b30, roughness: 0.52, metalness: 0.15
        });
        const matRiverWater = new THREE.MeshStandardMaterial({
            color: 0x0c2f35, roughness: 0.08, metalness: 0.12, transparent: true, opacity: 0.82, depthWrite: true
        });

        // 5. Nạp tệp mô hình GLB
        let mixer = null;
        let actions = [];
        let totalDuration = 12.5;
        let isPlaying = true;
        let timeScale = 1.0;

        function base64ToArrayBuffer(base64) {
            const binary = window.atob(base64);
            const len = binary.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binary.charCodeAt(i);
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
                        if (name.includes('sat') || name.includes('iron') || name.includes('mui')) child.material = matIronCap;
                        else if (name.includes('deo') || name.includes('carve') || name.includes('nghieng')) child.material = matCarvedWood;
                        else child.material = matLimWood;
                    } else if (name.includes('river') || name.includes('water') || name.includes('song') || name.includes('nuoc')) {
                        child.material = matRiverWater;
                    } else if (name.includes('buom') || name.includes('sail')) {
                        child.material = matBatwingSail;
                    } else if (name.includes('roof') || name.includes('tile') || name.includes('ngoi')) {
                        child.material = matRoofTiles;
                    } else if (name.includes('namhan') || name.includes('han')) {
                        child.material = matHanHull;
                    } else if (name.includes('hull') || name.includes('thuyen') || name.includes('than')) {
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
            loader.load('bach_dang_battle_optimized.glb', (gltf) => {
                initSceneWithModel(gltf);
            }, 
            (xhr) => {
                const percent = Math.round((xhr.loaded / (xhr.total || 1100000)) * 100);
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

        btnOrbit.onclick = () => { setActiveBtn(btnOrbit); setCameraView({x: 25, y: 16, z: 22}, {x: 0, y: 0, z: 0}); };
        btnStakes.onclick = () => { setActiveBtn(btnStakes); setCameraView({x: 6.0, y: 4.0, z: 6.0}, {x: -0.5, y: 0.5, z: -0.5}); };
        btnHan.onclick = () => { setActiveBtn(btnHan); setCameraView({x: -8.0, y: 6.0, z: -8.0}, {x: -1.0, y: 2.0, z: -1.5}); };
        btnViet.onclick = () => { setActiveBtn(btnViet); setCameraView({x: 6.0, y: 4.5, z: 3.5}, {x: 2.0, y: 0.5, z: 10.0}); };

        // 7. Timeline, Stage Updates & Playback UI
        const btnPlay = document.getElementById('btn-play-pause');
        const slider = document.getElementById('timeline-slider');
        const lblTime = document.getElementById('lbl-timeline');
        const btnSpeed = document.getElementById('btn-speed');
        const stageBanner = document.getElementById('stage-banner');
        const tideMeter = document.getElementById('tide-meter');

        function updateStageDisplay(progress) {
            const s_curve = 3.0 * (progress ** 2) - 2.0 * (progress ** 3);
            const zTide = 1.40 - s_curve * 3.20;
            const tideSign = zTide >= 0 ? '+' : '';
            tideMeter.innerText = '🌊 Triều: ' + tideSign + zTide.toFixed(2) + 'm';

            if (progress < 0.35) {
                stageBanner.innerText = 'Pha 1: Triều cường (+1.4m) - Thuyền Đại Việt nhử giặc qua bãi cọc';
                stageBanner.style.borderColor = 'rgba(56, 189, 248, 0.5)';
                stageBanner.style.color = '#38bdf8';
            } else if (progress < 0.55) {
                stageBanner.innerText = 'Pha 2: Triều rút - Lâu thuyền đâm trúng cọc ngầm, vỡ mạn nghiêng 25°';
                stageBanner.style.borderColor = 'rgba(239, 68, 68, 0.6)';
                stageBanner.style.color = '#f87171';
            } else {
                stageBanner.innerText = 'Pha 3: Triều kiệt (-1.8m) - Trơ bãi cọc nhọn, quân ta tổng phản công đại thắng';
                stageBanner.style.borderColor = 'rgba(245, 215, 110, 0.6)';
                stageBanner.style.color = '#fde047';
            }
        }

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
                const p = parseFloat(slider.value);
                lblTime.innerText = "Tiến Trình: " + Math.round(p * 100) + "%";
                updateStageDisplay(p);
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
                updateStageDisplay(progress);
            }

            fireLight.intensity = 2.8 + Math.sin(clock.getElapsedTime() * 8.0) * 0.8;
            controls.update();
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
`;

fs.writeFileSync(htmlPath, htmlContent, 'utf8');
console.log('=== ĐÃ CẬP NHẬT THÀNH CÔNG INDEX.HTML VỚI ĐỒ HỌA SÂN KHẤU VÀ TỰ ĐỘNG ĐO ĐẠC TRIỀU RÚT! ===');
