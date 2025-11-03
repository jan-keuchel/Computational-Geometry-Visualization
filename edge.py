# pyright: reportMissingImports=false
import pygame

import constants
import math_helper
from node import Node


class Edge:
    _next_id: int = 0

    def __init__(self, 
                 a:Node,
                 b:Node,
                 weight=None) -> None:

        self.id = Edge._next_id
        Edge._next_id += 1

        self.a  = a
        self.b  = b

        if weight == None:
            self.weight: float = math_helper.distance(a.p, b.p)
        else:
            self.weight: float = weight

    def other(self, n:Node) -> Node:
        if self.a == n:
            return self.b
        else:
            return self.a


    def draw(self, screen, color=None, width=1) -> None:

        if color == None:
            color = constants.EDGE_COLOR
        pygame.draw.aaline(screen, 
                           color,
                           (self.a.p.x, self.a.p.y), 
                           (self.b.p.x, self.b.p.y),
                           width)

class EdgeDrawContainer:
    def __init__(self, e:Edge, color, width:int) -> None:
        self.e     = e
        self.color = color
        self.width = width

    def draw(self, screen) -> None:
        self.e.draw(screen, self.color, self.width)
