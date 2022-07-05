"""Game scene"""
from pyghelpers import Scene

from chip8.py_game import PyGameCHIP8Interpreter
from menu.constants import GAME_SCENE_KEY


class GameScene(Scene):
    """Game scene"""

    def __init__(self, window) -> None:
        """Init scene"""
        self.emulator = PyGameCHIP8Interpreter(window=window)

    def getSceneKey(self) -> str:
        """Get scene key"""
        return GAME_SCENE_KEY

    def handleInputs(self, events, keyPressedList) -> None:
        """Handle inputs"""

    def enter(self, data) -> None:
        """Enter scene"""

    def draw(self) -> None:
        """Draw UI elements"""
