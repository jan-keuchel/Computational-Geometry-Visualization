# pyright: reportMissingImports=false
import random
from typing import List
import constants
from graph import Edge, Graph, GraphDrawContainer, Node
from point import Point
from window import Window
import pygame


class Visualizer:
    def __init__(self) -> None:
        self.window = Window(constants.WIN_WIDTH, constants.WIN_HEIGHT)
        self.G: Graph = Graph()
        self.G.set_anim_step_callback(self.anim_step)
        self.clock = pygame.time.Clock()
        self.CH: List[Node] = []
        self.MST: List[Edge] = []
        self.intersections: List[Node] = []

    def reset_graph(self) -> None:
        """
        `reset_graph` deletes all calcualted structures such as 
        convex hulls or MSTs. The nodes stay the same.
        """
        self.G.empty_graph()

    def new_nodes(self, num_nodes=10) -> None:
        """
        `new_nodes` deletes the entire graph with it's associated data
        and generates a new set of nodes.
        """
        self.reset_graph()
        self.G.generate_random_nodes(num_nodes)

    def new_segments(self, num_segments=10) -> None:
        """
        `new_segments` generates `num_segments` random segments in the plane.
        """
        self.new_nodes(2 * num_segments);
        nodes: List[Node] = self.G.V.copy()
        for _ in range(num_segments):
            u: Node = random.choice(nodes)
            nodes.remove(u)
            v: Node = random.choice(nodes)
            nodes.remove(v)
            self.G._add_edge(u, v)

    def new_custom_nodes(self) -> None:
        """
        `new_custom_nodes` switches to an interactive mode where the user 
        can manually place nodes onto the plane via mouse clicks. Clicking
        the left mouse button adds a node. Clicking the right mouse button
        removes the last added node.
        """
        self.reset_graph()

        continue_with_input = True
        while continue_with_input:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if len(self.G.V) < 3:
                            print("Please add at least 3 vertices.")
                            continue
                        continue_with_input = False
                        print("Done.")

                    if event.key == pygame.K_r:
                        self.reset_graph()
                        self.clear_screen()
                        self.render_screen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # LMB
                        x,y = pygame.mouse.get_pos()
                        self.G.add_node(Point(x, y))
                    if event.button == 3: # RMB
                        self.G.pop_node()
                    self.clear_screen()
                    self.render_nodes(True, constants.BLUE)
                    self.render_screen()



    def line_segment_intersection(self, algo: constants.line_segment_intersection_algos, animate=False):
        """
        `line_segment_intersection` finds all intersection between every line segments (edges).
        If no set of segments (edges) is present a new number of segments will be generated.
        """
        if len(self.G.V) == 0:
            self.new_segments()

        self.intersections = self.G.calculate_line_segement_intersections(algo, animate)


    def new_graph(self, type: constants.graph_type, num_nodes=20) -> None:
        self.G.generate_graph(type, num_nodes)


    def convex_hull(self, algo:constants.convex_hull_algos, animate=False) -> None:
        """
        `convex_hull` calcualtes the convex hull of the present set of nodes.
        If no set of nodes is present a new set will be generated. The algorithm
        used to caluclate the convex hull is specified in `algo`.
        """
        if len(self.G.V) == 0:
            self.new_nodes()

        self.CH = self.G.calculate_convex_hull(algo, animate)

    def mst(self, algo:constants.mst_algos) -> None:
        if self.G.E == None:
            self.new_nodes() # TODO: Generate fully connected

        self.MST  = self.G.mst(algo)

    # -------------------------------------------
    # ------------- Rendering -------------------
    # -------------------------------------------

    def clear_screen(self) -> None:
        self.window.clear()

    def render_screen(self) -> None:
        self.window.render()

    def render_nodes(self, compact=False, color=constants.ORANGE) -> None:
        self.G.draw_nodes(self.window.screen, color, compact)

    def render_intersects(self, compact=False, color=constants.GREEN) -> None:
        for v in self.intersections:
            v.draw(self.window.screen, compact, color)

    def render_edges(self,
                     edge_color=constants.EDGE_COLOR,
                     edge_width=1) -> None:
        self.G.draw_edges(
            self.window.screen,
            edge_color,
            edge_width
        )

    def render_graph(self, 
                     edge_color=constants.EDGE_COLOR,
                     edge_width=1,
                     compact=False,
                     node_col=constants.ORANGE) -> None:
        self.G.draw(
            self.window.screen,
            edge_col=edge_color,
            edge_width=edge_width,
            node_col=node_col,
            node_draw_compact=compact
        )

    def render_mst(self,
                   edge_col=constants.GREEN,
                   edge_width=2) -> None:
        if len(self.MST) == 0:
            self.mst(constants.mst_algos.PRIMS)

        for e in self.MST:
            e.draw(self.window.screen, edge_col, edge_width)

    def render_convex_hull(self,
                           edge_color=constants.RED,
                           edge_width=2,
                           animate=False) -> None:
        if self.CH == None:
            self.convex_hull(constants.convex_hull_algos.BRUTE_FORCE, animate)

        for i in range(len(self.CH)):
            Edge(self.CH[i], self.CH[(i+1) % len(self.CH)]).draw(
                self.window.screen, edge_color, edge_width
            )

    def anim_step(self, graph_container:GraphDrawContainer) -> None:
        self.clear_screen()
        drawables = graph_container.get_all_drawables()
        for drawable in drawables:
            drawable.draw(self.window.screen)

        self.render_screen()
        self.clock.tick(constants.FPS)
