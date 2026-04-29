"""Các lớp sprite dạng vector và các primitive phát hiện va chạm.

Cung cấp các lớp cơ sở cho mọi thực thể đa giác trong game, bao gồm
phép xoay, tịnh tiến, di chuyển, co giãn, và phát hiện va chạm bằng
bounding-rectangle và line-segment intersection.
"""

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    Copyright (C) 2008  Nick Redshaw
#    Copyright (C) 2018  Francisco Sanchez Arroyo

import pygame
import sys
import os
import math
import random
from math import *
from pygame.math import Vector2 as Vector2d
from util.geometry import *


class VectorSprite:
    """Lớp cơ sở cho các sprite đa giác hỗ trợ xoay và tịnh tiến.

    Quản lý vị trí, vận tốc, vận tốc góc, và cung cấp các phương thức
    biến đổi đỉnh đa giác, render, di chuyển, và phát hiện va chạm.

    Attributes:
        position: Tọa độ world-space hiện tại, dạng Vector2d.
        heading: Vector vận tốc, dạng Vector2d.
        angle: Góc xoay hiện tại tính bằng độ.
        vAngle: Vận tốc góc (độ/frame).
        pointlist: Danh sách đỉnh đa giác gốc (tọa độ local-space).
        color: Tuple màu RGB dùng để render.
        ttl: Số frame còn lại trước khi tự hủy.
    """

    def __init__(self, position, heading, pointlist, angle=0, color=(255, 255, 255)):
        """Khởi tạo sprite với vị trí, vận tốc, và hình dạng đa giác.

        Args:
            position: Vị trí world-space ban đầu, dạng Vector2d.
            heading: Vector vận tốc ban đầu, dạng Vector2d.
            pointlist: Danh sách tuple (x, y) xác định các đỉnh đa giác.
            angle: Góc xoay ban đầu tính bằng độ. Mặc định 0.
            color: Tuple màu RGB. Mặc định trắng (255, 255, 255).
        """
        self.position = position
        self.heading = heading
        self.angle = angle
        self.vAngle = 0
        self.pointlist = pointlist  
        self.color = color
        self.ttl = 25


    def rotateAndTransform(self):
        """Áp dụng phép xoay và tịnh tiến lên toàn bộ đỉnh đa giác.

        Lưu kết quả tọa độ screen-space vào ``self.transformedPointlist``.
        """
        newPointList = [self.rotatePoint(point) for point in self.pointlist]
        self.transformedPointlist = [
            self.translatePoint(point) for point in newPointList]

    def draw(self):
        """Tính toán các đỉnh đã biến đổi để render.

        Returns:
            Danh sách tọa độ đỉnh trong screen-space.
        """
        self.rotateAndTransform()
        return self.transformedPointlist

    def translatePoint(self, point):
        """Tịnh tiến một điểm từ local-space sang world-space.

        Args:
            point: Tọa độ local-space dạng (x, y).

        Returns:
            Điểm đã tịnh tiến dạng list [x, y].
        """
        newPoint = []
        newPoint.append(point[0] + self.position.x)
        newPoint.append(point[1] + self.position.y)
        return newPoint

    def move(self):
        """Cập nhật vị trí theo vector vận tốc và cập nhật góc xoay."""
        self.position.x = self.position.x + self.heading.x
        self.position.y = self.position.y + self.heading.y
        self.angle = self.angle + self.vAngle


    def rotatePoint(self, point):
        """Xoay một điểm quanh gốc tọa độ theo góc hiện tại.

        Args:
            point: Tọa độ local-space dạng (x, y).

        Returns:
            Điểm đã xoay dạng list [x, y], làm tròn xuống số nguyên.
        """
        newPoint = []
        cosVal = math.cos(radians(self.angle))
        sinVal = math.sin(radians(self.angle))
        newPoint.append(point[0] * cosVal + point[1] * sinVal)
        newPoint.append(point[1] * cosVal - point[0] * sinVal)

        newPoint = [int(point) for point in newPoint]
        return newPoint

    def scale(self, point, scale):
        """Co giãn một điểm theo hệ số tỷ lệ đồng nhất.

        Args:
            point: Tọa độ dạng (x, y).
            scale: Hệ số co giãn.

        Returns:
            Điểm đã co giãn dạng list [x, y], làm tròn xuống số nguyên.
        """
        newPoint = []
        newPoint.append(point[0] * scale)
        newPoint.append(point[1] * scale)
        newPoint = [int(point) for point in newPoint]
        return newPoint

    def collidesWith(self, target):
        """Kiểm tra chồng lấn bounding box (AABB) với sprite khác.

        Args:
            target: VectorSprite cần kiểm tra.

        Returns:
            True nếu hai bounding rectangle chồng lấn, False nếu không.
        """
        if self.rect.colliderect(target.rect):
            return True
        else:
            return False

    def checkPolygonCollision(self, target):
        """Kiểm tra va chạm đa giác chính xác bằng line-segment intersection.

        Duyệt qua tất cả các cặp cạnh giữa sprite này và target
        để tìm điểm giao nhau.

        Args:
            target: VectorSprite cần kiểm tra.

        Returns:
            Điểm giao nhau dạng [x, y] nếu tìm thấy, hoặc None.
        """
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



class Point(VectorSprite):
    """Sprite tối giản dạng pixel đơn, dùng cho đạn và hạt hiệu ứng.

    Tự động gỡ bỏ khỏi Stage khi hết thời gian sống (ttl).

    Attributes:
        stage: Instance Stage quản lý sprite này.
        ttl: Số frame còn lại trước khi tự hủy.
    """
    pointlist = [(0, 0), (1, 1), (1, 0), (0, 1)]

    def __init__(self, position, heading, stage):
        """Khởi tạo Point sprite.

        Args:
            position: Vị trí world-space, dạng Vector2d.
            heading: Vector vận tốc, dạng Vector2d.
            stage: Instance Stage quản lý sprite.
        """
        VectorSprite.__init__(self, position, heading, self.pointlist)
        self.stage = stage
        self.ttl = 30

    def move(self):
        """Cập nhật vị trí và giảm thời gian sống.

        Gỡ sprite khỏi Stage khi ttl về 0.
        """
        self.ttl -= 1
        if (self.ttl <= 0):
            self.stage.removeSprite(self)

        VectorSprite.move(self)
