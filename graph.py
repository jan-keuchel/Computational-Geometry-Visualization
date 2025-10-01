from typing import List

import constants
from edge import Edge
from node import Node
from point import Point

import random



class Graph:
    def __init__(self,  V: List[Node] | None = None,
                 E: List[Edge] | None = None) -> None:
        self.V: List[Node] = V if V is not None else []
        self.E: List[Edge] = E if E is not None else []

    def init(self) -> None:
        self.V.append(Node(Point(100, 100)))
        self.V.append(Node(Point(300, 180)))
        self.V.append(Node(Point(150, 250)))

        self.E.append(Edge(self.V[0], self.V[1]))
        self.E.append(Edge(self.V[1], self.V[2]))

        Node._add_edge(self.V[0], self.V[1], self.E[0])
        Node._add_edge(self.V[1], self.V[2], self.E[1])

    def generate_random(self, num_vertices=10) -> None:
        for _ in range(num_vertices):
            x: int = random.randint(30, 770)
            y: int = random.randint(30, 570)
            self.V.append(Node(Point(x, y)))

    def generate_fully_connected(self, num_vertices=10) -> None:
        for _ in range(num_vertices):
            x: int = random.randint(30, 770)
            y: int = random.randint(30, 570)
            self.V.append(Node(Point(x, y)))

        for i in range(len(self.V)):
            for j in range(i + 1, len(self.V)):
                u = self.V[i]
                v = self.V[j]
                self.E.append(Edge(u, v, False))

    def draw(self, screen, draw_compact=False) -> None:
        for e in self.E:
            e.draw(screen)
        for v in self.V:
            v.draw(screen, draw_compact)
