#!/usr/bin/env python3
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

# TODO
# safe area on new life
# sounds thump

# Notes:
# random.randrange returns an int
# random.uniform returns a float
# p for pause
# j for toggle showing FPS
# o for frame advance whilst paused

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

    """
    Lớp điều khiển chính xử lý vòng lặp Game.
    
    Attributes:
        explodingTtl (int): Thời gian hiển thị Tàu bị phá hủy trước khi trừ mạng và hồi sinh.
        stage (Stage): Đối tượng khung màn hình quản lý.
        paused (bool): Cờ chặn vòng lặp để Tạm dừng game.
        showingFPS (bool): Bật/Tắt hiển thị FPS.
        frameAdvance (bool): Cờ gỡ lỗi cho phép tua Game từng Frame một (để Debug).
        gameState (str): Trạng thái Màn chơi ("attract_mode" chờ ở Menu, "playing" đang chơi).
        rockList (list): Cấu trúc mảng chứa toàn bộ Thiên thạch.
        saucer (Saucer): Đối tượng Đĩa bay địch.
        secondsCount (int): Đồng hồ đếm Tick của Game.
        score (int): Hệ thống tính điểm.
        ship (Ship): Tàu vũ trụ - nhân vật do người chơi điều khiển.
        lives (int): Số Mạng còn lại của tàu.
    """
    explodingTtl = 180

    def __init__(self):
        """Hàm khởi tạo thiết lập các thuộc tính ban đầu cho đối tượng."""
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
        self.ship = None
        self.lives = 0

    def initialiseGame(self):
        """Thiết lập lại giá trị để bắt đầu một Màn chơi/Lượt chơi mới."""
        self.gameState = 'playing'
        [self.stage.removeSprite(sprite)
         for sprite in self.rockList]  # clear old rocks
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
        """Tạo và tái lập lại Tàu vũ trụ của người chơi trên màn hình."""
        if self.ship:
            [self.stage.spriteList.remove(debris)
             for debris in self.ship.shipDebrisList]
        self.ship = Ship(self.stage)
        self.stage.addSprite(self.ship.thrustJet)
        self.stage.addSprite(self.ship)

    def createLivesList(self):
        """Khởi tạo danh sách mạng sống (Giao diện góc trái)."""
        self.lives += 1
        self.livesList = []
        for i in range(1, self.startLives):
            self.addLife(i)

    def addLife(self, lifeNumber):
        """Thêm một mạng cho Tàu Vũ Trụ."""
        self.lives += 1
        ship = Ship(self.stage)
        self.stage.addSprite(ship)
        ship.position.x = self.stage.width - \
            (lifeNumber * ship.rect.width) - 10
        ship.position.y = 0 + ship.rect.height
        self.livesList.append(ship)

    def createRocks(self, numRocks):
        """Sinh ra N số lượng Thiên thạch to ban đầu với vận tốc ngẫu nhiên."""
        for _ in range(0, numRocks):
            position = Vector2d(random.randrange(-10, 10),
                                random.randrange(-10, 10))

            newRock = Rock(self.stage, position, Rock.largeRockType)
            self.stage.addSprite(newRock)
            self.rockList.append(newRock)

    def playGame(self):

        """Vòng lặp trò chơi (Main Game Loop) chạy ở 60 FPS."""
        clock = pygame.time.Clock()

        frameCount = 0.0
        timePassed = 0.0
        self.fps = 0.0
        # Main loop
        while True:

            # calculate fps
            timePassed += clock.tick(60)
            frameCount += 1
            if frameCount % 10 == 0:  # every 10 frames
                # nearest integer
                self.fps = round((frameCount / (timePassed / 1000.0)))
                # reset counter
                timePassed = 0
                frameCount = 0

            self.secondsCount += 1

            self.input(pygame.event.get())

            # pause
            if self.paused and not self.frameAdvance:
                self.displayPaused()
                continue

            self.stage.screen.fill((10, 10, 10))
            self.stage.moveSprites()
            self.stage.drawSprites()
            self.doSaucerLogic()
            self.displayScore()
            if self.showingFPS:
                self.displayFps()  # for debug
            self.checkScore()

            # Process keys
            if self.gameState == 'playing':
                self.playing()
            elif self.gameState == 'exploding':
                self.exploding()
            else:
                self.displayText()

            # Double buffer draw
            pygame.display.flip()

    def playing(self):
        """Xử lý các logic, bắt phím, và tương tác khi Game đang ở trạng thái PLAYING."""
        if self.lives == 0:
            self.gameState = 'attract_mode'
        else:
            self.processKeys()
            self.checkCollisions()
            if len(self.rockList) == 0:
                self.levelUp()

    def doSaucerLogic(self):
        """Xử lý logic tự hành và bắn súng của Tàu địch (UFO)."""
        if self.saucer is not None:
            if self.saucer.laps >= 2:
                self.killSaucer()

        # Create a saucer
        if self.secondsCount % 2000 == 0 and self.saucer is None:
            randVal = random.randrange(0, 10)
            if randVal <= 3:
                self.saucer = Saucer(
                    self.stage, Saucer.smallSaucerType, self.ship)
            else:
                self.saucer = Saucer(
                    self.stage, Saucer.largeSaucerType, self.ship)
            self.stage.addSprite(self.saucer)

    def exploding(self):
        """Xử lý chuỗi thời gian khi tàu đang chìm trong vụ nổ chờ hồi sinh."""
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
        """Tăng độ khó (Sinh thêm thiên thạch) sau khi đã tiêu diệt toàn bộ thiên thạch hiện tại."""
        self.numRocks += 1
        self.createRocks(self.numRocks)

    # move this kack somewhere else!
    def displayText(self):
        """Vẽ các đoạn text trên màn hình Menu."""
        font1 = pygame.font.Font('../res/Hyperspace.otf', 50)
        font2 = pygame.font.Font('../res/Hyperspace.otf', 20)
        font3 = pygame.font.Font('../res/Hyperspace.otf', 30)

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

    def displayScore(self):
        """Vẽ điểm số (Score) của người chơi hiện tại."""
        font1 = pygame.font.Font('../res/Hyperspace.otf', 30)
        scoreStr = str("%02d" % self.score)
        scoreText = font1.render(scoreStr, True, (200, 200, 200))
        scoreTextRect = scoreText.get_rect(centerx=100, centery=45)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def displayPaused(self):
        """Vẽ chữ Paused nếu game bị dừng."""
        if self.paused:
            font1 = pygame.font.Font('../res/Hyperspace.otf', 30)
            pausedText = font1.render("Paused", True, (255, 255, 255))
            textRect = pausedText.get_rect(
                centerx=self.stage.width/2, centery=self.stage.height/2)
            self.stage.screen.blit(pausedText, textRect)
            pygame.display.update()

    # Should move the ship controls into the ship class
    def input(self, events):
        """Quản lý sự kiện bàn phím."""
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
                    # Start a new game
                    if event.key == K_SPACE:
                        self.initialiseGame()

                if event.key == K_p:
                    if self.paused:  # (is True)
                        self.paused = False
                    else:
                        self.paused = True

                if event.key == K_j:
                    if self.showingFPS:  # (is True)
                        self.showingFPS = False
                    else:
                        self.showingFPS = True

                if event.key == K_F11:
                    pygame.display.toggle_fullscreen()

                # if event.key == K_k:
                    # self.killShip()
            elif event.type == KEYUP:
                if event.key == K_o:
                    self.frameAdvance = True

    def processKeys(self):
        """Xử lý luồng lực đẩy (Thrust), ấn trái phải quay Tàu."""
        key = pygame.key.get_pressed()

        if key[K_LEFT] or key[K_z]:
            self.ship.rotateLeft()
        elif key[K_RIGHT] or key[K_x]:
            self.ship.rotateRight()

        if key[K_UP] or key[K_n]:
            self.ship.increaseThrust()
            self.ship.thrustJet.accelerating = True
        else:
            self.ship.thrustJet.accelerating = False

    # Check for ship hitting the rocks etc.

    def checkCollisions(self):

        # Ship bullet hit rock?
        """Tiến hành kiểm tra tất cả các Va Chạm của Game thông qua truy cập QuadTree."""
        newRocks = []
        shipHit, saucerHit = False, False

        # DSA: QuadTree Build
        bounds = pygame.Rect(0, 0, self.stage.width, self.stage.height)
        self.quadtree = QuadTree(bounds, 4)
        
        all_objects = self.rockList.copy()
        if self.ship and not self.ship.inHyperSpace:
            all_objects.append(self.ship)
        if self.saucer:
            all_objects.append(self.saucer)
            
        for obj in all_objects:
            self.quadtree.insert(obj)

        # Rocks
        for rock in self.rockList:
            rockHit = False
            
            # DSA: QuadTree Query
            potential_hits = self.quadtree.get_potential_intersections(rock)

            if not self.ship.inHyperSpace and self.ship in potential_hits:
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

                if self.ship.bulletCollision(self.saucer):
                    saucerHit = True
                    self.score += self.saucer.scoreValue

            if self.ship.bulletCollision(rock):
                rockHit = True

            if rockHit:
                self.rockList.remove(rock)
                self.stage.spriteList.remove(rock)

                if rock.rockType == Rock.largeRockType:
                    playSound("explode1")
                    newRockType = Rock.mediumRockType
                    self.score += 50
                elif rock.rockType == Rock.mediumRockType:
                    playSound("explode2")
                    newRockType = Rock.smallRockType
                    self.score += 100
                else:
                    playSound("explode3")
                    self.score += 200

                if rock.rockType != Rock.smallRockType:
                    # new rocks
                    for _ in range(0, 2):
                        position = Vector2d(rock.position.x, rock.position.y)
                        newRock = Rock(self.stage, position, newRockType)
                        self.stage.addSprite(newRock)
                        self.rockList.append(newRock)

                self.createDebris(rock)

        # Saucer bullets
        if self.saucer is not None:
            if not self.ship.inHyperSpace:
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

            # comment in to pause on collision
            #self.paused = True

    def killShip(self):
        """Tiêu diệt Tàu Vũ Trụ, sinh hạt debris nổ tung và hiển thị âm thanh."""
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
        """Tiêu diệt Tàu Lạ (UFO), cộng điểm người chơi."""
        stopSound("lsaucer")
        stopSound("ssaucer")
        playSound("explode2")
        self.stage.removeSprite(self.saucer)
        self.saucer = None

    def createDebris(self, sprite):
        """Tạo các hạt bụi/mảnh vụn khi vỡ thực thể."""
        for _ in range(0, 25):
            position = Vector2d(sprite.position.x, sprite.position.y)
            debris = Debris(position, self.stage)
            self.stage.addSprite(debris)

    def displayFps(self):
        """Vẽ FPS (Khung hình trên giây) ở viền màn hình (DebugMode)."""
        font2 = pygame.font.Font('../res/Hyperspace.otf', 15)
        fpsStr = str(self.fps)+(' FPS')
        scoreText = font2.render(fpsStr, True, (255, 255, 255))
        scoreTextRect = scoreText.get_rect(
            centerx=(self.stage.width/2), centery=15)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def checkScore(self):
        """Xác định xem người chơi đã qua mốc để thưởng thêm 1 Mạng hay chưa."""
        if self.score > 0 and self.score > self.nextLife:
            playSound("extralife")
            self.nextLife += 10000
            self.addLife(self.lives)


# Script to run the game
if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

initSoundManager()
game = Asteroids()  # create object game from class Asteroids
game.playGame()

####
