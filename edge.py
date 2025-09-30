# pyright: reportMissingImports=false
import constants
from node import Node
import pygame

class Edge:
    _next_id = 0

    def __init__(self, a:Node, b:Node, is_directed=False) -> None:
        self.id = Edge._next_id
        Edge._next_id += 1

        self.a  = a
        self.b  = b
        self.is_directed = is_directed

    def draw(self, screen) -> None:
        pygame.draw.aaline(screen, 
                           constants.FOREGROUND,
                           (self.a.x, self.a.y), 
                           (self.b.x, self.b.y))


