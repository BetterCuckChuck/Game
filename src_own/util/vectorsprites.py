#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Copyright (C) 2008  Nick Redshaw
#    Copyright (C) 2018  Francisco Sanchez Arroyo
#

import pygame
import sys
import os
import math
import random
from math import *
from pygame.math import Vector2 as Vector2d
from util.geometry import *


class VectorSprite:

    """
    Lớp hỗ trợ cho logic xoay (Rotate) và di chuyển (Transform) của thực thể.
    
    Attributes:
        position (Vector2d): Tọa độ (X, Y) của thực thể.
        heading (Vector2d): Vector gia tốc.
        angle (float/int): Góc nghiêng/xoay hiện tại so với phương thẳng đứng ban đầu.
        vAngle (float/int): Gia tốc tự xoay.
        pointlist (list): Danh sách mảng các điểm của vật thể (Origin Point) dùng để vẽ cấu trúc Đa giác.
        color (tuple): Bộ màu RGB hiển thị.
        ttl (int): (Time-To-Live) số frame còn lại trước khi đối tượng tự phân mảnh hoặc biến mất.
    """
    def __init__(self, position, heading, pointlist, angle=0, color=(255, 255, 255)):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
        self.position = position
        self.heading = heading
        self.angle = angle
        self.vAngle = 0
        self.pointlist = pointlist  # raw pointlist
        self.color = color
        self.ttl = 25

        #self.color = color = (random.randrange(40,255),random.randrange(40,255),random.randrange(40,255))

    # rotate each x,y coord by the angle, then translate it to the x,y position
    def rotateAndTransform(self):
        """Tính toán hình học (Cos, Sin) để hoán đổi chiều đa giác dựa trên hướng nhìn."""
        newPointList = [self.rotatePoint(point) for point in self.pointlist]
        self.transformedPointlist = [
            self.translatePoint(point) for point in newPointList]

    # draw the sprite
    def draw(self):
        """In điểm ảnh lên Screen Frame."""
        self.rotateAndTransform()
        return self.transformedPointlist

    # translate each point to the current x, y position
    def translatePoint(self, point):
        """Hàm tịnh tiến dịch chuyển gốc tọa độ theo góc Offset."""
        newPoint = []
        newPoint.append(point[0] + self.position.x)
        newPoint.append(point[1] + self.position.y)
        return newPoint

    # Move the sprite by the velocity
    def move(self):
        # Apply velocity
        """Đẩy toạ độ x,y về phía trước dựa theo gia tốc vận tốc."""
        self.position.x = self.position.x + self.heading.x
        self.position.y = self.position.y + self.heading.y
        self.angle = self.angle + self.vAngle

        # needed?
        # self.rotateAndTransform()

    # Rotate a point by the given angle
    def rotatePoint(self, point):
        """Sử dụng Toán Sinh Học xoay các điểm quanh Tâm."""
        newPoint = []
        cosVal = math.cos(radians(self.angle))
        sinVal = math.sin(radians(self.angle))
        newPoint.append(point[0] * cosVal + point[1] * sinVal)
        newPoint.append(point[1] * cosVal - point[0] * sinVal)

        # Keep points as integers
        newPoint = [int(point) for point in newPoint]
        return newPoint

    # Scale a point
    def scale(self, point, scale):
        """Phóng to thu nhỏ kích thước của các Điểm đa giác."""
        newPoint = []
        newPoint.append(point[0] * scale)
        newPoint.append(point[1] * scale)
        # Keep points as integers
        newPoint = [int(point) for point in newPoint]
        return newPoint

    def collidesWith(self, target):
        """Xác nhận hộp biên (BoundingRect) của hai yếu tố có trùng lập với nhau hay không."""
        if self.rect.colliderect(target.rect):
            return True
        else:
            return False

    # Check each line from pointlist1 for intersection with
    # the lines in pointlist2
    def checkPolygonCollision(self, target):
        """Kiểm tra độ chính xác điểm-đoạn 100% bằng thuật toán Line-Segment Intersection."""
        for i in range(0, len(self.transformedPointlist)):
            for j in range(0, len(target.transformedPointlist)):
                p1 = self.transformedPointlist[i-1]
                p2 = self.transformedPointlist[i]
                p3 = target.transformedPointlist[j-1]
                p4 = target.transformedPointlist[j]
                p = calculateIntersectPoint(p1, p2, p3, p4)
                if (p != None):
                    return p

        return None

# Used for bullets and debris


class Point(VectorSprite):

    # Class attributes
    """
    Lớp Point đại diện cho một Điểm trên màn hình (đạn).
    
    Attributes:
        stage (Stage): Đối tượng màn chơi chứa danh sách danh mục gốc.
        ttl (int): Tuổi thọ đếm lùi trước khi tự hủy khỏi Stage.
    """
    pointlist = [(0, 0), (1, 1), (1, 0), (0, 1)]

    def __init__(self, position, heading, stage):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
        VectorSprite.__init__(self, position, heading, self.pointlist)
        self.stage = stage
        self.ttl = 30

    def move(self):
        """Đẩy toạ độ x,y về phía trước dựa theo gia tốc vận tốc."""
        self.ttl -= 1
        if (self.ttl <= 0):
            self.stage.removeSprite(self)

        VectorSprite.move(self)
