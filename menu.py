#!/usr/bin/env python3
"""
Game UI for Chip8 emulator
"""
import pygame
from pyghelpers import pyghelpers

from menu.game_scene import GameScene
from menu.menu_scene import MenuScene

WIDTH = 640
HEIGHT = 480
FPS = 30

DATA_DIR = "menu/data"
ROM_DIR = "roms"

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CHIP-8 Emulator")
scenes = [
    MenuScene(window, data_dir=DATA_DIR, rom_dir=ROM_DIR),
    GameScene(window),
]
scene_manager = pyghelpers.SceneMgr(scenes, FPS)
scene_manager.run()
