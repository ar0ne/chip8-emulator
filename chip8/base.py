"""
CHIP-8 Interpreter.
"""
import abc
import random
from collections import defaultdict, deque


class CHIP8Interpreter(abc.ABC):
    """Interpreter for CHIP-8

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

    MEMORY_START = 0x200  # 512
    MEMORY_SIZE = 4096
    ROWS = 64
    COLUMNS = 32

    FONT_SIZE_IN_BYTES = 0x5
    # fmt: off
    FONTS = [
        0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
    ]  # 16 x 5
    # fmt: on

    def __init__(
        self,
        trace_mode: bool = False,
    ) -> None:
        """Init emulator"""

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
        self.DISPLAY_SIZE = len(self.display)  # 2048
        # memory 4kb by 8 bits
        self.memory = [0] * self.MEMORY_SIZE
        # 8 bits registers (GPIO)
        self.gpio = [0] * 16
        # 16 bit (This register is generally used to store memory addresses, so only the
        # lowest (rightmost) 12 bits are usually used)
        self.I = 0
        # The program counter should be 16-bit, and is used to store the currently
        # executing address. Start from 0x200 (512), since beginning of memory reserved for
        # interpreter
        self.program_counter = self.MEMORY_START
        # The stack pointer can be 8-bit, it is used to point to the topmost level of the stack
        self.stack_counter = 0
        self.working = False
        self.drawing = False
        # set of pressed keyboard keys
        self.pressed_key = set()
        # show debug logs if enabled
        self.trace_mode = trace_mode
        # load fonts set into memory
        for i, font in enumerate(self.FONTS):
            self.memory[i] = font
        # define mapping op codes to handlers
        self.OPS_MAPPING = defaultdict(
            lambda: self.unknown_op_code,
            {
                0x0000: self._0000,
                0x00E0: self._00E0,
                0x00EE: self._00EE,
                0x1000: self._1nnn,
                0x2000: self._2nnn,
                0x3000: self._3xkk,
                0x4000: self._4xkk,
                0x5000: self._5xy0,
                0x6000: self._6xkk,
                0x7000: self._7xkk,
                0x8000: self._8000,
                0x8001: self._8xy1,
                0x8002: self._8xy2,
                0x8003: self._8xy3,
                0x8004: self._8xy4,
                0x8005: self._8xy5,
                0x8006: self._8xy6,
                0x8007: self._8xy7,
                0x800E: self._8xyE,
                0x9000: self._9xy0,
                0xA000: self._Annn,
                0xB000: self._Bnnn,
                0xC000: self._Cxkk,
                0xD000: self._Dxyn,
                0xE000: self._E000,
                0xE09E: self._Ex9E,
                0xE0A1: self._ExA1,
                0xF000: self._F000,
                0xF007: self._Fx07,
                0xF00A: self._Fx0A,
                0xF015: self._Fx15,
                0xF018: self._Fx18,
                0xF01E: self._Fx1E,
                0xF029: self._Fx29,
                0xF033: self._Fx33,
                0xF055: self._Fx55,
                0xF065: self._Fx65,
            },
        )

    @property
    def vx(self) -> int:
        """extract vx from op code (nibble=4bits)"""
        return (self.op_code & 0x0F00) >> 8

    @property
    def vy(self) -> int:
        """Extract Vy from op code (nibble=4bits)"""
        return (self.op_code & 0x00F0) >> 4

    @property
    def VF(self) -> int:
        """Get VF"""
        return self.gpio[0xF]

    @VF.setter
    def VF(self, val: int) -> None:
        self.gpio[0xF] = val

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
                self.memory[self.MEMORY_START + i] = ord(byte)
                i += 1
                byte = f.read(1)

    def run(self) -> None:
        """Run program"""
        self.working = True
        while self.working:
            self.read_keyboard()
            self.process_op_code()
            self.draw()
            self.update_timers()
        self.stop()

    @abc.abstractmethod
    def read_keyboard(self) -> None:
        """Read from keyboard"""
        pass

    @abc.abstractmethod
    def play_sound(self) -> None:
        """Play buzz sound"""

    @abc.abstractmethod
    def draw(self) -> None:
        """Update display"""

    def update_timers(self) -> None:
        """Update display and sound timers"""
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
            if not self.sound_timer:
                self.play_sound()

    def stop(self) -> None:
        """Stop running"""

    def process_op_code(self) -> None:
        """Read op code and process it"""
        # op code consist 2 bytes (16 bits)
        self.op_code = (self.memory[self.program_counter] << 8) | self.memory[
            self.program_counter + 1
        ]
        self.program_counter += 2  # each instruction is 2 bytes

        # process op code
        self._process_op_code()

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
        """

        code = self.op_code & 0xF000
        self._run_instruction(code)

    def _run_instruction(self, code: int) -> None:
        """Maps code to known op codes"""
        func = self.OPS_MAPPING[code]

        if self.trace_mode:
            self.debug_current_state(code, func.__name__)

        func()

    def _0000(self) -> None:
        """
        Not real opcode.
        There are 3 instructions that starts from 0x0XXX.
        """
        code = self.op_code & 0xF0FF
        if code == 0x0000:
            self._0nnn()
        else:
            self._run_instruction(code)

    def _00E0(self) -> None:
        """
        00E0 - CLS
        Clear the display.
        """
        self.display = [0] * self.COLUMNS * self.ROWS
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
        self.program_counter = self.op_code & 0x0FFF

    def _1nnn(self) -> None:
        """
        1nnn - JP addr
        Jump to location nnn.

        The interpreter sets the program counter to nnn.
        """
        self.program_counter = self.op_code & 0x0FFF

    def _2nnn(self) -> None:
        """
        2nnn - CALL addr
        Call subroutine at nnn.

        The interpreter increments the stack pointer, then puts the current PC on the top of the
        stack. The PC is then set to nnn.
        """
        self.stack.append(self.program_counter)
        self.program_counter = self.op_code & 0x0FFF

    def _3xkk(self) -> None:
        """
        SE Vx, byte - Skip next instruction if Vx = kk
        The interpreter compares register Vx to kk, and if they are equal, increments the program
        counter by 2.
        """
        if self.gpio[self.vx] == self.op_code & 0x00FF:
            self.program_counter += 2

    def _4xkk(self) -> None:
        """
        SNE Vx, byte - skip next instruction if Vx != kk.
        The interpreter compares register Vx to kk, and if they are not equal, increments the
        program counter by 2.
        """
        if self.gpio[self.vx] != self.op_code & 0x00FF:
            self.program_counter += 2

    def _5xy0(self) -> None:
        """
        5xy0 - SE Vx, Vy
        Skip next instruction if Vx = Vy.

        The interpreter compares register Vx to register Vy, and if they are equal, increments
        the program counter by 2.
        """
        if self.gpio[self.vx] == self.gpio[self.vy]:
            self.program_counter += 2

    def _6xkk(self) -> None:
        """
        6xkk - LD Vx, byte
        Set Vx = kk.

        The interpreter puts the value kk into register Vx.
        """
        kk = self.op_code & 0x00FF  # extract the lower 8 bits
        self.gpio[self.vx] = kk

    def _7xkk(self) -> None:
        """
        7xkk - ADD Vx, byte
        Set Vx = Vx + kk.

        Adds the value kk to the value of register Vx, then stores the result in Vx.
        """
        kk = self.op_code & 0x00FF  # extract the lower 8 bits
        self.gpio[self.vx] += kk
        self.gpio[self.vx] &= 0xFF

    def _8000(self) -> None:
        """Not real op code"""
        code = self.op_code & 0xF00F
        if code == 0x8000:
            self._8xy0()
        else:
            self._run_instruction(code)

    def _8xy0(self) -> None:
        """
        8xy0 - LD Vx, Vy
        Set Vx = Vy.

        Stores the value of register Vy in register Vx.
        """
        self.gpio[self.vx] = self.gpio[self.vy]

    def _8xy1(self) -> None:
        """
        8xy1 - OR Vx, Vy
        Set Vx = Vx OR Vy.

        Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise
        OR compares the corresponding bits from two values, and if either bit is 1, then the same
        bit in the result is also 1. Otherwise, it is 0.
        """
        self.gpio[self.vx] |= self.gpio[self.vy]

    def _8xy2(self) -> None:
        """
        8xy2 - AND Vx, Vy
        Set Vx = Vx AND Vy.

        Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise
        AND compares the corresponding bits from two values, and if both bits are 1, then the same
        bit in the result is also 1. Otherwise, it is 0.
        """
        self.gpio[self.vx] &= self.gpio[self.vy]

    def _8xy3(self) -> None:
        """
        8xy3 - XOR Vx, Vy
        Set Vx = Vx XOR Vy.

        Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx.
        An exclusive OR compares the corresponding bits from two values, and if the bits are not
        both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.
        """
        self.gpio[self.vx] ^= self.gpio[self.vy]

    def _8xy4(self) -> None:
        """
        8xy4 - ADD Vx, Vy
        Set Vx = Vx + Vy, set VF = carry.

        The values of Vx and Vy are added together. If the result is greater than 8 bits
        (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept,
        and stored in Vx.
        """
        sum = self.gpio[self.vx] + self.gpio[self.vy]
        self.VF = 1 if sum > 0xFF else 0  # VF
        # 256 & 0xFF == 0b0, is it ok to not have 8bits?
        self.gpio[self.vx] = sum & 0xFF

    def _8xy5(self) -> None:
        """
        8xy5 - SUB Vx, Vy
        Set Vx = Vx - Vy, set VF = NOT borrow.

        If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the
        results stored in Vx.
        """
        sub = self.gpio[self.vx] - self.gpio[self.vy]
        self.VF = 1 if sub > 0 else 0
        self.gpio[self.vx] = sub

    def _8xy6(self) -> None:
        """
        8xy6 - SHR Vx {, Vy}
        Set Vx = Vx SHR 1.

        If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is
        divided by 2.
        """
        self.VF = self.gpio[self.vx] & 0x1
        self.gpio[self.vx] >>= 1
        self.gpio[self.vx] &= 0xFF

        if self.trace_mode:
            print("[8xy6] %.4X" % (self.gpio[self.vx]))

    def _8xy7(self) -> None:
        """
        8xy7 - SUBN Vx, Vy
        Set Vx = Vy - Vx, set VF = NOT borrow.

        If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results
        stored in Vx.
        """
        sub = self.gpio[self.vy] - self.gpio[self.vx]
        self.VF = 1 if sub > 0 else 0
        self.gpio[self.vx] = sub

    def _8xyE(self) -> None:
        """
        8xyE - SHL Vx {, Vy}
        Set Vx = Vx SHL 1.

        If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is
        multiplied by 2.
        """
        # vx - 4 bit (15)
        self.VF = (self.gpio[self.vx] >> 7) & 0x1
        self.gpio[self.vx] <<= 1
        self.gpio[self.vx] &= 0xFF

    def _9xy0(self) -> None:
        """
        9xy0 - SNE Vx, Vy
        Skip next instruction if Vx != Vy.

        The values of Vx and Vy are compared, and if they are not equal, the program counter is
        increased by 2.
        """
        if self.gpio[self.vx] != self.gpio[self.vy]:
            self.program_counter += 2

    def _Annn(self) -> None:
        """
        Annn - LD I, addr
        Set I = nnn.

        The value of register I is set to nnn.
        """
        self.I = self.op_code & 0x0FFF

    def _Bnnn(self) -> None:
        """
        Bnnn - JP V0, addr
        Jump to location nnn + V0.

        The program counter is set to nnn plus the value of V0.
        """
        self.program_counter = (self.op_code & 0x0FFF) + self.gpio[0]

    def _Cxkk(self) -> None:
        """
        Cxkk - RND Vx, byte
        Set Vx = random byte AND kk.

        The interpreter generates a random number from 0 to 255, which is then ANDed with the value
        kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.
        """
        random_byte = random.randint(0, 0xFF)
        kk = self.op_code & 0x00FF
        self.gpio[self.vx] = (random_byte & kk) & 0xFF

    def _Dxyn(self) -> None:
        """
        Dxyn - DRW Vx, Vy, nibble
        Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

        Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
        Each row of 8 pixels is read as bit-coded starting from memory location I;
        I value doesn't change after the execution of this instruction.
        VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn,
        and to 0 if that doesn't happen
        """
        x = self.gpio[self.vx] & 0xFF  # 0..63
        y = self.gpio[self.vy] & 0xFF  # 0..31 pixels
        height = self.op_code & 0x000F
        length = 8
        self.VF = 0
        for col in range(height):
            pixel = self.memory[self.I + col]
            for row in range(length):
                if not (pixel & (0x80 >> row)):
                    # bin(0x80) == 0b1000 0000
                    continue
                # we should limit index within row and column limits
                idx = (
                    ((x + row) % self.ROWS + (y + col) % self.COLUMNS * self.ROWS)
                ) % self.DISPLAY_SIZE
                if self.display[idx] == 1:
                    self.VF = 1
                self.display[idx] ^= 1

        self.drawing = True

    def _E000(self) -> None:
        """Not real op code"""
        code = self.op_code & 0xF0FF
        self._run_instruction(code)

    def _Ex9E(self) -> None:
        """
        Ex9E - SKP Vx
        Skip next instruction if key with the value of Vx is pressed.

        Checks the keyboard, and if the key corresponding to the value of Vx is currently in the
        down position, PC is increased by 2.
        """
        if self.gpio[self.vx] in self.pressed_key:
            self.program_counter += 2

    def _ExA1(self) -> None:
        """
        ExA1 - SKNP Vx
        Skip next instruction if key with the value of Vx is not pressed.

        Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up
        position, PC is increased by 2.
        """
        if self.gpio[self.vx] not in self.pressed_key:
            self.program_counter += 2

    def _F000(self) -> None:
        """Not real op code"""
        code = self.op_code & 0xF0FF
        self._run_instruction(code)

    def _Fx07(self) -> None:
        """
        Fx07 - LD Vx, DT
        Set Vx = delay timer value.

        The value of DT is placed into Vx.
        """
        self.gpio[self.vx] = self.delay_timer

    def _Fx0A(self) -> None:
        """
        Fx0A - LD Vx, K
        Wait for a key press, store the value of the key in Vx.

        All execution stops until a key is pressed, then the value of that key is stored in Vx.
        """
        if not self.pressed_key:
            self.program_counter -= 2  # cycle until key pressed

        for key in self.pressed_key:
            self.gpio[self.vx] = key

    def _Fx15(self) -> None:
        """
        Fx15 - LD DT, Vx
        Set delay timer = Vx.

        DT is set equal to the value of Vx.
        """
        self.delay_timer = self.gpio[self.vx]

    def _Fx18(self) -> None:
        """
        Fx18 - LD ST, Vx
        Set sound timer = Vx.

        ST is set equal to the value of Vx.
        """
        self.sound_timer = self.gpio[self.vx]

    def _Fx1E(self) -> None:
        """
        Fx1E - ADD I, Vx
        Set I = I + Vx.

        The values of I and Vx are added, and the results are stored in I.
        """
        self.VF = 1 if (self.VF + self.gpio[self.vx]) > 0xFFF else 0
        self.I += self.gpio[self.vx]

    def _Fx29(self) -> None:
        """
        Fx29 - LD F, Vx
        Set I = location of sprite for digit Vx.

        The value of I is set to the location for the hexadecimal sprite corresponding to the value
        of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
        """
        # each font sprite consists 5 hex numbers, starting from 0 in memory
        self.I = self.gpio[self.vx] * self.FONT_SIZE_IN_BYTES

    def _Fx33(self) -> None:
        """
        Fx33 - LD B, Vx
        Store BCD representation of Vx in memory locations I, I+1, and I+2.

        The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at
        location in I, the tens digit at location I+1, and the ones digit at location I+2.
        """
        vx = self.gpio[self.vx]
        hundreds = int((vx % 1000) / 100)
        tens = int((vx % 100) / 10)
        ones = vx % 10
        self.memory[self.I], self.memory[self.I + 1], self.memory[self.I + 2] = (
            hundreds,
            tens,
            ones,
        )
        if self.trace_mode:
            print("[FX33] %d, %d, %d" % (hundreds, tens, ones))

    def _Fx55(self) -> None:
        """
        Fx55 - LD [I], Vx
        Store registers V0 through Vx in memory starting at location I.

        The interpreter copies the values of registers V0 through Vx into memory, starting at the
        address in I.
        """
        for i in range(self.vx):
            self.memory[self.I + i] = self.gpio[i]
        self.I += self.vx + 1

    def _Fx65(self) -> None:
        """
        Fx65 - LD Vx, [I]
        Read registers V0 through Vx from memory starting at location I.

        The interpreter reads values from memory starting at location I into registers V0 through Vx
        """
        for i in range(self.vx):
            self.gpio[i] = self.memory[self.I + i]
        self.I += self.vx + 1

    def unknown_op_code(self) -> None:
        """Not real op code"""
        print("Unknown op code %s, %s", bin(self.op_code), hex(self.op_code))

    def debug_current_state(self, code, func) -> None:
        """Print current state of memory"""
        print(
            "[%.4X->%s] PC: %d | OP: %.4X | X: %d | Y: %d | I: %.4X"
            % (
                code,
                func,
                self.program_counter,
                self.op_code,
                self.vx,
                self.vy,
                self.I,
            )
        )
        print("-" * 45)
        for i in range(4):
            print(
                "V%d: %d\tV%d: %d\tV%d: %d\tV%d: %d"
                % (
                    i,
                    self.gpio[i],
                    4 + i,
                    self.gpio[4 + i],
                    8 + i,
                    self.gpio[8 + i],
                    12 + i,
                    self.gpio[12 + i],
                )
            )
        print("-" * 45)
