"""Game scene"""
import pygame
from pygame.surface import Surface
from pyghelpers import Scene

from chip8.py_game import PyGameCHIP8Interpreter
from menu.constants import BLACK, GAME_SCENE_KEY, MENU_SCENE_KEY, SELECTED_ROM


class GameScene(Scene):
    """Game scene"""

    TOP_OFFSET = 30

    def __init__(self, window: Surface) -> None:
        """Init scene"""
        self.window = window
        self.emulator = None

    def getSceneKey(self) -> str:
        """Get scene key"""
        return GAME_SCENE_KEY

    def handleInputs(self, events, keyPressedList) -> None:
        """Handle inputs"""
        for event in events:
            if event.type == pygame.K_DOWN:
                if event.key == pygame.K_ESCAPE:
                    self.goToScene(MENU_SCENE_KEY)

    def enter(self, data) -> None:
        """Enter scene"""
        selected_rom = self.request(MENU_SCENE_KEY, SELECTED_ROM)
        self.emulator = PyGameCHIP8Interpreter(window=self.window)
        self.emulator.load_rom(f"roms/{selected_rom}")

    def update(self):
        self.emulator.run()
        pygame.event.clear()
        self.goToScene(MENU_SCENE_KEY)

    def draw(self):
        self.window.fill(BLACK)
