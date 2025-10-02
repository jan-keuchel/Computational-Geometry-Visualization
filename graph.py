from typing import Callable, Dict, List
from collections import defaultdict

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

        self.adj_mat: Dict[int, Dict[int, Edge]] = defaultdict(dict)

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
        """
        `_generate_random_nodes` generates `num_vertices` nodes
        at random locations with a minimal pair-wise distance
        of `constants.MIN_NODE_OFFSET`.
        """
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

    def _add_random_ni_edge_from_node(self, n:Node) -> bool:
        """
        Adds a random non-intersecting edge to the graph that 
        starts at `n`. As this is not always possible, the return 
        value indicates the success of the operation.
        """
        if not n in self.V:
            return False

        remaining_nodes = self.V.copy()
        remaining_nodes.remove(n)

        u = random.choice(self.V)
        new_edge = Edge(n, u)

        found_intersect = True
        while found_intersect:
            if not remaining_nodes:
                return False

            u = random.choice(remaining_nodes)
            if u.id == n.id or u.id in self.adj_mat[n.id]:
                remaining_nodes.remove(u)
                continue

            found_intersect = False
            new_edge = Edge(n, u)

            for e in self.E:
                if math_helper.line_segment_intersection(new_edge.a.p, new_edge.b.p, e.a.p, e.b.p):
                    found_intersect = True
                    remaining_nodes.remove(u)
                    break

        self._add_edge(new_edge.a, new_edge.b)
        return True

    def _add_random_ni_edge(self) -> bool:
        """
        Adds a random non-intersecting edge to the graph. As this is not always
        possible the return value indicates the success of the operation.
        """
        # TODO
        return True

    def _clear_edges(self) -> None:
        """
        `_clear_edges` deletes all edge data stored in the Graph class.
        Meaning: `Graph.E` is cleared and the adjacency matrix `adj_mat`
        is emptied.
        """
        self.E.clear()
        self.adj_mat.clear()

    def _set_edges(self, E:List[Edge]) -> None:
        """
        `_set_edges` sets the list of edges of the Graph to the provided
        edges `E` and updates the adjacency matrix accordingly.
        """
        self.E = E
        for e in self.E:
            self._update_adjacency_matrix(e.a, e.b, e)

    def _update_adjacency_matrix(self, a:Node, b:Node, e:Edge) -> None:
        """
        `_update_adjacency_matrix` updates on cell of the adjacency
        matrix with at the proivded index with the proivded edge.
        """
        self.adj_mat[a.id][b.id] = e
        self.adj_mat[b.id][a.id] = e

    def _add_edge(self, a:Node, b:Node) -> bool:
        """
        `_add_edge` inserts a new edge into the list of edges `Graph.E`
        and updates the adjacency matrix.
        Conditions:
        - Self-directed eges are ignored.
        - Egges that are already present are ignored.
        """
        # No self directed edges
        if a.id == b.id:
            return False

        # Edge a-->b or b-->a already present
        if (b.id in self.adj_mat[a.id]) or (a.id in self.adj_mat[b.id]):
            return False

        new_edge = Edge(a, b)
        self.E.append(new_edge)
        self._update_adjacency_matrix(a, b, new_edge)

        return True
        

    def _gen_fully_connected(self, num_vertices=10) -> None:
        """
        `_gen_fully_connected` generates a fully connected graph.
        """
        self._generate_random_nodes(num_vertices)

        for i in range(len(self.V)):
            for j in range(i + 1, len(self.V)):
                self._add_edge(self.V[i], self.V[j])

    def _gen_mst(self, num_vertices=10) -> None:
        """
        `_gen_mst` generates a minimal spanning tree based on the graphs nodes.
        """
        self._gen_fully_connected(num_vertices)

        mst = mst_prims(self)

        self._clear_edges()
        self._set_edges(mst)

    def _gen_mst_no_deg_1(self, num_vertices=10) -> None:
        """
        `_gen_mst_no_deg_1` first generates a minimal spanning tree
        and then adds in additional edges to the nodes that have a
        degree of 1. The new edges will not intersect with other edges.
        """
        self._gen_mst(num_vertices)

        for v in self.V:
            if len(self.adj_mat[v.id]) == 1: # Nodes of degree 1
                self._add_random_ni_edge_from_node(v)

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

    def print(self) -> None:
        print("Nodes:")
        for i, n in enumerate(self.V):
            print(f"degree(node_{n.id}) = ", len(self.adj_mat[n.id]))
        print("Edges:")
        for i, edge in enumerate(self.E):
            print(f"edges[{i}]: {edge.a.id} -- {edge.b.id}")
        
        print("\nAdjacency Matrix:")
        for node_id in sorted(self.adj_mat.keys()):
            neighbors = {}
            for nb_id, edge in self.adj_mat[node_id].items():
                neighbors[nb_id] = f"Edge(id={edge.id}, weight={edge.weight:.2f})"
            print(f"map[{node_id}] = {neighbors}")


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




