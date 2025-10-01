# pyright: reportMissingImports=false
import constants
from point import Point
import pygame
import pygame.gfxdraw


class Node:
    _next_id = 0

    @staticmethod
    def add_edge(a: "Node", b: "Node", edge) -> bool:
        """
        add_edge adds a connection to the specified nodes. `a`, `b` must
        differ. Also: `a == edge.a` and `b == edge.b` is mandatory.
        In case of a non-directed edge, it is automatically added to
        both nodes.
        """

        # No self directed edge
        if a == b:
            return False
        
        # Edge needs to be specified in relation to given a, b
        if a != edge.a or b != edge.b:
            return False

        if edge.is_directed:
            edge.a._add_edge(edge.b, edge)
        else:
            edge.a._add_edge(edge.b, edge)
            edge.b._add_edge(edge.a, edge)

        return True

    def __init__(self, p:Point) -> None:
        self.id = Node._next_id
        Node._next_id += 1

        self.p = p

        self.edges = {} # [id] --> Edge

    def _add_edge(self, neighbor:"Node", edge) -> bool:
        """
        _add_edge adds the given edge `edge` to the edge map of `self`.
        In case `edge` is directed and points to `self` the function
        returns without alterations.
        Note: For non-directed edges both edge maps of `edge.a` and `edge.b`
        have to be updated manually!
        """

        if edge.is_directed and edge.a != self:
            return False

        self.edges[neighbor] = edge
        return True

    def draw(self, screen, draw_compact=False) -> None:
        if draw_compact:
            w = 8
            pygame.gfxdraw.box(screen, (self.p.x - w/2, self.p.y - w/2, w, w), constants.BLUE)
        else:
            pygame.gfxdraw.filled_circle(screen, self.p.x, self.p.y, 15, constants.BLUE)
            pygame.gfxdraw.aacircle(screen, self.p.x, self.p.y, 15, constants.FOREGROUND)

            text_surface = constants.font.render(f"{self.id}", True, (255, 240, 250))
            text_rect = text_surface.get_rect(center=(self.p.x, self.p.y))
            screen.blit(text_surface, text_rect)


