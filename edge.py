# pyright: reportMissingImports=false
import constants
from point import Point
import pygame

class Edge:
    def __init__(self, id:int, a:Point, b:Point) -> None:
        self.id = id
        self.a  = a
        self.b  = b

    def draw(self, screen) -> None:
        pygame.draw.aaline(screen, 
                           constants.FOREGROUND,
                           (self.a.x, self.a.y), 
                           (self.b.x, self.b.y))


