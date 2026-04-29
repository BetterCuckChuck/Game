"""Tàu người chơi và hiệu ứng lửa động cơ.

Cung cấp lớp Ship cho tàu vũ trụ do người chơi điều khiển với
hệ thống đẩy, xoay, hyperspace, và vũ khí, cùng lớp ThrustJet
cho hiệu ứng khí xả động cơ.
"""

import random
from util.vectorsprites import *
from shooter import *
from math import *
from soundManager import *


class Ship(Shooter):
    """Tàu vũ trụ do người chơi điều khiển với hệ thống đẩy, xoay, và vũ khí.

    Xử lý gia tốc, giảm tốc, xoay, dịch chuyển hyperspace,
    bắn đạn, và hiệu ứng phá hủy.

    Attributes:
        acceleration: Lực đẩy áp dụng mỗi frame.
        decelaration: Hệ số ma sát áp dụng mỗi frame.
        maxVelocity: Giới hạn tốc độ tối đa.
        thrustJet: Instance ThrustJet cho hiệu ứng khí xả.
        shipDebrisList: Danh sách mảnh vụn khi tàu bị phá hủy.
        visible: Tàu có đang được render hay không.
        inHyperSpace: Tàu có đang trong trạng thái hyperspace (bất tử) hay không.
    """
    acceleration = 0.2
    decelaration = -0.005
    maxVelocity = 10
    turnAngle = 6
    bulletVelocity = 13.0
    maxBullets = 4
    bulletTtl = 35

    def __init__(self, stage):
        """Khởi tạo tàu tại tâm màn hình với cấu hình mặc định.

        Args:
            stage: Instance Stage quản lý sprite.
        """
        position = Vector2d(stage.width/2, stage.height/2)
        heading = Vector2d(0, 0)
        self.thrustJet = ThrustJet(stage, self)
        self.shipDebrisList = []
        self.visible = True
        self.inHyperSpace = False
        pointlist = [(0, -10), (6, 10), (3, 7), (-3, 7), (-6, 10)]

        Shooter.__init__(self, position, heading, pointlist, stage)
        self.color = (50, 255, 50)

    def draw(self):
        """Render tàu, xử lý chuyển tiếp khi thoát hyperspace.

        Returns:
            Danh sách các đỉnh đa giác đã biến đổi.
        """
        if self.visible:
            if not self.inHyperSpace:
                VectorSprite.draw(self)
            else:
                self.hyperSpaceTtl -= 1
                if self.hyperSpaceTtl == 0:
                    self.inHyperSpace = False
                    self.color = (50, 255, 50)
                    self.thrustJet.color = (255, 50, 50)
                    self.position.x = random.randrange(0, self.stage.width)
                    self.position.y = random.randrange(0, self.stage.height)
                    position = Vector2d(self.position.x, self.position.y)
                    self.thrustJet.position = position

        return self.transformedPointlist

    def rotateLeft(self):
        """Xoay tàu ngược chiều kim đồng hồ một góc turnAngle."""
        self.angle += self.turnAngle
        self.thrustJet.angle += self.turnAngle

    def rotateRight(self):
        """Xoay tàu theo chiều kim đồng hồ một góc turnAngle."""
        self.angle -= self.turnAngle
        self.thrustJet.angle -= self.turnAngle

    def increaseThrust(self):
        """Áp dụng lực đẩy theo hướng mũi tàu hiện tại.

        Lực đẩy bị giới hạn tại maxVelocity. Phát âm thanh thrust.
        """
        playSoundContinuous("thrust")
        if math.hypot(self.heading.x, self.heading.y) > self.maxVelocity:
            return

        dx = self.acceleration * math.sin(radians(self.angle)) * -1
        dy = self.acceleration * math.cos(radians(self.angle)) * -1
        self.changeVelocity(dx, dy)

    def decreaseThrust(self):
        """Áp dụng ma sát để giảm dần vận tốc.

        Dừng âm thanh thrust khi được gọi.
        """
        stopSound("thrust")
        if (self.heading.x == 0 and self.heading.y == 0):
            return

        dx = self.heading.x * self.decelaration
        dy = self.heading.y * self.decelaration
        self.changeVelocity(dx, dy)

    def changeVelocity(self, dx, dy):
        """Thay đổi vận tốc của cả tàu và thrust jet.

        Args:
            dx: Lượng thay đổi vận tốc theo trục ngang.
            dy: Lượng thay đổi vận tốc theo trục dọc.
        """
        self.heading.x += dx
        self.heading.y += dy
        self.thrustJet.heading.x += dx
        self.thrustJet.heading.y += dy

    def move(self):
        """Cập nhật vị trí và áp dụng ma sát giảm tốc."""
        VectorSprite.move(self)
        self.decreaseThrust()

    def explode(self):
        """Phân rã tàu thành các mảnh vụn riêng lẻ theo từng cạnh."""
        pointlist = [(0, -10), (6, 10)]
        self.addShipDebris(pointlist)
        pointlist = [(6, 10), (3, 7)]
        self.addShipDebris(pointlist)
        pointlist = [(3, 7), (-3, 7)]
        self.addShipDebris(pointlist)
        pointlist = [(-3, 7), (-6, 10)]
        self.addShipDebris(pointlist)
        pointlist = [(-6, 10), (0, -10)]
        self.addShipDebris(pointlist)


    def addShipDebris(self, pointlist):
        """Tạo một mảnh vụn từ một cạnh của tàu.

        Mảnh vụn kế thừa màu của tàu và trôi ra xa tâm tàu
        với vận tốc ngẫu nhiên.

        Args:
            pointlist: Danh sách hai điểm xác định cạnh.
        """
        heading = Vector2d(0, 0)
        position = Vector2d(self.position.x, self.position.y)
        debris = VectorSprite(position, heading, pointlist, self.angle)
        debris.color = (50, 255, 50)

        self.stage.addSprite(debris)

        centerX = debris.rect.centerx
        centerY = debris.rect.centery

        debris.heading.x = ((centerX - self.position.x) +
                            0.1) / random.uniform(20, 40)
        debris.heading.y = ((centerY - self.position.y) +
                            0.1) / random.uniform(20, 40)
        self.shipDebrisList.append(debris)


    def fireBullet(self):
        """Bắn đạn theo hướng mũi tàu hiện tại.

        Không bắn được khi đang trong trạng thái hyperspace.
        """
        if self.inHyperSpace == False:
            vx = self.bulletVelocity * math.sin(radians(self.angle)) * -1
            vy = self.bulletVelocity * math.cos(radians(self.angle)) * -1
            heading = Vector2d(vx, vy)
            Shooter.fireBullet(self, heading, self.bulletTtl,
                               self.bulletVelocity)
            playSound("fire")

    def enterHyperSpace(self):
        """Kích hoạt nhảy hyperspace, ẩn tàu và bật trạng thái bất tử.

        Tàu xuất hiện lại tại vị trí ngẫu nhiên sau khi hết thời gian
        hyperspace.
        """
        if not self.inHyperSpace:
            self.inHyperSpace = True
            self.hyperSpaceTtl = 100
            self.color = (0, 0, 0)
            self.thrustJet.color = (0, 0, 0)


class ThrustJet(VectorSprite):
    """Hiệu ứng khí xả động cơ gắn liền với tàu người chơi.

    Render ngọn lửa tam giác phía sau tàu khi đang đẩy.
    Ẩn đi khi tàu không đẩy hoặc đang trong hyperspace.

    Attributes:
        accelerating: Động cơ có đang hoạt động hay không.
        ship: Tham chiếu đến instance Ship gốc.
    """
    pointlist = [(-3, 7), (0, 13), (3, 7)]

    def __init__(self, stage, ship):
        """Khởi tạo thrust jet gắn với tàu.

        Args:
            stage: Instance Stage quản lý sprite.
            ship: Instance Ship gốc.
        """
        position = Vector2d(stage.width/2, stage.height/2)
        heading = Vector2d(0, 0)
        self.accelerating = False
        self.ship = ship
        VectorSprite.__init__(self, position, heading, self.pointlist)

    def draw(self):
        """Render ngọn lửa, bật/tắt hiển thị theo trạng thái động cơ.

        Returns:
            Danh sách các đỉnh đa giác đã biến đổi.
        """
        if self.accelerating and self.ship.inHyperSpace == False:
            self.color = (255, 50, 50)
        else:
            self.color = (0, 0, 0)

        VectorSprite.draw(self)
        return self.transformedPointlist
