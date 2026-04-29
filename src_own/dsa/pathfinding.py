"""Các thuật toán pathfinding trên lưới cho AI tàu địch.

Cung cấp lớp GridPathfinder với cài đặt A* và BFS hoạt động
trên lưới 2D rời rạc hóa. Lưới được xây dựng động từ vị trí
chướng ngại vật kèm dự đoán quỹ đạo cho các vật thể di chuyển.
"""

import math
import heapq
from collections import deque
from pygame.math import Vector2 as Vector2d


class GridPathfinder:
    """Pathfinder trên lưới rời rạc với thuật toán A* và BFS.

    Xây dựng lưới chướng ngại vật từ vị trí thiên thạch và đạn
    (bao gồm dự đoán vị trí tương lai), sau đó tìm đường bằng
    A* hoặc BFS. Trả về node khả đạt gần nhất khi không có đường
    đi hoàn chỉnh.

    Attributes:
        width: Chiều rộng world (pixel).
        height: Chiều cao world (pixel).
        cell_size: Kích thước ô lưới (pixel).
        cols: Số cột trong lưới.
        rows: Số hàng trong lưới.
    """

    def __init__(self, width, height, cell_size=64):
        """Khởi tạo kích thước lưới pathfinder.

        Args:
            width: Chiều rộng world (pixel).
            height: Chiều cao world (pixel).
            cell_size: Kích thước ô lưới (pixel). Mặc định 64.
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = int(width / cell_size) + 1
        self.rows = int(height / cell_size) + 1

    def build_grid(self, rocks, bullets, saucer_bullet_list):
        """Xây dựng lưới chướng ngại vật từ vị trí hiện tại và dự đoán.

        Args:
            rocks: Danh sách instance Rock cần đánh dấu.
            bullets: Danh sách toàn bộ Bullet đang hoạt động.
            saucer_bullet_list: Đạn của đĩa bay (loại trừ khỏi đánh dấu).

        Returns:
            Mảng 2D với grid[col][row] = 1 cho ô blocked, 0 cho ô đi được.
        """
        grid = [[0 for _ in range(self.rows)] for _ in range(self.cols)]
        for rock in rocks:
            cx = int(rock.position.x / self.cell_size)
            cy = int(rock.position.y / self.cell_size)
            if 0 <= cx < self.cols and 0 <= cy < self.rows:
                grid[cx][cy] = 1
            for t in range(5, 75, 10):
                px = (rock.position.x + rock.heading.x * t) % self.width
                py = (rock.position.y + rock.heading.y * t) % self.height
                pcx = int(px / self.cell_size)
                pcy = int(py / self.cell_size)
                if 0 <= pcx < self.cols and 0 <= pcy < self.rows:
                    grid[pcx][pcy] = 1
        for bullet in bullets:
            if bullet not in saucer_bullet_list:
                cx = int(bullet.position.x / self.cell_size)
                cy = int(bullet.position.y / self.cell_size)
                if 0 <= cx < self.cols and 0 <= cy < self.rows:
                    grid[cx][cy] = 1
                for t in range(5, 45, 10):
                    px = bullet.position.x + bullet.heading.x * t
                    py = bullet.position.y + bullet.heading.y * t
                    pcx = int(px / self.cell_size)
                    pcy = int(py / self.cell_size)
                    if 0 <= pcx < self.cols and 0 <= pcy < self.rows:
                        grid[pcx][pcy] = 1
        return grid

    def get_neighbors(self, grid, x, y):
        """Trả về các ô lân cận đi được theo 8 hướng.

        Args:
            grid: Lưới chướng ngại vật từ build_grid.
            x: Chỉ số cột ô hiện tại.
            y: Chỉ số hàng ô hiện tại.

        Returns:
            Danh sách tuple (col, row) các ô lân cận đi được.
        """
        neighbors = []
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(1,-1),(-1,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows and grid[nx][ny] == 0:
                neighbors.append((nx, ny))
        return neighbors

    def astar(self, grid, start_pos, target_pos):
        """Tìm đường bằng A* với heuristic Manhattan distance.

        Args:
            grid: Lưới chướng ngại vật từ build_grid.
            start_pos: Vị trí bắt đầu, dạng Vector2d (world-space).
            target_pos: Vị trí mục tiêu, dạng Vector2d (world-space).

        Returns:
            Waypoint tiếp theo dạng Vector2d, hoặc None.
        """
        sx, sy = int(start_pos.x / self.cell_size), int(start_pos.y / self.cell_size)
        tx, ty = int(target_pos.x / self.cell_size), int(target_pos.y / self.cell_size)
        sx = max(0, min(self.cols - 1, sx))
        sy = max(0, min(self.rows - 1, sy))
        tx = max(0, min(self.cols - 1, tx))
        ty = max(0, min(self.rows - 1, ty))
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
            for nxt in self.get_neighbors(grid, current[0], current[1]):
                tentative_g_score = g_score[current] + 1
                if nxt not in g_score or tentative_g_score < g_score[nxt]:
                    came_from[nxt] = current
                    g_score[nxt] = tentative_g_score
                    f_score = tentative_g_score + abs(nxt[0] - tx) + abs(nxt[1] - ty)
                    heapq.heappush(open_set, (f_score, nxt))
        if closest_node != (sx, sy):
            current = closest_node
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            if path:
                return Vector2d(path[0][0]*self.cell_size+self.cell_size/2, path[0][1]*self.cell_size+self.cell_size/2)
        return None

    def bfs(self, grid, start_pos, target_pos):
        """Tìm đường bằng BFS (breadth-first search).

        Args:
            grid: Lưới chướng ngại vật từ build_grid.
            start_pos: Vị trí bắt đầu, dạng Vector2d (world-space).
            target_pos: Vị trí mục tiêu, dạng Vector2d (world-space).

        Returns:
            Waypoint tiếp theo dạng Vector2d, hoặc None.
        """
        sx, sy = int(start_pos.x / self.cell_size), int(start_pos.y / self.cell_size)
        tx, ty = int(target_pos.x / self.cell_size), int(target_pos.y / self.cell_size)
        sx = max(0, min(self.cols - 1, sx))
        sy = max(0, min(self.rows - 1, sy))
        tx = max(0, min(self.cols - 1, tx))
        ty = max(0, min(self.rows - 1, ty))
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
                return Vector2d(path[0][0]*self.cell_size+self.cell_size/2, path[0][1]*self.cell_size+self.cell_size/2)
        return None
