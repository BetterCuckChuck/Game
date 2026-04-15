import pygame
import math
from dsa.quadtree import QuadTree

class CollisionDetector:
    """Base Class định nghĩa API Xét va chạm."""
    def detect_collisions(self, collidables, bullets, player, enemy):
        """
        Giao diện hàm Xét va chạm chung.

        :param collidables: danh sách các phần tử có thể va chạm (Thiên thạch).
        :param bullets: danh sách đạn.
        :param player: Phi thuyền của người chơi.
        :param enemy: Tàu địch.
        :return: set các tuple, mô tả các cặp đối tượng vừa va chạm.
        """
        raise NotImplementedError("Lỗi: Chưa triển khai hàm detect_collisions")

class BruteForceCollision(CollisionDetector):
    """Lớp BruteForceCollision cho hệ thống xét va chạm bằng Brute-Force."""
    def detect_collisions(self, collidables, bullets, player, enemy):
        """Hàm bổ trợ mở rộng detect_collisions."""
        collisions = set()
        all_objects = collidables.copy()
        if player and player.active:
            all_objects.append(player)
        if enemy and enemy.active:
            all_objects.append(enemy)
        for b in bullets:
            all_objects.append(b)

        # O(N^2) comparison
        for i in range(len(all_objects)):
            for j in range(i + 1, len(all_objects)):
                obj1 = all_objects[i]
                obj2 = all_objects[j]
                
                # Check rect collision first
                if obj1.rect.colliderect(obj2.rect):
                    # For simplicity, we use circular collision if rects overlap
                    dist = math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)
                    if dist < (obj1.radius + obj2.radius):
                        collisions.add((obj1, obj2))
        return collisions



class QuadTreeCollision(CollisionDetector):
    """Lớp QuadTreeCollision cho hệ thống xét va chạm bằng Quad Tree"""
    def __init__(self, screen_width, screen_height):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
        self.boundary = pygame.Rect(0, 0, screen_width, screen_height)

    def detect_collisions(self, collidables, bullets, player, enemy):
        """Hàm bổ trợ mở rộng detect_collisions."""
        collisions = set()
        
        # Tạo cây: O(N * logN)
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

        # Truy vấn cây: O(N * logN) (N truy vấn, logN mỗi truy vấn)
        for obj in all_objects:
            # Tạo bounding box (hitbox hình vuông) vừa khớp hitbox của vật thể
            query_range = pygame.Rect(obj.x - obj.radius, obj.y - obj.radius, 
                                        obj.radius * 2, obj.radius * 2)
            nearby_objects = []
            qt.query(query_range, nearby_objects)
            
            for other in nearby_objects:
                if obj != other:
                    dist = math.dist((obj.x, obj.y), (other.x, other.y))
                    if dist < (obj.radius + other.radius):
                        # Tránh xét lặp
                        pair = tuple(sorted([obj, other], key=id))
                        collisions.add(pair)

        return collisions
