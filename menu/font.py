import pygame
from pygame.locals import *

from menu.constants import BLACK, WHITE


class Font:
    """Custom font for retro games"""

    MAPPING = " abcdefghijklmnopqrstuvwxyz0123456789-+:,.=!)(?><"

    def __init__(
        self,
        font_path: str,
        font_size: tuple[int, int],
        color: tuple[int, int, int] = WHITE,
    ) -> None:
        """Init font"""
        self.font_size = font_size
        self.color = color
        # Dict to hold the letter images
        self.letters = {}
        letters = {}
        strip = pygame.image.load(font_path).convert_alpha()
        for i, x in enumerate(range(len(self.MAPPING))):
            letters[self.MAPPING[i]] = pygame.Surface(self.font_size)
            letters[self.MAPPING[i]].blit(strip, (-x * self.font_size[0], 0))

        # Create the letters
        for letter in letters:
            letter_img = letters[letter]
            self.letters[letter] = pygame.Surface(self.font_size)
            self.letters[letter].set_colorkey((0, 0, 0), RLEACCEL)
            for y in range(letter_img.get_height()):
                for x in range(letter_img.get_width()):
                    if letter_img.get_at((x, y)) == (255, 255, 255, 255):
                        self.letters[letter].set_at((x, y), WHITE)
                    x += 1
                y += 1

    def render(self, text: str) -> pygame.Surface:
        """Render image for text"""
        text = text.lower()
        img = pygame.Surface((len(text) * self.font_size[0], self.font_size[1]))
        img.set_colorkey(BLACK, RLEACCEL)
        pos = 0
        for char in text:
            if char in self.letters:
                img.blit(self.letters[char], (pos, 0))
            pos += self.font_size[0]
        return img

    def get_width(self) -> int:
        """Get font width"""
        return self.font_size[0]

    def get_height(self) -> int:
        """Get font height"""
        return self.font_size[1]
