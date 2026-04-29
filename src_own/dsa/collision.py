"""Các chiến lược phát hiện va chạm bằng brute-force và QuadTree.

Cung cấp lớp cơ sở trừu tượng CollisionDetector và hai cài đặt cụ thể:
BruteForceCollision cho kiểm tra O(n^2) từng cặp, và QuadTreeCollision
cho phát hiện tối ưu bằng phân vùng không gian.
"""

import pygame
import math
from dsa.quadtree import QuadTree


class CollisionDetector:
    """Lớp cơ sở trừu tượng định nghĩa giao diện phát hiện va chạm."""

    def detect_collisions(self, collidables, bullets, player, enemy):
        """Phát hiện tất cả va chạm giữa các thực thể.

        Args:
            collidables: Danh sách thực thể va chạm được (thiên thạch).
            bullets: Danh sách đạn đang hoạt động.
            player: Instance Ship người chơi, hoặc None.
            enemy: Instance Saucer tàu địch, hoặc None.

        Returns:
            Set các tuple, mỗi tuple chứa một cặp đối tượng va chạm.

        Raises:
            NotImplementedError: Phải được override bởi lớp con.
        """
        raise NotImplementedError("Lớp con phải cài đặt detect_collisions")


class BruteForceCollision(CollisionDetector):
    """Phát hiện va chạm O(n^2) bằng kiểm tra khoảng cách từng cặp."""

    def detect_collisions(self, collidables, bullets, player, enemy):
        """Phát hiện va chạm bằng kiểm tra mọi cặp đối tượng.

        Sử dụng lọc sơ bộ bằng bounding-rectangle, sau đó xác nhận
        bằng kiểm tra khoảng cách dựa trên bán kính.

        Args:
            collidables: Danh sách thực thể va chạm được.
            bullets: Danh sách đạn đang hoạt động.
            player: Instance Ship người chơi, hoặc None.
            enemy: Instance Saucer tàu địch, hoặc None.

        Returns:
            Set các tuple chứa cặp đối tượng va chạm.
        """
        collisions = set()
        all_objects = collidables.copy()
        if player and player.active:
            all_objects.append(player)
        if enemy and enemy.active:
            all_objects.append(enemy)
        for b in bullets:
            all_objects.append(b)
        for i in range(len(all_objects)):
            for j in range(i + 1, len(all_objects)):
                obj1 = all_objects[i]
                obj2 = all_objects[j]
                if obj1.rect.colliderect(obj2.rect):
                    dist = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
                    if dist < (obj1.radius + obj2.radius):
                        collisions.add((obj1, obj2))
        return collisions


class QuadTreeCollision(CollisionDetector):
    """Phát hiện va chạm tối ưu bằng QuadTree phân vùng không gian."""

    def __init__(self, screen_width, screen_height):
        """Khởi tạo với kích thước màn hình cho boundary QuadTree.

        Args:
            screen_width: Độ phân giải ngang (pixel).
            screen_height: Độ phân giải dọc (pixel).
        """
        self.boundary = pygame.Rect(0, 0, screen_width, screen_height)

    def detect_collisions(self, collidables, bullets, player, enemy):
        """Phát hiện va chạm bằng QuadTree phân vùng không gian.

        Chèn toàn bộ đối tượng vào QuadTree, sau đó truy vấn
        đối tượng lân cận cho từng thực thể để giảm số lần kiểm tra.

        Args:
            collidables: Danh sách thực thể va chạm được.
            bullets: Danh sách đạn đang hoạt động.
            player: Instance Ship người chơi, hoặc None.
            enemy: Instance Saucer tàu địch, hoặc None.

        Returns:
            Set các tuple chứa cặp đối tượng va chạm, sắp xếp theo
            id để tránh trùng lặp.
        """
        collisions = set()
        qt = QuadTree(self.boundary, 4)
        all_objects = collidables.copy()
        if player and player.active:
            all_objects.append(player)
        if enemy and enemy.active:
            all_objects.append(enemy)
        for bullet in bullets:
            all_objects.append(bullet)
        for obj in all_objects:
            qt.insert(obj)
        for obj in all_objects:
            query_range = pygame.Rect(obj.x - obj.radius, obj.y - obj.radius,
                                        obj.radius * 2, obj.radius * 2)
            nearby_objects = []
            qt.query(query_range, nearby_objects)
            for other in nearby_objects:
                if obj != other:
                    dist = math.dist((obj.x, obj.y), (other.x, other.y))
                    if dist < (obj.radius + other.radius):
                        pair = tuple(sorted([obj, other], key=id))
                        collisions.add(pair)
        return collisions
