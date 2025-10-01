from typing import List

import constants
import math_helper
from edge import Edge
from node import Node
from point import Point

import random



class Graph:
    def __init__(self,  V: List[Node] | None = None,
                 E: List[Edge] | None = None) -> None:
        self.V: List[Node] = V if V is not None else []
        self.E: List[Edge] = E if E is not None else []

    def _generate_random_nodes(self, num_vertices=10) -> None:
        # Guarantee minimal distance of MIN_NODE_OFFSET 
        # between every pair of nodes.
        for _ in range(num_vertices):
            too_close = False
            x: int = random.randint(30, 770)
            y: int = random.randint(30, 570)
            for v in self.V:
                if math_helper.distance(Point(x, y), v.p) < constants.MIN_NODE_OFFSET:
                    too_close = True
                    break

            while too_close:
                too_close = False
                x = random.randint(30, 770)
                y = random.randint(30, 570)
                for v in self.V:
                    if math_helper.distance(Point(x, y), v.p) < constants.MIN_NODE_OFFSET:
                        too_close = True
                        break

            self.V.append(Node(Point(x, y)))

    def generate_fully_connected(self, num_vertices=10) -> None:
        self._generate_random_nodes(num_vertices)

        for i in range(len(self.V)):
            for j in range(i + 1, len(self.V)):
                u = self.V[i]
                v = self.V[j]
                self.E.append(Edge(u, v, is_directed=False))

    def draw(self, screen, draw_compact=False) -> None:
        for e in self.E:
            e.draw(screen)
        for v in self.V:
            v.draw(screen, draw_compact)
