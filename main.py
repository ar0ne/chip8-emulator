"""
CHIP-8 Interpreter.
"""
from collections import deque

# 16 x 5
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
        # executing address. Start from 0x200, since beginning of memory reserved for interpreter
        self.program_counter = 0x200
        # The stack pointer can be 8-bit, it is used to point to the topmost level of the stack
        self.stack_counter = 0
        #
        self.working = False
        self.drawing = False

        # load fonts set into memory
        for i, font in enumerate(FONTS):
            self.memory[i] = font

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
            byte = f.read(1)
            # read byte by byte and place in memory from 0x200 (512)
            while byte:
                self.memory[i + 0x200] = ord(byte)
                i += 1
                byte = f.read(1)

    def start(self) -> None:
        """Start program"""
        self.working = True
        while self.working:
            self.process()
            self.draw()

    def draw(self) -> None:
        """Update display"""
        if self.drawing:
            pass

    def process(self) -> None:
        """Read op code and process it"""
        self.op_code = self.memory[self.program_counter]

        # process op code
        self._process_op_code()

        self.program_counter += 2  # each instruction is 2 bytes

        # update timers

        if self.program_counter >= 4096:
            self.working = False

    def _process_op_code(self) -> None:
        """
        Process operational code.

        nnn or addr - A 12-bit value, the lowest 12 bits of the instruction
        n or nibble - A 4-bit value, the lowest 4 bits of the instruction
        x - A 4-bit value, the lower 4 bits of the high byte of the instruction
        y - A 4-bit value, the upper 4 bits of the low byte of the instruction
        kk or byte - An 8-bit value, the lowest 8 bits of the instruction

        00E0 - CLS
        00EE - RET
        0nnn - SYS addr
        1nnn - JP addr
        2nnn - CALL addr
        3xkk - SE Vx, byte
        4xkk - SNE Vx, byte
        5xy0 - SE Vx, Vy
        6xkk - LD Vx, byte
        7xkk - ADD Vx, byte
        8xy0 - LD Vx, Vy
        8xy1 - OR Vx, Vy
        8xy2 - AND Vx, Vy
        8xy3 - XOR Vx, Vy
        8xy4 - ADD Vx, Vy
        8xy5 - SUB Vx, Vy
        8xy6 - SHR Vx {, Vy}
        8xy7 - SUBN Vx, Vy
        8xyE - SHL Vx {, Vy}
        9xy0 - SNE Vx, Vy
        Annn - LD I, addr
        Bnnn - JP V0, addr
        Cxkk - RND Vx, byte
        Dxyn - DRW Vx, Vy, nibble
        Ex9E - SKP Vx
        ExA1 - SKNP Vx
        Fx07 - LD Vx, DT
        Fx0A - LD Vx, K
        Fx15 - LD DT, Vx
        Fx18 - LD ST, Vx
        Fx1E - ADD I, Vx
        Fx29 - LD F, Vx
        Fx33 - LD B, Vx
        Fx55 - LD [I], Vx
        Fx65 - LD Vx, [I]

        0x0010:
            0x0010 & 0xf000 = 0x0000
            0x0010 & 0x0f0f = 0x0000 => 00E0
        """

        code = self.op_code & 0xF000
        if code == 0x0000:
            self._0000()

    def _0000(self) -> None:
        """
        Not real opcode.
        There are 3 instructions that starts from 0x0XXX.
        """
        code = self.op_code & 0xF0FF
        if code == 0x00E0:
            self._00E0()
        elif code == 0x00EE:
            self._00EE()
        else:
            self._0nnn()

    def _00E0(self) -> None:
        """
        00E0 - CLS
        Clear the display.
        """
        self.display = [0] * 64 * 32
        self.drawing = True

    def _00EE(self) -> None:
        """
        00EE - RET
        Return from a subroutine.

        The interpreter sets the program counter to the address at the top of the stack, then
        subtracts 1 from the stack pointer.
        """
        self.program_counter = self.stack.pop()

    def _0nnn(self) -> None:
        """
        0nnn - SYS addr
        Jump to a machine code routine at nnn.

        This instruction is only used on the old computers on which Chip-8 was originally
        implemented. It is ignored by modern interpreters.
        """
        nnn = self.op_code & 0x0FFF
        self.program_counter = nnn

    def _1nnn(self) -> None:
        """
        1nnn - JP addr
        Jump to location nnn.

        The interpreter sets the program counter to nnn.
        """
        nnn = self.op_code & 0x0FFF
        self.program_counter = nnn

    def _2nnn(self) -> None:
        """
        2nnn - CALL addr
        Call subroutine at nnn.

        The interpreter increments the stack pointer, then puts the current PC on the top of the
        stack. The PC is then set to nnn.
        """
        self.stack.append(self.program_counter)
        nnn = self.op_code & 0x0FFF
        self.program_counter = nnn

    def _3xkk(self) -> None:
        """
        SE Vx, byte - Skip next instruction if Vx = kk
        The interpreter compares register Vx to kk, and if they are equal, increments the program
        counter by 2.
        """
        # TODO: is it correct?
        kk = self.op_code & 0x00FF
        Vx = self.op_code & 0x0F00  # how to get which v0-VF it is?
        if kk == Vx:
            self.program_counter += 2

    def _4xkk(self) -> None:
        """
        SNE Vx, byte - skip next instruction if Vx != kk.
        The interpreter compares register Vx to kk, and if they are not equal, increments the
        program counter by 2.
        """
        # TODO

    def _5xy0(self) -> None:
        """
        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy.

        The interpreter compares register Vx to register Vy, and if they are equal, increments
        the program counter by 2.
        """
        # TODO

    def _6xkk(self) -> None:
        """
        6xkk - LD Vx, byte
        Set Vx = kk.

        The interpreter puts the value kk into register Vx.
        """
        # TODO

    def _7xkk(self) -> None:
        """
        7xkk - ADD Vx, byte
        Set Vx = Vx + kk.

        Adds the value kk to the value of register Vx, then stores the result in Vx.
        """
        # TODO

    def _8xy0(self) -> None:
        """
        8xy0 - LD Vx, Vy
        Set Vx = Vy.

        Stores the value of register Vy in register Vx.
        """
        # TODO

    def _8xy1(self) -> None:
        """
        8xy1 - OR Vx, Vy
        Set Vx = Vx OR Vy.

        Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise
        OR compares the corresponding bits from two values, and if either bit is 1, then the same
        bit in the result is also 1. Otherwise, it is 0.
        """
        # TODO

    def _8xy2(self) -> None:
        """
        8xy2 - AND Vx, Vy
        Set Vx = Vx AND Vy.

        Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise
        AND compares the corresponding bits from two values, and if both bits are 1, then the same
        bit in the result is also 1. Otherwise, it is 0.
        """
        # TODO

    def _8xy3(self) -> None:
        """
        8xy3 - XOR Vx, Vy
        Set Vx = Vx XOR Vy.

        Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx.
        An exclusive OR compares the corresponding bits from two values, and if the bits are not
        both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
        """
        # TODO

    def _8xy4(self) -> None:
        """
        8xy4 - ADD Vx, Vy
        Set Vx = Vx + Vy, set VF = carry.

        The values of Vx and Vy are added together. If the result is greater than 8 bits
        (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept,
        and stored in Vx.
        """
        # TODO

    def _8xy5(self) -> None:
        """
        8xy5 - SUB Vx, Vy
        Set Vx = Vx - Vy, set VF = NOT borrow.

        If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the
        results stored in Vx.
        """
        # TODO

    def _8xy6(self) -> None:
        """
        8xy6 - SHR Vx {, Vy}
        Set Vx = Vx SHR 1.

        If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is
        divided by 2.
        """
        # TODO

    def _8xy7(self) -> None:
        """
        8xy7 - SUBN Vx, Vy
        Set Vx = Vy - Vx, set VF = NOT borrow.

        If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results
        stored in Vx.
        """
        # TODO

    def _8xyE(self) -> None:
        """
        8xyE - SHL Vx {, Vy}
        Set Vx = Vx SHL 1.

        If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is
        multiplied by 2.
        """
        # TODO

    def _9xy0(self) -> None:
        """
        9xy0 - SNE Vx, Vy
        Skip next instruction if Vx != Vy.

        The values of Vx and Vy are compared, and if they are not equal, the program counter is
        increased by 2.
        """
        # TODO

    def _Annn(self) -> None:
        """
        Annn - LD I, addr
        Set I = nnn.

        The value of register I is set to nnn.
        """
        # TODO

    def _Bnnn(self) -> None:
        """
        Bnnn - JP V0, addr
        Jump to location nnn + V0.

        The program counter is set to nnn plus the value of V0.
        """
        # TODO

    def _Cxkk(self) -> None:
        """
        Cxkk - RND Vx, byte
        Set Vx = random byte AND kk.

        The interpreter generates a random number from 0 to 255, which is then ANDed with the value
         kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.
        """
        # TODO

    def _Dxyn(self) -> None:
        """
        Dxyn - DRW Vx, Vy, nibble
        Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

        The interpreter reads n bytes from memory, starting at the address stored in I. These bytes
        are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the
        existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set
        to 0. If the sprite is positioned so part of it is outside the coordinates of the display,
        it wraps around to the opposite side of the screen. See instruction 8xy3 for more
        information on XOR, and section 2.4, Display, for more information on the Chip-8 screen
        and sprites.
        """
        # TODO

    def _Ex9E(self) -> None:
        """
        Ex9E - SKP Vx
        Skip next instruction if key with the value of Vx is pressed.

        Checks the keyboard, and if the key corresponding to the value of Vx is currently in the
        down position, PC is increased by 2.
        """
        # TODO

    def _ExA1(self) -> None:
        """
        ExA1 - SKNP Vx
        Skip next instruction if key with the value of Vx is not pressed.

        Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up
        position, PC is increased by 2.
        """
        # TODO

    def _Fx07(self) -> None:
        """
        Fx07 - LD Vx, DT
        Set Vx = delay timer value.

        The value of DT is placed into Vx.
        """
        # TODO

    def _Fx0A(self) -> None:
        """
        Fx0A - LD Vx, K
        Wait for a key press, store the value of the key in Vx.

        All execution stops until a key is pressed, then the value of that key is stored in Vx.
        """
        # TODO

    def _Fx15(self) -> None:
        """
        Fx15 - LD DT, Vx
        Set delay timer = Vx.

        DT is set equal to the value of Vx.
        """
        # TODO

    def _Fx18(self) -> None:
        """
        Fx18 - LD ST, Vx
        Set sound timer = Vx.

        ST is set equal to the value of Vx.
        """
        # TODO

    def Fx1E(self) -> None:
        """
        Fx1E - ADD I, Vx
        Set I = I + Vx.

        The values of I and Vx are added, and the results are stored in I.
        """
        # TODO

    def Fx29(self) -> None:
        """
        Fx29 - LD F, Vx
        Set I = location of sprite for digit Vx.

        The value of I is set to the location for the hexadecimal sprite corresponding to the value
        of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
        """
        # TODO

    def Fx33(self) -> None:
        """
        Fx33 - LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, and I+2.

        The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at
        location in I, the tens digit at location I+1, and the ones digit at location I+2.
        """
        # TODO

    def Fx55(self) -> None:
        """
        Fx55 - LD [I], Vx
        Store registers V0 through Vx in memory starting at location I.

        The interpreter copies the values of registers V0 through Vx into memory, starting at the
        address in I.
        """
        # TODO

    def Fx65(self) -> None:
        """
        Fx65 - LD Vx, [I]
        Read registers V0 through Vx from memory starting at location I.

        The interpreter reads values from memory starting at location I into registers V0 through Vx
        """
        # TODO


if __name__ == "__main__":
    interpreter = CHIP8Interpreter()
    interpreter.load_rom("rom/TETRIS.ch8")
    interpreter.start()
