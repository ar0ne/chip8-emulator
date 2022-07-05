"""Game scene"""
import pygame
from pygame.surface import Surface
from pyghelpers import Scene

from chip8.py_game import PyGameCHIP8Interpreter
from menu.constants import BLACK, GAME_SCENE_KEY, MENU_SCENE_KEY, SELECTED_ROM


class GameScene(Scene):
    """Game scene"""

    def __init__(self, window: Surface) -> None:
        """Init scene"""
        self.window = window
        self.emulator = None

    def getSceneKey(self) -> str:
        """Get scene key"""
        return GAME_SCENE_KEY

    def enter(self, data) -> None:
        """Enter scene"""
        selected_rom = self.request(MENU_SCENE_KEY, SELECTED_ROM)
        # clear screen on enter, because some roms could load pretty long time
        self.window.fill(BLACK)
        pygame.display.flip()
        # create emulator and load rom
        self.emulator = PyGameCHIP8Interpreter(window=self.window)
        self.emulator.load_rom(f"roms/{selected_rom}")

    def update(self) -> None:
        """
        Update scene on each frame.

        Since emulator has own loop, we just give control to it and return to menu when it's
        finished.
        """
        self.emulator.run()
        # clear event, otherwise scene manager will quit the app
        pygame.event.clear()
        # force redirect to menu scene
        self.goToScene(MENU_SCENE_KEY)

    def draw(self) -> None:
        """Draw scene"""

    def handleInputs(self, events, keyPressedList) -> None:
        """Handle inputs"""
