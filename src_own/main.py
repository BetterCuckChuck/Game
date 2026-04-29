"""Entry point và controller chính của game Asteroids.

Cài đặt lớp Asteroids chứa vòng lặp game chính, máy trạng thái,
pipeline phát hiện va chạm, hệ thống tính điểm, và quản lý
vòng đời thực thể.
"""

import pygame
import sys
import os
import random
from pygame.locals import *
from util.vectorsprites import *
from ship import *
from stage import *
from enemies import *
from shooter import *
from soundManager import *
from dsa.quadtree import QuadTree


class Asteroids():
    """Controller chính quản lý vòng lặp game và trạng thái.

    Điều phối tất cả hệ thống con bao gồm render, xử lý input,
    phát hiện va chạm, tính điểm, và quản lý vòng đời thực thể.

    Attributes:
        explodingTtl: Thời lượng animation phá hủy tàu (frame).
        stage: Instance Stage quản lý display surface.
        paused: Game có đang tạm dừng hay không.
        showingFPS: Có hiển thị bộ đếm FPS hay không.
        frameAdvance: Cờ debug cho chế độ bước từng frame.
        gameState: Trạng thái hiện tại ('attract_mode', 'playing', 'exploding').
        rockList: Danh sách toàn bộ instance Rock đang hoạt động.
        saucer: Instance Saucer đang hoạt động, hoặc None.
        secondsCount: Bộ đếm frame dùng cho các sự kiện định thời.
        score: Điểm hiện tại của người chơi.
        ship: Instance Ship của người chơi.
        lives: Số mạng còn lại.
    """
    explodingTtl = 180

    def __init__(self):
        """Khởi tạo game ở chế độ attract mode với cấu hình mặc định."""
        self.stage = Stage('Atari Asteroids', (1024, 768))
        self.paused = False
        self.showingFPS = False
        self.frameAdvance = False
        self.gameState = "attract_mode"
        self.rockList = []
        self.createRocks(3)
        self.saucer = None
        self.secondsCount = 1
        self.score = 0
        self.nextLife = 10000
        self.ship = None
        self.lives = 0

    def initialiseGame(self):
        """Đặt lại toàn bộ trạng thái game và bắt đầu phiên chơi mới."""
        self.gameState = 'playing'
        [self.stage.removeSprite(sprite)
         for sprite in self.rockList]  
        if self.saucer is not None:
            self.killSaucer()
        self.startLives = 5
        self.createNewShip()
        self.createLivesList()
        self.score = 0
        self.rockList = []
        self.numRocks = 3
        self.nextLife = 10000

        self.createRocks(self.numRocks)
        self.secondsCount = 1

    def createNewShip(self):
        """Tạo tàu người chơi mới tại tâm màn hình và đăng ký sprite."""
        if self.ship:
            [self.stage.spriteList.remove(debris)
             for debris in self.ship.shipDebrisList]
        self.ship = Ship(self.stage)
        self.stage.addSprite(self.ship.thrustJet)
        self.stage.addSprite(self.ship)

    def createLivesList(self):
        """Tạo các icon đếm mạng trên HUD ở góc phải trên."""
        self.lives += 1
        self.livesList = []
        for i in range(1, self.startLives):
            self.addLife(i)

    def addLife(self, lifeNumber):
        """Thêm icon mạng vào HUD và tăng bộ đếm mạng.

        Args:
            lifeNumber: Vị trí thứ tự của icon mạng dùng cho layout.
        """
        self.lives += 1
        ship = Ship(self.stage)
        self.stage.addSprite(ship)
        ship.position.x = self.stage.width - \
            (lifeNumber * ship.rect.width) - 10
        ship.position.y = 0 + ship.rect.height
        self.livesList.append(ship)

    def createRocks(self, numRocks):
        """Spawn thiên thạch lớn tại các rìa màn hình ngẫu nhiên.

        Args:
            numRocks: Số thiên thạch lớn cần spawn.
        """
        for _ in range(0, numRocks):
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top':
                pos_x = random.randrange(0, self.stage.width)
                pos_y = 0
            elif edge == 'bottom':
                pos_x = random.randrange(0, self.stage.width)
                pos_y = self.stage.height
            elif edge == 'left':
                pos_x = 0
                pos_y = random.randrange(0, self.stage.height)
            else:
                pos_x = self.stage.width
                pos_y = random.randrange(0, self.stage.height)
                
            position = Vector2d(pos_x, pos_y)

            newRock = Rock(self.stage, position, Rock.largeRockType)
            newRock.safe_timer = 15
            self.stage.addSprite(newRock)
            self.rockList.append(newRock)

    def playGame(self):
        """Chạy vòng lặp game chính ở 60 FPS."""
        clock = pygame.time.Clock()

        frameCount = 0.0
        timePassed = 0.0
        self.fps = 0.0
        while True:

            timePassed += clock.tick(60)
            frameCount += 1
            if frameCount % 10 == 0:  
                self.fps = round((frameCount / (timePassed / 1000.0)))
                timePassed = 0
                frameCount = 0

            self.secondsCount += 1

            self.input(pygame.event.get())

            if self.paused and not self.frameAdvance:
                self.displayPaused()
                continue

            self.stage.screen.fill((10, 10, 10))
            self.stage.moveSprites()
            self.stage.drawSprites()
            self.doSaucerLogic()
            self.displayScore()
            if self.showingFPS:
                self.displayFps()  
            self.checkScore()

            if self.gameState == 'playing':
                self.playing()
            elif self.gameState == 'exploding':
                self.exploding()
            else:
                self.checkCollisions()
                if self.secondsCount % 420 == 0:
                    self.createRocks(1)
                if len(self.rockList) == 0:
                    self.createRocks(3)
                self.displayText()

            pygame.display.flip()

    def playing(self):
        """Xử lý logic mỗi frame khi game đang ở trạng thái playing."""
        if self.lives == 0:
            self.gameState = 'attract_mode'
        else:
            self.processKeys()
            self.checkCollisions()
            
            # Tự động sinh thêm 1 thiên thạch lớn mỗi 7 giây (420 frames)
            # Điều này giúp game liên tục có thiên thạch mới mà không cần đợi dọn sạch bản đồ
            if self.secondsCount % 420 == 0:
                self.createRocks(1)
                
            if len(self.rockList) == 0:
                self.levelUp()

    def doSaucerLogic(self):
        """Quản lý vòng đời đĩa bay: despawn khi đạt giới hạn lap và spawn đĩa bay mới theo timer."""
        if self.saucer is not None:
            if self.saucer.laps >= 2:
                self.killSaucer()

        if self.secondsCount % 300 == 0 and self.saucer is None:
            randVal = random.randrange(0, 10)
            if randVal <= 3:
                self.saucer = Saucer(self.stage, Saucer.largeSaucerType, self.ship)
            elif randVal <= 7:
                self.saucer = Saucer(self.stage, Saucer.smallSaucerType, self.ship)
            else:
                self.saucer = Saucer(self.stage, Saucer.hardSaucerType, self.ship)
            self.stage.addSprite(self.saucer)

    def exploding(self):
        """Xử lý animation phá hủy tàu và đếm ngược respawn."""
        self.checkCollisions()
        self.doSaucerLogic()
        self.explodingCount += 1
        if self.explodingCount > self.explodingTtl:
            self.gameState = 'playing'
            [self.stage.spriteList.remove(debris)
             for debris in self.ship.shipDebrisList]
            self.ship.shipDebrisList = []

            if self.lives == 0:
                self.ship.visible = False
            else:
                self.createNewShip()

    def levelUp(self):
        """Tăng cấp độ khó bằng cách spawn thêm thiên thạch."""
        self.numRocks += 1
        self.createRocks(self.numRocks)

    def displayText(self):
        """Render màn hình tiêu đề với tên game, hướng dẫn, và bản quyền."""
        font1 = pygame.font.Font('../res/Hyperspace.otf', 50)
        font2 = pygame.font.Font('../res/Hyperspace.otf', 20)
        font3 = pygame.font.Font('../res/Hyperspace.otf', 30)
        font4 = pygame.font.Font('../res/Hyperspace.otf', 15)

        titleText = font1.render('Asteroids', True, (180, 180, 180))
        titleTextRect = titleText.get_rect(centerx=self.stage.width/2)
        titleTextRect.y = self.stage.height/2 - titleTextRect.height*2
        self.stage.screen.blit(titleText, titleTextRect)

        keysText = font2.render(
            '(C) 1979 Atari INC.', True, (255, 255, 255))
        keysTextRect = keysText.get_rect(centerx=self.stage.width/2)
        keysTextRect.y = self.stage.height - keysTextRect.height - 20
        self.stage.screen.blit(keysText, keysTextRect)

        instructionText = font3.render(
            'Press SPACE to Play', True, (200, 200, 200))
        instructionTextRect = instructionText.get_rect(
            centerx=self.stage.width/2)
        instructionTextRect.y = self.stage.height/2 - instructionTextRect.height
        self.stage.screen.blit(instructionText, instructionTextRect)

        controls = [
            "W / UP : Thrust",
            "A / LEFT : Rotate Left",
            "D / RIGHT : Rotate Right",
            "F / L : Fire",
            "H : Hyperspace",
            "P : Pause",
            "F11 : Fullscreen",
            "M : Mute/Unmute"
        ]
        
        start_y = instructionTextRect.y + 60
        for i, text in enumerate(controls):
            ctrl_text = font4.render(text, True, (220, 220, 220))
            ctrl_rect = ctrl_text.get_rect(centerx=self.stage.width/2)
            ctrl_rect.y = start_y + (i * 25)
            self.stage.screen.blit(ctrl_text, ctrl_rect)

    def displayScore(self):
        """Render điểm số hiện tại ở góc trái trên màn hình."""
        font1 = pygame.font.Font('../res/Hyperspace.otf', 30)
        scoreStr = str("%02d" % self.score)
        scoreText = font1.render(scoreStr, True, (200, 200, 200))
        scoreTextRect = scoreText.get_rect(centerx=100, centery=45)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def displayPaused(self):
        """Render overlay tạm dừng khi game bị pause."""
        if self.paused:
            font1 = pygame.font.Font('../res/Hyperspace.otf', 30)
            pausedText = font1.render("Paused", True, (255, 255, 255))
            textRect = pausedText.get_rect(
                centerx=self.stage.width/2, centery=self.stage.height/2)
            self.stage.screen.blit(pausedText, textRect)
            pygame.display.update()

    def input(self, events):
        """Xử lý các sự kiện input pygame cho điều khiển game.

        Args:
            events: Danh sách sự kiện pygame từ frame hiện tại.
        """
        self.frameAdvance = False
        for event in events:
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                if self.gameState == 'playing':
                    if event.key == K_f or event.key == K_l:
                        self.ship.fireBullet()
                    elif event.key == K_h:
                        self.ship.enterHyperSpace()
                elif self.gameState == 'attract_mode':
                    if event.key == K_SPACE:
                        self.initialiseGame()

                if event.key == K_p:
                    if self.paused:  
                        self.paused = False
                    else:
                        self.paused = True

                if event.key == K_j:
                    if self.showingFPS:  
                        self.showingFPS = False
                    else:
                        self.showingFPS = True

                if event.key == K_m:
                    toggleMute()

                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()

            elif event.type == KEYUP:
                if event.key == K_o:
                    self.frameAdvance = True

    def processKeys(self):
        """Đọc trạng thái phím giữ cho điều khiển liên tục (đẩy, xoay)."""
        key = pygame.key.get_pressed()

        if key[K_LEFT] or key[K_z] or key[K_a]:
            self.ship.rotateLeft()
        elif key[K_RIGHT] or key[K_x] or key[K_d]:
            self.ship.rotateRight()

        if key[K_UP] or key[K_n] or key[K_w]:
            self.ship.increaseThrust()
            self.ship.thrustJet.accelerating = True
        else:
            self.ship.thrustJet.accelerating = False


    def checkCollisions(self):
        """Thực hiện toàn bộ kiểm tra va chạm bằng QuadTree phân vùng không gian.

        Xử lý va chạm thiên thạch-thiên thạch, thiên thạch-tàu,
        thiên thạch-đĩa bay, đạn-thiên thạch, và đạn-đĩa bay.
        Quản lý phân mảnh thiên thạch, cập nhật điểm, và phá hủy thực thể.
        """
        newRocks = []
        shipHit, saucerHit = False, False

        bounds = pygame.Rect(0, 0, self.stage.width, self.stage.height)
        self.quadtree = QuadTree(bounds, 4)
        
        all_objects = self.rockList.copy()
        if self.ship and not self.ship.inHyperSpace and self.gameState == 'playing':
            all_objects.append(self.ship)
        if self.saucer:
            all_objects.append(self.saucer)
            
        for obj in all_objects:
            self.quadtree.insert(obj)

        for rock in self.rockList:
            if getattr(rock, 'safe_timer', 0) > 0:
                rock.safe_timer -= 1
                
            rockHit = False
            
            potential_hits = self.quadtree.get_potential_intersections(rock)

            for other in potential_hits:
                if other != rock and isinstance(other, Rock):
                    if getattr(rock, 'safe_timer', 0) > 0 or getattr(other, 'safe_timer', 0) > 0:
                        continue
                    if rock.collidesWith(other):
                        p = rock.checkPolygonCollision(other)
                        if p is not None:
                            v1_sq = rock.heading.x**2 + rock.heading.y**2
                            v2_sq = other.heading.x**2 + other.heading.y**2
                            
                            rock_survives = False
                            other_survives = False
                                
                            threshold_sq = 3.0
                            
                            if rock.rockType < other.rockType and v1_sq > v2_sq:
                                rock_survives = True
                            elif rock.rockType > other.rockType and v1_sq > v2_sq * threshold_sq:
                                rock_survives = True
                                
                            if other.rockType < rock.rockType and v2_sq > v1_sq:
                                other_survives = True
                            elif other.rockType > rock.rockType and v2_sq > v1_sq * threshold_sq:
                                other_survives = True
                                
                            both_destroyed = not rock_survives and not other_survives

                            if not other_survives:
                                if other in self.rockList:
                                    self.rockList.remove(other)
                                    self.stage.spriteList.remove(other)
                                    self.createDebris(other)
                                    playSound("explode" + str(other.rockType + 1))
                                    if other.rockType != Rock.smallRockType:
                                        nType = Rock.mediumRockType if other.rockType == Rock.largeRockType else Rock.smallRockType
                                        num_spawn = 1 if both_destroyed else 2
                                        for _ in range(num_spawn):
                                            pos = Vector2d(other.position.x, other.position.y)
                                            nR = Rock(self.stage, pos, nType)
                                            nR.safe_timer = 15
                                            self.stage.addSprite(nR)
                                            self.rockList.append(nR)
                                            
                            if not rock_survives:
                                if both_destroyed:
                                    rock.spawn_single_fragment = True
                                rockHit = True
                                break

            if self.ship and not self.ship.inHyperSpace and self.ship in potential_hits and self.gameState == 'playing':
                if rock.collidesWith(self.ship):
                    p = rock.checkPolygonCollision(self.ship)
                    if p is not None:
                        shipHit = True
                        rockHit = True

            if self.saucer is not None and self.saucer in potential_hits:
                if rock.collidesWith(self.saucer):
                    saucerHit = True
                    rockHit = True

            if self.saucer is not None:
                if self.saucer.bulletCollision(rock):
                    rockHit = True

                if self.ship and self.ship.bulletCollision(self.saucer):
                    saucerHit = True
                    if self.gameState == 'playing':
                        self.score += self.saucer.scoreValue

            if self.ship and self.ship.bulletCollision(rock):
                rockHit = True

            if rockHit:
                self.rockList.remove(rock)
                self.stage.spriteList.remove(rock)

                if rock.rockType == Rock.largeRockType:
                    playSound("explode1")
                    newRockType = Rock.mediumRockType
                    if self.gameState == 'playing':
                        self.score += 50
                elif rock.rockType == Rock.mediumRockType:
                    playSound("explode2")
                    newRockType = Rock.smallRockType
                    if self.gameState == 'playing':
                        self.score += 100
                else:
                    playSound("explode3")
                    if self.gameState == 'playing':
                        self.score += 200

                if rock.rockType != Rock.smallRockType:
                    num_spawn = 1 if getattr(rock, 'spawn_single_fragment', False) else 2
                    for _ in range(0, num_spawn):
                        position = Vector2d(rock.position.x, rock.position.y)
                        newRock = Rock(self.stage, position, newRockType)
                        newRock.safe_timer = 15
                        self.stage.addSprite(newRock)
                        self.rockList.append(newRock)

                self.createDebris(rock)

        if self.saucer is not None:
            if self.ship and not self.ship.inHyperSpace and self.gameState == 'playing':
                if self.saucer.bulletCollision(self.ship):
                    shipHit = True

                potential_saucer_hits = self.quadtree.get_potential_intersections(self.saucer)
                if self.ship in potential_saucer_hits and self.saucer.collidesWith(self.ship):
                    shipHit = True
                    saucerHit = True

            if saucerHit:
                self.createDebris(self.saucer)
                self.killSaucer()

        if shipHit:
            self.killShip()


    def killShip(self):
        """Phá hủy tàu người chơi, kích hoạt hiệu ứng nổ, và chuyển sang trạng thái exploding."""
        stopSound("thrust")
        playSound("explode2")
        self.explodingCount = 0
        self.lives -= 1
        if (self.livesList):
            ship = self.livesList.pop()
            self.stage.removeSprite(ship)

        self.stage.removeSprite(self.ship)
        self.stage.removeSprite(self.ship.thrustJet)
        self.gameState = 'exploding'
        self.ship.explode()

    def killSaucer(self):
        """Phá hủy đĩa bay đang hoạt động, dừng âm thanh, và xóa tham chiếu."""
        stopSound("lsaucer")
        stopSound("ssaucer")
        playSound("explode2")
        self.stage.removeSprite(self.saucer)
        self.saucer = None

    def createDebris(self, sprite):
        """Spawn hạt debris tại vị trí sprite, kế thừa màu của sprite.

        Args:
            sprite: Sprite bị phá hủy dùng để tạo debris.
        """
        for _ in range(0, 25):
            position = Vector2d(sprite.position.x, sprite.position.y)
            debris = Debris(position, self.stage)
            if hasattr(sprite, 'color'):
                debris.color = sprite.color
            self.stage.addSprite(debris)

    def displayFps(self):
        """Render bộ đếm FPS hiện tại ở giữa trên màn hình."""
        font2 = pygame.font.Font('../res/Hyperspace.otf', 15)
        fpsStr = str(self.fps)+(' FPS')
        scoreText = font2.render(fpsStr, True, (255, 255, 255))
        scoreTextRect = scoreText.get_rect(
            centerx=(self.stage.width/2), centery=15)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def checkScore(self):
        """Thưởng thêm một mạng khi điểm vượt mốc 10.000 điểm."""
        if self.score > 0 and self.score > self.nextLife:
            playSound("extralife")
            self.nextLife += 10000
            self.addLife(self.lives)


if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

initSoundManager()
game = Asteroids()  
game.playGame()

