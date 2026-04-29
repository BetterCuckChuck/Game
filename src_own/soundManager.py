"""Module quản lý âm thanh cho game Asteroids.

Cung cấp các hàm nạp, phát, dừng, và tắt tiếng (mute)
toàn bộ hiệu ứng âm thanh thông qua pygame.mixer.
"""

import pygame
import sys
import os
import random
from pygame.locals import *

sounds = {}  

is_muted = False


def initSoundManager():
    """Khởi tạo mixer và nạp toàn bộ file âm thanh từ đĩa."""
    pygame.mixer.init()
    sounds["fire"] = pygame.mixer.Sound("../res/FIRE.WAV")
    sounds["explode1"] = pygame.mixer.Sound("../res/EXPLODE1.WAV")
    sounds["explode2"] = pygame.mixer.Sound("../res/EXPLODE2.WAV")
    sounds["explode3"] = pygame.mixer.Sound("../res/EXPLODE3.WAV")
    sounds["lsaucer"] = pygame.mixer.Sound("../res/LSAUCER.WAV")
    sounds["ssaucer"] = pygame.mixer.Sound("../res/SSAUCER.WAV")
    sounds["thrust"] = pygame.mixer.Sound("../res/THRUST.WAV")
    sounds["sfire"] = pygame.mixer.Sound("../res/SFIRE.WAV")
    sounds["extralife"] = pygame.mixer.Sound("../res/LIFE.WAV")


def toggleMute():
    """Bật/tắt trạng thái mute toàn cục.

    Khi chuyển sang mute, tất cả âm thanh đang phát sẽ bị dừng ngay.
    """
    global is_muted
    is_muted = not is_muted
    if is_muted:
        for sound in sounds.values():
            sound.stop()


def playSound(soundName):
    """Phát một hiệu ứng âm thanh một lần.

    Args:
        soundName: Khóa định danh âm thanh trong dictionary sounds.
    """
    if not is_muted:
        channel = sounds[soundName].play()


def playSoundContinuous(soundName):
    """Phát một hiệu ứng âm thanh lặp liên tục.

    Args:
        soundName: Khóa định danh âm thanh trong dictionary sounds.
    """
    if not is_muted:
        channel = sounds[soundName].play(-1)


def stopSound(soundName):
    """Dừng một hiệu ứng âm thanh đang phát.

    Args:
        soundName: Khóa định danh âm thanh trong dictionary sounds.
    """
    channel = sounds[soundName].stop()
