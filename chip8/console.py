"""
Run CHIP-8 emulator in terminal.
"""
import os
import time

from chip8.base import CHIP8Interpreter


class ConsoleCHIP8Interpreter(CHIP8Interpreter):
    """
    Console Interpreter for CHIP-8
    """

    def update_timers(self) -> None:
        """Update display and sound timers, and stick to frame rate"""
        super().update_timers()
        time.sleep(0.003)

    def read_keyboard(self) -> None:
        """Read from keyboard"""
        # TODO: read from keyboard

    def draw(self) -> None:
        """Update display"""
        if not any(self.display):
            return
        os.system("clear")
        for col in range(self.COLUMNS):
            for row in range(self.ROWS):
                if self.display[row + col * self.ROWS]:
                    print("x", end="")
                else:
                    print(" ", end="")
            print("")

    def play_sound(self) -> None:
        """Play buzz sound"""
        print("Sound!")
