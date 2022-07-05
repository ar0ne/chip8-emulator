"""
Run CHIP-8 Interpreter with PyGame.
"""

import pygame
from pygame import constants as pygame_constants

from chip8.base import CHIP8Interpreter

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 180

"""
16-key hexadecimal keypad with the following layout.

1, 2, 3, C,
4, 5, 6, D,
7, 8, 9, E,
A, 0, B, F,
"""
KEYBOARD_MAP = {
    pygame_constants.K_1: 0x1,
    pygame_constants.K_2: 0x2,
    pygame_constants.K_3: 0x3,
    pygame_constants.K_4: 0xC,
    pygame_constants.K_q: 0x4,
    pygame_constants.K_w: 0x5,
    pygame_constants.K_e: 0x6,
    pygame_constants.K_r: 0xD,
    pygame_constants.K_a: 0x7,
    pygame_constants.K_s: 0x8,
    pygame_constants.K_d: 0x9,
    pygame_constants.K_f: 0xE,
    pygame_constants.K_z: 0xA,
    pygame_constants.K_x: 0,
    pygame_constants.K_c: 0xB,
    pygame_constants.K_v: 0xF,
}


class PyGameCHIP8Interpreter(CHIP8Interpreter):
    """PyGame CHIP-8 emulator"""

    def __init__(
        self,
        window: pygame.Surface | None,
        screen_width: int = 640,
        screen_height: int = 320,
        block_size: int = 10,
        trace_mode: bool = False,
        keyboard_mapping: dict | None = None,
    ) -> None:
        super().__init__(trace_mode)
        self.BLOCK_SIZE = block_size
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_width, screen_height
        assert block_size * self.ROWS <= screen_width, "Screen width is invalid."
        assert block_size * self.COLUMNS <= screen_height, "Screen height is invalid."

        if not window:
            # init pygame and screen
            pygame.init()
            self.screen = pygame.display.set_mode(
                (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            )
            pygame.display.set_caption("CHIP8 emulator")
        else:
            self.screen = window

        self.clock = pygame.time.Clock()

        if not keyboard_mapping:
            # if not present, use default mapping
            keyboard_mapping = KEYBOARD_MAP
        self.keyboard = keyboard_mapping

    def update_timers(self) -> None:
        """Update display and sound timers, and stick to required frame rate"""
        super().update_timers()
        self.clock.tick(FPS)

    def draw(self) -> None:
        """Update display"""
        if not self.drawing:
            return

        # clear screen
        self.screen.fill(BLACK)
        # draw current display
        for row in range(self.ROWS):
            for col in range(self.COLUMNS):
                if self.display[row + col * self.ROWS]:
                    pygame.draw.rect(
                        self.screen,
                        WHITE,
                        pygame.Rect(
                            row * self.BLOCK_SIZE,
                            col * self.BLOCK_SIZE,
                            self.BLOCK_SIZE,
                            self.BLOCK_SIZE,
                        ),
                    )
        # update full display to the screen
        pygame.display.flip()
        # toggle drawing flag
        self.drawing = False

    def read_keyboard(self) -> None:
        """Read from keyboard"""
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        self.pressed_key.clear()
        for key in self.keyboard.keys():
            if pressed[key]:
                self.pressed_key.add(self.keyboard[key])
        if pressed[pygame_constants.K_ESCAPE]:
            self.working = False

    def play_sound(self) -> None:
        """Play buzz sound"""
        # TODO: play sound
