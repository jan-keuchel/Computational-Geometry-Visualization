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

        self.p = p

    def draw(self, screen, draw_compact=False, color=None) -> None:
        if color == None:
            color = constants.BLUE

        if draw_compact:
            w = 8
            pygame.gfxdraw.box(screen, (self.p.x - w/2, self.p.y - w/2, w, w), color)
        else:
            pygame.gfxdraw.filled_circle(screen, self.p.x, self.p.y, 15, color)
            pygame.gfxdraw.aacircle(screen, self.p.x, self.p.y, 15, constants.FOREGROUND)

            text_surface = constants.font.render(f"{self.id}", True, (255, 240, 250))
            text_rect = text_surface.get_rect(center=(self.p.x, self.p.y))
            screen.blit(text_surface, text_rect)



class NodeDrawContainer:
    def __init__(self, n:Node, draw_compact:bool, color) -> None:
        self.n = n
        self.draw_compact = draw_compact
        self.color = color

    def draw(self, screen) -> None:
        self.n.draw(screen, self.draw_compact, self.color)
        
