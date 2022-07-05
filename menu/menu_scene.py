"""Menu scene"""
import os.path
from os import listdir
from os.path import isfile, join

import pygame
from pygame.surface import Surface
from pyghelpers import Scene

from menu import font
from menu.constants import BLACK, GAME_SCENE_KEY, MENU_SCENE_KEY, SELECTED_ROM, WHITE


def check_file_extension(file: str, extension: str) -> bool:
    """Check that file has correct extension"""
    args = os.path.splitext(file)
    if not (args and len(args) == 2):
        return False
    return extension.casefold() == args[1][1:].casefold()


class MenuScene(Scene):
    """Menu scene"""

    def __init__(self, window: Surface, data_dir: str, rom_dir: str) -> None:
        """Init scene"""
        self.window = window
        self.WINDOW_WIDTH = window.get_width()
        self.WINDOW_HEIGHT = window.get_height()
        self.logo_img = pygame.image.load(f"{data_dir}/logo.png")
        self.font = font.Font(f"{data_dir}/nes-font.png", (8, 8))
        self.roms = self.read_files_from_folder(rom_dir, "ch8")
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
            btn_image = pygame.transform.scale2x(btn_image)
            self.rom_buttons.append(btn_image)
        # add button to display next page
        next_page_image = self.font.render("...")
        next_page_image = pygame.transform.scale2x(next_page_image)
        self.next_page_button = next_page_image

        self.TOP_OFFSET = 30
        self.line_margin = 60
        self.line1_y = self.TOP_OFFSET * 3 + self.logo_img.get_height()
        self.line2_y = self.WINDOW_HEIGHT - 50
        self.line_x = (self.line_margin, self.WINDOW_WIDTH - self.line_margin)
        self.current_page_x = (
            self.WINDOW_WIDTH / 2 - self.pages[self.current_page].get_width() / 2
        )
        self.current_page_y = self.window.get_height() - 30
        self.logo_img_x = self.WINDOW_WIDTH / 2 - self.logo_img.get_width() / 2
        self.logo_img_y = self.TOP_OFFSET
        self.button_x_offset = self.TOP_OFFSET
        self.button_y_offset = self.logo_img.get_height() * 2.5
        self.second_column_x_offset = self.WINDOW_WIDTH / 2 + 60
        self.btn_border_margin = 4

    def draw(self) -> None:
        """Draw UI elements"""
        self.window.fill(BLACK)
        # logo
        self.window.blit(
            self.logo_img,
            (
                self.logo_img_x,
                self.logo_img_y,
            ),
        )
        # up line
        pygame.draw.line(
            self.window,
            WHITE,
            (self.line_x[0], self.line1_y),
            (self.line_x[1], self.line1_y),
        )
        # bottom line
        pygame.draw.line(
            self.window,
            WHITE,
            (self.line_x[0], self.line2_y),
            (self.line_x[1], self.line2_y),
        )
        # buttons and selected box
        self.draw_game_select_buttons()
        # current page text
        self.window.blit(
            self.pages[self.current_page],
            (
                self.current_page_x,
                self.current_page_y,
            ),
        )

    def draw_game_select_buttons(self) -> None:
        """Draw game buttons"""
        btn_page = self.rom_buttons[
            self.current_page
            * self.page_size : (self.current_page + 1)
            * self.page_size
        ]
        btn_page.append(self.next_page_button)

        for idx, game_btn in enumerate(btn_page):
            x = self.button_x_offset + 80 if idx < 5 else self.second_column_x_offset
            y = self.button_y_offset + 40 * (idx % 5)
            if idx == self.selected_rom_index:
                pygame.draw.rect(
                    self.window,
                    WHITE,
                    (
                        x - self.btn_border_margin,
                        y - self.btn_border_margin,
                        game_btn.get_width() + self.btn_border_margin,
                        game_btn.get_height() + self.btn_border_margin,
                    ),
                    1,
                )
            self.window.blit(game_btn, (x, y))

    def getSceneKey(self) -> str:
        """Get unique scene key"""
        return MENU_SCENE_KEY

    def handleInputs(self, events, keyPressedList) -> None:
        """Handle inputs"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_rom_index += 1
                    if self.selected_rom_index >= self.current_page_size:
                        self.selected_rom_index = 0
                if event.key == pygame.K_UP:
                    self.selected_rom_index -= 1
                    if self.selected_rom_index < 0:
                        self.selected_rom_index = self.current_page_size - 1
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if self.selected_rom_index != self.current_page_size - 1:
                        self.goToScene(GAME_SCENE_KEY)
                    else:
                        self.current_page += 1
                        self.selected_rom_index = 0
                        last_page = (
                            self.current_page == len(self.roms) // self.page_size + 1
                        )
                        if last_page:
                            self.current_page = 0

    def read_files_from_folder(self, folder, extension) -> list[str]:
        """Get all file names from folder with required format"""
        return [
            f
            for f in listdir(folder)
            if isfile(join(folder, f)) and check_file_extension(f, extension)
        ]

    @property
    def current_page_size(self) -> int:
        """Count size of the current page (including next page button)"""
        last_page = self.current_page == len(self.roms) // self.page_size
        if last_page:
            return len(self.roms) % (self.current_page * self.page_size) + 1
        else:
            return self.page_size + 1

    def respond(self, requestID) -> str | None:
        """Provide selected rom to game scene"""
        if requestID == SELECTED_ROM:
            return self.roms[
                self.selected_rom_index + self.current_page * self.page_size
            ]
