"""

"""
import os
import sys
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
        pass

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


if __name__ == "__main__":
    interpreter = ConsoleCHIP8Interpreter(trace_mode=True)
    interpreter.load_rom(sys.argv[1])
    interpreter.run()
