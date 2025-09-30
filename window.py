# pyright: reportMissingImports=false
import pygame

class Window:
    def __init__(self, width, height) -> None:
        self.screen = pygame.display.set_mode((width, height))
        self.font   = pygame.font.SysFont('Hack Nerd Font', 18)

    def clear(self):
        self.screen.fill((30, 30, 35))

    def render(self):
        pygame.display.flip()
