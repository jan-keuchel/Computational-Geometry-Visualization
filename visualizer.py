from typing import List
import constants
from edge import Edge
from graph import Graph
from node import Node
from window import Window


class Visualizer:
    def __init__(self) -> None:
        self.window = Window(800, 600)
        self.G: Graph = Graph()

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

    def convex_hull(self, algo:constants.convex_hull_algos) -> None:
        """
        `convex_hull` calcualtes the convex hull of the present set of nodes.
        If no set of nodes is present a new set will be generated. The algorithm
        used to caluclate the convex hull is specified in `algo`.
        """
        if self.G.V == None:
            self.new_nodes()

        self.CH: List[Node] = self.G.calculate_convex_hull(algo)

    # -------------------------------------------
    # ------------- Rendering -------------------
    # -------------------------------------------

    def clear_screen(self) -> None:
        self.window.clear()

    def render_screen(self) -> None:
        self.window.render()

    def render_nodes(self, compact=False, color=constants.ORANGE) -> None:
        self.G.draw_nodes(self.window.screen, color, compact)

    def render_convex_hull(self, color=constants.RED) -> None:
        if self.CH == None:
            self.convex_hull(constants.convex_hull_algos.BRUTE_FORCE)

        for i in range(len(self.CH)):
            Edge(self.CH[i], self.CH[(i+1) % len(self.CH)]).draw(
                self.window.screen, color, 2
            )

