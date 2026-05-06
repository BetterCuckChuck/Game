"""
Tàu người chơi và hiệu ứng lửa động cơ.

Cung cấp lớp Ship cho tàu vũ trụ do người chơi điều khiển với
hệ thống đẩy, xoay, hyperspace, và vũ khí, cùng lớp ThrustJet
cho hiệu ứng khí xả động cơ.

Last Modified: 2026-05-06
"""

import random
from util.vectorsprites import *
from shooter import *
from math import *
from soundManager import *


class Ship(Shooter):
    """
    Tàu vũ trụ do người chơi điều khiển với hệ thống đẩy, xoay, và vũ khí.

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

    Last Modified: 2026-05-06
    """
    acceleration = 0.27
    decelaration = -0.008
    maxVelocity = 10
    turnAngle = 6.5
    bulletVelocity = 18.0
    maxBullets = 100
    bulletTtl = 45

    def __init__(self, stage):
        """
        Khởi tạo tàu tại tâm màn hình với cấu hình mặc định.

        Args:
            stage: Instance Stage quản lý sprite.

        Last Modified: 2026-05-06
        """
        position = Vector2d(stage.width/2, stage.height/2)
        heading = Vector2d(0, 0)
        self.thrustJet = ThrustJet(stage, self)
        self.shipDebrisList = []
        self.visible = True
        self.inHyperSpace = False
        self.burstCooldown = 0
        self.fireLevel = 1
        self.powerupTimer = 0
        self.invincible = False
        self.invincibleTimer = 0
        pointlist = [(0, -9), (5, 9), (3, 7), (-3, 7), (-5, 9)]

        Shooter.__init__(self, position, heading, pointlist, stage)
        self.color = (50, 255, 50)
        self._baseColor = (50, 255, 50)

    def draw(self):
        """
        Render tàu, xử lý chuyển tiếp hyperspace và nhấp nháy bất tử.

        Returns:
            Danh sách các đỉnh đa giác đã biến đổi.

        Last Modified: 2026-05-06
        """
        if self.visible:
            if not self.inHyperSpace:
                if self.invincible:
                    if (self.invincibleTimer // 4) % 2 == 0:
                        self.color = self._baseColor
                    else:
                        self.color = (20, 80, 20)
                VectorSprite.draw(self)
            else:
                self.hyperSpaceTtl -= 1
                if self.hyperSpaceTtl == 0:
                    self.inHyperSpace = False
                    self.color = self._baseColor
                    self.thrustJet.color = (255, 50, 50)
                    self.position.x = random.randrange(0, self.stage.width)
                    self.position.y = random.randrange(0, self.stage.height)
                    position = Vector2d(self.position.x, self.position.y)
                    self.thrustJet.position = position

        return self.transformedPointlist

    def rotateLeft(self):
        """
        Xoay tàu ngược chiều kim đồng hồ một góc turnAngle.

        Last Modified: 2026-05-06
        """
        self.angle += self.turnAngle
        self.thrustJet.angle += self.turnAngle

    def rotateRight(self):
        """
        Xoay tàu theo chiều kim đồng hồ một góc turnAngle.

        Last Modified: 2026-05-06
        """
        self.angle -= self.turnAngle
        self.thrustJet.angle -= self.turnAngle

    def increaseThrust(self):
        """
        Áp dụng lực đẩy theo hướng mũi tàu hiện tại.

        Lực đẩy bị giới hạn tại maxVelocity. Phát âm thanh thrust.

        Last Modified: 2026-05-06
        """
        playSoundContinuous("thrust")
        if math.hypot(self.heading.x, self.heading.y) > self.maxVelocity:
            return

        dx = self.acceleration * math.sin(radians(self.angle)) * -1
        dy = self.acceleration * math.cos(radians(self.angle)) * -1
        self.changeVelocity(dx, dy)

    def decreaseThrust(self):
        """
        Áp dụng ma sát để giảm dần vận tốc.

        Dừng âm thanh thrust khi được gọi.

        Last Modified: 2026-05-06
        """
        stopSound("thrust")
        if (self.heading.x == 0 and self.heading.y == 0):
            return

        dx = self.heading.x * self.decelaration
        dy = self.heading.y * self.decelaration
        self.changeVelocity(dx, dy)

    def changeVelocity(self, dx, dy):
        """
        Thay đổi vận tốc của cả tàu và thrust jet.

        Args:
            dx: Lượng thay đổi vận tốc theo trục ngang.
            dy: Lượng thay đổi vận tốc theo trục dọc.

        Last Modified: 2026-05-06
        """
        self.heading.x += dx
        self.heading.y += dy
        self.thrustJet.heading.x += dx
        self.thrustJet.heading.y += dy

    def move(self):
        """
        Cập nhật vị trí, áp dụng ma sát giảm tốc, và tick cooldown.

        Last Modified: 2026-05-06
        """
        VectorSprite.move(self)
        self.decreaseThrust()
        if self.burstCooldown > 0:
            self.burstCooldown -= 1
        if self.powerupTimer > 0:
            self.powerupTimer -= 1
            if self.powerupTimer == 0:
                self.fireLevel = 1
        if self.invincibleTimer > 0:
            self.invincibleTimer -= 1
            if self.invincibleTimer == 0:
                self.invincible = False
                self.color = self._baseColor

    def explode(self):
        """
        Phân rã tàu thành các mảnh vụn riêng lẻ theo từng cạnh.

        Last Modified: 2026-05-06
        """
        pointlist = [(0, -9), (5, 9)]
        self.addShipDebris(pointlist)
        pointlist = [(5, 9), (3, 7)]
        self.addShipDebris(pointlist)
        pointlist = [(3, 7), (-3, 7)]
        self.addShipDebris(pointlist)
        pointlist = [(-3, 7), (-5, 9)]
        self.addShipDebris(pointlist)
        pointlist = [(-5, 9), (0, -9)]
        self.addShipDebris(pointlist)


    def addShipDebris(self, pointlist):
        """
        Tạo một mảnh vụn từ một cạnh của tàu.

        Mảnh vụn kế thừa màu của tàu và trôi ra xa tâm tàu
        với vận tốc ngẫu nhiên.

        Args:
            pointlist: Danh sách hai điểm xác định cạnh.

        Last Modified: 2026-05-06
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
        """
        Bắn đạn theo hướng mũi tàu hiện tại.

        Hỗ trợ nhiều cấp độ đạn song song (Multi-Fire).
        Không bắn được khi đang trong trạng thái hyperspace.

        Last Modified: 2026-05-06
        """
        if self.inHyperSpace:
            return

        angle_rad = radians(self.angle)
        vx = self.bulletVelocity * math.sin(angle_rad) * -1
        vy = self.bulletVelocity * math.cos(angle_rad) * -1
        
        # Tính toán offset vuông góc để các viên đạn song song
        perp_x = math.cos(angle_rad)
        perp_y = math.sin(angle_rad)
        
        spacing = 12 # Khoảng cách giữa các viên đạn (tăng từ 10)
        
        # Nếu fireLevel > 1, bắn nhiều viên song song
        start_offset = -(self.fireLevel - 1) * spacing / 2
        
        for i in range(self.fireLevel):
            offset = start_offset + i * spacing
            pos = Vector2d(self.position.x + perp_x * offset,
                          self.position.y - perp_y * offset)
            heading = Vector2d(vx, vy)
            Shooter.fireBullet(self, heading, self.bulletTtl,
                               self.bulletVelocity, position=pos)
        
        playSound("fire")

    def fireBurst(self):
        """
        Bắn đạn theo hình nón, số tia và số đạn mỗi tia tăng theo fireLevel.

        Cấp 1: 5 tia x 3 đạn.
        Cấp 3: 9 tia x 4 đạn.
        Cấp 4: 11 tia x 4 đạn.
        ...
        Cooldown 60 frame (1 giây).

        Returns:
            True nếu burst thành công, False nếu đang cooldown.

        Last Modified: 2026-05-06
        """
        if self.inHyperSpace or self.burstCooldown > 0:
            return False
        
        angle_rad = radians(self.angle)
        
        # Tính toán số tia đạn dựa trên fireLevel (mặc định 5 tia ở cấp 1)
        extra_levels = max(0, self.fireLevel - 1)
        num_rays = 5 + extra_levels * 2
        bullets_per_ray = 3 + extra_levels // 2
        
        # Giới hạn góc trải rộng (spread) tối đa ±40 độ
        total_spread = min(40, 20 + extra_levels * 5)
        
        # Tính toán góc cho từng tia
        for i in range(num_rays):
            if num_rays > 1:
                offset_deg = -total_spread + (i * (2 * total_spread) / (num_rays - 1))
            else:
                offset_deg = 0
                
            a = angle_rad + radians(offset_deg)
            vx = self.bulletVelocity * math.sin(a) * -1
            vy = self.bulletVelocity * math.cos(a) * -1
            
            for b in range(bullets_per_ray):
                ttl = self.bulletTtl - b * 7 # Giảm TTL để tạo trail
                # Spawn đạn tại vị trí tàu
                heading = Vector2d(vx, vy)
                Shooter.fireBullet(self, heading, ttl, self.bulletVelocity)
                
        self.burstCooldown = 60
        playSound("fire")
        return True

    def enterHyperSpace(self):
        """
        Kích hoạt nhảy hyperspace, ẩn tàu và bật trạng thái bất tử.

        Tàu xuất hiện lại tại vị trí ngẫu nhiên sau khi hết thời gian
        hyperspace.

        Last Modified: 2026-05-06
        """
        if not self.inHyperSpace:
            self.inHyperSpace = True
            self.hyperSpaceTtl = 100
            self.color = (0, 0, 0)
            self.thrustJet.color = (0, 0, 0)


class ThrustJet(VectorSprite):
    """
    Hiệu ứng khí xả động cơ gắn liền với tàu người chơi.

    Render ngọn lửa tam giác phía sau tàu khi đang đẩy.
    Ẩn đi khi tàu không đẩy hoặc đang trong hyperspace.

    Attributes:
        accelerating: Động cơ có đang hoạt động hay không.
        ship: Tham chiếu đến instance Ship gốc.

    Last Modified: 2026-05-06
    """
    pointlist = [(-3, 7), (0, 13), (3, 7)]

    def __init__(self, stage, ship):
        """
        Khởi tạo thrust jet gắn với tàu.

        Args:
            stage: Instance Stage quản lý sprite.
            ship: Instance Ship gốc.

        Last Modified: 2026-05-06
        """
        position = Vector2d(stage.width/2, stage.height/2)
        heading = Vector2d(0, 0)
        self.accelerating = False
        self.ship = ship
        VectorSprite.__init__(self, position, heading, self.pointlist)

    def draw(self):
        """
        Render ngọn lửa, bật/tắt hiển thị theo trạng thái động cơ.

        Returns:
            Danh sách các đỉnh đa giác đã biến đổi.

        Last Modified: 2026-05-06
        """
        if self.accelerating and self.ship.inHyperSpace == False:
            self.color = (255, 50, 50)
        else:
            self.color = (0, 0, 0)

        VectorSprite.draw(self)
        return self.transformedPointlist
