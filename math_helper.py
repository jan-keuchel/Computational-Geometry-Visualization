import math

from point import Point

def distance(p1:Point, p2:Point) -> float:
    return math.sqrt(math.pow(p2.x - p1.x, 2) + \
                     math.pow(p2.y - p1.y, 2))





