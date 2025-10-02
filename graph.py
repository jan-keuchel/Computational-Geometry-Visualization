from typing import Callable, Dict, List

import constants
from constants import graph_type
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

        self._graph_gen_algos: Dict[graph_type, Callable] = {
            graph_type.FULLY_CONNECTED: self._gen_fully_connected,
            graph_type.MST: self._gen_mst,
            graph_type.MST_NO_DEG_1: self._gen_mst_no_deg_1,
        }

    # -------------------------------------
    # --------- Graph Generation ----------
    # -------------------------------------
    def generate_graph(self, type: graph_type=graph_type.FULLY_CONNECTED, num_vertices=10):
        gen = self._graph_gen_algos[type]
        gen(num_vertices)

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

    def _clear_edges(self) -> None:
        for v in self.V:
            v.edges.clear()
        self.E.clear()

    def _set_edges(self, E:List[Edge]) -> None:
        self.E = E
        for e in self.E:
            Node.add_edge(e.a, e.b, e)

    def _add_edge(self, e:Edge) -> None:
        self.E.append(e)
        Node.add_edge(e.a, e.b, e)

    def _gen_fully_connected(self, num_vertices=10) -> None:
        self._generate_random_nodes(num_vertices)

        for i in range(len(self.V)):
            for j in range(i + 1, len(self.V)):
                u = self.V[i]
                v = self.V[j]
                e = Edge(u, v, is_directed=False)
                self._add_edge(e)

    def _gen_mst(self, num_vertices=10) -> None:
        self._gen_fully_connected(num_vertices)

        mst = mst_prims(self)

        self._clear_edges()
        self._set_edges(mst)

    def _gen_mst_no_deg_1(self, num_vertices=10) -> None:
        self._gen_mst(num_vertices)

        for v in self.V:
            if len(v.edges) == 1: # Nodes of degree 1
                u = random.choice(self.V)
                new_edge = Edge(v, u)

                found_intersect = True
                while found_intersect:
                    u = random.choice(self.V)
                    if u == v or u in v.edges:
                        continue

                    found_intersect = False
                    new_edge = Edge(v, u)

                    for e in self.E:
                        if math_helper.line_segment_intersection(new_edge.a.p, new_edge.b.p, e.a.p, e.b.p):
                            found_intersect = True
                            break

                self._add_edge(new_edge)

    # ------------------------------
    # --------- Rendering ----------
    # ------------------------------

    def draw(self, screen, edge_col=None, edge_width=1, node_col=None, node_draw_compact=False) -> None:
        self.draw_edges(screen, edge_col, edge_width)
        self.draw_nodes(screen, node_col, node_draw_compact)

    def draw_edges(self, screen, color=None, width=1) -> None:
        if color == None:
            color = constants.EDGE_COLOR
        for e in self.E:
            e.draw(screen, color, width)

    def draw_nodes(self, screen, color=None, draw_compact=False) -> None:
        if color == None:
            color = constants.FOREGROUND
        for v in self.V:
            v.draw(screen, draw_compact)


# ------------------------------------
# ----------- Algorithms  ------------
# ------------------------------------

def _all_eq(ints:List[int]) -> bool:
    return all(x == ints[0] for x in ints)

def mst_prims(G:Graph):
    """
    Only for undirected graphs.
    """

    union = Union(len(G.V))
    edges = sorted(G.E, key=lambda e: e.weight, reverse=True)
    mst: List[Edge] = []

    for _ in range(len(G.V) - 1):

        smallest_edge = edges.pop()
        u = smallest_edge.a
        v = smallest_edge.b

        while union.get_representative(u.id) == union.get_representative(v.id):
            smallest_edge = edges.pop()
            u = smallest_edge.a
            v = smallest_edge.b

        union.union(u.id, v.id)
        mst.append(smallest_edge)

    return mst




# ------------------------------------
# --------- Data structures ----------
# ------------------------------------

class Union:
    def __init__(self, n:int) -> None:
        self._representatives: List[int] = list(range(n))

    def union(self, u:int, v:int) -> None:
        if u == v:
            return
        
        rep_u = self._representatives[u]
        rep_v = self._representatives[v]

        (new_rep, to_replace) = (rep_u, rep_v) if rep_u < rep_v else (rep_v, rep_u)

        for i in range(len(self._representatives)):
            if self._representatives[i] == to_replace:
                self._representatives[i] = new_rep

    def get_representative(self, idx:int) -> int:
        return self._representatives[idx]




