import pygame
import math

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
    """Lớp BruteForceCollision đại diện cho hệ thống tương ứng."""
    def detect_collisions(self, collidables, bullets, player, enemy):
        """Hàm bổ trợ mở rộng detect_collisions xử lý tác vụ tương ứng."""
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

class QuadTree:
    """Cấu trúc dữ liệu Cây Tứ Phân phân chia không gian để tối ưu va chạm O(N log N)."""
    def __init__(self, boundary, capacity):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
        self.boundary = boundary # pygame.Rect
        self.capacity = capacity
        self.objects = []
        self.divided = False

    def subdivide(self):
        """Phân chia Node hiện tại thành 4 tứ phân: Đông Bắc, Tây Bắc, Đông Nam, Tây Nam."""
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.w, self.boundary.h
        hw, hh = w / 2, h / 2
        
        self.northeast = QuadTree(pygame.Rect(x + hw, y, hw, hh), self.capacity)
        self.northwest = QuadTree(pygame.Rect(x, y, hw, hh), self.capacity)
        self.southeast = QuadTree(pygame.Rect(x + hw, y + hh, hw, hh), self.capacity)
        self.southwest = QuadTree(pygame.Rect(x, y + hh, hw, hh), self.capacity)
        self.divided = True

    def insert(self, obj):
        """Nạp một đối tượng (có boundingRect) vào Cây Tứ Phân."""
        if not self.boundary.colliderect(obj.rect):
            return False

        if len(self.objects) < self.capacity:
            self.objects.append(obj)
            return True
        
        if not self.divided:
            self.subdivide()

        return (self.northeast.insert(obj) or 
                self.northwest.insert(obj) or 
                self.southeast.insert(obj) or 
                self.southwest.insert(obj))

    def query(self, range_rect, found):
        """Truy vấn mảng các đối tượng nằm trong không gian giao cắt với ô range_rect."""
        if not self.boundary.colliderect(range_rect):
            return

        for obj in self.objects:
            if range_rect.colliderect(obj.rect):
                found.append(obj)

        if self.divided:
            self.northeast.query(range_rect, found)
            self.northwest.query(range_rect, found)
            self.southeast.query(range_rect, found)
            self.southwest.query(range_rect, found)

class QuadTreeCollision(CollisionDetector):
    """Lớp QuadTreeCollision đại diện cho hệ thống tương ứng."""
    def __init__(self, screen_width, screen_height):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
        self.boundary = pygame.Rect(0, 0, screen_width, screen_height)

    def detect_collisions(self, collidables, bullets, player, enemy):
        """Hàm bổ trợ mở rộng detect_collisions xử lý tác vụ tương ứng."""
        collisions = set()
        
        # Build tree per frame. O(N log N)
        qt = QuadTree(self.boundary, 4)
        all_objects = collidables.copy()
        if player and player.active:
            all_objects.append(player)
        if enemy and enemy.active:
            all_objects.append(enemy)
        for b in bullets:
            all_objects.append(b)

        for obj in all_objects:
            qt.insert(obj)

        # Query tree. O(N log N)
        for obj in all_objects:
            # Create a bounding box based on radius x 2
            query_range = pygame.Rect(obj.x - obj.radius, obj.y - obj.radius, 
                                      obj.radius * 2, obj.radius * 2)
            nearby_objects = []
            qt.query(query_range, nearby_objects)
            
            for other in nearby_objects:
                if obj != other:
                    dist = math.hypot(obj.x - other.x, obj.y - other.y)
                    if dist < (obj.radius + other.radius):
                        # Use sorted tuple to avoid A,B and B,A duplication
                        pair = tuple(sorted([obj, other], key=id))
                        collisions.add(pair)

        return collisions
