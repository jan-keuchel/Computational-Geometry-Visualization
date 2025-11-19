# pyright: reportMissingImports=false
import math
import random
from typing import Callable, Dict, Generator, List
import constants
from graph import Drawable, Edge, Graph, GraphDrawContainer, Node
from math_helper import get_angle
from node import NodeDrawContainer
from point import Point
from state_machine import State, StateMachine
from window import Window
import pygame
import pygame.mouse


class Visualizer:
    def __init__(self) -> None:
        self.window = Window(constants.WIN_WIDTH, constants.WIN_HEIGHT)

        # The graph on which algorithms are performed
        self.G: Graph = Graph()

        # Generation of input
        self.number_of_nodes_to_generate = 10
        self.number_of_segments_to_generate = 10

        # Input Event
        self.latest_input_event: pygame.event.Event
        self.last_node_selected: Node | None = None
        self.current_polygon_node_chain: List[Node] = []

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

        self.state_machine.set_action(State.NORMAL, pygame.K_d, self.reset_all)

        self.state_machine.set_action(State.MANUAL_NODES, pygame.K_d, self.reset_all)
        self.state_machine.set_action(State.MANUAL_NODES, pygame.BUTTON_LEFT, self._helper_add_node)
        self.state_machine.set_action(State.MANUAL_NODES, pygame.BUTTON_RIGHT, self._helper_remove_node)

        self.state_machine.set_action(State.MANUAL_EDGES, pygame.K_d, self.G.clear_edges)
        self.state_machine.set_action(State.MANUAL_EDGES, pygame.BUTTON_LEFT, self._helper_add_edge)
        self.state_machine.set_action(State.MANUAL_EDGES, pygame.BUTTON_RIGHT, self._helper_remove_edge)

        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.K_d, self._helper_clear_segments)
        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.BUTTON_LEFT, self._helper_add_segment)
        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.BUTTON_RIGHT, self._helper_remove_segment)

        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.BUTTON_LEFT, self._helper_add_node_to_polygon)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.BUTTON_RIGHT, self._helper_remove_node_from_polygon)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.K_RETURN, self._helper_from_polygon_cycle)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.K_ESCAPE, self._helper_abort_polygon)

        self.state_machine.set_action(State.GEN_NODES, pygame.K_RETURN, self._helper_new_nodes_and_render)
        self.state_machine.set_action(State.GEN_NODES, pygame.K_UP,    lambda: self._helper_update_num_nodes_gen(1))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_RIGHT, lambda: self._helper_update_num_nodes_gen(5))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_DOWN,  lambda: self._helper_update_num_nodes_gen(-1))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_LEFT,  lambda: self._helper_update_num_nodes_gen(-5))

        self.state_machine.set_action(State.GEN_SEGMENTS, pygame.K_RETURN, self._helper_new_segments_and_render)
        self.state_machine.set_action(State.GEN_SEGMENTS, pygame.K_UP,    lambda: self._helper_update_num_segments_gen(1))
        self.state_machine.set_action(State.GEN_SEGMENTS, pygame.K_RIGHT, lambda: self._helper_update_num_segments_gen(5))
        self.state_machine.set_action(State.GEN_SEGMENTS, pygame.K_DOWN,  lambda: self._helper_update_num_segments_gen(-1))
        self.state_machine.set_action(State.GEN_SEGMENTS, pygame.K_LEFT,  lambda: self._helper_update_num_segments_gen(-5))

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

        self.forall_states_set_action(pygame.K_MINUS, self.toggle_compact_nodes)

    
    def forall_states_set_action(self, key: int, func: Callable) -> None:
        for state in State:
            self.state_machine.set_action(state, key, func)

    def toggle_compact_nodes(self) -> None:
        Node.compact_nodes = not Node.compact_nodes

    def _helper_new_nodes_and_render(self) -> None:
        self.new_nodes(self.number_of_nodes_to_generate)
        self.update_screen()

    def _helper_update_num_nodes_gen(self, change: int) -> None:
        if change > 0:
            self.number_of_nodes_to_generate += change
        elif self.number_of_nodes_to_generate > 0:
            self.number_of_nodes_to_generate += change
        self._helper_new_nodes_and_render()

    def _helper_new_segments_and_render(self) -> None:
        self.new_segments(self.number_of_segments_to_generate)
        self.update_screen()

    def _helper_update_num_segments_gen(self, change: int) -> None:
        if change > 0:
            self.number_of_segments_to_generate += change
        elif self.number_of_segments_to_generate > 0:
            self.number_of_segments_to_generate -= change
        self.new_segments(self.number_of_segments_to_generate)

    def _helper_add_node(self) -> None:
        x, y = pygame.mouse.get_pos()
        self.G.add_node(Point(x, y))

    def _helper_remove_node(self) -> None:
        x, y = pygame.mouse.get_pos()
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                self.G.remove_node(n)

    def _helper_add_edge(self) -> None:
        x, y = pygame.mouse.get_pos()

        # Find all clicked on nodes
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is None:
                    selected = n
                else:
                    print("Warning: Please only select a single node.")
                    return
        
        # Didn't click any node
        if selected is None:
            return

        # Check if another node has been clicked before
        if self.last_node_selected is None:
            self.last_node_selected = selected
            return

        # Add the new edge and reset the "status"
        self.G.add_edge(self.last_node_selected, selected)
        self.last_node_selected = None

    def _helper_remove_edge(self) -> None:
        x, y = pygame.mouse.get_pos()

        # Find all clicked on nodes
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is None:
                    selected = n
                else:
                    print("Warning: Please only select a single node.")
                    return
        
        # Didn't click any node
        if selected is None:
            return

        # Check if another node has been clicked before
        if self.last_node_selected is None:
            self.last_node_selected = selected
            return

        # Add the new edge and reset the "status"
        connected_to = self.G.adj_mat.get(self.last_node_selected.id, None)
        if connected_to is not None:
            if selected.id in connected_to:
                self.G.remove_edge(self.G.adj_mat[self.last_node_selected.id][selected.id])

                self.last_node_selected = None
            else:
                self.last_node_selected = selected

    def _helper_add_segment(self) -> None:
        x, y = pygame.mouse.get_pos()

        # Check for click onto existing node
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                print("Warning: Please don't click onto existing nodes when adding a segment.")
                return

        self._helper_add_node()
        self._helper_add_edge()

    def _helper_remove_segment(self) -> None:
        x, y = pygame.mouse.get_pos()

        # Find all clicked on nodes
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is None:
                    selected = n
                else:
                    print("Warning: Please only select a single node.")
                    return
        
        # Didn't click any node
        if selected is None:
            return

        # Check if selected node is of degree 1
        connected_to = self.G.adj_mat.get(selected.id, None)
        if connected_to is not None:
            if len(connected_to) != 1:
                print(f"Warning: You can only select nodes of degree 1. (len={len(connected_to)})")
                for k in connected_to:
                    print(f"connected to: {k}")
                for v in connected_to.values():
                    print(f"edge values: {v}")
                return

        # Check if another node has been clicked before
        if self.last_node_selected is None:
            self.last_node_selected = selected
            return

        a_connected_to = self.G.adj_mat.get(self.last_node_selected.id, None)
        b_connected_to = connected_to
        if a_connected_to is not None and b_connected_to is not None:
            # Check if both nodes are connected to one another
            if selected.id in a_connected_to and \
                self.last_node_selected.id in b_connected_to:

                self.G.remove_edge(self.G.adj_mat[self.last_node_selected.id][selected.id])
                self.G.remove_node(self.last_node_selected)
                self.G.remove_node(selected)

                self.last_node_selected = None
            else:
                self.last_node_selected = selected

    def _helper_add_node_to_polygon(self) -> None:
        # Add new node to chain and graph
        x, y = pygame.mouse.get_pos()
        n: Node = Node(Point(x, y))
        self.current_polygon_node_chain.append(n)
        self.G.add_node(n)

        if len(self.current_polygon_node_chain) == 1:
            return

        self.G.add_edge(self.current_polygon_node_chain[-2],
                        self.current_polygon_node_chain[-1])

    def _helper_remove_node_from_polygon(self) -> None:
        if len(self.current_polygon_node_chain) == 0:
            return

        self.G.pop_node()
        self.current_polygon_node_chain.pop()

    def _helper_from_polygon_cycle(self) -> None:
        if len(self.current_polygon_node_chain) >= 2:
            self.G.add_edge(self.current_polygon_node_chain[-1],
                            self.current_polygon_node_chain[0])

            
            # Calculate inner angle sum to check for definition of
            # polygon in counter-clockwise order of vertices
            inner_angle_sum:float = 0
            for i in range(len(self.current_polygon_node_chain)):
                inner_angle_sum += get_angle(self.current_polygon_node_chain[i-1].p,
                                             self.current_polygon_node_chain[i].p,
                                             self.current_polygon_node_chain[(i+1) % len(self.current_polygon_node_chain)].p)

            # Reverse order if IAS != 180° * (n-2)
            if math.degrees(inner_angle_sum) - (180 * (len(self.current_polygon_node_chain) - 2)) > 1e-6:
                print("before: ")
                for n in self.G.V:
                    print(f"{n.id} ")
                first = self.G.V.index(self.current_polygon_node_chain[0])
                last = self.G.V.index(self.current_polygon_node_chain[-1])
                for i in range(first, int((first + last) / 2), 1):
                    temp: Node = self.G.V[i]
                    self.G.V[i] = self.G.V[last - (i - first)]
                    self.G.V[last - (i - first)] = temp

                print("after: ")
                for n in self.G.V:
                    print(f"{n.id} ")

            self.current_polygon_node_chain.clear()

    def _helper_abort_polygon(self) -> None:
        for n in self.current_polygon_node_chain:
            self.G.remove_node(n)
        self.current_polygon_node_chain.clear()


    def _helper_clear_segments(self) -> None:
        nodes_to_remove: List[Node] = []
        for n in self.G.V:
            if len(self.G.adj_mat[n.id]) == 1:
                other_id = next(iter(self.G.adj_mat[n.id]))
                if len(self.G.adj_mat[other_id]) == 1:
                    if n not in nodes_to_remove:
                        nodes_to_remove.append(n)
                    other = (self.G.adj_mat[n.id][other_id].other(n))
                    if other not in nodes_to_remove:
                        nodes_to_remove.append(other)

        for n in nodes_to_remove:
            self.G.remove_node(n)

        
    def process_input(self, event: pygame.event.Event) -> None:
        self.latest_input_event = event
        self.state_machine.handle_event(event)

    def get_state(self) -> State:
        return self.state_machine.current_state

    def increase_fps(self) -> None:
        self.fps += 1

    def decrease_fps(self) -> None:
        if self.fps > 1:
            self.fps -= 1

    def set_problem(self, prob: constants.problem_types) -> None:
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

        self.update_screen()
    
    def step_simulation(self) -> None:

        if self.current_problem == constants.problem_types.CH:
            if self.gen_CH is None:
                print("Error: CH-generator not initialized.")
                return

            try:
                self.latest_simulation_state = next(self.gen_CH)
            except StopIteration as e:
                self.state_machine.reset_state()
                self.res_CH = e.value
                self.render_result()

        elif self.current_problem == constants.problem_types.LSI:
            if self.gen_LSI is None:
                print("Error: LSI-generator not initialized.")
                return

            try:
                self.latest_simulation_state = next(self.gen_LSI)
            except StopIteration as e:
                self.state_machine.reset_state()
                self.res_LSI = e.value
                self.render_result()
            

    def reset_all(self) -> None:
        self.reset_graph()
        self.res_CH.clear()
        self.res_LSI.clear()
        self.res_MST.clear()
        self.latest_simulation_state = GraphDrawContainer()

    def reset_graph(self) -> None:
        """
        `reset_graph` deletes all calcualted structures such as 
        convex hulls or MSTs. The nodes stay the same.
        """
        self.G.reset_graph()

    def new_nodes(self, num_nodes=10) -> None:
        """
        `new_nodes` deletes the entire graph with it's associated data
        and generates a new set of nodes.
        """
        self.reset_all()
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
                    self.render_nodes(constants.BLUE)
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
                    self.render_nodes(constants.BLUE)
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
        self.G.draw(self.window.screen, constants.EDGE_COLOR, node_col=constants.BLUE)
        self.render_state()
        self.display_screen()

    def render_result(self) -> None:
        self.clear_screen()
        self.G.draw(self.window.screen, constants.EDGE_COLOR, node_col=constants.BLUE)
        
        if self.current_problem == constants.problem_types.CH:
            self.latest_simulation_state = GraphDrawContainer.convert_node_chain_to_GDC(self.res_CH, constants.RED, constants.GREEN, 5)
        elif self.current_problem == constants.problem_types.LSI:
            gdc: GraphDrawContainer = GraphDrawContainer()
            intersections: List[Drawable] = [
                NodeDrawContainer(n, constants.GREEN)
                for n in self.res_LSI
            ]
            gdc.add_layer(intersections)
            self.latest_simulation_state = gdc

        self.render_state()
        self.display_screen()

    def display_screen(self) -> None:
        self.window.render()

    def render_nodes(self, color=constants.ORANGE) -> None:
        self.G.draw_nodes(self.window.screen, color)

    def render_intersects(self, color=constants.GREEN) -> None:
        for v in self.res_LSI:
            v.draw(self.window.screen, color)

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
                     node_col=constants.ORANGE) -> None:
        self.G.draw(
            self.window.screen,
            edge_col=edge_color,
            edge_width=edge_width,
            node_col=node_col,
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
