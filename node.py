# pyright: reportMissingImports=false
import pygame

import constants
from constants import NODE_FULL_SIZE, NODE_COMPACT_SIZE, FOREGROUND
from point import Point


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
            w = NODE_COMPACT_SIZE
            pygame.gfxdraw.box(screen, (self.p.x - w/2, self.p.y - w/2, w, w), color)
        else:
            pygame.gfxdraw.filled_circle(screen, self.p.x, self.p.y, NODE_FULL_SIZE, color)
            pygame.gfxdraw.aacircle(screen, self.p.x, self.p.y, NODE_FULL_SIZE, FOREGROUND)

            text_surface = constants.font.render(f"{self.id}", True, (FOREGROUND))
            text_rect = text_surface.get_rect(center=(self.p.x, self.p.y))
            screen.blit(text_surface, text_rect)

class NodeDrawContainer:
    def __init__(self, n:Node, draw_compact:bool, color) -> None:
        self.n = n
        self.draw_compact = draw_compact
        self.color = color

    def draw(self, screen) -> None:
        self.n.draw(screen, self.draw_compact, self.color)
        
