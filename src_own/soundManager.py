"""
Module quản lý âm thanh cho game Asteroids.

Cung cấp các hàm nạp, phát, dừng, và tắt tiếng (mute)
toàn bộ hiệu ứng âm thanh thông qua pygame.mixer.

Last Modified: 2026-05-13
"""

import pygame
import sys
import os
import random
from pygame.locals import *
from res_path import resource_path

sounds = {}  

is_muted = False


def initSoundManager():
    """
    Khởi tạo mixer và nạp toàn bộ file âm thanh từ đĩa.

    Last Modified: 2026-05-13
    """
    pygame.mixer.init()
    sounds["fire"] = pygame.mixer.Sound(resource_path("FIRE.WAV"))
    sounds["explode1"] = pygame.mixer.Sound(resource_path("EXPLODE1.WAV"))
    sounds["explode2"] = pygame.mixer.Sound(resource_path("EXPLODE2.WAV"))
    sounds["explode3"] = pygame.mixer.Sound(resource_path("EXPLODE3.WAV"))
    sounds["lsaucer"] = pygame.mixer.Sound(resource_path("LSAUCER.WAV"))
    sounds["ssaucer"] = pygame.mixer.Sound(resource_path("SSAUCER.WAV"))
    sounds["thrust"] = pygame.mixer.Sound(resource_path("THRUST.WAV"))
    sounds["sfire"] = pygame.mixer.Sound(resource_path("SFIRE.WAV"))
    sounds["extralife"] = pygame.mixer.Sound(resource_path("LIFE.WAV"))


def toggleMute():
    """
    Bật/tắt trạng thái mute toàn cục.

    Khi chuyển sang mute, tất cả âm thanh đang phát sẽ bị dừng ngay.

    Last Modified: 2026-05-13
    """
    global is_muted
    is_muted = not is_muted
    if is_muted:
        for sound in sounds.values():
            sound.stop()


def playSound(soundName):
    """
    Phát một hiệu ứng âm thanh một lần.

    Args:
        soundName: Khóa định danh âm thanh trong dictionary sounds.

    Last Modified: 2026-05-13
    """
    if not is_muted:
        channel = sounds[soundName].play()


def playSoundContinuous(soundName):
    """
    Phát một hiệu ứng âm thanh lặp liên tục.

    Args:
        soundName: Khóa định danh âm thanh trong dictionary sounds.

    Last Modified: 2026-05-13
    """
    if not is_muted:
        channel = sounds[soundName].play(-1)


def stopSound(soundName):
    """
    Dừng một hiệu ứng âm thanh đang phát.

    Args:
        soundName: Khóa định danh âm thanh trong dictionary sounds.

    Last Modified: 2026-05-13
    """
    channel = sounds[soundName].stop()
