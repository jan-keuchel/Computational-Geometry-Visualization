# pyright: reportMissingImports=false
import constants
import math_helper
from node import Node
import pygame

class Edge:
    _next_id: int = 0

    def __init__(self, 
                 a:Node,
                 b:Node,
                 weight=None,
                 is_directed=False) -> None:

        self.id = Edge._next_id
        Edge._next_id += 1

        self.a  = a
        self.b  = b
        self.is_directed = is_directed

        if weight == None:
            self.weight: float = math_helper.distance(a.p, b.p)
        else:
            self.weight: float = weight


    def draw(self, screen) -> None:
        pygame.draw.aaline(screen, 
                           constants.FOREGROUND,
                           (self.a.p.x, self.a.p.y), 
                           (self.b.p.x, self.b.p.y))


