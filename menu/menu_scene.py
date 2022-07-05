"""Menu scene"""
import os.path
from os import listdir
from os.path import isfile, join

import pygame
from pygame.surface import Surface
from pyghelpers import Scene

from menu import font
from menu.button import Button
from menu.constants import BLACK, GAME_SCENE_KEY, MENU_SCENE_KEY, WHITE


def check_file_extension(file, extension):
    args = os.path.splitext(file)
    if not (args and len(args) == 2):
        return False
    return extension.casefold() == args[1][1:].casefold()


class MenuScene(Scene):
    """Menu scene"""

    TOP_OFFSET = 30

    def __init__(self, window: Surface, data_dir: str, rom_dir: str) -> None:
        """Init scene"""
        self.window = window
        self.logo_img = pygame.image.load(f"{data_dir}/logo.png")
        self.font = font.RetroFont("menu/data/nes-font.png", (8, 8))
        self.roms = self.read_files_from_folder(rom_dir)
        self.roms.sort()
        self.page_size = 9
        self.current_page = 0
        self.rom_buttons = []
        self.selected_rom_index = 0
        self.pages = [
            self.font.render(f"Page: {page + 1}")
            for page in range(len(self.roms) // self.page_size + 1)
        ]
        for rom_name in self.roms:
            btn_image = self.font.render(rom_name[:-4])
            btn_image_scaled = pygame.transform.scale2x(btn_image)
            button = Button(
                btn_image_scaled,
                (0, 0),
                lambda _, __: print("hello"),
            )
            self.rom_buttons.append(button)
        # add button to display next page
        next_page_image = self.font.render("...")
        next_page_image_scaled = pygame.transform.scale2x(next_page_image)
        self.next_page_button = Button(
            next_page_image_scaled,
            (0, 0),
            lambda _, __: print("hello"),
        )

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
        self.draw_game_select_buttons()
        self.window.blit(self.pages[self.current_page], (10, 10))

    def draw_game_select_buttons(self) -> None:
        """Draw game buttons"""
        x_offset = self.TOP_OFFSET
        y_offset = self.logo_img.get_height() * 2.5
        second_column_x_offset = self.window.get_width() / 2
        btn_border_margin = 4
        btn_page = self.rom_buttons[
            self.current_page
            * self.page_size : (self.current_page + 1)
            * self.page_size
        ]
        btn_page.append(self.next_page_button)

        for idx, game_btn in enumerate(btn_page):
            if idx >= 5:
                x_offset = second_column_x_offset
            x = x_offset + 80
            y = y_offset + 40 * (idx % 5)
            if idx == self.selected_rom_index:
                pygame.draw.rect(
                    self.window,
                    WHITE,
                    (
                        x - btn_border_margin,
                        y - btn_border_margin,
                        game_btn.image.get_width() + btn_border_margin,
                        game_btn.image.get_height() + btn_border_margin,
                    ),
                    1,
                )
            self.window.blit(game_btn.image, (x, y))

    def getSceneKey(self) -> str:
        """Get unique scene key"""
        return MENU_SCENE_KEY

    def handleInputs(self, events, keyPressedList) -> None:
        """Handle inputs"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_rom_index += 1
                    if self.selected_rom_index > self.page_size:
                        self.selected_rom_index = 0
                if event.key == pygame.K_UP:
                    self.selected_rom_index -= 1
                    if self.selected_rom_index < 0:
                        self.selected_rom_index = self.page_size
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if not self.selected_rom_index % 10:
                        # self.goToScene(GAME_SCENE_KEY)
                        pass
                    else:
                        self.current_page += 1
                        self.selected_rom_index = (
                            self.selected_rom_index
                            if self.current_page * (self.page_size + 1) < len(self.roms)
                            else 0
                        )
                        last_page = (
                            self.current_page == len(self.roms) // self.page_size + 1
                        )
                        if last_page:
                            self.current_page = 0

    def read_files_from_folder(self, folder, extension="ch8") -> list[str]:
        """Get all file names from folder with required format"""
        return [
            f
            for f in listdir(folder)
            if isfile(join(folder, f)) and check_file_extension(f, extension)
        ]
