import math

from point import Point

def distance(p1:Point, p2:Point) -> float:
    return math.sqrt(math.pow(p2.x - p1.x, 2) + \
                     math.pow(p2.y - p1.y, 2))

def right_of(a1:Point, a2:Point, v:Point) -> float:
    """
    Returns
    `x` > 0 iff `v` is right of line `a1`--`a2`. 
    `x` = 0 iff `v` is on the line `a1`--`a2`
    `x` < 0 iff `v` is left of line `a1`--`a2`
    """
    return ((a2.y - a1.y) * (v.x - a1.x) - (a2.x - a1.x) * (v.y - a1.y))


def line_segment_intersection(a1:Point, a2:Point, b1:Point, b2:Point) -> bool:
    """
    Returns `True` iff line A intersects with line B. Endpoints included.
    """
    return ((right_of(a1, a2, b1) * right_of(a1, a2, b2) < 0) and 
            (right_of(b1, b2, a1) * right_of(b1, b2, a2) < 0))


