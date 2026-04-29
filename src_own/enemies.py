"""Các thực thể địch: thiên thạch, hạt hiệu ứng, và AI đĩa bay.

Cung cấp lớp Rock cho thiên thạch với ba cấp kích thước,
Debris cho hiệu ứng hạt khi phá hủy, và Saucer cho tàu địch
với ba cấp độ khó sử dụng AI pathfinding.
"""

import random
from util.vectorsprites import *
from shooter import *
from soundManager import *
from dsa.pathfinding import GridPathfinder

class Rock(VectorSprite):
    """Thiên thạch với hình dạng, kích thước, và vận tốc ngẫu nhiên.

    Thiên thạch có ba cấp kích thước (lớn, vừa, nhỏ) với hệ số
    vận tốc và tỷ lệ tương ứng. Mỗi thiên thạch xoay chậm và sử dụng
    một trong bốn dạng đa giác định sẵn.

    Attributes:
        rockType: Chỉ số cấp kích thước (0=lớn, 1=vừa, 2=nhỏ).
        rockShape: Bộ đếm class-level xoay vòng qua các biến thể đa giác.
        velocities: Vận tốc tối đa theo từng cấp.
        scales: Hệ số co giãn đa giác theo từng cấp.
    """
    largeRockType = 0
    mediumRockType = 1
    smallRockType = 2   
    
    velocities = (2.2, 2.8, 3.4)    
    scales = (2.5, 1.5, 0.6)

    rockShape = 1    
    
    def __init__(self, stage, position, rockType):
        """Khởi tạo thiên thạch với hướng bay ngẫu nhiên.

        Args:
            stage: Instance Stage quản lý sprite.
            position: Vị trí spawn, dạng Vector2d.
            rockType: Chỉ số cấp kích thước (0=lớn, 1=vừa, 2=nhỏ).
        """
        scale = Rock.scales[rockType]
        velocity = Rock.velocities[rockType]                
        heading = Vector2d(random.uniform(-velocity, velocity), random.uniform(-velocity, velocity))
        
        if heading.x == 0:
            heading.x = 0.1
        
        if heading.y == 0:
            heading.y = 0.1
                        
        self.rockType = rockType  
        pointlist = self.createPointList()
        newPointList = [self.scale(point, scale) for point in pointlist]        
        VectorSprite.__init__(self, position, heading, newPointList)
                
    
    def createPointList(self):
        """Tạo danh sách đỉnh đa giác cho biến thể hình dạng hiện tại.

        Xoay vòng qua bốn dạng đa giác định sẵn để tạo sự
        đa dạng hình ảnh giữa các thiên thạch.

        Returns:
            Danh sách tuple (x, y) xác định các đỉnh đa giác.
        """
        if (Rock.rockShape == 1):
            pointlist = [(-4,-12), (6,-12), (13, -4), (13, 5), (6, 13), (0,13), (0,4),\
                     (-8,13), (-15, 4), (-7,1), (-15,-3)]
 
        elif (Rock.rockShape == 2):
            pointlist = [(-6,-12), (1,-5), (8, -12), (15, -5), (12,0), (15,6), (5,13),\
                         (-7,13), (-14,7), (-14,-5)]
            
        elif (Rock.rockShape == 3):
            pointlist = [(-7,-12), (1,-9), (8,-12), (15,-5), (8,-3), (15,4), (8,12),\
                         (-3,10), (-6,12), (-14,7), (-10,0), (-14,-5)]            

        elif (Rock.rockShape == 4):
            pointlist = [(-7,-11), (3,-11), (13,-5), (13,-2), (2,2), (13,8), (6,14),\
                         (2,10), (-7,14), (-15,5), (-15,-5), (-5,-5), (-7,-11)]

        Rock.rockShape += 1
        if (Rock.rockShape == 5):
            Rock.rockShape = 1

        return pointlist
    
    def move(self):
        """Cập nhật vị trí và áp dụng xoay đều."""
        VectorSprite.move(self)                        
        
        self.angle += 1
    

class Debris(Point):    
    """Hạt hiệu ứng ngắn hạn sinh ra khi thực thể bị phá hủy.

    Kế thừa màu từ thực thể bị phá hủy và mờ dần theo thời gian
    bằng cách giảm giá trị RGB mỗi frame.

    Attributes:
        ttl: Số frame còn lại (mặc định 50).
    """

    def __init__(self, position, stage):
        """Khởi tạo hạt debris với vận tốc trôi ngẫu nhiên.

        Args:
            position: Vị trí spawn, dạng Vector2d.
            stage: Instance Stage quản lý sprite.
        """
        heading = Vector2d(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))
        Point.__init__(self, position, heading, stage)
        self.ttl = 50
    
    def move(self):    
        """Cập nhật vị trí và làm mờ dần màu về đen."""
        Point.move(self)
        r,g,b = self.color
        r = max(0, r - 5)
        g = max(0, g - 5)
        b = max(0, b - 5)
        self.color = (r,g,b)
        

class Saucer(Shooter):
    """Tàu địch với ba cấp độ khó.

    - Lớn (type 0): Di chuyển dích dắc đơn giản, không dùng pathfinding.
    - Vừa (type 1): Dùng BFS pathfinding để né chướng ngại vật.
    - Khó (type 2): Dùng A* pathfinding để tối ưu tránh chướng ngại vật.

    Cả ba cấp đều ngắm và bắn vào tàu người chơi. Khi người chơi
    bị phá hủy, đĩa bay chuyển về di chuyển ngang đơn giản và
    ngừng bắn cho đến khi thoát khỏi màn hình.

    Attributes:
        saucerType: Chỉ số cấp độ khó (0=lớn, 1=vừa, 2=khó).
        ship: Tham chiếu đến Ship người chơi để ngắm bắn.
        scoreValue: Điểm thưởng khi bị tiêu diệt.
        laps: Số lần đã đi qua rìa màn hình (wrap-around).
        lastx: Tọa độ x frame trước để phát hiện wrap.
        pathfinder: Instance GridPathfinder để tránh chướng ngại vật.
        fire_cooldown: Số frame còn lại trước khi được bắn tiếp.
    """
    largeSaucerType = 0
    smallSaucerType = 1
    hardSaucerType = 2

    velocities = (1.5, 2.5, 3.5)    
    scales = (1.8, 1.4, 1.0)
    scores = (500, 1000, 2000)
    colors = [(255, 255, 0), (255, 165, 0), (255, 50, 50)]
    pointlist = [(-9,0), (-3,-3), (-2,-6), (-2,-6), (2,-6), (3,-3), (9,0), (-9,0), (-3,4), (3,4), (9,0)]
    maxBulletsList = [1, 2, 4]
    bulletTtl = [60, 90, 120]
    bulletVelocityList = [4.0, 6.0, 8.0]
    fire_delays = [60, 45, 30]
    
    def __init__(self, stage, saucerType, ship):                
        """Khởi tạo đĩa bay với cấu hình theo cấp độ khó.

        Args:
            stage: Instance Stage quản lý sprite.
            saucerType: Chỉ số cấp độ khó (0=lớn, 1=vừa, 2=khó).
            ship: Tham chiếu đến Ship người chơi để ngắm bắn.
        """
        position = Vector2d(0.0, random.randrange(0, stage.height))
        heading = Vector2d(self.velocities[saucerType], 0.0)
        self.saucerType = saucerType
        self.ship = ship
        self.scoreValue = self.scores[saucerType]
        stopSound("ssaucer")
        stopSound("lsaucer")            
        if saucerType == self.largeSaucerType:            
            playSoundContinuous("lsaucer")            
        else:            
            playSoundContinuous("ssaucer")
        self.laps = 0
        self.lastx = 0
        self.pathfinder = GridPathfinder(stage.width, stage.height, 64)
        
        newPointList = [self.scale(point, self.scales[saucerType]) for point in self.pointlist]
        Shooter.__init__(self, position, heading, newPointList, stage)
        self.color = self.colors[saucerType]
        self.maxBullets = self.maxBulletsList[saucerType]
        self.fire_cooldown = 0
        
    def move(self):        
        """Cập nhật vị trí theo chiến lược di chuyển tương ứng cấp độ.

        Đĩa bay lớn và đĩa bay khi không có mục tiêu sống dùng di chuyển
        dích dắc ngang đơn giản. Đĩa bay vừa và khó dùng BFS và A*
        pathfinding để di chuyển về phía người chơi trong khi tránh
        chướng ngại vật.
        """
        ship_alive = self.ship is not None and self.ship in self.stage.spriteList and not self.ship.inHyperSpace
        
        if self.saucerType == self.largeSaucerType or not ship_alive:
            if self.heading.x == 0:
                self.heading.x = self.velocities[self.saucerType]
            self.heading.x = math.copysign(self.velocities[self.saucerType], self.heading.x)
            
            Shooter.move(self)  
            
            if (self.position.x > self.stage.width * 0.33) and (self.position.x < self.stage.width * 0.66):
                self.heading.y = self.heading.x
            else:
                self.heading.y = 0
        else:
            rocks = []
            bullets = []
            for sprite in self.stage.spriteList:
                if isinstance(sprite, Rock):
                    rocks.append(sprite)
                elif isinstance(sprite, Bullet):
                    bullets.append(sprite)
            
            grid = self.pathfinder.build_grid(rocks, bullets, self.bullets)
            
            if self.saucerType == self.smallSaucerType:
                next_pos = self.pathfinder.bfs(grid, self.position, self.ship.position)
            else:
                next_pos = self.pathfinder.astar(grid, self.position, self.ship.position)
                
            if next_pos:
                dx = next_pos.x - self.position.x
                dy = next_pos.y - self.position.y
                mag = math.sqrt(dx*dx + dy*dy)
                if mag > 0:
                    self.heading.x = self.velocities[self.saucerType] * (dx/mag)
                    self.heading.y = self.velocities[self.saucerType] * (dy/mag)
            
            Shooter.move(self)
        
        if ship_alive:
            self.fireBullet()
        
        if abs(self.lastx - self.position.x) > self.stage.width / 2:
            self.laps += 1
            if not ship_alive:
                self.laps = 10  # Force immediate despawn in main.py
        self.lastx = self.position.x
                
    def fireBullet(self):
        """Bắn đạn nhắm vào tàu người chơi.

        Tuân thủ fire cooldown và giới hạn băng đạn theo cấp độ.
        Đạn kế thừa màu của đĩa bay để phân biệt trực quan.
        """
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
            return
            
        if self.ship is not None and len(self.bullets) < self.maxBulletsList[self.saucerType]:            
            dx = self.ship.position.x - self.position.x
            dy = self.ship.position.y - self.position.y
            mag = math.sqrt(dx*dx + dy*dy)
            if mag > 0:
                vel = self.bulletVelocityList[self.saucerType]
                heading = Vector2d(vel * (dx/mag), vel * (dy/mag))
                shotFired = Shooter.fireBullet(self, heading, self.bulletTtl[self.saucerType], vel)
                if shotFired:
                    playSound("sfire")
                    self.fire_cooldown = self.fire_delays[self.saucerType]
