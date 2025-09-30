from typing import List

import constants
from edge import Edge
from node import Node
from point import Point



class Graph:
    def __init__(self,  V: List[Node] | None = None,
                 E: List[Edge] | None = None) -> None:
        self.V = V if V is not None else []
        self.E = E if E is not None else []

    def init_graph(self) -> None:
        self.V.append(Node(Point(100, 100)))
        self.V.append(Node(Point(300, 180)))
        self.V.append(Node(Point(150, 250)))

        self.E.append(Edge(self.V[0], self.V[1]))
        self.E.append(Edge(self.V[1], self.V[2]))

        Node._add_edge(self.V[0], self.V[1], self.E[0])
        Node._add_edge(self.V[1], self.V[2], self.E[1])

    def draw(self, screen) -> None:
        for e in self.E:
            e.draw(screen)
        for v in self.V:
            v.draw(screen)
