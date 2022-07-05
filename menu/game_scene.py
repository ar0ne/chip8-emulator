"""Game scene"""
import pygame
from pygame.surface import Surface
from pyghelpers import Scene

from chip8.py_game import PyGameCHIP8Interpreter
from menu.constants import BLACK, GAME_SCENE_KEY, MENU_SCENE_KEY, SELECTED_ROM


class GameScene(Scene):
    """Game scene"""

    TOP_OFFSET = 30

    def __init__(self, window: Surface, data_dir: str) -> None:
        """Init scene"""
        self.window = window
        self.logo_img = pygame.image.load(f"{data_dir}/logo.png")
        self.emulator = PyGameCHIP8Interpreter(window=window)

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
        self.emulator.load_rom(f"roms/{selected_rom}")
        self.emulator.run()

    def draw(self) -> None:
        """Draw UI elements"""
        self.window.fill(BLACK)
        self.window.blit(
            self.logo_img,
            (
                self.window.get_width() / 2 - self.logo_img.get_width() / 2,
                self.TOP_OFFSET,
            ),
        )
