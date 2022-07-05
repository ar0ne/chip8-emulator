import pygame
from pyghelpers import pyghelpers

from menu.game_scene import GameScene
from menu.menu_scene import MenuScene

WIDTH = 640
HEIGHT = 480
FPS = 30

pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GAME_TITLE_TXT")
scenes = [
    MenuScene(window, data_dir="menu/data", rom_dir="roms"),
    GameScene(window),
]
scene_manager = pyghelpers.SceneMgr(scenes, FPS)
scene_manager.run()
