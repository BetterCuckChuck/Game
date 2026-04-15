import pygame

class QuadTree:
    """
    Lớp QuadTree sử dụng trong Xử lí va chạm.
    
    Attributes:
        objects (list): Danh sách các đối tượng Node quản lý.
        divided (bool): Cờ đánh dấu Node vượt quá capacity.
        boundary (pygame.Rect): pygame.Rect quản lý không gian của Node.
        capacity (int): Số lượng đối tượng tối đa trước khi Cây Tứ Phân thực hiện chia nhỏ.
    """
    def __init__(self, boundary, capacity=4):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
        self.boundary = boundary
        self.capacity = capacity
        self.objects = []
        self.divided = False



    def subdivide(self):
        """Phân chia Node hiện tại thành 4 phần: Đông Bắc, Tây Bắc, Đông Nam, Tây Nam."""
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.w, self.boundary.h
        hw, hh = w / 2, h / 2
        
        self.northeast = QuadTree(pygame.Rect(x + hw, y, hw, hh), self.capacity)
        self.northwest = QuadTree(pygame.Rect(x, y, hw, hh), self.capacity)
        self.southeast = QuadTree(pygame.Rect(x + hw, y + hh, hw, hh), self.capacity)
        self.southwest = QuadTree(pygame.Rect(x, y + hh, hw, hh), self.capacity)
        self.divided = True

    def insert(self, obj):
        """Nạp một đối tượng vào Cây Tứ Phân."""
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
                if obj not in found:
                    found.append(obj)

        if self.divided:
            self.northeast.query(range_rect, found)
            self.northwest.query(range_rect, found)
            self.southeast.query(range_rect, found)
            self.southwest.query(range_rect, found)
            
    def get_potential_intersections(self, target):
        """Trích xuất những phần tử lân cận nằm chung khu vực phân vùng (Tối ưu tìm kiếm)."""
        found = []
        self.query(target.rect, found)
        return found
