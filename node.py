# pyright: reportMissingImports=false
import pygame
import pygame.gfxdraw

class Node:
    def __init__(self, id:int, x:int, y:int) -> None:
        self.id = id
        self.x  = x
        self.y  = y

    def draw(self, screen, font) -> None:
        pygame.gfxdraw.aacircle(screen, self.x, self.y, 15, (255, 240, 250))

        text_surface = font.render(f"{self.id}", True, (255, 240, 250))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, text_rect)


