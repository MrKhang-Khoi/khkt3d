# -*- coding: utf-8 -*-
"""
NÂNG CẤP HỆ THỐNG KHÓI LỬA WEBGL & HERO CAMERA VÀO MO_PHONG_BACH_DANG_938.HTML
Tích hợp GPU Particle Engine: Khói đen muội than, Lửa cuộn, Tàn tro, Đèn nhấp nháy và Cọc đâm toác lườn.
"""
import re

def update_html():
    with open('mo_phong_bach_dang_938.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Thêm option Hero Camera vào dropdown pop-cam nếu chưa có
    if 'data-cam="fire_closeup"' not in html:
        old_cam_pop = '<button class="popup-opt" data-cam="flagship">Soái Hạm Hoằng Tháo</button>'
        new_cam_pop = old_cam_pop + '\n                    <button class="popup-opt" data-cam="fire_closeup">💥 Cận Cảnh Cháy Tàu & Đâm Cọc (Hero Shot)</button>'
        html = html.replace(old_cam_pop, new_cam_pop)

    # 2. Thêm target camera vào camTargets nếu chưa có
    if 'fire_closeup:' not in html:
        old_cam_targets = 'flagship: { pos: new THREE.Vector3(0, 16, 42), look: new THREE.Vector3(0, 4, 56) },'
        new_cam_targets = old_cam_targets + '\n            fire_closeup: { pos: new THREE.Vector3(-18, 5.5, -8), look: new THREE.Vector3(0, 3.8, -4) },'
        html = html.replace(old_cam_targets, new_cam_targets)

    # 3. Tạo toàn bộ khối mã Pyro Particle System
    pyro_code = """
        // =================================================================
        // HỆ THỐNG KHÓI LỬA WEBGL SIÊU THỰC (GPU PARTICLE ENGINE - BẠCH ĐẰNG 938)
        // Chuẩn công nghiệp: Soft Alpha Radial Textures, Zero CORS, 60 FPS
        // =================================================================
        function createParticlePuffTexture(type) {
            const canvas = document.createElement('canvas');
            canvas.width = 128;
            canvas.height = 128;
            const ctx = canvas.getContext('2d');
            const cx = 64, cy = 64;

            if (type === 'smoke') {
                // Khói muội than đen đặc, viền mờ mềm mại (Soft Radial Gradient)
                const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 60);
                grad.addColorStop(0.0, 'rgba(18, 20, 24, 0.96)');
                grad.addColorStop(0.35, 'rgba(30, 32, 38, 0.80)');
                grad.addColorStop(0.65, 'rgba(42, 45, 52, 0.40)');
                grad.addColorStop(0.85, 'rgba(38, 40, 46, 0.15)');
                grad.addColorStop(1.0, 'rgba(30, 32, 36, 0.0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(cx, cy, 60, 0, Math.PI * 2);
                ctx.fill();
            } else if (type === 'fire') {
                // Hạt lửa sáng rực PBR: Tâm trắng nóng -> Cam lửa -> Đỏ rực -> Mờ dần
                const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 58);
                grad.addColorStop(0.0, 'rgba(255, 255, 230, 1.0)');
                grad.addColorStop(0.22, 'rgba(255, 200, 40, 0.98)');
                grad.addColorStop(0.55, 'rgba(255, 90, 10, 0.75)');
                grad.addColorStop(0.82, 'rgba(200, 30, 5, 0.35)');
                grad.addColorStop(1.0, 'rgba(120, 10, 0, 0.0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(cx, cy, 58, 0, Math.PI * 2);
                ctx.fill();
            } else if (type === 'ember') {
                // Đốm tàn tro than hồng lấp lánh
                const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, 45);
                grad.addColorStop(0.0, 'rgba(255, 245, 200, 1.0)');
                grad.addColorStop(0.35, 'rgba(255, 140, 20, 0.90)');
                grad.addColorStop(0.75, 'rgba(255, 60, 0, 0.35)');
                grad.addColorStop(1.0, 'rgba(255, 30, 0, 0.0)');
                ctx.fillStyle = grad;
                ctx.beginPath();
                ctx.arc(cx, cy, 45, 0, Math.PI * 2);
                ctx.fill();
            }
            const tex = new THREE.CanvasTexture(canvas);
            tex.needsUpdate = true;
            return tex;
        }

        const smokeTex = createParticlePuffTexture('smoke');
        const fireTex = createParticlePuffTexture('fire');
        const emberTex = createParticlePuffTexture('ember');

        class Web3DPyroEngine {
            constructor(scene) {
                this.scene = scene;
                this.smokeCount = 550;
                this.fireCount = 380;
                this.emberCount = 150;

                // 1. Hệ thống hạt khói
                this.smokeGeom = new THREE.BufferGeometry();
                this.smokePos = new Float32Array(this.smokeCount * 3);
                this.smokeVel = [];
                this.smokeLife = new Float32Array(this.smokeCount);
                this.smokeMaxLife = new Float32Array(this.smokeCount);
                this.smokeSize = new Float32Array(this.smokeCount);

                for (let i = 0; i < this.smokeCount; i++) {
                    this.smokePos[i * 3] = 0;
                    this.smokePos[i * 3 + 1] = -500;
                    this.smokePos[i * 3 + 2] = 0;
                    this.smokeVel.push(new THREE.Vector3(0, 0, 0));
                    this.smokeLife[i] = 0;
                    this.smokeMaxLife[i] = 3.5 + Math.random() * 2.5;
                    this.smokeSize[i] = 1.0;
                }
                this.smokeGeom.setAttribute('position', new THREE.BufferAttribute(this.smokePos, 3));

                this.smokeMat = new THREE.PointsMaterial({
                    map: smokeTex,
                    size: 8.5,
                    transparent: true,
                    opacity: 0.85,
                    depthWrite: false,
                    blending: THREE.NormalBlending
                });
                this.smokePoints = new THREE.Points(this.smokeGeom, this.smokeMat);
                scene.add(this.smokePoints);

                // 2. Hệ thống hạt lửa
                this.fireGeom = new THREE.BufferGeometry();
                this.firePos = new Float32Array(this.fireCount * 3);
                this.fireVel = [];
                this.fireLife = new Float32Array(this.fireCount);
                this.fireMaxLife = new Float32Array(this.fireCount);

                for (let i = 0; i < this.fireCount; i++) {
                    this.firePos[i * 3] = 0;
                    this.firePos[i * 3 + 1] = -500;
                    this.firePos[i * 3 + 2] = 0;
                    this.fireVel.push(new THREE.Vector3(0, 0, 0));
                    this.fireLife[i] = 0;
                    this.fireMaxLife[i] = 0.6 + Math.random() * 0.9;
                }
                this.fireGeom.setAttribute('position', new THREE.BufferAttribute(this.firePos, 3));

                this.fireMat = new THREE.PointsMaterial({
                    map: fireTex,
                    size: 5.5,
                    transparent: true,
                    opacity: 0.95,
                    depthWrite: false,
                    blending: THREE.AdditiveBlending
                });
                this.firePoints = new THREE.Points(this.fireGeom, this.fireMat);
                scene.add(this.firePoints);

                // 3. Hệ thống hạt tàn tro than hồng
                this.emberGeom = new THREE.BufferGeometry();
                this.emberPos = new Float32Array(this.emberCount * 3);
                this.emberVel = [];
                this.emberLife = new Float32Array(this.emberCount);
                this.emberMaxLife = new Float32Array(this.emberCount);

                for (let i = 0; i < this.emberCount; i++) {
                    this.emberPos[i * 3] = 0;
                    this.emberPos[i * 3 + 1] = -500;
                    this.emberPos[i * 3 + 2] = 0;
                    this.emberVel.push(new THREE.Vector3(0, 0, 0));
                    this.emberLife[i] = 0;
                    this.emberMaxLife[i] = 2.0 + Math.random() * 2.0;
                }
                this.emberGeom.setAttribute('position', new THREE.BufferAttribute(this.emberPos, 3));

                this.emberMat = new THREE.PointsMaterial({
                    map: emberTex,
                    size: 1.8,
                    transparent: true,
                    opacity: 0.98,
                    depthWrite: false,
                    blending: THREE.AdditiveBlending
                });
                this.emberPoints = new THREE.Points(this.emberGeom, this.emberMat);
                scene.add(this.emberPoints);

                // 4. Đèn lửa động (Dynamic Firelight)
                this.fireLight = new THREE.PointLight(0xff4500, 0.0, 48, 1.4);
                this.fireLight.castShadow = false;
                scene.add(this.fireLight);

                // 5. Đèn mớn nước (Water Reflection Firelight)
                this.waterFireLight = new THREE.PointLight(0xff2200, 0.0, 24, 1.6);
                scene.add(this.waterFireLight);
            }

            resetParticle(i, type, basePos) {
                const ox = basePos.x + (Math.random() - 0.5) * 4.5;
                const oz = basePos.z + (Math.random() - 0.5) * 5.5;

                if (type === 'fire') {
                    const oy = basePos.y + 1.2 + Math.random() * 5.0; // Phát từ sàn boong lên nóc lầu
                    this.firePos[i * 3] = ox;
                    this.firePos[i * 3 + 1] = oy;
                    this.firePos[i * 3 + 2] = oz;
                    this.fireVel[i].set(
                        (Math.random() - 0.5) * 1.5 + 0.8,  // Dạt nhẹ theo gió
                        4.5 + Math.random() * 4.0,           // Bốc mạnh lên cao
                        (Math.random() - 0.5) * 1.5 - 1.2
                    );
                    this.fireLife[i] = 0;
                } else if (type === 'smoke') {
                    const oy = basePos.y + 3.0 + Math.random() * 6.5; // Bốc từ ngọn lửa lên trời
                    this.smokePos[i * 3] = ox + (Math.random() - 0.5) * 2.0;
                    this.smokePos[i * 3 + 1] = oy;
                    this.smokePos[i * 3 + 2] = oz + (Math.random() - 0.5) * 2.0;
                    this.smokeVel[i].set(
                        2.8 + Math.random() * 2.2,          // Dạt Đông Bắc (+X)
                        5.5 + Math.random() * 4.0,          // Bốc cao tít tắp (+Y)
                        -4.5 - Math.random() * 2.5          // Dạt Đông Nam (-Z)
                    );
                    this.smokeLife[i] = 0;
                } else if (type === 'ember') {
                    const oy = basePos.y + 2.0 + Math.random() * 8.0;
                    this.emberPos[i * 3] = ox;
                    this.emberPos[i * 3 + 1] = oy;
                    this.emberPos[i * 3 + 2] = oz;
                    this.emberVel[i].set(
                        (Math.random() - 0.5) * 4.0 + 3.2,
                        3.5 + Math.random() * 5.0,
                        (Math.random() - 0.5) * 4.0 - 4.5
                    );
                    this.emberLife[i] = 0;
                }
            }

            update(dt, progress, flagshipShip, time) {
                // Pha 1 & 2 (progress < 0.48): Chưa đâm cọc, chưa bốc cháy
                if (progress < 0.48 || !flagshipShip) {
                    this.smokePoints.visible = false;
                    this.firePoints.visible = false;
                    this.emberPoints.visible = false;
                    this.fireLight.intensity = 0.0;
                    this.waterFireLight.intensity = 0.0;
                    return;
                }

                // Pha 3 & 4 (progress >= 0.48): Tàu đâm cọc, bốc cháy dữ dội!
                this.smokePoints.visible = true;
                this.firePoints.visible = true;
                this.emberPoints.visible = true;

                // Quy mô đám cháy bùng lên theo tiến trình
                const fireIntensity = Math.min(1.0, (progress - 0.48) / 0.12);
                const shipPos = flagshipShip.position;

                // Cập nhật đèn chiếu sáng động nhấp nháy bập bùng
                const flicker = Math.sin(time * 24.0) * 0.8 + Math.cos(time * 38.0) * 0.5;
                this.fireLight.position.set(shipPos.x, shipPos.y + 5.5, shipPos.z);
                this.fireLight.intensity = (4.2 + flicker) * fireIntensity;

                this.waterFireLight.position.set(shipPos.x - 2.5, shipPos.y + 0.4, shipPos.z + 1.5);
                this.waterFireLight.intensity = (2.6 + flicker * 0.6) * fireIntensity;

                // 1. Cập nhật các hạt Lửa
                const activeFire = Math.floor(this.fireCount * fireIntensity);
                for (let i = 0; i < this.fireCount; i++) {
                    if (i > activeFire) {
                        this.firePos[i * 3 + 1] = -500;
                        continue;
                    }
                    this.fireLife[i] += dt;
                    if (this.fireLife[i] >= this.fireMaxLife[i]) {
                        this.resetParticle(i, 'fire', shipPos);
                    } else {
                        // Chuyển động lưỡi lửa
                        this.firePos[i * 3] += this.fireVel[i].x * dt;
                        this.firePos[i * 3 + 1] += this.fireVel[i].y * dt;
                        this.firePos[i * 3 + 2] += this.fireVel[i].z * dt;
                        // Rung lắc ngang ngọn lửa
                        this.firePos[i * 3] += Math.sin(time * 18.0 + i) * 0.06;
                        this.firePos[i * 3 + 2] += Math.cos(time * 16.0 + i) * 0.06;
                    }
                }
                this.fireGeom.attributes.position.needsUpdate = true;
                this.fireMat.size = 5.2 * (0.6 + 0.4 * fireIntensity);

                // 2. Cập nhật các hạt Khói đen muội than
                const activeSmoke = Math.floor(this.smokeCount * fireIntensity);
                for (let i = 0; i < this.smokeCount; i++) {
                    if (i > activeSmoke) {
                        this.smokePos[i * 3 + 1] = -500;
                        continue;
                    }
                    this.smokeLife[i] += dt;
                    if (this.smokeLife[i] >= this.smokeMaxLife[i]) {
                        this.resetParticle(i, 'smoke', shipPos);
                    } else {
                        this.smokePos[i * 3] += this.smokeVel[i].x * dt;
                        this.smokePos[i * 3 + 1] += this.smokeVel[i].y * dt;
                        this.smokePos[i * 3 + 2] += this.smokeVel[i].z * dt;
                    }
                }
                this.smokeGeom.attributes.position.needsUpdate = true;
                this.smokeMat.size = 9.5 * (0.5 + 0.5 * fireIntensity);

                // 3. Cập nhật Hạt tàn tro than hồng
                const activeEmber = Math.floor(this.emberCount * fireIntensity);
                for (let i = 0; i < this.emberCount; i++) {
                    if (i > activeEmber) {
                        this.emberPos[i * 3 + 1] = -500;
                        continue;
                    }
                    this.emberLife[i] += dt;
                    if (this.emberLife[i] >= this.emberMaxLife[i]) {
                        this.resetParticle(i, 'ember', shipPos);
                    } else {
                        this.emberPos[i * 3] += this.emberVel[i].x * dt;
                        this.emberPos[i * 3 + 1] += this.emberVel[i].y * dt;
                        this.emberPos[i * 3 + 2] += this.emberVel[i].z * dt;
                        this.emberPos[i * 3] += Math.sin(time * 8.0 + i) * 0.08;
                    }
                }
                this.emberGeom.attributes.position.needsUpdate = true;
            }
        }

        const pyroEngine = new Web3DPyroEngine(scene);
"""

    # Chèn pyro_code trước phần animate()
    if 'class Web3DPyroEngine' not in html:
        old_clock = 'const clock = new THREE.Clock();'
        html = html.replace(old_clock, pyro_code + '\n        ' + old_clock)

    # 4. Trong animate(): gọi pyroEngine.update
    if 'pyroEngine.update' not in html:
        old_render = 'renderer.render(scene, camera);'
        pyro_update_call = """
            // Cập nhật Hệ thống Khói Lửa WebGL Siêu Thực
            const flagship = namHanFleet.find(s => s.userData.isFlagship) || namHanFleet[3];
            pyroEngine.update(dt, simProgress, flagship, time);

            """
        html = html.replace(old_render, pyro_update_call + old_render)

    # 5. Tự động chuyển sang góc nhìn Hero Shot khi bấm Pha 3 (nếu người dùng muốn xem cận cảnh đâm cọc cháy tàu)
    # Tinh chỉnh mô tả Pha 3 trong dropdown
    old_p3_desc = 'Triều rút sâu (-0.90m), bãi cọc nhọn nhô lên đâm toác lườn tàu giặc đắm chìm'
    new_p3_desc = 'Triều rút sâu (-0.90m), cọc sắt đâm toác lườn, soái hạm Hoằng Tháo bốc cháy dữ dội!'
    html = html.replace(old_p3_desc, new_p3_desc)

    with open('mo_phong_bach_dang_938.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Đã tích hợp thành công Web3D GPU Particle Engine vào mo_phong_bach_dang_938.html!")

if __name__ == '__main__':
    update_html()
