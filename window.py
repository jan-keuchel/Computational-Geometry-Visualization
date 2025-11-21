# pyright: reportMissingImports=false
import pygame

import constants

class Window:
    def __init__(self, width, height) -> None:
        self.screen = pygame.display.set_mode((width, height))

    def clear(self):
        self.screen.fill(constants.BACKGROUND)

    def render(self):
        pygame.display.flip()
