"""
Các thuật toán pathfinding trên lưới cho AI tàu địch.

Cung cấp lớp GridPathfinder với cài đặt BFS và Weighted A* hoạt động
trên lưới 2D rời rạc hóa.
- BFS (tàu Trung Bình): Tìm đường ngắn nhất trên lưới nhị phân (0/1).
- Weighted A* (tàu Khó): Tìm đường an toàn nhất trên bản đồ nhiệt
  nguy hiểm (danger heatmap) với chi phí liên tục, ưu tiên né xa
  vùng nguy hiểm thay vì chỉ né chướng ngại vật trực tiếp.

Last Modified: 2026-05-13
"""

import math
import heapq
from collections import deque
from pygame.math import Vector2 as Vector2d

# Chi phí ô không thể đi qua (vị trí hiện tại của vật thể)
IMPASSABLE = 999
# Chi phí nền cho ô an toàn
BASE_COST = 1


class GridPathfinder:
    """
    Pathfinder trên lưới rời rạc với BFS và Weighted A*.

    - build_grid(): Lưới nhị phân cho BFS (blocked/unblocked).
    - build_heatmap(): Bản đồ nhiệt nguy hiểm cho Weighted A*,
      mỗi ô mang chi phí liên tục tỷ lệ nghịch với khoảng cách
      đến nguồn nguy hiểm gần nhất.

    Attributes:
        width: Chiều rộng world (pixel).
        height: Chiều cao world (pixel).
        cell_size: Kích thước ô lưới (pixel).
        cols: Số cột trong lưới.
        rows: Số hàng trong lưới.

    Last Modified: 2026-05-13
    """

    def __init__(self, width, height, cell_size=40):
        """
        Khởi tạo kích thước lưới pathfinder.

        Args:
            width: Chiều rộng world (pixel).
            height: Chiều cao world (pixel).
            cell_size: Kích thước ô lưới (pixel). Mặc định 40.

        Last Modified: 2026-05-13
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1

    def _mark_danger(self, grid, cx, cy, value):
        """
        Đánh dấu một ô trên lưới với giá trị tối đa.

        Args:
            grid: Mảng 2D lưới.
            cx: Chỉ số cột.
            cy: Chỉ số hàng.
            value: Giá trị chi phí cần gán (giữ lại giá trị lớn hơn).

        Last Modified: 2026-05-13
        """
        if 0 <= cx < self.cols and 0 <= cy < self.rows:
            grid[cx][cy] = max(grid[cx][cy], value)

    def build_grid(self, rocks, bullets, saucer_bullet_list):
        """
        Xây dựng lưới nhị phân cho BFS (0 = đi được, 1 = blocked).

        Đánh dấu vị trí hiện tại và quỹ đạo dự đoán của thiên thạch
        và đạn người chơi (có xử lý screen wrapping).

        Args:
            rocks: Danh sách instance Rock.
            bullets: Danh sách toàn bộ Bullet đang hoạt động.
            saucer_bullet_list: Đạn của đĩa bay (loại trừ khỏi đánh dấu).

        Returns:
            Mảng 2D với grid[col][row] = 1 (blocked) hoặc 0 (đi được).

        Last Modified: 2026-05-13
        """
        grid = [[0 for _ in range(self.rows)] for _ in range(self.cols)]
        for rock in rocks:
            cx = int(rock.position.x / self.cell_size)
            cy = int(rock.position.y / self.cell_size)
            self._mark_danger(grid, cx, cy, 1)
            for t in range(5, 75, 10):
                px = (rock.position.x + rock.heading.x * t) % self.width
                py = (rock.position.y + rock.heading.y * t) % self.height
                self._mark_danger(grid, int(px / self.cell_size), int(py / self.cell_size), 1)
        for bullet in bullets:
            if bullet not in saucer_bullet_list:
                cx = int(bullet.position.x / self.cell_size)
                cy = int(bullet.position.y / self.cell_size)
                self._mark_danger(grid, cx, cy, 1)
                for t in range(5, 45, 10):
                    px = bullet.position.x + bullet.heading.x * t
                    py = bullet.position.y + bullet.heading.y * t
                    self._mark_danger(grid, int(px / self.cell_size), int(py / self.cell_size), 1)
        return grid

    def build_heatmap(self, rocks, bullets, saucer_bullet_list):
        """
        Xây dựng bản đồ nhiệt nguy hiểm cho Weighted A*.

        Thay vì nhị phân (0/1), mỗi ô mang chi phí liên tục:
        - IMPASSABLE (999): Vị trí hiện tại của vật thể (không đi qua).
        - Chi phí cao: Ô nằm trên quỹ đạo dự đoán hoặc lân cận nguồn
          nguy hiểm (giảm dần theo khoảng cách).
        - BASE_COST (1): Ô an toàn.

        Điều này khiến Weighted A* chủ động né xa vùng nguy hiểm
        thay vì chỉ tránh ô bị blocked.

        Args:
            rocks: Danh sách instance Rock.
            bullets: Danh sách toàn bộ Bullet đang hoạt động.
            saucer_bullet_list: Đạn của đĩa bay (loại trừ).

        Returns:
            Mảng 2D với grid[col][row] = chi phí đi qua ô đó (float).

        Last Modified: 2026-05-13
        """
        grid = [[BASE_COST for _ in range(self.rows)] for _ in range(self.cols)]

        def spread_danger(cx, cy, core_cost, radius=2):
            """
            Lan tỏa chi phí nguy hiểm từ tâm ra các ô lân cận.
            
            Args:
                cx: Tọa độ x của ô trung tâm.
                cy: Tọa độ y của ô trung tâm.
                core_cost: Chi phí tại ô trung tâm.
                radius: Bán kính lan tỏa (số ô).

            Last Modified: 2026-05-13
            """
            self._mark_danger(grid, cx, cy, core_cost)
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    if dr == 0 and dc == 0:
                        continue
                    dist = max(abs(dr), abs(dc))
                    falloff_cost = core_cost / (dist + 1)
                    if falloff_cost > BASE_COST:
                        nx, ny = cx + dc, cy + dr
                        self._mark_danger(grid, nx, ny, falloff_cost)

        for rock in rocks:
            cx = int(rock.position.x / self.cell_size)
            cy = int(rock.position.y / self.cell_size)
            spread_danger(cx, cy, IMPASSABLE, radius=2)
            for t in range(5, 75, 10):
                px = (rock.position.x + rock.heading.x * t) % self.width
                py = (rock.position.y + rock.heading.y * t) % self.height
                trail_cost = max(20, 80 - t)
                spread_danger(int(px / self.cell_size), int(py / self.cell_size), trail_cost, radius=1)

        for bullet in bullets:
            if bullet not in saucer_bullet_list:
                cx = int(bullet.position.x / self.cell_size)
                cy = int(bullet.position.y / self.cell_size)
                spread_danger(cx, cy, IMPASSABLE, radius=1)
                for t in range(5, 45, 10):
                    px = bullet.position.x + bullet.heading.x * t
                    py = bullet.position.y + bullet.heading.y * t
                    trail_cost = max(15, 60 - t)
                    spread_danger(int(px / self.cell_size), int(py / self.cell_size), trail_cost, radius=1)

        return grid

    def get_neighbors(self, grid, x, y):
        """
        Trả về các ô lân cận đi được theo 8 hướng (cho BFS, lưới nhị phân).

        Args:
            grid: Lưới nhị phân từ build_grid.
            x: Chỉ số cột ô hiện tại.
            y: Chỉ số hàng ô hiện tại.

        Returns:
            Danh sách tuple (col, row) các ô lân cận có giá trị 0.

        Last Modified: 2026-05-13
        """
        neighbors = []
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows and grid[nx][ny] == 0:
                neighbors.append((nx, ny))
        return neighbors

    def get_weighted_neighbors(self, heatmap, x, y):
        """
        Trả về các ô lân cận đi được kèm chi phí (cho Weighted A*).

        Ô có chi phí >= IMPASSABLE được coi là không đi qua được.

        Args:
            heatmap: Bản đồ nhiệt từ build_heatmap.
            x: Chỉ số cột ô hiện tại.
            y: Chỉ số hàng ô hiện tại.

        Returns:
            Danh sách tuple (col, row, cost) các ô lân cận đi được.

        Last Modified: 2026-05-13
        """
        neighbors = []
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                cost = heatmap[nx][ny]
                if cost < IMPASSABLE:
                    neighbors.append((nx, ny, cost))
        return neighbors

    def weighted_astar(self, heatmap, start_pos, target_pos):
        """
        Tìm đường an toàn nhất bằng Weighted A* trên danger heatmap.

        Khác với A* nhị phân, chi phí di chuyển qua mỗi ô bằng giá trị
        heatmap tại ô đó. Đường đi tối ưu cân bằng giữa khoảng cách
        ngắn nhất và mức nguy hiểm tích lũy thấp nhất.

        Args:
            heatmap: Bản đồ nhiệt từ build_heatmap.
            start_pos: Vị trí bắt đầu, dạng Vector2d (world-space).
            target_pos: Vị trí mục tiêu, dạng Vector2d (world-space).

        Returns:
            Waypoint tiếp theo dạng Vector2d, hoặc None.

        Last Modified: 2026-05-13
        """
        sx = max(0, min(self.cols - 1, int(start_pos.x / self.cell_size)))
        sy = max(0, min(self.rows - 1, int(start_pos.y / self.cell_size)))
        tx = max(0, min(self.cols - 1, int(target_pos.x / self.cell_size)))
        ty = max(0, min(self.rows - 1, int(target_pos.y / self.cell_size)))

        open_set = []
        heapq.heappush(open_set, (0, (sx, sy)))
        came_from = {}
        g_score = {(sx, sy): 0}

        closest_node = (sx, sy)
        closest_dist = abs(sx - tx) + abs(sy - ty)

        while open_set:
            _, current = heapq.heappop(open_set)

            dist = abs(current[0] - tx) + abs(current[1] - ty)
            if dist < closest_dist:
                closest_dist = dist
                closest_node = current

            if current == (tx, ty):
                break

            for nx, ny, cell_cost in self.get_weighted_neighbors(heatmap, current[0], current[1]):
                tentative_g = g_score[current] + cell_cost
                nxt = (nx, ny)
                if nxt not in g_score or tentative_g < g_score[nxt]:
                    came_from[nxt] = current
                    g_score[nxt] = tentative_g
                    heuristic = abs(nx - tx) + abs(ny - ty)
                    f_score = tentative_g + heuristic
                    heapq.heappush(open_set, (f_score, nxt))

        if closest_node != (sx, sy):
            current = closest_node
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            if path:
                return Vector2d(
                    path[0][0] * self.cell_size + self.cell_size / 2,
                    path[0][1] * self.cell_size + self.cell_size / 2
                )
        return None

    def bfs(self, grid, start_pos, target_pos):
        """
        Tìm đường ngắn nhất bằng BFS trên lưới nhị phân.

        Args:
            grid: Lưới nhị phân từ build_grid.
            start_pos: Vị trí bắt đầu, dạng Vector2d (world-space).
            target_pos: Vị trí mục tiêu, dạng Vector2d (world-space).

        Returns:
            Waypoint tiếp theo dạng Vector2d, hoặc None.

        Last Modified: 2026-05-13
        """
        sx = max(0, min(self.cols - 1, int(start_pos.x / self.cell_size)))
        sy = max(0, min(self.rows - 1, int(start_pos.y / self.cell_size)))
        tx = max(0, min(self.cols - 1, int(target_pos.x / self.cell_size)))
        ty = max(0, min(self.rows - 1, int(target_pos.y / self.cell_size)))

        queue = deque([(sx, sy)])
        came_from = {(sx, sy): None}
        closest_node = (sx, sy)
        closest_dist = abs(sx - tx) + abs(sy - ty)

        while queue:
            current = queue.popleft()
            dist = abs(current[0] - tx) + abs(current[1] - ty)
            if dist < closest_dist:
                closest_dist = dist
                closest_node = current
            if current == (tx, ty):
                break
            for nxt in self.get_neighbors(grid, current[0], current[1]):
                if nxt not in came_from:
                    came_from[nxt] = current
                    queue.append(nxt)

        if closest_node != (sx, sy):
            current = closest_node
            path = []
            curr = current
            while came_from[curr] is not None:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            if path:
                return Vector2d(
                    path[0][0] * self.cell_size + self.cell_size / 2,
                    path[0][1] * self.cell_size + self.cell_size / 2
                )
        return None
