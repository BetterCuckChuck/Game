"""
QuadTree phân vùng không gian cho phát hiện va chạm.

Cung cấp cấu trúc dữ liệu QuadTree đệ quy chia không gian 2D
thành các phần tư, cho phép truy vấn va chạm broad-phase O(n log n)
thay vì brute-force O(n^2).

Last Modified: 2026-05-06
"""

import pygame


class QuadTree:
    """
    Chỉ mục không gian đệ quy phân vùng 2D thành bốn phần tư.

    Các đối tượng được lưu tại node lá với sức chứa cấu hình được.
    Khi vượt sức chứa, node chia thành bốn con (NE, NW, SE, SW)
    và phân phối đối tượng tương ứng.

    Attributes:
        boundary: pygame.Rect xác định vùng không gian của node.
        capacity: Số đối tượng tối đa trước khi chia nhỏ.
        objects: Danh sách sprite lưu tại node này.
        divided: Node đã được chia nhỏ hay chưa.

    Last Modified: 2026-05-06
    """

    def __init__(self, boundary, capacity=4):
        """
        Khởi tạo node QuadTree với boundary cho trước.

        Args:
            boundary: pygame.Rect xác định vùng không gian.
            capacity: Số đối tượng tối đa trước khi chia. Mặc định 4.

        Last Modified: 2026-05-06
        """
        self.boundary = boundary
        self.capacity = capacity
        self.objects = []
        self.divided = False

    def subdivide(self):
        """
        Chia node thành bốn phần tư bằng nhau (NE, NW, SE, SW).

        Last Modified: 2026-05-06
        """
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.w, self.boundary.h
        hw, hh = w / 2, h / 2
        self.northeast = QuadTree(pygame.Rect(x + hw, y, hw, hh), self.capacity)
        self.northwest = QuadTree(pygame.Rect(x, y, hw, hh), self.capacity)
        self.southeast = QuadTree(pygame.Rect(x + hw, y + hh, hw, hh), self.capacity)
        self.southwest = QuadTree(pygame.Rect(x, y + hh, hw, hh), self.capacity)
        self.divided = True

    def insert(self, obj):
        """
        Chèn sprite vào cây dựa trên bounding rect.

        Nếu node đã đầy, chia nhỏ trước rồi chèn vào phần tư phù hợp.

        Args:
            obj: Sprite có thuộc tính ``rect`` để định vị không gian.

        Returns:
            True nếu chèn thành công, False nếu nằm ngoài boundary.

        Last Modified: 2026-05-06
        """
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
        """
        Truy vấn các đối tượng có bounding rect giao với vùng tìm kiếm.

        Tìm kiếm đệ quy các phần tư con giao với hình chữ nhật truy vấn.

        Args:
            range_rect: pygame.Rect xác định vùng tìm kiếm.
            found: Danh sách đầu ra, đối tượng tìm thấy được append vào.

        Last Modified: 2026-05-06
        """
        if not self.boundary.colliderect(range_rect):
            return
        for obj in self.objects:
            if range_rect.colliderect(obj.rect):
                if obj not in found:
                    found.append(obj)
        if self.divided:
            self.northeast.query(range_rect, found)
            self.northwest.query(range_rect, found)
            self.southeast.query(range_rect, found)
            self.southwest.query(range_rect, found)

    def get_potential_intersections(self, target):
        """
        Trả về các đối tượng cùng vùng phân vùng với target.

        Wrapper tiện ích cho query() sử dụng bounding rect của target.

        Args:
            target: Sprite có thuộc tính ``rect``.

        Returns:
            Danh sách sprite nằm cùng vùng không gian với target.

        Last Modified: 2026-05-06
        """
        found = []
        self.query(target.rect, found)
        return found
