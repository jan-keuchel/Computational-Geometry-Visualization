# pyright: reportMissingImports=false
import pygame
import pygame.gfxdraw

from typing import Callable, Dict, List, Union
from collections import defaultdict

import constants
from constants import BORDER_OFFSET, FOREGROUND, NODE_COMPACT_SIZE, NODE_FULL_SIZE, WIN_HEIGHT, WIN_WIDTH, graph_type, convex_hull_algos, mst_algos
import math_helper
from point import Point

import random


# -------------------------
# --------- Node ----------
# -------------------------
class Node:
    _next_id = 0

    def __init__(self, p:Point) -> None:
        self.id = Node._next_id
        Node._next_id += 1

        self.p = p

    def draw(self, screen, draw_compact=False, color=None) -> None:
        if color == None:
            color = constants.BLUE

        if draw_compact:
            w = NODE_COMPACT_SIZE
            pygame.gfxdraw.box(screen, (self.p.x - w/2, self.p.y - w/2, w, w), color)
        else:
            pygame.gfxdraw.filled_circle(screen, self.p.x, self.p.y, NODE_FULL_SIZE, color)
            pygame.gfxdraw.aacircle(screen, self.p.x, self.p.y, NODE_FULL_SIZE, constants.FOREGROUND)

            text_surface = constants.font.render(f"{self.id}", True, (FOREGROUND))
            text_rect = text_surface.get_rect(center=(self.p.x, self.p.y))
            screen.blit(text_surface, text_rect)

class NodeDrawContainer:
    def __init__(self, n:Node, draw_compact:bool, color) -> None:
        self.n = n
        self.draw_compact = draw_compact
        self.color = color

    def draw(self, screen) -> None:
        self.n.draw(screen, self.draw_compact, self.color)
        




# -------------------------
# --------- Edge ----------
# -------------------------
class Edge:
    _next_id: int = 0

    def __init__(self, 
                 a:Node,
                 b:Node,
                 weight=None) -> None:

        self.id = Edge._next_id
        Edge._next_id += 1

        self.a  = a
        self.b  = b

        if weight == None:
            self.weight: float = math_helper.distance(a.p, b.p)
        else:
            self.weight: float = weight


    def draw(self, screen, color=None, width=1) -> None:

        if color == None:
            color = constants.EDGE_COLOR
        pygame.draw.aaline(screen, 
                           color,
                           (self.a.p.x, self.a.p.y), 
                           (self.b.p.x, self.b.p.y),
                           width)

class EdgeDrawContainer:
    def __init__(self, e:Edge, color, width:int) -> None:
        self.e     = e
        self.color = color
        self.width = width

    def draw(self, screen) -> None:
        self.e.draw(screen, self.color, self.width)

    @staticmethod
    def convert_edge_list_to_Drawable_list(edges: List[Edge], col, w:int) -> List['Drawable']:
        edc_list: List[Drawable] = [
            EdgeDrawContainer(e, color=col, width=w)
            for e in edges
        ]
        return edc_list




# --------------------------
# --------- Graph ----------
# --------------------------
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

        self._mst_algos: Dict[mst_algos, Callable] = {
            mst_algos.PRIMS: self._mst_prims,
        }

        self._convex_hull_algos: Dict[convex_hull_algos, Callable] = {
            convex_hull_algos.BRUTE_FORCE: self._CH_brute_force,
            convex_hull_algos.GRAHAM_SCAN: self._CH_graham_scan,
            convex_hull_algos.JARVIS_MARCH: self._CH_jarvis_march,
        }

    def set_anim_step_callback(self, cb:Callable) -> None:
        self.anim_step = cb


    # -------------------------------------
    # --------- Graph Generation ----------
    # -------------------------------------

    def generate_graph(self, type: graph_type=graph_type.FULLY_CONNECTED, num_vertices=10):
        gen = self._graph_gen_algos[type]
        gen(num_vertices)

    def generate_random_nodes(self, num_vertices=10) -> None:
        """
        `_generate_random_nodes` generates `num_vertices` nodes
        at random locations with a minimal pair-wise distance
        of `constants.MIN_NODE_OFFSET`.
        """
        # Guarantee minimal distance of MIN_NODE_OFFSET 
        # between every pair of nodes.
        for _ in range(num_vertices):
            too_close = False
            x: int = random.randint(BORDER_OFFSET, WIN_WIDTH - BORDER_OFFSET)
            y: int = random.randint(BORDER_OFFSET, WIN_HEIGHT - BORDER_OFFSET)
            for v in self.V:
                if math_helper.distance(Point(x, y), v.p) < constants.MIN_NODE_OFFSET:
                    too_close = True
                    break

            while too_close:
                too_close = False
                x = random.randint(BORDER_OFFSET, WIN_WIDTH - BORDER_OFFSET)
                y = random.randint(BORDER_OFFSET, WIN_HEIGHT - BORDER_OFFSET)
                for v in self.V:
                    if math_helper.distance(Point(x, y), v.p) < constants.MIN_NODE_OFFSET:
                        too_close = True
                        break

            self.V.append(Node(Point(x, y)))


    # -------------------------------------
    # ----------- Convex Hull  ------------
    # -------------------------------------

    def calculate_convex_hull(self, algo:convex_hull_algos, animate=False) -> List[Node]:
        ch_algo = self._convex_hull_algos[algo]
        return ch_algo(animate)


    def _CH_brute_force(self, animate=False) -> List[Node]:
        """
        `_CH_brute_force` computes the convex hull of the graphs nodes.
        This is done by testing for every possible edge, if every other
        node is to the right of said edge. The way the convex hull is
        represented is a chain of points in clockwise order.
        Running time: O(n^3)
        Note: As the rendering is y-positive as downward, the image is drawn
        in counter-clockwise order!
        """
        CH: List[Node] = []
        CH_edges: List[Edge] = []

        # Calculate CH_edges:
        for u in self.V:
            for v in self.V:
                # Ensure u != v -> No self directed edge:
                if u.id == v.id: 
                    continue

                if animate:
                    draw_container: GraphDrawContainer = GraphDrawContainer()

                    # Add current Edge
                    draw_container.add_layer(EdgeDrawContainer.convert_edge_list_to_Drawable_list([Edge(u,v)], constants.RED, 3))

                    # Add asured CH edges
                    CH_layer: List[Drawable] = [
                        EdgeDrawContainer(e, color=constants.GREEN, width=5)
                        for e in CH_edges
                    ]
                    draw_container.add_layer(CH_layer)

                    # Add nodes for the end rendering
                    nodes_layer: List[Drawable] = [
                        NodeDrawContainer(n, draw_compact=False, color=constants.BLUE)
                        for n in self.V
                    ]
                    draw_container.add_layer(nodes_layer)
                    self.anim_step(draw_container)

                valid = True
                for w in self.V:
                    # Only compare other nodes to this potential edge:
                    if w.id == u.id or w.id == v.id: 
                        continue

                    if not (math_helper.right_of(u.p, v.p, w.p) > 0):
                        valid = False
                        break

                if valid:
                    CH_edges.append(Edge(u, v))

        # Extract Nodes in clock-wise order:
        start_edge = CH_edges.pop()
        CH.append(start_edge.a)
        CH.append(start_edge.b)
        while CH_edges:
            end_node = CH[-1]
            for e in CH_edges:
                if e.a.id == end_node.id: # Found next edge
                    CH.append(e.b)
                    CH_edges.remove(e)
                    break

        CH.pop()

        return CH

    def _CH_graham_scan(self, animate=False) -> List[Node]:
        """
        `_CH_graham_scan` is an implementation of the Graham's scan algorithm
        for computing the convex hull of a set of vertices.The way the 
        convex hull is represented is a chain of points in clockwise order.
        Running time: O(n*log(n))
        Note: As the rendering is y-positive as downward, the image is drawn
        in counter-clockwise order!
        """
        U: List[Node] = [] # Upper hull
        L: List[Node] = [] # Lower hull
        V = sorted(self.V, key=lambda v: (v.p.x, v.p.y))

        # Initialize upper hull
        U.append(V[0])
        U.append(V[1])

        for i in range(2, len(V)):
            U.append(V[i])

            if animate:
                draw_container: GraphDrawContainer = GraphDrawContainer()

                # Add edges of the current hull
                current_upper_hull: List[Drawable] = []
                for k in range(len(U) - 1):
                    current_upper_hull.append(EdgeDrawContainer(
                        Edge(U[k], U[k+1]), color=constants.ORANGE, width=3
                    ))
                draw_container.add_layer(current_upper_hull)

                # Add generic nodes
                nodes_layer: List[Drawable] = [
                    NodeDrawContainer(n, draw_compact=False, color=constants.BLUE)
                    for n in self.V
                ]
                draw_container.add_layer(nodes_layer)

                # Add nodes in CH
                CH_nodes: List[Drawable] = [
                    NodeDrawContainer(n, draw_compact=False, color=constants.RED)
                    for n in U
                ]
                draw_container.add_layer(CH_nodes)

                # Draw
                self.anim_step(draw_container)


            # While at least 3 nodes on the stack and last
            # 3 nodes make a left hand turn, pop the second to last
            # node off of the stack.
            while len(U) > 2 and math_helper.right_of(U[-3].p, U[-2].p, U[-1].p) < 0:
                U.remove(U[len(U) - 2])
                if animate:
                    draw_container: GraphDrawContainer = GraphDrawContainer()

                    # Add edges of the current hull
                    current_upper_hull: List[Drawable] = []
                    for k in range(len(U) - 1):
                        current_upper_hull.append(EdgeDrawContainer(
                            Edge(U[k], U[k+1]), color=constants.ORANGE, width=3
                        ))
                    draw_container.add_layer(current_upper_hull)

                    # Add generic nodes
                    nodes_layer: List[Drawable] = [
                        NodeDrawContainer(n, draw_compact=False, color=constants.BLUE)
                        for n in self.V
                    ]
                    draw_container.add_layer(nodes_layer)

                    # Add nodes in CH
                    CH_nodes: List[Drawable] = [
                        NodeDrawContainer(n, draw_compact=False, color=constants.RED)
                        for n in U
                    ]
                    draw_container.add_layer(CH_nodes)

                    # Draw
                    self.anim_step(draw_container)






        # Initialize lower hull
        L.append(V[-1])
        L.append(V[-2])

        for i in range(2, len(V)):
            L.append(V[len(V)-1-i])


            if animate:
                draw_container: GraphDrawContainer = GraphDrawContainer()

                # Add Upper Hull
                current_upper_hull: List[Drawable] = []
                for k in range(len(U) - 1):
                    current_upper_hull.append(EdgeDrawContainer(
                        Edge(U[k], U[k+1]), color=constants.GREEN, width=3
                    ))
                draw_container.add_layer(current_upper_hull)

                # Add edges of the current hull
                current_upper_hull: List[Drawable] = []
                for k in range(len(L) - 1):
                    current_upper_hull.append(EdgeDrawContainer(
                        Edge(L[k], L[k+1]), color=constants.ORANGE, width=3
                    ))
                draw_container.add_layer(current_upper_hull)

                # Add generic nodes
                nodes_layer: List[Drawable] = [
                    NodeDrawContainer(n, draw_compact=False, color=constants.BLUE)
                    for n in self.V
                ]
                draw_container.add_layer(nodes_layer)

                # Add nodes in CH
                CH_nodes: List[Drawable] = [
                    NodeDrawContainer(n, draw_compact=False, color=constants.RED)
                    for n in L
                ]
                draw_container.add_layer(CH_nodes)

                # Draw
                self.anim_step(draw_container)

            while len(L) > 2 and math_helper.right_of(L[-3].p, L[-2].p, L[-1].p) < 0:


                if animate:
                    L.remove(L[len(L) - 2])
                    draw_container: GraphDrawContainer = GraphDrawContainer()

                    # Add Upper Hull
                    current_upper_hull: List[Drawable] = []
                    for k in range(len(U) - 1):
                        current_upper_hull.append(EdgeDrawContainer(
                            Edge(U[k], U[k+1]), color=constants.GREEN, width=3
                        ))
                    draw_container.add_layer(current_upper_hull)

                    # Add edges of the current hull
                    current_upper_hull: List[Drawable] = []
                    for k in range(len(L) - 1):
                        current_upper_hull.append(EdgeDrawContainer(
                            Edge(L[k], L[k+1]), color=constants.ORANGE, width=3
                        ))
                    draw_container.add_layer(current_upper_hull)

                    # Add generic nodes
                    nodes_layer: List[Drawable] = [
                        NodeDrawContainer(n, draw_compact=False, color=constants.BLUE)
                        for n in self.V
                    ]
                    draw_container.add_layer(nodes_layer)

                    # Add nodes in CH
                    CH_nodes: List[Drawable] = [
                        NodeDrawContainer(n, draw_compact=False, color=constants.RED)
                        for n in L
                    ]
                    draw_container.add_layer(CH_nodes)

                    # Draw
                    self.anim_step(draw_container)

        # Remove duplicate Nodes
        L.pop(0)
        L.pop(-1)

        U.extend(L)
        return U


    def _CH_jarvis_march(self, animate=False) -> List[Node]:
        """
        `_CH_jarvis_march` is an implementation of the Jarvis March algorithm
        for computing the convex hull of a set of vertices. The way the 
        convex hull is represented is a chain of points in clockwise order.
        Running time: `O(n*k)` with `n` nodes and `k` nodes in the convex hull.
        Note: As the rendering is y-positive as downward, the image is drawn
        in counter-clockwise order!
        """

        CH: List[Node] = []
        others: List[Node] = self.V.copy()

        # Find left most point
        current: Node = self.V[0]
        for v in self.V:
            if v.p.x < current.p.x:
                current = v

        CH.append(current)

        # Take first node as potential new_node that isn't the left most node
        others.remove(current)
        new_node: Node = others[0]
        others.append(current)
        
        for _ in range(len(self.V)):
            # Find new node of CH
            for p in others:
                if math_helper.right_of(current.p, new_node.p, p.p) < 0:
                    new_node = p

            current = new_node
            CH.append(current)
            others.remove(current)

            if new_node.id == CH[0].id:
                break

            # Choose new node that is not the "target" node
            others.remove(CH[0])
            new_node = others[0]
            others.append(CH[0])

        return CH

    # --------------------------------
    # ----------- Helper  ------------
    # --------------------------------


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

    def empty_graph(self) -> None:
        self.clear_edges()
        self.clear_vertices()

    def clear_edges(self) -> None:
        """
        `_clear_edges` deletes all edge data stored in the Graph class.
        Meaning: `Graph.E` is cleared and the adjacency matrix `adj_mat`
        is emptied.
        """
        self.E.clear()
        self.adj_mat.clear()

    def clear_vertices(self) -> None:
        self.V.clear()


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
        self.generate_random_nodes(num_vertices)

        for i in range(len(self.V)):
            for j in range(i + 1, len(self.V)):
                self._add_edge(self.V[i], self.V[j])

    def _gen_mst(self, num_vertices=10) -> None:
        """
        `_gen_mst` generates a minimal spanning tree based on the graphs nodes.
        """
        self._gen_fully_connected(num_vertices)

        mst = self._mst_prims()

        self.clear_edges()
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

    def mst(self, algo:mst_algos) -> List[Edge]:
        mst_algo = self._mst_algos[algo]
        return mst_algo()


    def _mst_prims(self) -> List[Edge]:
        """
        Only for undirected graphs.
        """

        union = CustomUnion(len(self.V))
        edges = sorted(self.E, key=lambda e: e.weight, reverse=True)
        mst: List[Edge] = []

        for _ in range(len(self.V) - 1):

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

class CustomUnion:
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




# -------------------------------
# --------- Animations ----------
# -------------------------------

Drawable = Union[NodeDrawContainer, EdgeDrawContainer]

class GraphDrawContainer:
    def __init__(self) -> None:
        self.layers: List[List[Drawable]] = []

    def add_layer(self, layer: List[Drawable]) -> None:
        self.layers.append(layer)

    def get_all_drawables(self) -> List[Drawable]:
        return [drawable for layer in self.layers for drawable in layer]

    def empty(self) -> None:
        self.layers.clear()

