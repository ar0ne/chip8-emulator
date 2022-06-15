"""
CHIP-8 Interpreter.
"""
from collections import deque

FONTS = [
    0xF0,
    0x90,
    0x90,
    0x90,
    0xF0,  # 0
    # 0 - 9, A - F
]


class CHIP8Interpreter:
    """
    Interpreter for CHIP-8

                                    Memory
        Each memory location is 8 bits (byte) 4Kb - 0x000 (0) to 0xFFF (4095). First 512 bytes
        (0x000-0x1FF) for interpreter and should not be used.

                                    Registers
        CHIP-8 has 16 8-bit data registers named V0 to VF. The VF register doubles as a flag for
    some instructions; thus, it should be avoided. In an addition operation, VF is the carry
    flag, while in subtraction, it is the "no borrow" flag. In the draw instruction VF is set
    upon pixel collision.
        The address register, which is named I, is 12 bits wide and is used with several opcodes
    that involve memory operations.

                                    The stack
        Used to store return address from subroutines.

                                    Timers
        Delay and sound times

                                    Input
        Keyboard

                                    Display
        Graphics are drawn to the screen solely by drawing sprites, which are 8 pixels wide
    and may be from 1 to 15 pixels in height. Sprite pixels are XOR'd with corresponding screen
    pixels. In other words, sprite pixels that are set flip the color of the corresponding
    screen pixel, while unset sprite pixels do nothing. The carry flag (VF) is set to 1 if any
    screen pixels are flipped from set to unset when a sprite is drawn and set to 0 otherwise.
    This is used for collision detection.
    (0,0)     (63,0)

    (0,31)    (63,31)

                                    Sound
        A beeping sound is played when the value of the sound timer is nonzero.
    """

    def __init__(self) -> None:
        """Init VM"""

        # This timer is intended to be used for timing the events of games.
        # Its value can be set and read.
        self.delay_timer = 0
        # This timer is used for sound effects. When its value is nonzero,
        # a beeping sound is made.
        self.sound_timer = 0
        # The stack is an array of 16 16-bit values for up to 12 levels of nesting
        self.stack = deque()
        # display monochrome with resolution 64x32 pixels
        self.display = [0] * 64 * 32
        # memory 4kb by 8 bits
        self.memory = [0] * 4096
        # 8 bits registers (GPIO)
        self.v0 = 0
        self.v1 = 0
        self.v2 = 0
        self.v3 = 0
        self.v4 = 0
        self.v5 = 0
        self.v6 = 0
        self.v7 = 0
        self.v8 = 0
        self.v9 = 0
        self.vA = 0
        self.vB = 0
        self.vC = 0
        self.vD = 0
        self.vE = 0
        self.vF = 0  # should not be used by any programs
        # 16 bit (This register is generally used to store memory addresses, so only the
        # lowest (rightmost) 12 bits are usually used)
        self.I = 0
        # The program counter should be 16-bit, and is used to store the currently
        # executing address. Start from 0x200, since beggining of memory reserved for interpreter
        self.program_counter = 0x200
        # The stack pointer can be 8-bit, it is used to point to the topmost level of the stack
        self.stack_counter = 0
        #
        self.working = False
        self.drawing = False

    def load_rom(self, path_to_rom: str) -> None:
        """
        Load binary from rom file into memory

        All instructions are 2 bytes long and are stored most-significant-byte first. In memory,
        the first byte of each instruction should be located at an even addresses. If a program
        includes sprite data, it should be padded so any instructions following it will be
        properly situated in RAM.
        """
        with open(path_to_rom, "rb") as f:
            i = 0
            byte = f.read(1)  # read one byte
            while byte:
                self.memory[i + 0x200] = ord(byte)
                i += 1
                byte = f.read(1)

    def start(self) -> None:
        """Start program"""
        self.working = True
        while self.working:
            self.draw()

    def draw(self) -> None:
        """Update display"""
        if self.drawing:
            pass


if __name__ == "__main__":
    interpreter = CHIP8Interpreter()
    interpreter.load_rom("rom/TETRIS.ch8")
    interpreter.start()
