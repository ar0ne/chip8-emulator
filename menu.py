"""Game menu scene"""
import os.path
from os import listdir
from os.path import isfile, join

import pygame
import pyghelpers
from pyghelpers import Scene

from menu import font
from menu.button import Button

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def check_file_extension(file, extension):
    args = os.path.splitext(file)
    if not (args and len(args) == 2):
        return False
    return extension.casefold() == args[1][1:].casefold()


class MenuScene(Scene):
    """Menu scene"""

    TOP_OFFSET = 30

    def __init__(self, window, dir="menu") -> None:
        """Init scene"""
        self.window = window
        self.logo_img = pygame.image.load(f"{dir}/logo.png")
        self.font = font.NesFont()
        self.roms = self.read_files_from_folder("roms")
        self.roms.sort()
        self.page_size = 10
        self.current_page = 1
        self.rom_buttons = []
        self.selected_rom_index = 0
        for rom_name in self.roms[
            (self.current_page - 1)
            * self.page_size : self.page_size
            * self.current_page
            - 1
        ]:
            btn_image = self.font.render(rom_name[:-4])
            btn_image_scaled = pygame.transform.scale2x(btn_image)
            button = Button(
                btn_image_scaled,
                (0, 0),
                lambda _, __: print("hello"),
            )
            self.rom_buttons.append(button)

    def enter(self, data) -> None:
        """Enter scene"""

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
        x_offset = self.TOP_OFFSET
        y_offset = self.logo_img.get_height() * 2.5
        btn_border_margin = 4
        for idx, rom_btn in enumerate(self.rom_buttons):
            if idx >= len(self.rom_buttons) / 2:
                x_offset = self.window.get_width() / 2
            x = x_offset + 80
            y = y_offset + 40 * (idx % 5)
            if idx == self.selected_rom_index:
                pygame.draw.rect(
                    self.window,
                    WHITE,
                    (
                        x - btn_border_margin,
                        y - btn_border_margin,
                        rom_btn.image.get_width() + btn_border_margin,
                        rom_btn.image.get_height() + btn_border_margin,
                    ),
                    1,
                )
            self.window.blit(rom_btn.image, (x, y))

    def getSceneKey(self) -> str:
        """Get unique scene key"""
        return "MENU"

    def handleInputs(self, events, keyPressedList) -> None:
        """Handle inputs"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_rom_index += 1
                    if self.selected_rom_index >= 9:
                        self.selected_rom_index = 0
                if event.key == pygame.K_UP:
                    self.selected_rom_index -= 1
                    if self.selected_rom_index < 0:
                        self.selected_rom_index = 9
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    pass

    def read_files_from_folder(self, folder, extension="ch8") -> list[str]:
        """Get all file names from folder with required format"""
        return [
            f
            for f in listdir(folder)
            if isfile(join(folder, f)) and check_file_extension(f, extension)
        ]


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("GAME_TITLE_TXT")
    scenes = [MenuScene(window)]
    scene_manager = pyghelpers.SceneMgr(scenes, 30)
    scene_manager.run()
