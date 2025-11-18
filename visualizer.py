# pyright: reportMissingImports=false
import math
import random
from typing import Callable, Dict, Generator, List
import constants
from graph import Drawable, Edge, Graph, GraphDrawContainer, Node
from math_helper import get_angle
from point import Point
from state_machine import State, StateMachine
from window import Window
import pygame


class Visualizer:
    def __init__(self) -> None:
        self.window = Window(constants.WIN_WIDTH, constants.WIN_HEIGHT)

        # The graph on which algorithms are performed
        self.G: Graph = Graph()

        # State and menu management
        self.state_machine = StateMachine()
        self.set_sm_actions()

        # Animation control
        self.fps = 1
        self.latest_simulation_state: GraphDrawContainer = GraphDrawContainer()

        # The problem that is being solved currently
        self.current_problem: constants.problem_types | None = None

        # Generator functions for the different problems
        self.algos_CH: Dict[constants.convex_hull_algos, Callable] = {
            constants.convex_hull_algos.BRUTE_FORCE:  self.G.CH_brute_force,
            constants.convex_hull_algos.GRAHAM_SCAN:  self.G.CH_graham_scan,
            constants.convex_hull_algos.JARVIS_MARCH: self.G.CH_jarvis_march,
        }
        self.algos_LSI: Dict[constants.lsi_algos, Callable] = {
            constants.lsi_algos.BRUTE_FORCE: self.G.LSI_brute_force,
        }

        # Generator objects per problem type
        self.gen_CH:  Generator[GraphDrawContainer, None, List[Node]] | None = None
        self.gen_LSI: Generator[GraphDrawContainer, None, List[Node]] | None = None

        # Result data:
        self.res_CH: List[Node] = []
        self.res_LSI: List[Node] = []




        # TODO: from earlier. need to adjust 
        self.res_MST: List[Edge] = []

    def set_sm_actions(self) -> None:
        self.state_machine.set_action(State.DEL_NODES, pygame.K_a, self.G.clear_vertices)
        self.state_machine.set_action(State.DEL_EDGES, pygame.K_a, self.G.clear_edges)

        self.state_machine.set_action(State.GENERATE, pygame.K_n, self.new_nodes)
        self.state_machine.set_action(State.GENERATE, pygame.K_s, self.new_segments)

        self.state_machine.set_action(State.RUN, pygame.K_c, lambda: self.set_problem(constants.problem_types.CH))
        self.state_machine.set_action(State.RUN, pygame.K_t, lambda: self.set_problem(constants.problem_types.T))
        self.state_machine.set_action(State.RUN, pygame.K_l, lambda: self.set_problem(constants.problem_types.LSI))

        self.state_machine.set_action(State.CH, pygame.K_0, lambda: self.set_algorithm(constants.convex_hull_algos.BRUTE_FORCE))
        self.state_machine.set_action(State.CH, pygame.K_1, lambda: self.set_algorithm(constants.convex_hull_algos.GRAHAM_SCAN))
        self.state_machine.set_action(State.CH, pygame.K_2, lambda: self.set_algorithm(constants.convex_hull_algos.JARVIS_MARCH))

        self.state_machine.set_action(State.LSI, pygame.K_0, lambda: self.set_algorithm(constants.lsi_algos.BRUTE_FORCE))

        self.state_machine.set_action(State.PAUSE, pygame.K_RETURN, self.step)

        self.state_machine.set_action(State.ANIMATE, pygame.K_UP, self.increase_fps)
        self.state_machine.set_action(State.ANIMATE, pygame.K_DOWN, self.decrease_fps)

    def process_input(self, event: pygame.event.Event) -> None:
        self.state_machine.handle_event(event)

    def get_state(self) -> State:
        return self.state_machine.current_state

    def increase_fps(self) -> None:
        self.fps += 1

    def decrease_fps(self) -> None:
        if self.fps > 1:
            self.fps -= 1

    def set_problem(self, prob: constants.problem_types) -> None:
        print("[Visualizer] New problem:", prob.value)
        self.current_problem = prob

    def set_algorithm(self, algo) -> None:
        if self.current_problem == constants.problem_types.CH:
            gen_func = self.algos_CH[algo]
            self.gen_CH = gen_func()
        elif self.current_problem == constants.problem_types.LSI:
            gen_func = self.algos_LSI[algo]
            self.gen_LSI = gen_func()
        else:
            print(f"Error: Problemtype is not set properly: {self.current_problem}, provided algorithm: {algo}")

    def step(self) -> None:
        self.step_simulation()

        self.clear_screen()
        self.render_state()
        self.display_screen()
    
    def step_simulation(self) -> None:
        print("[Visualizer] step")

        if self.current_problem == constants.problem_types.CH:
            if self.gen_CH is None:
                print("Error: CH-generator not initialized.")
                return

            try:
                self.latest_simulation_state = next(self.gen_CH)
            except StopIteration as e:
                self.state_machine.reset_state()
                self.res_CH = e.value

        elif self.current_problem == constants.problem_types.LSI:
            if self.gen_LSI is None:
                print("Error: LSI-generator not initialized.")
                return

            try:
                self.latest_simulation_state = next(self.gen_LSI)
            except StopIteration as e:
                self.state_machine.reset_state()
                self.res_LSI = e.value
            

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
        print("[DEBUG|VIS] new nodes generated...")

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
            self.G.add_edge(u, v)

    def new_custom_nodes(self) -> None:
        """
        `new_custom_nodes` switches to an interactive mode where the user 
        can manually place nodes onto the plane via mouse clicks. Clicking
        the left mouse button adds a node. Clicking the right mouse button
        removes the last added node. Clicking "Return" submits the nodes.
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

                    if event.key == pygame.K_r:
                        self.reset_graph()
                        self.clear_screen()
                        self.display_screen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # LMB
                        x,y = pygame.mouse.get_pos()
                        self.G.add_node(Point(x, y))
                    if event.button == 3: # RMB
                        self.G.pop_node()
                    self.clear_screen()
                    self.render_nodes(True, constants.BLUE)
                    self.display_screen()

    def new_custom_polygon(self) -> None:
        """
        `new_custom_polygon` switches to an interactive mode where the user 
        can manually place nodes onto the plane via mouse clicks. The nodes 
        are connected, forming a chain and resulting in a polygon. Clicking
        the left mouse button adds a node. Clicking the right mouse button
        removes the last added node. Clicking "Return" results in a 
        connection of the last placed node with the first placed node.
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
                        self.G.add_edge(
                            self.G.V[0],
                            self.G.V[-1]
                        )

                    if event.key == pygame.K_r:
                        self.reset_graph()
                        self.clear_screen()
                        self.display_screen()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # LMB
                        x,y = pygame.mouse.get_pos()
                        self.G.add_node(Point(x, y))
                        if len(self.G.V) > 1:
                            self.G.add_edge(
                                self.G.V[-2],
                                self.G.V[-1]
                            )
                    if event.button == 3: # RMB
                        self.G.pop_node()

                    self.clear_screen()
                    self.render_edges()
                    self.render_nodes(True, constants.BLUE)
                    self.display_screen()

        # Calculate inner angle sum to check for definition of
        # polygon in counter-clockwise order of vertices
        inner_angle_sum:float = 0
        for i in range(len(self.G.V)):
            inner_angle_sum += get_angle(self.G.V[i-1].p,
                                         self.G.V[i].p,
                                         self.G.V[(i+1) % len(self.G.V)].p)

        # Reverse order if IAS != 180° * (n-2)
        if math.degrees(inner_angle_sum) - (180 * (len(self.G.V) - 2)) > 1e-6:
            self.G.V.reverse()

    def new_graph(self, type: constants.graph_type, num_nodes=20) -> None:
        self.G.generate_graph(type, num_nodes)

    def mst(self, algo:constants.mst_algos) -> None:
        if self.G.E == None:
            self.new_nodes() # TODO: Generate fully connected

        self.res_MST  = self.G.mst(algo)

    # -------------------------------------------
    # ------------- Rendering -------------------
    # -------------------------------------------

    def clear_screen(self) -> None:
        self.window.clear()

    def render_state(self) -> None:
        items: List[Drawable] = self.latest_simulation_state.get_all_drawables()
        for d in items:
            d.draw(self.window.screen)

    def update_screen(self) -> None:
        self.clear_screen()
        self.G.draw(self.window.screen, node_draw_compact=True)
        self.render_state()
        self.display_screen()

    def display_screen(self) -> None:
        self.window.render()

    def render_nodes(self, compact=False, color=constants.ORANGE) -> None:
        self.G.draw_nodes(self.window.screen, color, compact)

    def render_intersects(self, compact=False, color=constants.GREEN) -> None:
        for v in self.res_LSI:
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
        if len(self.res_MST) == 0:
            self.mst(constants.mst_algos.PRIMS)

        for e in self.res_MST:
            e.draw(self.window.screen, edge_col, edge_width)

    def render_convex_hull(self,
                           edge_color=constants.RED,
                           edge_width=2) -> None:
        for i in range(len(self.res_CH)):
            Edge(self.res_CH[i], self.res_CH[(i+1) % len(self.res_CH)]).draw(
                self.window.screen, edge_color, edge_width
            )
