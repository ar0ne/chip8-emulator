import pygame
from pygame.locals import *

WHITE = (255, 255, 255)


class NesFont:
    """Custom font"""

    def __init__(self):

        # Dict to hold the letter images
        self.letters = {}

        letters = {}
        format = " abcdefghijklmnopqrstuvwxyz0123456789-+:,.=!)(?><"
        self.font = {"file": "nes-font.png", "size": (8, 8)}
        self.color = WHITE
        strip = pygame.image.load("menu/nes-font.png").convert_alpha()
        i = 0
        for x in range(len(format)):
            letters[format[i]] = pygame.Surface(self.font["size"])
            letters[format[i]].blit(strip, (-x * self.font["size"][0], 0))
            i += 1

        # Create the letters
        for letter in letters:
            letterimg = letters[letter]
            self.letters[letter] = pygame.Surface(self.font["size"])
            self.letters[letter].set_colorkey((0, 0, 0), RLEACCEL)
            for y in range(letterimg.get_height()):
                for x in range(letterimg.get_width()):
                    if letterimg.get_at((x, y)) == (255, 255, 255, 255):
                        self.letters[letter].set_at((x, y), WHITE)
                    x += 1
                y += 1

    def render(self, text):
        text = text.lower()
        img = pygame.Surface((len(text) * self.font["size"][0], self.font["size"][1]))
        img.set_colorkey((0, 0, 0), RLEACCEL)
        pos = 0
        for char in text:
            if char in self.letters:
                img.blit(self.letters[char], (pos, 0))
            pos += self.font["size"][0]
        return img

    def get_width(self):
        return self.font["size"][0]

    def get_height(self):
        return self.font["size"][1]
