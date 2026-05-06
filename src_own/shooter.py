"""
Lớp cơ sở Shooter và lớp đạn Bullet.

Định nghĩa mixin Shooter cho các thực thể có khả năng bắn đạn,
và lớp Bullet đại diện cho từng viên đạn riêng lẻ.

Last Modified: 2026-05-06
"""

import random
from util.vectorsprites import *
from util import *


class Shooter(VectorSprite):
    """
    Lớp cơ sở trừu tượng cho các thực thể có khả năng bắn đạn.

    Quản lý danh sách đạn đang hoạt động và cung cấp các phương thức
    bắn đạn mới, phát hiện va chạm đạn-mục tiêu.

    Attributes:
        bullets: Danh sách các instance Bullet đang hoạt động.
        stage: Instance Stage quản lý sprite.

    Last Modified: 2026-05-06
    """

    def __init__(self, position, heading, pointlist, stage):
        """
        Khởi tạo Shooter với vị trí và tham chiếu Stage.

        Args:
            position: Vị trí world-space, dạng Vector2d.
            heading: Vector vận tốc, dạng Vector2d.
            pointlist: Danh sách đỉnh đa giác xác định hình dạng.
            stage: Instance Stage quản lý sprite.

        Last Modified: 2026-05-06
        """
        VectorSprite.__init__(self, position, heading, pointlist)
        self.bullets = []
        self.stage = stage

    def fireBullet(self, heading, ttl, velocity, position=None):
        """
        Tạo viên đạn mới nếu chưa đạt giới hạn băng đạn.

        Args:
            heading: Vector vận tốc của đạn, dạng Vector2d.
            ttl: Thời gian sống tính bằng frame.
            velocity: Tốc độ vô hướng của đạn.
            position: Vị trí tùy chỉnh (tùy chọn), mặc định dùng vị trí của shooter.

        Returns:
            True nếu đạn được tạo thành công, None nếu băng đạn đầy.

        Last Modified: 2026-05-06
        """
        if (len(self.bullets) < self.maxBullets):
            if position is None:
                position = Vector2d(self.position.x, self.position.y)
            else:
                # Đảm bảo position là bản sao Vector2d mới để tránh tham chiếu chung
                position = Vector2d(position.x, position.y)
                
            newBullet = Bullet(position, heading, self,
                               ttl, velocity, self.stage)
            self.bullets.append(newBullet)
            self.stage.addSprite(newBullet)
            return True

    def bulletCollision(self, target):
        """
        Kiểm tra đạn đang hoạt động có trúng mục tiêu không.

        Đạn trúng mục tiêu sẽ bị đặt ttl về 0.

        Args:
            target: VectorSprite cần kiểm tra va chạm.

        Returns:
            True nếu ít nhất một viên đạn trúng, False nếu không.

        Last Modified: 2026-05-06
        """
        collisionDetected = False
        for bullet in self.bullets:
            if bullet.ttl > 0 and target.collidesWith(bullet):
                collisionDetected = True
                bullet.ttl = 0

        return collisionDetected



class Bullet(Point):
    """
    Viên đạn được bắn ra bởi một Shooter.

    Kế thừa màu từ Shooter đã bắn nó. Tự gỡ khỏi danh sách đạn
    của Shooter khi hết thời gian sống.

    Attributes:
        shooter: Instance Shooter đã bắn viên đạn này.
        ttl: Số frame còn lại trước khi hết hạn.
        velocity: Tốc độ vô hướng của đạn.

    Last Modified: 2026-05-06
    """
    pointlist = [(-1, -1), (1, -1), (1, 1), (-1, 1)]

    def __init__(self, position, heading, shooter, ttl, velocity, stage):
        """
        Khởi tạo đạn với quỹ đạo và quyền sở hữu.

        Args:
            position: Vị trí spawn, dạng Vector2d.
            heading: Vector vận tốc, dạng Vector2d.
            shooter: Instance Shooter sở hữu viên đạn.
            ttl: Thời gian sống tính bằng frame.
            velocity: Tốc độ vô hướng của đạn.
            stage: Instance Stage quản lý sprite.

        Last Modified: 2026-05-06
        """
        Point.__init__(self, position, heading, stage)
        self.shooter = shooter
        self.ttl = ttl
        self.velocity = velocity
        self.color = shooter.color

    def move(self):
        """
        Cập nhật vị trí và gỡ khỏi danh sách đạn khi hết hạn.

        Last Modified: 2026-05-06
        """
        Point.move(self)
        if (self.ttl <= 0):
            self.shooter.bullets.remove(self)
