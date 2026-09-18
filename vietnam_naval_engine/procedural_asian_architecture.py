import bpy
import bmesh
import math
from mathutils import Vector, Matrix, Euler

def generate_tile_roof(bm, x_center, y_center, z_base, length_x, width_y, roof_height=1.15, overhang=0.55):
    '''
    Mái Ngói Âm Dương 3D Cổ Truyền:
    - Khối dốc mái lợp ván đáy kín nước (Solid timber ceiling/roof deck).
    - Hàng trăm viên ngói ống úp bán nguyệt 3D (Cylindrical Tile Ridges).
    - Đầu ngói trích thủy (Eave roundels) trang trí mép mái.
    - Bờ nóc (Ridge beam) và hai đầu Kìm Nóc (Chiwen) uốn cong.
    '''
    # 1. Khối dốc mái lợp ván đáy kín nước (Solid under-roof deck)
    lx = length_x + overhang * 2
    wy = width_y + overhang * 2
    top_lx = length_x * 0.45
    top_wy = 0.30

    pts_base = [
        Vector((x_center - lx*0.5, y_center - wy*0.5, z_base - 0.04)),
        Vector((x_center + lx*0.5, y_center - wy*0.5, z_base - 0.04)),
        Vector((x_center + lx*0.5, y_center + wy*0.5, z_base - 0.04)),
        Vector((x_center - lx*0.5, y_center + wy*0.5, z_base - 0.04)),
        Vector((x_center - top_lx*0.5, y_center - top_wy*0.5, z_base + roof_height)),
        Vector((x_center + top_lx*0.5, y_center - top_wy*0.5, z_base + roof_height)),
        Vector((x_center + top_lx*0.5, y_center + top_wy*0.5, z_base + roof_height)),
        Vector((x_center - top_lx*0.5, y_center + top_wy*0.5, z_base + roof_height)),
    ]
    vb = [bm.verts.new(p) for p in pts_base]
    bm.faces.new([vb[3], vb[2], vb[1], vb[0]])
    bm.faces.new([vb[0], vb[1], vb[5], vb[4]])
    bm.faces.new([vb[1], vb[2], vb[6], vb[5]])
    bm.faces.new([vb[2], vb[3], vb[7], vb[6]])
    bm.faces.new([vb[3], vb[0], vb[4], vb[7]])
    bm.faces.new([vb[4], vb[5], vb[6], vb[7]])

    # 2. Các hàng ngói bán nguyệt 3D (Over-tile Ridges) nổi trên mặt mái
    num_rows_x = int(length_x / 0.28) # Mỗi hàng ngói cách nhau 28cm
    dx = (length_x - 0.1) / max(1, num_rows_x - 1)

    for side_y in [-1, 1]:
        for ri in range(num_rows_x):
            cur_x = (x_center - length_x*0.5 + 0.05) + ri * dx
            p_top = Vector((cur_x, y_center + side_y * top_wy * 0.5, z_base + roof_height + 0.02))
            p_bot = Vector((cur_x, y_center + side_y * (width_y * 0.5 + overhang), z_base - 0.02))

            diff = p_bot - p_top
            r_len = diff.length
            mid = (p_top + p_bot) * 0.5
            dir_v = diff.normalized()

            up = Vector((0, 0, 1))
            ax = up.cross(dir_v)
            if ax.length > 1e-4:
                ax.normalize()
                ang = math.acos(max(-1.0, min(1.0, up.dot(dir_v))))
                rmat = Matrix.Rotation(ang, 4, ax)
            else:
                rmat = Matrix.Identity(4)

            # Hàng ngói ống úp bán nguyệt nổi gờ 3D
            mat_tile = Matrix.Translation(mid) @ rmat
            bmesh.ops.create_cone(
                bm, cap_ends=True, segments=8,
                radius1=0.062, radius2=0.052, depth=r_len,
                matrix=mat_tile
            )

            # Đầu ngói diềm trích thủy (Hình tròn trang trí ở mép giọt tranh)
            bmesh.ops.create_cone(
                bm, cap_ends=True, segments=12,
                radius1=0.075, radius2=0.075, depth=0.04,
                matrix=Matrix.Translation(p_bot) @ rmat
            )

    # 3. Bờ nóc trung tâm (Ridge Beam) & Kìm Nóc (Chiwen)
    r_start = Vector((x_center - top_lx * 0.75, y_center, z_base + roof_height + 0.08))
    r_end   = Vector((x_center + top_lx * 0.75, y_center, z_base + roof_height + 0.08))
    r_mid = (r_start + r_end) * 0.5
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation(r_mid) @ Matrix.Diagonal(Vector((top_lx * 1.5, 0.24, 0.20, 1.0)))
    )

    for p_end, dir_k in [(r_start, -1), (r_end, 1)]:
        bmesh.ops.create_cone(
            bm, cap_ends=True, segments=10,
            radius1=0.11, radius2=0.02, depth=0.55,
            matrix=Matrix.Translation(p_end + Vector((dir_k * 0.18, 0, 0.25))) @ Matrix.Rotation(math.radians(dir_k * 40), 4, 'Y')
        )

def generate_dougong_brackets(bm, x_center, y_center, z_eave, length_x, width_y):
    '''Hệ thống Đẩu Củng (Dou-gong Brackets) gỗ chìa ra đỡ mái lầu'''
    num_brackets = int(length_x / 0.85)
    dx = (length_x - 0.4) / max(1, num_brackets - 1)

    for side_y in [-1, 1]:
        y_pos = y_center + side_y * (width_y * 0.5 - 0.05)
        for bi in range(num_brackets):
            bx = (x_center - length_x * 0.5 + 0.2) + bi * dx
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation(Vector((bx, y_pos, z_eave - 0.14))) @ Matrix.Diagonal(Vector((0.22, 0.22, 0.12, 1.0)))
            )
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation(Vector((bx, y_pos + side_y * 0.16, z_eave - 0.07))) @ Matrix.Diagonal(Vector((0.16, 0.36, 0.09, 1.0)))
            )
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation(Vector((bx, y_pos + side_y * 0.30, z_eave - 0.01))) @ Matrix.Diagonal(Vector((0.14, 0.32, 0.08, 1.0)))
            )

def generate_timber_wall_with_lattice_windows(bm, x_center, y_center, z_base, z_height, length_x, width_y):
    '''
    Tường Vách Gỗ Cổ Điển với Hệ Thống Khung Cột, Vách Ván Ghép Dày và Chấn Song Cửa Sổ:
    - Khối vách ván gỗ dày (Solid timber core wall).
    - Các cột trụ tròn ở 4 góc và các cột quân.
    - Khung dầm xà ngang bo viền.
    - Các ô cửa sổ có khung bao và nan chấn song gỗ (Lattice bars).
    '''
    # 1. Khối vách ván gỗ kín chịu lực (Solid Timber Core)
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=Matrix.Translation(Vector((x_center, y_center, z_base + z_height*0.5))) @ \
               Matrix.Diagonal(Vector((length_x * 0.98, width_y * 0.98, z_height, 1.0)))
    )

    # 2. Bốn cột trụ gỗ tròn ở 4 góc
    rad_pillar = 0.12
    for cx in [x_center - length_x*0.5 + rad_pillar, x_center + length_x*0.5 - rad_pillar]:
        for cy in [y_center - width_y*0.5 + rad_pillar, y_center + width_y*0.5 - rad_pillar]:
            bmesh.ops.create_cone(
                bm, cap_ends=True, segments=12,
                radius1=rad_pillar, radius2=rad_pillar, depth=z_height + 0.05,
                matrix=Matrix.Translation(Vector((cx, cy, z_base + z_height*0.5)))
            )

    # 3. Dầm xà ngang trên và dưới
    for side_y in [-1, 1]:
        y_beam = y_center + side_y * (width_y*0.5 + 0.01)
        # Xà trên
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation(Vector((x_center, y_beam, z_base + z_height - 0.08))) @ Matrix.Diagonal(Vector((length_x + 0.05, 0.12, 0.16, 1.0)))
        )
        # Xà đáy
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation(Vector((x_center, y_beam, z_base + 0.08))) @ Matrix.Diagonal(Vector((length_x + 0.05, 0.12, 0.16, 1.0)))
        )

        # 4. Các ô cửa sổ chấn song gỗ (Lattice Windows)
        num_windows = 3
        win_spacing = length_x / (num_windows + 1)
        for wi in range(num_windows):
            wx = (x_center - length_x*0.5) + (wi + 1) * win_spacing
            w_center = Vector((wx, y_beam + side_y * 0.03, z_base + z_height*0.5))

            # Khung bao cửa sổ gỗ dày nổi gờ 3D
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation(w_center) @ Matrix.Diagonal(Vector((0.95, 0.12, 1.10, 1.0)))
            )
            # Khung khoét cửa sổ bên trong
            bmesh.ops.create_cube(
                bm, size=1.0,
                matrix=Matrix.Translation(w_center + Vector((0, side_y * 0.02, 0))) @ Matrix.Diagonal(Vector((0.75, 0.14, 0.90, 1.0)))
            )
            # Nan chấn song cửa sổ gỗ (Lattice Bars - 4 song dọc)
            for li in range(4):
                lx = wx - 0.28 + li * 0.19
                bmesh.ops.create_cone(
                    bm, cap_ends=True, segments=8,
                    radius1=0.024, radius2=0.024, depth=0.88,
                    matrix=Matrix.Translation(Vector((lx, y_beam + side_y * 0.09, z_base + z_height*0.5)))
                )

def generate_balustrade(bm, x_center, y_center, z_floor, length_x, width_y, rail_height=0.75):
    '''Lan Can Bao Lơn Gỗ Chạm Khắc Có Hàng Con Tiện Đều Đặn'''
    for side_y in [-1, 1]:
        y_rail = y_center + side_y * (width_y * 0.5)
        # Tay vịn trên
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation(Vector((x_center, y_rail, z_floor + rail_height))) @ Matrix.Diagonal(Vector((length_x, 0.12, 0.08, 1.0)))
        )
        # Gờ đế chân
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.Translation(Vector((x_center, y_rail, z_floor + 0.05))) @ Matrix.Diagonal(Vector((length_x, 0.12, 0.08, 1.0)))
        )
        # Hàng con tiện gỗ tiện tròn (Balusters)
        num_balusters = int(length_x / 0.32)
        bdx = (length_x - 0.2) / max(1, num_balusters - 1)
        for bi in range(num_balusters):
            cur_bx = (x_center - length_x*0.5 + 0.1) + bi * bdx
            bmesh.ops.create_cone(
                bm, cap_ends=True, segments=8,
                radius1=0.028, radius2=0.028, depth=rail_height - 0.12,
                matrix=Matrix.Translation(Vector((cur_bx, y_rail, z_floor + rail_height*0.5)))
            )

def generate_rippling_cloth_flag(bm, pole_pos, flag_w=2.8, flag_h=1.8, segs_x=24, segs_z=14):
    '''Lá Cờ Soái Vải Mô Phỏng Sóng Gió Bernoulli và Nếp Gấp Mềm Mại'''
    grid = []
    for zi in range(segs_z + 1):
        tz = zi / segs_z
        cur_z = pole_pos.z - tz * flag_h
        row = []
        for xi in range(segs_x + 1):
            tx = xi / segs_x
            cur_x = pole_pos.x - tx * flag_w
            wave1 = math.sin(tx * 4.2 * math.pi) * (0.05 + tx * 0.25)
            wave2 = math.cos(tx * 2.5 * math.pi + tz * 2.0) * (tx * 0.12)
            cur_y = pole_pos.y + wave1 + wave2

            if tx > 0.65:
                indent = math.sin((tx - 0.65) / 0.35 * math.pi) * 0.25
                cur_x += indent

            v = bm.verts.new(Vector((cur_x, cur_y, cur_z)))
            row.append(v)
        grid.append(row)

    for zi in range(segs_z):
        for xi in range(segs_x):
            bm.faces.new([grid[zi][xi], grid[zi][xi+1], grid[zi+1][xi+1], grid[zi+1][xi]])
