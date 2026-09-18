# QUY TRÌNH SẢN XUẤT 3D CHUẨN CÔNG NGHIỆP & TỰ ĐỘNG HÓA WEB3D
## DỰ ÁN: MÔ PHỎNG ĐẠI CHIẾN BẠCH ĐẰNG 938 (NGÔ QUYỀN PHÁ QUÂN NAM HÁN)
**Tiêu chuẩn áp dụng:** Blender Studio Open Movie Pipeline, Pixar OpenUSD, Khronos glTF 2.0, Three.js WebGL/WebGPU.

---

## I. NGUYÊN TẮC CỐT TỬ CỦA QUY TRÌNH CÔNG NGHIỆP (ASSET-CENTRIC PIPELINE)

Trong sản xuất CGI/VFX và Game chuyên nghiệp (Pixar, ILM, Weta, Blender Studio):
> **"Tuyệt đối không bao giờ dựng toàn bộ thế giới trong một file cảnh duy nhất."**
> Mọi thành phần phải được sản xuất độc lập thành các **Master Assets**, trải qua kiểm thử chất lượng (LookDev), sau đó mới được **Liên kết động (Linking)** và **Ghi đè thuộc tính (Library Overrides)** vào phân cảnh tổng thể.

### Cấu trúc Thư mục Chuẩn Studio:
```
TEST_BLENDER/
├── assets/                          # KHO TÀI NGUYÊN ĐỘC LẬP
│   ├── props/
│   │   └── coc_bach_dang_master.blend       # Gỗ lim bịt sắt + 3 biến thể cong/gãy
│   ├── ships/
│   │   ├── thuyen_ta_ngoquyen_master.blend  # Thuyền Đại Việt + rig buồm + mái chèo
│   │   ├── lau_thuyen_namhan_intact.blend   # Lâu thuyền nguyên vẹn 3 tầng lầu
│   │   ├── lau_thuyen_namhan_punctured.blend# Biến thể: Thủng đáy, vỡ ván mạn
│   │   └── lau_thuyen_namhan_burnt.blend    # Biến thể: Cháy đen, trơ khung xà
│   └── characters/
│       └── thuy_binh_dai_viet.blend         # Quân sĩ chèo thuyền (gắn rig + anim cycle)
├── environments/                    # BỐI CẢNH & BẦU TRỜI ĐỘC LẬP
│   ├── terrain_trang_kenh_gis.blend         # Núi đá Tràng Kênh + bãi lầy sú vẹt
│   ├── sky_bach_dang_winter_938.blend       # Bầu trời lịch sử (Sun Position 938)
│   └── river_water_tide.blend               # Mặt nước sông + chu kỳ rút thủy triều
├── scenes/                          # SÂN KHẤU LẮP GHÉP TỔNG THỂ
│   └── dai_chien_bach_dang_assembly.blend   # File chính chỉ Link & Override các assets
└── web3d_export/                    # XUẤT BẢN RA WEB CHUẨN QUỐC TẾ
    ├── bach_dang_battle_optimized.glb      # File nhị phân glTF 2.0 chuẩn ISO/IEC 12113
    └── index.html                           # Ứng dụng WebGL tương tác qua Three.js
```

---

## II. ĐẶC TẢ CHUYỂN ĐỘNG VẬT LÝ TOÀN DIỆN (MOTION DYNAMICS)

Trận thủy chiến Bạch Đằng bao gồm 6 tầng chuyển động phức hợp:

### 1. Chuyển động Thân thuyền Bập bềnh trên Sóng (Boat Buoyancy Dynamics)
*   **3 Bậc tự do trên mặt nước**:
    *   *Pitch (Nhấp nhô mũi - đuôi)*: Thuyền gối đầu qua từng ngọn sóng sông cửa biển.
    *   *Roll (Chao đảo mạn trái - phải)*: Lắc lư theo lực đẩy của gió và nhịp chèo.
    *   *Heave (Nâng hạ theo phương thẳng đứng)*: Thuyền nâng lên khi triều dâng và hạ thấp khi triều rút.
*   **Chuyển động Va chạm & Mắc cạn (Grounding & Sinking Impulse)**:
    *   *Khựng lại đột ngột*: Khi đáy thuyền Nam Hán đâm trúng cọc ngầm ở tốc độ cao, thân thuyền bị giảm tốc tức thì (Deceleration impulse).
    *   *Nghiêng mạn nguy hiểm (Severe List)*: Cọc đâm lệch tâm lườn tàu làm thuyền nghiêng 20°–35°, nước tràn ồ ạt vào khoang làm thuyền chìm dần.

### 2. Chuyển động Xương Quân sĩ Chèo thuyền (Skeletal Rowing Cycles)
*   Chu kỳ chèo thuyền khép kín gồm 4 pha cơ học:
    1.  *Catch (Cắm chèo)*: Quân sĩ vươn người về trước, cắm lưỡi chèo xuống nước.
    2.  *Drive (Kéo lực)*: Đạp chân, ngửa lưng kéo mái chèo ngược dòng nước để đẩy thuyền tiến lên.
    3.  *Finish (Thoát nước)*: Nhấc mái chèo ra khỏi mặt nước.
    4.  *Recovery (Hồi vị)*: Đẩy tay chèo về phía trước chuẩn bị chu kỳ mới.
*   *Độ lệch pha (Commotion Phase Offset)*: Hàng chục tay chèo hai bên mạn có độ trễ 0.1s - 0.15s tạo nhịp sóng chèo tự nhiên như người thật.

### 3. Chuyển động Khí động học Cánh buồm & Cờ hiệu (Aerodynamics)
*   *Buồm Cánh Dơi*: Nan tre uốn cong tạo độ vồng (camber). Khi đổi hướng gió, buồm phồng căng (billowing) và vạt buồm rung nhẹ (flutter).
*   *Cờ hiệu ngũ sắc & Cờ tướng quân*: Bay phất phới theo sóng hình sin (Wiggle Bones) cuộn theo luồng gió mùa Đông Bắc.

### 4. Chuyển động Thủy triều Sông Bạch Đằng (Tidal Descent)
*   Mặt phẳng nước sông (`river_plane`) được keyframe dịch chuyển dọc trục Z hạ thấp từ mức **+1.5m** (triều cường ngập cọc) xuống **-2.0m** (triều kiệt lộ bãi cọc nhọn) trong vòng 300 khung hình.

### 5. Chuyển động Đạn đạo Mưa tên Hỏa công (Ballistics & VFX)
*   Hàng ngàn mũi tên lửa bắn từ hai bờ núi Tràng Kênh bay theo quỹ đạo hình parabol (được bake thành keyframe bằng `Cake_Particles`).

---

## III. TỰ ĐỘNG HÓA BẰNG PYTHON: LIÊN KẾT (LINKING) & GHI ĐÈ (LIBRARY OVERRIDES)

Đoạn mã Python điều phối lắp ráp cảnh tổng thể từ các Master Assets độc lập:

```python
import bpy
import os

def assemble_battle_scene(assets_dir):
    bpy.ops.wm.read_homefile(use_empty=True)
    scene = bpy.context.scene
    
    # 1. Liên kết Địa hình Núi Tràng Kênh (Link Collection)
    terrain_path = os.path.join(assets_dir, "environments", "terrain_trang_kenh_gis.blend")
    with bpy.data.libraries.load(terrain_path, link=True) as (data_from, data_to):
        data_to.collections = ["Collection_Terrain_TrangKenh"]
    
    col_terrain = data_to.collections[0]
    inst_terrain = bpy.data.objects.new("Terrain_Instance", None)
    inst_terrain.instance_type = 'COLLECTION'
    inst_terrain.instance_collection = col_terrain
    scene.collection.objects.link(inst_terrain)
    
    # 2. Liên kết Thuyền Ta & Tạo Library Override để Diễn hoạt Chuyển động
    ship_path = os.path.join(assets_dir, "assets", "ships", "thuyen_ta_ngoquyen_master.blend")
    with bpy.data.libraries.load(ship_path, link=True) as (data_from, data_to):
        data_to.collections = ["Collection_Thuyen_Ta"]
        
    col_ship = data_to.collections[0]
    inst_ship = bpy.data.objects.new("Thuyen_Ta_01", None)
    inst_ship.instance_type = 'COLLECTION'
    inst_ship.instance_collection = col_ship
    scene.collection.objects.link(inst_ship)
    
    # Tạo Library Override để đặt vị trí, xoay và diễn hoạt mà không sửa file gốc
    ship_override = inst_ship.override_hierarchy_create(scene, bpy.context.view_layer)
    print("-> Đã Link và tạo Library Override thành công cho Thuyền Ta!")
```

---

## IV. NƯỚNG CHUYỂN ĐỘNG & XUẤT RA CHUẨN QUỐC TẾ GLTF 2.0 (GLB)

Vì WebGL/Three.js không thể chạy trực tiếp các bộ tính toán vật lý nội bộ của Blender, toàn bộ chuyển động (xương, biến dạng, di chuyển) phải được **Nướng (Bake)** vào các kênh chuyển động chuẩn:

```python
def export_scene_to_gltf_glb(output_glb_path):
    print("-> Đang nướng Animation và xuất khẩu ra chuẩn ISO/IEC 12113 glTF 2.0...")
    
    bpy.ops.export_scene.gltf(
        filepath=output_glb_path,
        export_format='GLB',                 # File nhị phân nén duy nhất chứa mesh, PBR, anim
        export_image_format='AUTO',
        export_animations=True,              # Bắt buộc bật xuất animation
        export_bake_animation=True,          # Tự động nướng tất cả chu kỳ chuyển động
        export_animation_mode='ACTIONS',     # Xuất các NLA Tracks/Actions
        export_skins=True,                   # Xuất khung xương lính và buồm (Armatures)
        export_morph=True,                   # Xuất biến dạng sóng nước và vải buồm (Morph Targets)
        export_morph_animation=True,
        export_optimize_animation_size=True,
        export_apply=False                   # Giữ nguyên cấu trúc phân cấp armature
    )
    print(f"=== XUẤT THÀNH CÔNG FILE GLB: {output_glb_path} ===")
```

---

## V. ĐỌC VÀ XUẤT BẢN RA WEB3D TƯƠNG TÁC BẰNG THREE.JS

Tệp HTML hoàn chỉnh sử dụng thư viện **Three.js** chuẩn quốc tế để người xem có thể xoay 360°, zoom, và theo dõi toàn bộ trận thủy chiến đang chuyển động ngay trên trình duyệt:

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mô Phỏng 3D Đại Chiến Bạch Đằng 938 - Three.js WebGL</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: sans-serif; }
        #loading { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #fff; font-size: 20px; }
        #ui { position: absolute; bottom: 20px; left: 20px; color: #f5d76e; background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px; border: 1px solid #c5a059; }
    </style>
    <!-- Nạp Three.js qua ESM CDN chính thức -->
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
    <div id="loading">Đang tải trận chiến 3D Bạch Đằng 938...</div>
    <div id="ui">
        <h3 style="margin: 0 0 5px 0;">ĐẠI CHIẾN BẠCH ĐẰNG 938</h3>
        <div>Thời khắc: Mùa đông năm 938 - Triều rút trên sông Bạch Đằng</div>
        <div>Chuột trái: Xoay 360° | Chuột phải: Di chuyển | Cuộn chuột: Phóng to/Thu nhỏ</div>
    </div>

    <script type="module">
        import * as THREE from 'three';
        import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
        import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

        // 1. Khởi tạo Sân khấu (Scene), Máy quay (Camera) & Bộ kết xuất (Renderer)
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x8fa3ad); // Bầu trời sông nước mùa đông
        scene.fog = new THREE.FogExp2(0x8fa3ad, 0.005);

        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 2000);
        camera.position.set(60, 30, 80);

        const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.1;
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(renderer.domElement);

        // 2. Điều khiển Camera (Orbit Controls)
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2 - 0.02;

        // 3. Hệ thống Ánh sáng (Lighting)
        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1.2);
        scene.add(hemiLight);

        const dirLight = new THREE.DirectionalLight(0xfffaed, 2.5); // Ánh nắng mùa đông
        dirLight.position.set(100, 150, 50);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        scene.add(dirLight);

        // 4. Quản lý Diễn hoạt Chuyển động (Animation Mixer)
        let mixer;
        const clock = new THREE.Clock();

        // 5. Nạp Tệp Mô hình glTF/GLB chuẩn Quốc tế
        const loader = new GLTFLoader();
        loader.load('bach_dang_battle_optimized.glb', (gltf) => {
            document.getElementById('loading').style.display = 'none';
            const model = gltf.scene;
            model.traverse((child) => {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                }
            });
            scene.add(model);

            // Tự động kích hoạt toàn bộ các chuyển động đã nướng (thuyền bơi, lính chèo, nước rút)
            if (gltf.animations && gltf.animations.length > 0) {
                mixer = new THREE.AnimationMixer(model);
                gltf.animations.forEach((clip) => {
                    mixer.clipAction(clip).play();
                });
                console.log(`Đã kích hoạt ${gltf.animations.length} chu kỳ chuyển động đồng thời!`);
            }
        }, 
        (xhr) => {
            const percent = Math.round((xhr.loaded / xhr.total) * 100);
            document.getElementById('loading').innerText = `Đang tải: ${percent}%`;
        }, 
        (error) => {
            console.error('Lỗi khi nạp file 3D:', error);
            document.getElementById('loading').innerText = 'Không tìm thấy file bach_dang_battle_optimized.glb. Hãy chạy lệnh xuất từ Blender!';
        });

        // 6. Vòng lặp Kết xuất Thời gian thực (Render Loop 60 FPS)
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        function animate() {
            requestAnimationFrame(animate);
            const delta = clock.getDelta();
            if (mixer) mixer.update(delta);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
```
