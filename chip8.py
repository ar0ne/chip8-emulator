"""
Command interface to run CHIP-8 emulator.
"""
import argparse
import os
import sys

from chip8.console import ConsoleCHIP8Interpreter
from chip8.py_game import PyGameCHIP8Interpreter


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, "r")  # return an open file handle


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="chip8.py",
        description="""CHIP-8 Emulator""",
        epilog="""(c) Serj Ar[]ne 2022""",
    )

    parser.add_argument(
        "-t",
        "--type",
        choices=["console", "pygame"],
        default="pygame",
        help="Type of emulator. By default: pygame.",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="roms/WALL.ch8",
        type=lambda x: is_valid_file(parser, x),
        help="Path to ROM file.",
        metavar="FILE",
    )
    parser.add_argument("-d", "--debug", action=argparse.BooleanOptionalAction)
    return parser


parser = create_parser()
namespace = parser.parse_args(sys.argv[1:])

if namespace.type == "console":
    emulator = ConsoleCHIP8Interpreter(trace_mode=namespace.debug)
else:
    emulator = PyGameCHIP8Interpreter(window=None, trace_mode=namespace.debug)

emulator.load_rom(namespace.file.name)
emulator.run()
