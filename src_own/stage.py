"""
Module quản lý Stage cho game Asteroids.

Xử lý pygame display surface, render sprite, cập nhật di chuyển,
và screen wrapping cho toàn bộ thực thể trong game.

Last Modified: 2026-05-06
"""

import pygame
import sys
import os
from pygame.locals import *


class Stage:
    """
    Quản lý hiển thị và cập nhật toàn bộ sprite trên màn hình.

    Sở hữu pygame display surface và danh sách sprite chính. Xử lý
    render, cập nhật di chuyển, và screen wrapping dạng toroidal.

    Attributes:
        screen: Pygame display surface.
        spriteList: Danh sách toàn bộ sprite đang hoạt động.
        width: Độ phân giải ngang tính bằng pixel.
        height: Độ phân giải dọc tính bằng pixel.
        showBoundingBoxes: Cờ debug hiển thị viền AABB.

    Last Modified: 2026-05-06
    """

    def __init__(self, caption, dimensions=None):
        """
        Khởi tạo display và hệ thống quản lý sprite.

        Args:
            caption: Tiêu đề cửa sổ.
            dimensions: Độ phân giải dạng (width, height). Mặc định dùng
                độ phân giải gốc của màn hình chính.

        Last Modified: 2026-05-06
        """
        pygame.init()

        if dimensions == None:
            dimensions = pygame.display.list_modes()[0]

        pygame.display.set_mode(dimensions, FULLSCREEN)
        pygame.mouse.set_visible(False)


        pygame.display.set_caption(caption)
        self.screen = pygame.display.get_surface()
        self.spriteList = []
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.showBoundingBoxes = False

    def addSprite(self, sprite):
        """
        Đăng ký sprite để render và gán bounding rect ban đầu.

        Args:
            sprite: Instance VectorSprite cần thêm.

        Last Modified: 2026-05-06
        """
        self.spriteList.append(sprite)
        sprite.rect = pygame.draw.aalines(
            self.screen, sprite.color, True, sprite.draw())

    def removeSprite(self, sprite):
        """
        Gỡ sprite khỏi danh sách render.

        Args:
            sprite: Instance VectorSprite cần gỡ.

        Last Modified: 2026-05-06
        """
        self.spriteList.remove(sprite)

    def drawSprites(self):
        """
        Render toàn bộ sprite đã đăng ký, tùy chọn vẽ bounding box.

        Last Modified: 2026-05-06
        """
        for sprite in self.spriteList:
            sprite.rect = pygame.draw.aalines(
                self.screen, sprite.color, True, sprite.draw())
            if self.showBoundingBoxes == True:
                pygame.draw.rect(self.screen, (255, 255, 255),
                                 sprite.rect, 1)

    def moveSprites(self):
        """
        Cập nhật vị trí toàn bộ sprite và áp dụng screen wrapping.

        Last Modified: 2026-05-06
        """
        for sprite in self.spriteList:
            sprite.move()

            if sprite.position.x < 0:
                sprite.position.x = self.width

            if sprite.position.x > self.width:
                sprite.position.x = 0

            if sprite.position.y < 0:
                sprite.position.y = self.height

            if sprite.position.y > self.height:
                sprite.position.y = 0
