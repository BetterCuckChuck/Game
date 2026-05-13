"""
Entry point và controller chính của game Asteroids.

Cài đặt lớp Asteroids chứa vòng lặp game chính, máy trạng thái,
pipeline phát hiện va chạm, hệ thống tính điểm, và quản lý
vòng đời thực thể.

Last Modified: 2026-05-13
"""

import pygame
import sys
import os
import random
import time
from pygame.locals import *
from util.vectorsprites import *
from ship import *
from stage import *
from enemies import *
from shooter import *
from soundManager import *
from dsa.quadtree import QuadTree
from highscores import load_scores, add_score, get_top_score, qualifies, reset_scores
from res_path import resource_path
from config import load_config, show_settings_gui

class Asteroids():
    """
    Controller chính quản lý vòng lặp game và trạng thái.

    Điều phối tất cả hệ thống con bao gồm render, xử lý input,
    phát hiện va chạm, tính điểm, và quản lý vòng đời thực thể.

    Attributes:
        explodingTtl: Thời lượng animation phá hủy tàu (frame).
        stage: Instance Stage quản lý display surface.
        paused: Game có đang tạm dừng hay không.
        showingFPS: Có hiển thị bộ đếm FPS hay không.
        frameAdvance: Cờ debug cho chế độ bước từng frame.
        gameState: Trạng thái hiện tại ('attract_mode', 'playing', 'exploding', 'game_over').
        rockList: Danh sách toàn bộ instance Rock đang hoạt động.
        saucerList: Danh sách các Saucer đang hoạt động (tối đa 3).
        secondsCount: Bộ đếm frame dùng cho các sự kiện định thời.
        score: Điểm hiện tại của người chơi.
        lastRank: Vị trí xếp hạng của lần chơi vừa kết thúc.
        ship: Instance Ship của người chơi.
        lives: Số mạng còn lại.

    Last Modified: 2026-05-13
    """
    explodingTtl = 180

    def __init__(self):
        """
        Khởi tạo game ở chế độ attract mode với cấu hình mặc định.

        Last Modified: 2026-05-13
        """
        self.stage = Stage('Atari Asteroids')
        self.paused = False
        self.debugMode = False
        self.frameAdvance = False
        self.gameState = "attract_mode"
        self.rockList = []
        self.createRocks(8)
        self.saucerList = []
        self.secondsCount = 1
        self.score = 0
        self.nextLife = 10000
        self.ship = None
        self.lives = 0
        self.useQuadTree = True
        self.collisionTime = 0.0
        self.collisionEntityCount = 0
        self.floatingTexts = []
        self.clusterRadius = 150
        self._all_objects = []
        self.quadtree = None
        self.nextDualPowerup = 5000
        self.lastRank = None
        self.playerName = ""
        self._initDispatcher()

    def initialiseGame(self):
        """
        Đặt lại toàn bộ trạng thái game và bắt đầu phiên chơi mới.

        Last Modified: 2026-05-13
        """
        self.gameState = 'playing'
        [self.stage.removeSprite(sprite)
         for sprite in self.rockList]  
        for saucer in self.saucerList[:]:
            self.killSaucer(saucer)
        cfg = load_config()
        self.startLives = cfg.get("start_lives", 5)
        self.saucerMaxCount = cfg.get("saucer_max_count", 4)
        self.createNewShip()
        self.createLivesList()
        self.score = 0
        self.rockList = []
        self.numRocks = cfg.get("start_rocks", 15)
        self.nextLife = 10000
        self.nextDualPowerup = 5000

        self.createRocks(self.numRocks)
        self.secondsCount = 1

    def createNewShip(self):
        """
        Tạo tàu người chơi mới với bất tử và cập nhật tham chiếu cho đĩa bay.

        Last Modified: 2026-05-13
        """
        if self.ship:
            [self.stage.spriteList.remove(debris)
             for debris in self.ship.shipDebrisList]
        self.ship = Ship(self.stage)
        self.ship.invincible = True
        self.ship.invincibleTimer = 180
        self.stage.addSprite(self.ship.thrustJet)
        self.stage.addSprite(self.ship)
        for saucer in self.saucerList:
            saucer.ship = self.ship

    def createLivesList(self):
        """
        Tạo các icon đếm mạng trên HUD ở góc phải trên.

        Last Modified: 2026-05-13
        """
        self.lives += 1
        self.livesList = []
        for i in range(1, self.startLives):
            self.addLife(i)

    def addLife(self, lifeNumber):
        """
        Thêm icon mạng vào HUD và tăng bộ đếm mạng.

        Args:
            lifeNumber: Vị trí thứ tự của icon mạng dùng cho layout.

        Last Modified: 2026-05-13
        """
        self.lives += 1
        ship = Ship(self.stage)
        self.stage.addSprite(ship)
        ship.position.x = self.stage.width - \
            (lifeNumber * ship.rect.width) - 10
        ship.position.y = 0 + ship.rect.height
        self.livesList.append(ship)

    def createRocks(self, numRocks):
        """
        Spawn thiên thạch lớn tại các rìa màn hình ngẫu nhiên.

        Args:
            numRocks: Số thiên thạch lớn cần spawn.

        Last Modified: 2026-05-13
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
        """
        Chạy vòng lặp game chính ở 60 FPS.

        Last Modified: 2026-05-13
        """
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
            if self.debugMode:
                self.displayFps()
                self.displayCollisionInfo()
            self._updateFloatingTexts()
            self.checkScore()

            if self.gameState == 'playing':
                self.playing()
            elif self.gameState == 'exploding':
                self.exploding()
            elif self.gameState == 'entering_name':
                self.checkCollisions()
                if self.secondsCount % 300 == 0:
                    self.createRocks(2)
                if len(self.rockList) == 0:
                    self.createRocks(8)
                self.displayNameEntry()
            elif self.gameState == 'game_over':
                self.checkCollisions()
                if self.secondsCount % 300 == 0:
                    self.createRocks(2)
                if len(self.rockList) == 0:
                    self.createRocks(8)
                self.displayGameOver()
            elif self.gameState == 'confirm_reset_score':
                self.checkCollisions()
                if self.secondsCount % 300 == 0:
                    self.createRocks(2)
                if len(self.rockList) == 0:
                    self.createRocks(8)
                self.displayGameOver(show_reset_prompt=True)
            else:
                self.checkCollisions()
                if self.secondsCount % 300 == 0:
                    self.createRocks(2)
                if len(self.rockList) == 0:
                    self.createRocks(8)
                self.displayText()

            pygame.display.flip()

    def playing(self):
        """
        Xử lý logic mỗi frame khi game đang ở trạng thái playing.

        Last Modified: 2026-05-13
        """
        if self.lives == 0:
            if qualifies(self.score):
                self.playerName = ""
                self.gameState = 'entering_name'
            else:
                self.lastRank = None
                self.gameState = 'game_over'
        else:
            self.processKeys()
            self.checkCollisions()
            
            # Tự động sinh thêm 3 thiên thạch lớn mỗi 3 giây (180 frames)
            if self.secondsCount % 180 == 0:
                self.createRocks(3)
                
            if len(self.rockList) == 0:
                self.levelUp()

    def doSaucerLogic(self):
        """
        Quản lý vòng đời đĩa bay: despawn khi đạt giới hạn lap và spawn mới theo timer (tối đa 4).

        Last Modified: 2026-05-13
        """
        for saucer in self.saucerList[:]:
            if saucer.laps >= 2:
                self.killSaucer(saucer)

        max_saucers = getattr(self, 'saucerMaxCount', 4)
        if self.secondsCount % 150 == 0 and len(self.saucerList) < max_saucers:
            randVal = random.randrange(0, 10)
            if randVal <= 2:
                newSaucer = Saucer(self.stage, Saucer.largeSaucerType, self.ship)
            elif randVal <= 6:
                newSaucer = Saucer(self.stage, Saucer.smallSaucerType, self.ship)
            else:
                newSaucer = Saucer(self.stage, Saucer.hardSaucerType, self.ship)
            self.saucerList.append(newSaucer)
            self.stage.addSprite(newSaucer)

    def exploding(self):
        """
        Xử lý animation phá hủy tàu và đếm ngược respawn.

        Last Modified: 2026-05-13
        """
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
        """
        Tăng cấp độ khó bằng cách spawn thêm thiên thạch.

        Last Modified: 2026-05-13
        """
        self.numRocks += 2
        self.createRocks(self.numRocks)

    def displayText(self):
        """
        Render màn hình tiêu đề với tên game, hướng dẫn, điểm cao nhất, và bản quyền.

        Last Modified: 2026-05-13
        """
        font1 = pygame.font.Font(resource_path('Hyperspace.otf'), 50)
        font2 = pygame.font.Font(resource_path('Hyperspace.otf'), 20)
        font3 = pygame.font.Font(resource_path('Hyperspace.otf'), 30)
        font4 = pygame.font.Font(resource_path('Hyperspace.otf'), 15)

        titleText = font1.render('Asteroids', True, (180, 180, 180))
        titleTextRect = titleText.get_rect(centerx=self.stage.width/2)
        titleTextRect.y = self.stage.height/2 - titleTextRect.height*3
        self.stage.screen.blit(titleText, titleTextRect)

        # Hiển thị điểm cao nhất mọi thời đại
        top = get_top_score()
        if top > 0:
            hs_text = font3.render(f'HIGH SCORE: {top}', True, (255, 215, 0))
            hs_rect = hs_text.get_rect(centerx=self.stage.width/2)
            hs_rect.y = titleTextRect.y + titleTextRect.height + 10
            self.stage.screen.blit(hs_text, hs_rect)

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
            "G : Burst Fire (Cone)",
            "H : Hyperspace",
            "P : Pause",
            "M : Mute/Unmute",
            "T : Settings",
            "F11 : Fullscreen",
            "Ctrl+Alt+S : Self-Destruct"
        ]
        
        start_y = instructionTextRect.y + 60
        for i, text in enumerate(controls):
            ctrl_text = font4.render(text, True, (220, 220, 220))
            ctrl_rect = ctrl_text.get_rect(centerx=self.stage.width/2)
            ctrl_rect.y = start_y + (i * 25)
            self.stage.screen.blit(ctrl_text, ctrl_rect)

    def displayNameEntry(self):
        """
        Render màn hình nhập tên khi người chơi đạt top 10.

        Hiển thị điểm số, ô nhập tên với con trỏ nhấp nháy,
        và hướng dẫn nhấn Enter để xác nhận.

        Last Modified: 2026-05-13
        """
        cx = self.stage.width / 2
        font_title = pygame.font.Font(resource_path('Hyperspace.otf'), 50)
        font_score = pygame.font.Font(resource_path('Hyperspace.otf'), 30)
        font_label = pygame.font.Font(resource_path('Hyperspace.otf'), 22)
        font_input = pygame.font.Font(resource_path('Hyperspace.otf'), 36)
        font_hint = pygame.font.Font(resource_path('Hyperspace.otf'), 16)

        # Semi-transparent overlay
        overlay = pygame.Surface((self.stage.width, self.stage.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.stage.screen.blit(overlay, (0, 0))

        # NEW HIGH SCORE title
        title = font_title.render('NEW HIGH SCORE!', True, (255, 215, 0))
        title_rect = title.get_rect(centerx=cx, y=80)
        self.stage.screen.blit(title, title_rect)

        # Score display
        sc = font_score.render(f'SCORE: {self.score}', True, (255, 255, 255))
        sc_rect = sc.get_rect(centerx=cx, y=title_rect.bottom + 20)
        self.stage.screen.blit(sc, sc_rect)

        # "Enter your name:" label
        label = font_label.render('ENTER YOUR NAME:', True, (200, 200, 200))
        label_rect = label.get_rect(centerx=cx, y=sc_rect.bottom + 40)
        self.stage.screen.blit(label, label_rect)

        # Name input field with blinking cursor
        cursor_char = '_' if (self.secondsCount // 20) % 2 == 0 else ' '
        display_name = self.playerName + cursor_char
        name_text = font_input.render(display_name, True, (100, 255, 100))
        name_rect = name_text.get_rect(centerx=cx, y=label_rect.bottom + 15)

        # Draw input box background
        box_padding = 20
        box_rect = pygame.Rect(
            name_rect.x - box_padding,
            name_rect.y - box_padding // 2,
            max(name_rect.width + box_padding * 2, 300),
            name_rect.height + box_padding
        )
        box_rect.centerx = cx
        pygame.draw.rect(self.stage.screen, (40, 40, 40), box_rect)
        pygame.draw.rect(self.stage.screen, (100, 255, 100), box_rect, 2)

        # Re-center name text inside box
        name_rect.centerx = cx
        self.stage.screen.blit(name_text, name_rect)

        # Hint text
        hint = font_hint.render('Press ENTER to confirm  |  Max 10 characters', True, (150, 150, 150))
        hint_rect = hint.get_rect(centerx=cx, y=box_rect.bottom + 15)
        self.stage.screen.blit(hint, hint_rect)

    def displayGameOver(self, show_reset_prompt=False):
        """
        Args:
            show_reset_prompt: Bật/tắt trạng thái chờ reset.

        Render màn hình game over với bảng xếp hạng top 10 và điểm hiện tại.

        Hiển thị tiêu đề GAME OVER, điểm lần chơi vừa rồi, bảng top 10
        với highlight cho vị trí vừa đạt được, và lời nhắc nhấn SPACE.

        Last Modified: 2026-05-13
        """
        cx = self.stage.width / 2
        font_title = pygame.font.Font(resource_path('Hyperspace.otf'), 50)
        font_score = pygame.font.Font(resource_path('Hyperspace.otf'), 30)
        font_entry = pygame.font.Font(resource_path('Hyperspace.otf'), 18)
        font_prompt = pygame.font.Font(resource_path('Hyperspace.otf'), 24)
        font_header = pygame.font.Font(resource_path('Hyperspace.otf'), 22)

        # Semi-transparent overlay
        overlay = pygame.Surface((self.stage.width, self.stage.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.stage.screen.blit(overlay, (0, 0))

        # GAME OVER title
        go_text = font_title.render('GAME OVER', True, (255, 60, 60))
        go_rect = go_text.get_rect(centerx=cx, y=40)
        self.stage.screen.blit(go_text, go_rect)

        # Current score
        sc_text = font_score.render(f'YOUR SCORE: {self.score}', True, (255, 255, 255))
        sc_rect = sc_text.get_rect(centerx=cx, y=go_rect.bottom + 15)
        self.stage.screen.blit(sc_text, sc_rect)

        # Rank info
        if self.lastRank is not None:
            rank_color = (255, 215, 0) if self.lastRank <= 3 else (100, 255, 100)
            rank_text = font_header.render(
                f'NEW HIGH SCORE! RANK #{self.lastRank}', True, rank_color)
        else:
            rank_text = font_header.render(
                'Did not make the top 10', True, (180, 180, 180))
        rank_rect = rank_text.get_rect(centerx=cx, y=sc_rect.bottom + 8)
        self.stage.screen.blit(rank_text, rank_rect)

        # Top 10 header
        header = font_header.render('--- TOP 10 ---', True, (255, 215, 0))
        header_rect = header.get_rect(centerx=cx, y=rank_rect.bottom + 20)
        self.stage.screen.blit(header, header_rect)

        # Top 10 entries
        scores = load_scores()
        table_y = header_rect.bottom + 10
        row_height = 28

        for i in range(10):
            rank_num = i + 1
            if i < len(scores):
                entry = scores[i]
                entry_str = f'{rank_num:>2}.  {entry["name"]:<10s}  {entry["score"]:>8}'
            else:
                entry_str = f'{rank_num:>2}.  {"---":<10s}  {"---":>8}'

            # Highlight the player's rank
            if self.lastRank is not None and rank_num == self.lastRank:
                color = (255, 255, 100)
                entry_str += '  <-- YOU'
            elif rank_num <= 3:
                color = (255, 215, 0)
            else:
                color = (200, 200, 200)

            entry_text = font_entry.render(entry_str, True, color)
            entry_rect = entry_text.get_rect(centerx=cx, y=table_y + i * row_height)
            self.stage.screen.blit(entry_text, entry_rect)

        # Blinking prompt
        if show_reset_prompt:
            prompt = font_prompt.render('Are you sure? (Y/Enter to reset, other to cancel)', True, (255, 100, 100))
            prompt_rect = prompt.get_rect(centerx=cx, y=table_y + 10 * row_height + 25)
            self.stage.screen.blit(prompt, prompt_rect)
        elif (self.secondsCount // 30) % 2 == 0:
            prompt = font_prompt.render('Press SPACE to Play Again', True, (200, 200, 200))
            prompt_rect = prompt.get_rect(
                centerx=cx, y=table_y + 10 * row_height + 25)
            self.stage.screen.blit(prompt, prompt_rect)
            
            menu_prompt = font_entry.render('Press M for Main Menu', True, (150, 150, 150))
            menu_rect = menu_prompt.get_rect(
                centerx=cx, y=prompt_rect.bottom + 15)
            self.stage.screen.blit(menu_prompt, menu_rect)

    def displayScore(self):
        """
        Render điểm số hiện tại ở góc trái trên màn hình.

        Last Modified: 2026-05-13
        """
        font1 = pygame.font.Font(resource_path('Hyperspace.otf'), 30)
        scoreStr = str("%02d" % self.score)
        scoreText = font1.render(scoreStr, True, (200, 200, 200))
        scoreTextRect = scoreText.get_rect(centerx=100, centery=45)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def displayPaused(self):
        """
        Render overlay tạm dừng khi game bị pause.

        Last Modified: 2026-05-13
        """
        if self.paused:
            font1 = pygame.font.Font(resource_path('Hyperspace.otf'), 30)
            pausedText = font1.render("Paused", True, (255, 255, 255))
            textRect = pausedText.get_rect(
                centerx=self.stage.width/2, centery=self.stage.height/2)
            self.stage.screen.blit(pausedText, textRect)
            pygame.display.update()

    def input(self, events):
        """
        Xử lý các sự kiện input pygame cho điều khiển game.

        Args:
            events: Danh sách sự kiện pygame từ frame hiện tại.

        Last Modified: 2026-05-13
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
                    elif event.key == K_g:
                        self.ship.fireBurst()
                    elif event.key == K_h:
                        self.ship.enterHyperSpace()
                    elif (event.key == K_s
                          and event.mod & KMOD_CTRL
                          and event.mod & KMOD_ALT):
                        self.lives = 1
                        self.killShip()
                elif self.gameState == 'entering_name':
                    if event.key == K_RETURN:
                        name = self.playerName.strip() or "PLAYER"
                        self.lastRank = add_score(self.score, name)
                        self.gameState = 'game_over'
                    elif event.key == K_BACKSPACE:
                        self.playerName = self.playerName[:-1]
                    elif len(self.playerName) < 10 and event.unicode.isprintable() and event.unicode:
                        self.playerName += event.unicode.upper()
                elif self.gameState == 'confirm_reset_score':
                    if event.key in (K_y, K_RETURN):
                        reset_scores()
                        self.lastRank = None
                        self.gameState = 'game_over'
                    elif not (event.mod & KMOD_CTRL or event.mod & KMOD_ALT or event.mod & KMOD_SHIFT):
                        self.gameState = 'game_over'
                elif self.gameState in ('attract_mode', 'game_over'):
                    if event.key == K_SPACE:
                        self.initialiseGame()
                    elif self.gameState == 'attract_mode' and event.key == K_t:
                        show_settings_gui()
                    elif self.gameState == 'game_over' and (event.key == K_r and event.mod & KMOD_CTRL and event.mod & KMOD_ALT):
                        self.gameState = 'confirm_reset_score'

                if self.gameState != 'entering_name':
                    if event.key == K_p:
                        self.paused = not self.paused

                    if event.key == K_m:
                        if self.gameState == 'game_over':
                            self.gameState = 'attract_mode'
                        else:
                            toggleMute()

                    if event.key == K_F11:
                        pygame.display.toggle_fullscreen()

                    # Debug mode: Ctrl+Alt+Q to toggle
                    if (event.key == K_q
                            and event.mod & KMOD_CTRL
                            and event.mod & KMOD_ALT):
                        self.debugMode = not self.debugMode
                elif self.debugMode and event.key == K_q:
                    self.useQuadTree = not self.useQuadTree

            elif event.type == KEYUP:
                if self.debugMode and event.key == K_o:
                    self.frameAdvance = True

    def processKeys(self):
        """
        Đọc trạng thái phím giữ cho điều khiển liên tục (đẩy, xoay).

        Last Modified: 2026-05-13
        """
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
        """
        Phát hiện va chạm event-based và đo thời gian.

        Last Modified: 2026-05-13
        """
        t0 = time.perf_counter()

        ship = self.ship if (self.ship and not self.ship.inHyperSpace
                             and not self.ship.invincible) else None

        all_bullets = []
        if self.ship:
            all_bullets.extend(self.ship.bullets)
        for saucer in self.saucerList:
            all_bullets.extend(saucer.bullets)

        self._shipHit = False
        self._hitSaucers = set()
        self._destroyedRocks = set()

        for rock in self.rockList:
            if getattr(rock, 'safe_timer', 0) > 0:
                rock.safe_timer -= 1

        self.quadtree, self._all_objects = self.dispatcher.detect_and_dispatch(
            self.rockList[:], ship, self.saucerList[:], all_bullets,
            use_quadtree=self.useQuadTree,
            classify_fn=self._classifyCollision
        )

        for rock in list(self._destroyedRocks):
            if rock in self.rockList:
                self._destroyRock(rock)

        for saucer in list(self._hitSaucers):
            if saucer in self.saucerList:
                self.createDebris(saucer)
                self.killSaucer(saucer)

        if self._shipHit:
            self.killShip()

        self.collisionTime = (time.perf_counter() - t0) * 1000
        self.collisionEntityCount = len(self.rockList) + len(self.saucerList) + len(all_bullets) + (1 if ship else 0)

    def _classifyCollision(self, a, b):
        """
        Args:
            a: Thực thể A.
            b: Thực thể B.

        Phân loại cặp va chạm theo kiểu thực thể.

        Returns:
            Hằng số kiểu va chạm, hoặc None nếu không hợp lệ.

        Last Modified: 2026-05-13
        """
        from dsa.collision import (ROCK_ROCK, BULLET_ROCK, BULLET_SAUCER,
                                    BULLET_SHIP, ROCK_SHIP, ROCK_SAUCER,
                                    SAUCER_SHIP)

        a_rock = isinstance(a, Rock)
        b_rock = isinstance(b, Rock)
        a_bullet = isinstance(a, Bullet)
        b_bullet = isinstance(b, Bullet)
        a_saucer = isinstance(a, Saucer)
        b_saucer = isinstance(b, Saucer)
        a_ship = isinstance(a, Ship)
        b_ship = isinstance(b, Ship)

        if a_rock and b_rock:
            return ROCK_ROCK
        if (a_bullet and b_rock) or (b_bullet and a_rock):
            bullet = a if a_bullet else b
            if bullet.ttl > 0:
                return BULLET_ROCK
        if (a_bullet and b_saucer) or (b_bullet and a_saucer):
            bullet = a if a_bullet else b
            if isinstance(bullet.shooter, Ship) and bullet.ttl > 0:
                return BULLET_SAUCER
        if (a_bullet and b_ship) or (b_bullet and a_ship):
            bullet = a if a_bullet else b
            if isinstance(bullet.shooter, Saucer) and bullet.ttl > 0:
                return BULLET_SHIP
        if (a_rock and b_ship) or (b_rock and a_ship):
            return ROCK_SHIP
        if (a_rock and b_saucer) or (b_rock and a_saucer):
            return ROCK_SAUCER
        if (a_saucer and b_ship) or (b_saucer and a_ship):
            return SAUCER_SHIP
        return None

    def _initDispatcher(self):
        """
        Khởi tạo CollisionDispatcher và đăng ký handler.

        Last Modified: 2026-05-13
        """
        from dsa.collision import (CollisionDispatcher, ROCK_ROCK,
                                    BULLET_ROCK, BULLET_SAUCER,
                                    BULLET_SHIP, ROCK_SHIP,
                                    ROCK_SAUCER, SAUCER_SHIP)
        self.dispatcher = CollisionDispatcher(self.stage.width, self.stage.height)
        self.dispatcher.register(ROCK_ROCK, self._onRockRock)
        self.dispatcher.register(BULLET_ROCK, self._onBulletRock)
        self.dispatcher.register(BULLET_SAUCER, self._onBulletSaucer)
        self.dispatcher.register(BULLET_SHIP, self._onBulletShip)
        self.dispatcher.register(ROCK_SHIP, self._onRockShip)
        self.dispatcher.register(ROCK_SAUCER, self._onRockSaucer)
        self.dispatcher.register(SAUCER_SHIP, self._onSaucerShip)

    def _onRockRock(self, event):
        """
        Args:
            event: Sự kiện va chạm chứa entity_a và entity_b.

        Xử lý va chạm thiên thạch - thiên thạch. Bỏ qua nếu có thiên thạch siêu nhỏ.

        Last Modified: 2026-05-13
        """
        rock, other = event.entity_a, event.entity_b
        if rock.rockType == Rock.tinyRockType or other.rockType == Rock.tinyRockType:
            return
        if getattr(rock, 'safe_timer', 0) > 0 or getattr(other, 'safe_timer', 0) > 0:
            return
        p = rock.checkPolygonCollision(other)
        if p is None:
            return

        v1_sq = rock.heading.x**2 + rock.heading.y**2
        v2_sq = other.heading.x**2 + other.heading.y**2
        rock_survives, other_survives = False, False
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

        if not other_survives and other not in self._destroyedRocks:
            if other in self.rockList:
                self.rockList.remove(other)
                if other in self.stage.spriteList:
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
            self._destroyedRocks.add(rock)

    def _onBulletRock(self, event):
        """
        Args:
            event: Sự kiện va chạm.

        Xử lý đạn trúng thiên thạch.

        Last Modified: 2026-05-13
        """
        bullet = event.entity_a if isinstance(event.entity_a, Bullet) else event.entity_b
        rock = event.entity_a if isinstance(event.entity_a, Rock) else event.entity_b
        bullet.ttl = 0
        rock._killed_by_player = isinstance(bullet.shooter, Ship)
        self._destroyedRocks.add(rock)

    def _onBulletSaucer(self, event):
        """
        Args:
            event: Sự kiện va chạm.

        Xử lý đạn người chơi trúng đĩa bay.

        Last Modified: 2026-05-13
        """
        bullet = event.entity_a if isinstance(event.entity_a, Bullet) else event.entity_b
        saucer = event.entity_a if isinstance(event.entity_a, Saucer) else event.entity_b
        bullet.ttl = 0
        self._hitSaucers.add(saucer)
        if self.gameState == 'playing':
            multiplier = self._getClusterMultiplier(saucer)
            bonus = int(saucer.scoreValue * multiplier)
            self.score += bonus
            if multiplier > 1.0:
                self._spawnFloatingText(saucer.position, bonus, multiplier)

    def _onBulletShip(self, event):
        """
        Args:
            event: Sự kiện va chạm.

        Xử lý đạn đĩa bay trúng tàu người chơi.

        Last Modified: 2026-05-13
        """
        bullet = event.entity_a if isinstance(event.entity_a, Bullet) else event.entity_b
        bullet.ttl = 0
        if self.gameState == 'playing':
            self._shipHit = True

    def _onRockShip(self, event):
        """
        Args:
            event: Sự kiện va chạm.

        Xử lý va chạm thiên thạch - tàu. Tiny rock chỉ bị phá hủy, không hại tàu.

        Last Modified: 2026-05-13
        """
        rock = event.entity_a if isinstance(event.entity_a, Rock) else event.entity_b
        ship = event.entity_a if isinstance(event.entity_a, Ship) else event.entity_b
        p = rock.checkPolygonCollision(ship)
        if p is not None and self.gameState == 'playing':
            rock._killed_by_player = True
            self._destroyedRocks.add(rock)
            if rock.rockType != Rock.tinyRockType:
                self._shipHit = True

    def _onRockSaucer(self, event):
        """
        Args:
            event: Sự kiện va chạm.

        Xử lý va chạm thiên thạch - đĩa bay. Tiny rock chỉ bị phá hủy, không hại đĩa bay.

        Last Modified: 2026-05-13
        """
        rock = event.entity_a if isinstance(event.entity_a, Rock) else event.entity_b
        saucer = event.entity_a if isinstance(event.entity_a, Saucer) else event.entity_b
        self._destroyedRocks.add(rock)
        if rock.rockType != Rock.tinyRockType:
            self._hitSaucers.add(saucer)

    def _onSaucerShip(self, event):
        """
        Args:
            event: Sự kiện va chạm.

        Xử lý va chạm đĩa bay - tàu.

        Last Modified: 2026-05-13
        """
        saucer = event.entity_a if isinstance(event.entity_a, Saucer) else event.entity_b
        if self.gameState == 'playing':
            self._shipHit = True
            self._hitSaucers.add(saucer)

    def _destroyRock(self, rock):
        """
        Args:
            rock: Thiên thạch cần phá hủy.

        Phá hủy thiên thạch, tính điểm với cluster multiplier, và spawn mảnh.

        Last Modified: 2026-05-13
        """
        if rock not in self.rockList:
            return
        self.rockList.remove(rock)
        if rock in self.stage.spriteList:
            self.stage.spriteList.remove(rock)

        if rock.rockType == Rock.largeRockType:
            playSound("explode1")
            newRockType = Rock.mediumRockType
            baseScore = 200
        elif rock.rockType == Rock.mediumRockType:
            playSound("explode2")
            newRockType = Rock.smallRockType
            baseScore = 100
        elif rock.rockType == Rock.smallRockType:
            playSound("explode3")
            newRockType = Rock.tinyRockType
            baseScore = 50
        else:
            playSound("explode3")
            baseScore = 20

        if self.gameState == 'playing' and getattr(rock, '_killed_by_player', False):
            multiplier = self._getClusterMultiplier(rock)
            bonus = int(baseScore * multiplier)
            self.score += bonus
            if multiplier > 1.0:
                self._spawnFloatingText(rock.position, bonus, multiplier)

        if rock.rockType == Rock.smallRockType:
            position = Vector2d(rock.position.x, rock.position.y)
            newRock = Rock(self.stage, position, Rock.tinyRockType)
            newRock.safe_timer = 15
            self.stage.addSprite(newRock)
            self.rockList.append(newRock)
        elif rock.rockType != Rock.tinyRockType:
            num_spawn = 1 if getattr(rock, 'spawn_single_fragment', False) else 2
            for _ in range(num_spawn):
                position = Vector2d(rock.position.x, rock.position.y)
                newRock = Rock(self.stage, position, newRockType)
                newRock.safe_timer = 15
                self.stage.addSprite(newRock)
                self.rockList.append(newRock)

        self.createDebris(rock)

    def _getClusterMultiplier(self, target):
        """
        Args:
            target: Mục tiêu để tính toán.
        Returns:
            Hệ số nhân.

        Tính hệ số nhân điểm dựa trên mật độ cụm (dùng QuadTree hoặc brute-force).

        Last Modified: 2026-05-13
        """
        cx, cy = target.position.x, target.position.y
        r = self.clusterRadius
        query_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)

        if self.useQuadTree and self.quadtree:
            nearby = []
            self.quadtree.query(query_rect, nearby)
        else:
            nearby = [obj for obj in self._all_objects
                      if query_rect.collidepoint(obj.position.x, obj.position.y)]

        count = sum(1 for obj in nearby if obj is not target
                    and (obj.position.x - cx)**2 + (obj.position.y - cy)**2 <= r * r)

        if count >= 8: return 3.0
        elif count >= 5: return 2.5
        elif count >= 3: return 2.0
        elif count >= 1: return 1.5
        return 1.0

    def _spawnFloatingText(self, position, score, multiplier, text=None, color=None):
        """
        Args:
            position: Vị trí xuất hiện.
            score: Điểm số.
            multiplier: Hệ số nhân.
            text: Ký tự tùy chọn.
            color: Màu sắc tùy chọn.

        Tạo text điểm nổi tại vị trí phá hủy.

        Last Modified: 2026-05-13
        """
        if text is None:
            text = f"+{score} x{multiplier:.1f}"
        if color is None:
            color = (255, 200, 50)
        self.floatingTexts.append({
            'x': position.x, 'y': position.y,
            'text': text, 'color': color,
            'ttl': 90, 'max_ttl': 90
        })

    def _updateFloatingTexts(self):
        """
        Cập nhật và render các floating text điểm.

        Last Modified: 2026-05-13
        """
        font = pygame.font.Font(resource_path('Hyperspace.otf'), 16)
        for ft in self.floatingTexts[:]:
            ft['ttl'] -= 1
            ft['y'] -= 0.8
            if ft['ttl'] <= 0:
                self.floatingTexts.remove(ft)
                continue
            alpha_ratio = ft['ttl'] / ft['max_ttl']
            base_r, base_g, base_b = ft.get('color', (255, 200, 50))
            color = (int(base_r * alpha_ratio),
                     int(base_g * alpha_ratio),
                     int(base_b * alpha_ratio))
            text_surf = font.render(ft['text'], True, color)
            rect = text_surf.get_rect(centerx=ft['x'], centery=ft['y'])
            self.stage.screen.blit(text_surf, rect)

    def displayCollisionInfo(self):
        """
        Render thông tin phương pháp va chạm, số thực thể, và thời gian xử lý.

        Last Modified: 2026-05-13
        """
        font = pygame.font.Font(resource_path('Hyperspace.otf'), 14)
        method = "QuadTree" if self.useQuadTree else "Brute-Force"
        color = (100, 255, 100) if self.useQuadTree else (255, 200, 100)
        line1 = font.render(
            f"Collision: {method}  |  Entities: {self.collisionEntityCount}  |  Time: {self.collisionTime:.2f}ms",
            True, color)
        rect1 = line1.get_rect(centerx=self.stage.width / 2, centery=self.stage.height - 20)
        self.stage.screen.blit(line1, rect1)
        hint = font.render("[Q] Toggle Method", True, (120, 120, 120))
        rect2 = hint.get_rect(centerx=self.stage.width / 2, centery=self.stage.height - 40)
        self.stage.screen.blit(hint, rect2)

    def killShip(self):
        """
        Phá hủy tàu người chơi, kích hoạt hiệu ứng nổ, và chuyển sang trạng thái exploding.

        Last Modified: 2026-05-13
        """
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

    def killSaucer(self, saucer):
        """
        Phá hủy một đĩa bay, dừng âm thanh, và gỡ khỏi danh sách.

        Args:
            saucer: Instance Saucer cần phá hủy.

        Last Modified: 2026-05-13
        """
        stopSound("lsaucer")
        stopSound("ssaucer")
        playSound("explode2")
        self.stage.removeSprite(saucer)
        if saucer in self.saucerList:
            self.saucerList.remove(saucer)

    def createDebris(self, sprite):
        """
        Spawn hạt debris tại vị trí sprite, kế thừa màu của sprite.

        Args:
            sprite: Sprite bị phá hủy dùng để tạo debris.

        Last Modified: 2026-05-13
        """
        for _ in range(0, 25):
            position = Vector2d(sprite.position.x, sprite.position.y)
            debris = Debris(position, self.stage)
            if hasattr(sprite, 'color'):
                debris.color = sprite.color
            self.stage.addSprite(debris)

    def displayFps(self):
        """
        Render bộ đếm FPS hiện tại ở giữa trên màn hình.

        Last Modified: 2026-05-13
        """
        font2 = pygame.font.Font(resource_path('Hyperspace.otf'), 15)
        fpsStr = str(self.fps)+(' FPS')
        scoreText = font2.render(fpsStr, True, (255, 255, 255))
        scoreTextRect = scoreText.get_rect(
            centerx=(self.stage.width/2), centery=15)
        self.stage.screen.blit(scoreText, scoreTextRect)

    def checkScore(self):
        """
        Thưởng thêm mạng mỗi 10k điểm, nâng cấp đạn (Triple, Quad,...) mỗi 5k điểm.

        Last Modified: 2026-05-13
        """
        if self.score > 0 and self.score > self.nextLife:
            playSound("extralife")
            self.nextLife += 10000
            self.addLife(self.lives)

        if self.ship and self.score > 0 and self.score >= self.nextDualPowerup:
            # Nếu đang bắn đơn (level 1), nhảy vọt lên Triple (level 3)
            # Nếu đã có powerup, cộng dồn thêm 1 tia đạn (level 4, 5,...)
            if self.ship.fireLevel == 1:
                self.ship.fireLevel = 3
            else:
                self.ship.fireLevel += 1
                
            self.ship.powerupTimer = 300 # Reset timer về 5s
            self.nextDualPowerup += 5000
            
            # Tạo tên gọi tương ứng với số đạn
            level_names = {
                3: "TRIPLE", 4: "QUAD", 5: "PENTA", 
                6: "HEXA", 7: "HEPTA", 8: "OCTA", 
                9: "NONA", 10: "DECA"
            }
            p_name = level_names.get(self.ship.fireLevel, f"{self.ship.fireLevel}-WAY")
            
            self._spawnFloatingText(
                self.ship.position, 0, 0,
                text=f"{p_name} FIRE!", color=(50, 200, 255))


if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

initSoundManager()
game = Asteroids()  
game.playGame()

