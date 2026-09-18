# -*- coding: utf-8 -*-
"""
HOÀN THIỆN ĐỘNG CƠ KHÓI LỬA WEBGL THREE.JS SIÊU THỰC
- Khởi tạo hạt phân bổ đều theo tuổi thọ (xuất hiện tức thì khi vào Pha 3)
- Kích thước hạt tối ưu hiển thị rõ cả Toàn cảnh lẫn Cận cảnh (size 28m cho khói, 14m cho lửa)
- Bốc cháy trên Soái hạm Hoằng Tháo và 2 tàu hộ vệ bị cọc đâm
- Cột khói đen bốc cao 45m cuồn cuộn bạt theo gió Đông Bắc
"""
import re

def update_pyro_engine():
    with open('mo_phong_bach_dang_938.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Đoạn mã mới hoàn thiện của Web3DPyroEngine
    old_pyro_start = "// ================================================================="
    old_pyro_find = "class Web3DPyroEngine {"
    
    # Tìm vị trí bắt đầu của Web3DPyroEngine
    idx_class = html.find(old_pyro_find)
    if idx_class == -1:
        print("Không tìm thấy Web3DPyroEngine!")
        return

    # Tìm vị trí kết thúc class Web3DPyroEngine
    idx_engine_inst = html.find("const pyroEngine = new Web3DPyroEngine(scene);", idx_class)
    if idx_engine_inst == -1:
        print("Không tìm thấy pyroEngine instantiation!")
        return

    new_engine_class = """class Web3DPyroEngine {
            constructor(scene) {
                this.scene = scene;
                this.smokeCount = 650;
                this.fireCount = 450;
                this.emberCount = 200;

                // 1. Hệ thống hạt khói đen muội than
                this.smokeGeom = new THREE.BufferGeometry();
                this.smokePos = new Float32Array(this.smokeCount * 3);
                this.smokeVel = [];
                this.smokeLife = new Float32Array(this.smokeCount);
                this.smokeMaxLife = new Float32Array(this.smokeCount);

                for (let i = 0; i < this.smokeCount; i++) {
                    this.smokeMaxLife[i] = 4.0 + Math.random() * 3.0;
                    this.smokeLife[i] = Math.random() * this.smokeMaxLife[i]; // Phân bổ đều ngay từ đầu
                    this.smokePos[i * 3] = 0;
                    this.smokePos[i * 3 + 1] = -500;
                    this.smokePos[i * 3 + 2] = 0;
                    this.smokeVel.push(new THREE.Vector3(0, 0, 0));
                }
                this.smokeGeom.setAttribute('position', new THREE.BufferAttribute(this.smokePos, 3));

                this.smokeMat = new THREE.PointsMaterial({
                    map: smokeTex,
                    size: 26.0,
                    sizeAttenuation: true,
                    transparent: true,
                    opacity: 0.88,
                    depthWrite: false,
                    blending: THREE.NormalBlending
                });
                this.smokePoints = new THREE.Points(this.smokeGeom, this.smokeMat);
                scene.add(this.smokePoints);

                // 2. Hệ thống hạt lửa PBR cuộn xoáy
                this.fireGeom = new THREE.BufferGeometry();
                this.firePos = new Float32Array(this.fireCount * 3);
                this.fireVel = [];
                this.fireLife = new Float32Array(this.fireCount);
                this.fireMaxLife = new Float32Array(this.fireCount);

                for (let i = 0; i < this.fireCount; i++) {
                    this.fireMaxLife[i] = 0.8 + Math.random() * 1.0;
                    this.fireLife[i] = Math.random() * this.fireMaxLife[i];
                    this.firePos[i * 3] = 0;
                    this.firePos[i * 3 + 1] = -500;
                    this.firePos[i * 3 + 2] = 0;
                    this.fireVel.push(new THREE.Vector3(0, 0, 0));
                }
                this.fireGeom.setAttribute('position', new THREE.BufferAttribute(this.firePos, 3));

                this.fireMat = new THREE.PointsMaterial({
                    map: fireTex,
                    size: 14.5,
                    sizeAttenuation: true,
                    transparent: true,
                    opacity: 0.98,
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
                    this.emberMaxLife[i] = 2.5 + Math.random() * 2.5;
                    this.emberLife[i] = Math.random() * this.emberMaxLife[i];
                    this.emberPos[i * 3] = 0;
                    this.emberPos[i * 3 + 1] = -500;
                    this.emberPos[i * 3 + 2] = 0;
                    this.emberVel.push(new THREE.Vector3(0, 0, 0));
                }
                this.emberGeom.setAttribute('position', new THREE.BufferAttribute(this.emberPos, 3));

                this.emberMat = new THREE.PointsMaterial({
                    map: emberTex,
                    size: 3.5,
                    sizeAttenuation: true,
                    transparent: true,
                    opacity: 0.95,
                    depthWrite: false,
                    blending: THREE.AdditiveBlending
                });
                this.emberPoints = new THREE.Points(this.emberGeom, this.emberMat);
                scene.add(this.emberPoints);

                // 4. Ánh sáng lửa động (Dynamic Firelight)
                this.fireLight = new THREE.PointLight(0xff5500, 0.0, 75, 1.2);
                scene.add(this.fireLight);

                this.waterFireLight = new THREE.PointLight(0xff2200, 0.0, 45, 1.5);
                scene.add(this.waterFireLight);
            }

            resetParticle(i, type, basePos) {
                // Tâm đám cháy lấy từ Soái hạm hoặc 2 tàu bên cạnh
                const shipSelect = (i % 5 === 0) ? -28 : ((i % 7 === 0) ? +28 : 0);
                const ox = basePos.x + shipSelect + (Math.random() - 0.5) * 5.5;
                const oz = basePos.z + (Math.random() - 0.5) * 6.5;

                if (type === 'fire') {
                    const oy = basePos.y + 0.8 + Math.random() * 7.5; // Liếm từ mớn nước lên đỉnh cột buồm
                    this.firePos[i * 3] = ox;
                    this.firePos[i * 3 + 1] = oy;
                    this.firePos[i * 3 + 2] = oz;
                    this.fireVel[i].set(
                        (Math.random() - 0.5) * 2.0 + 1.2, // Gió Đông Bắc dạt sang +X
                        5.5 + Math.random() * 5.0,         // Bốc cao
                        (Math.random() - 0.5) * 2.0 - 1.8  // Gió dạt sang -Z
                    );
                    this.fireLife[i] = 0;
                } else if (type === 'smoke') {
                    const oy = basePos.y + 3.5 + Math.random() * 8.0;
                    this.smokePos[i * 3] = ox + (Math.random() - 0.5) * 3.0;
                    this.smokePos[i * 3 + 1] = oy;
                    this.smokePos[i * 3 + 2] = oz + (Math.random() - 0.5) * 3.0;
                    this.smokeVel[i].set(
                        3.5 + Math.random() * 3.0,         // Dạt mạnh theo gió mùa Đông Bắc
                        6.5 + Math.random() * 5.5,         // Bốc cao ngút trời lên tới 45m
                        -5.5 - Math.random() * 3.5
                    );
                    this.smokeLife[i] = 0;
                } else if (type === 'ember') {
                    const oy = basePos.y + 2.0 + Math.random() * 10.0;
                    this.emberPos[i * 3] = ox;
                    this.emberPos[i * 3 + 1] = oy;
                    this.emberPos[i * 3 + 2] = oz;
                    this.emberVel[i].set(
                        (Math.random() - 0.5) * 5.0 + 3.8,
                        4.0 + Math.random() * 6.0,
                        (Math.random() - 0.5) * 5.0 - 5.0
                    );
                    this.emberLife[i] = 0;
                }
            }

            update(dt, progress, flagshipShip, time) {
                if (progress < 0.45 || !flagshipShip) {
                    this.smokePoints.visible = false;
                    this.firePoints.visible = false;
                    this.emberPoints.visible = false;
                    this.fireLight.intensity = 0.0;
                    this.waterFireLight.intensity = 0.0;
                    return;
                }

                this.smokePoints.visible = true;
                this.firePoints.visible = true;
                this.emberPoints.visible = true;

                const fireIntensity = Math.min(1.0, (progress - 0.45) / 0.12);
                const shipPos = flagshipShip.position;

                // Ánh sáng lửa bập bùng chiếu rọi chiến trường
                const flicker = Math.sin(time * 26.0) * 1.2 + Math.cos(time * 41.0) * 0.8;
                this.fireLight.position.set(shipPos.x, shipPos.y + 6.5, shipPos.z);
                this.fireLight.intensity = (5.8 + flicker) * fireIntensity;

                this.waterFireLight.position.set(shipPos.x - 3.5, shipPos.y + 0.5, shipPos.z + 2.0);
                this.waterFireLight.intensity = (3.8 + flicker * 0.8) * fireIntensity;

                // 1. Cập nhật hạt Lửa
                const activeFire = Math.floor(this.fireCount * fireIntensity);
                for (let i = 0; i < this.fireCount; i++) {
                    if (i > activeFire) {
                        this.firePos[i * 3 + 1] = -500;
                        continue;
                    }
                    this.fireLife[i] += dt;
                    if (this.fireLife[i] >= this.fireMaxLife[i] || this.firePos[i * 3 + 1] < -100) {
                        this.resetParticle(i, 'fire', shipPos);
                    } else {
                        this.firePos[i * 3] += this.fireVel[i].x * dt;
                        this.firePos[i * 3 + 1] += this.fireVel[i].y * dt;
                        this.firePos[i * 3 + 2] += this.fireVel[i].z * dt;
                        this.firePos[i * 3] += Math.sin(time * 20.0 + i) * 0.08;
                    }
                }
                this.fireGeom.attributes.position.needsUpdate = true;
                this.fireMat.opacity = 0.95 * fireIntensity;

                // 2. Cập nhật hạt Khói đen muội than
                const activeSmoke = Math.floor(this.smokeCount * fireIntensity);
                for (let i = 0; i < this.smokeCount; i++) {
                    if (i > activeSmoke) {
                        this.smokePos[i * 3 + 1] = -500;
                        continue;
                    }
                    this.smokeLife[i] += dt;
                    if (this.smokeLife[i] >= this.smokeMaxLife[i] || this.smokePos[i * 3 + 1] < -100) {
                        this.resetParticle(i, 'smoke', shipPos);
                    } else {
                        this.smokePos[i * 3] += this.smokeVel[i].x * dt;
                        this.smokePos[i * 3 + 1] += this.smokeVel[i].y * dt;
                        this.smokePos[i * 3 + 2] += this.smokeVel[i].z * dt;
                        this.smokePos[i * 3] += Math.sin(time * 6.0 + i) * 0.05;
                    }
                }
                this.smokeGeom.attributes.position.needsUpdate = true;
                this.smokeMat.opacity = 0.86 * fireIntensity;

                // 3. Cập nhật hạt tàn tro than hồng
                const activeEmber = Math.floor(this.emberCount * fireIntensity);
                for (let i = 0; i < this.emberCount; i++) {
                    if (i > activeEmber) {
                        this.emberPos[i * 3 + 1] = -500;
                        continue;
                    }
                    this.emberLife[i] += dt;
                    if (this.emberLife[i] >= this.emberMaxLife[i] || this.emberPos[i * 3 + 1] < -100) {
                        this.resetParticle(i, 'ember', shipPos);
                    } else {
                        this.emberPos[i * 3] += this.emberVel[i].x * dt;
                        this.emberPos[i * 3 + 1] += this.emberVel[i].y * dt;
                        this.emberPos[i * 3 + 2] += this.emberVel[i].z * dt;
                        this.emberPos[i * 3] += Math.sin(time * 10.0 + i) * 0.12;
                    }
                }
                this.emberGeom.attributes.position.needsUpdate = true;
            }
        }
"""

    html = html[:idx_class] + new_engine_class + '\n        ' + html[idx_engine_inst:]

    # Cập nhật camera fire_closeup vị trí điện ảnh hơn:
    # camera đặt ở (-22, 7.5, -12), nhìn vào (0, 4.0, -4)
    old_fc = 'fire_closeup: { pos: new THREE.Vector3(-18, 5.5, -8), look: new THREE.Vector3(0, 3.8, -4) },'
    new_fc = 'fire_closeup: { pos: new THREE.Vector3(-24, 7.8, -12), look: new THREE.Vector3(0, 4.2, -4) },'
    html = html.replace(old_fc, new_fc)

    with open('mo_phong_bach_dang_938.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    with open('web3d_export/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("SUCCESS: Hoan tat nang cap Web3DPyroEngine cho ca 2 file HTML!")

if __name__ == '__main__':
    update_pyro_engine()
