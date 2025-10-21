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


# https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment
def point_line_segment_intersection(a1:Point, a2:Point, b1:Point, b2:Point, p:Point) -> bool:
    """
    `point_line_segment_intersection` calculates the point of intersection between
    the lines a1 -- a2 and b1 -- b2. The resulting 
    """
    x1: float = a1.x
    x2: float = a2.x
    x3: float = b1.x
    x4: float = b2.x

    y1: float = a1.y
    y2: float = a2.y
    y3: float = b1.y
    y4: float = b2.y

    denom: float = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
    if denom == 0:
        return False

    t: float =  ((x1 - x3)*(y3 - y4) - (y1 - y3)*(x3 - x4)) / denom
    u: float =  ((x1 - x2)*(y1 - y3) - (y1 - y2)*(x1 - x3)) / denom

    if not (t >= 0 and t <= 1 and u >= 0 and u <= 1):
        return False

    p.x = int(x1 + t * (x2 - x1))
    p.y = int(y1 + t * (y2 - y1))

    return True
