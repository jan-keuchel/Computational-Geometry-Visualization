# pyright: reportMissingImports=false
import constants
from point import Point
import pygame
import pygame.gfxdraw

class Node:
    _next_id = 0

    def __init__(self, p:Point) -> None:
        self.id = Node._next_id
        Node._next_id += 1

        self.x  = p.x
        self.y  = p.y

    def draw(self, screen, font, draw_compact=False) -> None:
        if draw_compact:
            w = 8
            pygame.gfxdraw.box(
                screen,
                (self.x - w/2, self.y - w/2,
                 w, w),
                constants.RED
            )
            pygame.gfxdraw.rectangle(
                screen,
                (self.x - w/2, self.y - w/2,
                 w, w),
                constants.FOREGROUND
            )
        else:
            pygame.gfxdraw.filled_circle(screen, self.x, self.y, 15, constants.BLUE)
            pygame.gfxdraw.aacircle(screen, self.x, self.y, 15, constants.FOREGROUND)

            text_surface = font.render(f"{self.id}", True, (255, 240, 250))
            text_rect = text_surface.get_rect(center=(self.x, self.y))
            screen.blit(text_surface, text_rect)


