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
        self.previous_input_event: pygame.event.Event
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
        """
        `set_sm_actions` defines the callbackfunctions that 
        the statemachine executes based on a current State and keystroke.
        """

        self.state_machine.set_action(State.NORMAL, pygame.K_d, self.reset_all)

        self.state_machine.set_action(State.MANUAL_NODES, pygame.K_d, self.reset_all)
        self.state_machine.set_action(State.MANUAL_NODES, pygame.BUTTON_LEFT, self._helper_add_node)
        self.state_machine.set_action(State.MANUAL_NODES, pygame.BUTTON_RIGHT, self._helper_remove_node)
        self.state_machine.set_action(State.MANUAL_NODES, pygame.K_ESCAPE, self._helper_reset_last_node_selected)

        self.state_machine.set_action(State.MANUAL_EDGES, pygame.K_d, self.G.clear_edges)
        self.state_machine.set_action(State.MANUAL_EDGES, pygame.BUTTON_LEFT, self._helper_add_edge)
        self.state_machine.set_action(State.MANUAL_EDGES, pygame.BUTTON_RIGHT, self._helper_remove_edge)
        self.state_machine.set_action(State.MANUAL_EDGES, pygame.K_ESCAPE, self._helper_reset_last_node_selected)

        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.K_d, self._helper_clear_segments)
        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.BUTTON_LEFT, self._helper_add_segment)
        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.BUTTON_RIGHT, self._helper_remove_segment)
        self.state_machine.set_action(State.MANUAL_SEGMENTS, pygame.K_ESCAPE, self._helper_reset_last_node_selected)

        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.BUTTON_LEFT, self._helper_add_node_to_polygon)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.BUTTON_RIGHT, self._helper_remove_node_from_polygon)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.BUTTON_MIDDLE, self._helper_delete_polygon)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.K_RETURN, self._helper_form_polygon_cycle)
        self.state_machine.set_action(State.MANUAL_POLYGONS, pygame.K_ESCAPE, self._helper_abort_polygon)

        self.state_machine.set_action(State.GEN_NODES, pygame.K_RETURN, lambda: self.new_nodes(self.number_of_nodes_to_generate))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_UP,    lambda: self._helper_update_num_nodes_gen(1))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_RIGHT, lambda: self._helper_update_num_nodes_gen(5))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_DOWN,  lambda: self._helper_update_num_nodes_gen(-1))
        self.state_machine.set_action(State.GEN_NODES, pygame.K_LEFT,  lambda: self._helper_update_num_nodes_gen(-5))

        self.state_machine.set_action(State.GEN_SEGMENTS, pygame.K_RETURN, lambda: self.new_segments(self.number_of_segments_to_generate))
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

        self._forall_states_set_action(pygame.K_MINUS, self.toggle_compact_nodes)

    
    def _forall_states_set_action(self, key: int, func: Callable) -> None:
        """
        `_forall_states_set_action` is a helper function to define callbacks
        that are the same for every single state (such as quitting the application).
        """
        for state in State:
            self.state_machine.set_action(state, key, func)

    def toggle_compact_nodes(self) -> None:
        Node.compact_nodes = not Node.compact_nodes

    def _helper_reset_last_node_selected(self) -> None:
        self.last_node_selected = None

    def _helper_update_num_nodes_gen(self, change: int) -> None:
        """
        `_helper_update_num_nodes_gen` changes the number of nodes that will 
        be generated by `change`. This number is capped to be non-negative.
        """
        self.number_of_nodes_to_generate += change
        if self.number_of_nodes_to_generate < 0:
            self.number_of_nodes_to_generate = 0

        self.new_nodes(self.number_of_nodes_to_generate)

    def _helper_update_num_segments_gen(self, change: int) -> None:
        """
        `_helper_update_num_segments_gen` changes the number of segments that 
        will be generated by `change`. This number is capped to be non-negative.
        """
        self.number_of_segments_to_generate += change
        if self.number_of_segments_to_generate < 0:
            self.number_of_segments_to_generate = 0

        self.new_segments(self.number_of_segments_to_generate)

    def _helper_add_node(self) -> None:
        """
        `_helper_add_node` takes the current cursor position and adds
        a not with that coordinate ot the graph.
        """
        x, y = pygame.mouse.get_pos()
        self.G.add_node(Point(x, y))

    def _helper_remove_node(self) -> None:
        """
        `_helper_remove_node` checks if any node is below the cursor position.
        The hitbox of the nodes is based on `Node.compact_nodes`.
        If multiple nodes are below the cursor, they will all be removed.
        """
        x, y = pygame.mouse.get_pos()
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                self.G.remove_node(n)

    def _helper_add_edge(self) -> None:
        """
        `_helper_add_edge` is state dependent on `self.last_node_selected` and 
        `self.previous_input_event`. It checks if any node has been clicked on. 
        If multiple nodes could have been selected because they are ontop of one
        another, the function is aborted. On the first call, `self.last_node_selected`
        is set. On the second call a new edge from `self.last_node_selected` to the
        newly selected node is added to the graph. If the same node is clicked twice
        `self.last_node_selected` is not updated and the next node selection will
        add an edge to the graph.
        """

        # If the previous action was not to select a node for adding
        # a new edge, reset the state variable `self.last_node_selected`
        if self.previous_input_event.type != pygame.MOUSEBUTTONDOWN or \
            self.previous_input_event.button != pygame.BUTTON_LEFT:

            self.last_node_selected = None

        x, y = pygame.mouse.get_pos()

        # Find all clicked on nodes
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is None:
                    selected = n
                else:
                    print(f"{constants.WARNING}Warning: Please only select a single node.{constants.RESET}")
                    self.state_machine.inc_num_help_lines()
                    return
        
        # Didn't click any node
        if selected is None:
            return

        # Check if another node has been clicked before or
        # the same node was clicked again
        if self.last_node_selected is None or \
            self.last_node_selected.id == selected.id:

            self.last_node_selected = selected
            return

        # Add the new edge and reset the "status"
        self.G.add_edge(self.last_node_selected, selected)
        self.last_node_selected = None

    def _helper_remove_edge(self) -> None:
        """
        `_helper_remove_edge` is state dependent on `self.last_node_selected` and 
        `self.previous_input_event`. It checks if any node has been clicked on. 
        If multiple nodes could have been selected because they are ontop of one
        another, the function is aborted. On the first call, `self.last_node_selected`
        is set. On the second call the edge from `self.last_node_selected` to the
        newly selected node is removed from the graph if present. If the same node 
        is clicked twice `self.last_node_selected` is not updated and the next 
        node selection will remove an edge from the graph.
        """

        # If the previous action was not to select a node for removal
        # of an edge, reset the state variable `self.last_node_selected`
        if self.previous_input_event.type != pygame.MOUSEBUTTONDOWN or \
            self.previous_input_event.button != pygame.BUTTON_RIGHT:

            self.last_node_selected = None


        x, y = pygame.mouse.get_pos()

        # Find all clicked on nodes
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is None:
                    selected = n
                else:
                    print(f"{constants.WARNING}Warning: Please only select a single node.{constants.RESET}")
                    self.state_machine.inc_num_help_lines()
                    return
        
        # Didn't click any node
        if selected is None:
            return

        # Check if another node has been clicked before or
        # the same node was clicked again
        if self.last_node_selected is None or \
            self.last_node_selected.id == selected.id:

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
        """
        `_helper_add_segment` adds a new node and then calls `_helper_add_edge`
        to simulat the clicking onto a node which is thus selected for the 
        adding of a new edge. It is not possible to click onto an existing node.
        """
        x, y = pygame.mouse.get_pos()

        # Check for click onto existing node
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                print(f"{constants.WARNING}Warning: Please don't click onto existing nodes when adding a segment.{constants.RESET}")
                self.state_machine.inc_num_help_lines()
                return

        self._helper_add_node()
        self._helper_add_edge()

    def _helper_remove_segment(self) -> None:
        """
        `_helper_remove_segment` is state dependent on `self.last_node_selected`.
        It removes 2 nodes and an edge from the graph if both are of degree 1 and
        connected to one another.
        """

        x, y = pygame.mouse.get_pos()

        # Find all clicked on nodes
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is None:
                    selected = n
                else:
                    print(f"{constants.WARNING}Warning: Please only select a single node.{constants.RESET}")
                    self.state_machine.inc_num_help_lines()
                    return
        
        # Didn't click any node
        if selected is None:
            return

        # Check if selected node is of degree 1
        connected_to = self.G.adj_mat.get(selected.id, None)
        if connected_to is not None:
            if len(connected_to) != 1:
                print(f"{constants.WARNING}Warning: You can only select nodes of degree 1. (len={len(connected_to)}){constants.RESET}")
                self.state_machine.inc_num_help_lines()
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
        """
        `_helper_add_node_to_polygon` appends a new node to 
        `self.current_polygon_node_chain` and inserts an edge to that
        new node.
        """

        # Add new node to chain and graph
        x, y = pygame.mouse.get_pos()
        n: Node = Node(Point(x, y))
        self.current_polygon_node_chain.append(n)
        self.G.add_node(n)

        self.last_node_selected = n

        if len(self.current_polygon_node_chain) == 1:
            return

        self.G.add_edge(self.current_polygon_node_chain[-2],
                        self.current_polygon_node_chain[-1])


    def _helper_remove_node_from_polygon(self) -> None:
        """
        `_helper_remove_node_from_polygon` pops the last node off of
        `self.current_polygon_node_chain`.
        """
        if len(self.current_polygon_node_chain) == 0:
            return

        self.G.pop_node()
        self.current_polygon_node_chain.pop()
        
        if len(self.current_polygon_node_chain) > 0:
            self.last_node_selected = self.current_polygon_node_chain[-1]
        else:
            self.last_node_selected = None

    def _helper_delete_polygon(self) -> None:
        """
        `_helper_delete_polygon` checks if the selected node is part
        of a polygon. If so, the entire polygon (Nodes and Edges) are removed.
        """
        # Get clicked node
        x, y = pygame.mouse.get_pos()
        selected: Node | None = None
        for n in self.G.V:
            if Node.point_inside_node(n, Point(x, y)):
                if selected is not None:
                    print(f"{constants.WARNING}Warning: Please only select a single node.{constants.RESET}")
                    self.state_machine.inc_num_help_lines()
                    return
                selected = n

        if selected is None:
            return

        for m in self.G.polygon_map.get(selected.id, []):
            self.G.remove_node(m)

    def _helper_form_polygon_cycle(self) -> None:
        """
        `_helper_from_polygon_cycle` connects the last node added to
        `self.current_polygon_node_chain` with the first one if there are
        at least 3 nodes.
        """
        if len(self.current_polygon_node_chain) >= 3:
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
                self.current_polygon_node_chain.reverse()

            # Create a new copy of polygon list and have every item
            # in the map share the same list.
            # References to original nodes stay in tact!
            new_polygon = self.current_polygon_node_chain[:]
            for n in new_polygon:
                self.G.polygon_map[n.id] = new_polygon

            self.current_polygon_node_chain.clear()
            self.last_node_selected = None

    def _helper_abort_polygon(self) -> None:
        """
        `_helper_abort_polygon` empties `self.current_polygon_node_chain`
        and removes nodes and edges from the graph.
        """
        for n in self.current_polygon_node_chain:
            self.G.remove_node(n)
        self.current_polygon_node_chain.clear()

        self._helper_reset_last_node_selected()


    def _helper_clear_segments(self) -> None:
        """
        `_helper_clear_segments` removes every segment of `self.G`.
        A segment consists of 2 nodes of degree 1 connected by an edge.
        """
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
        self.state_machine.handle_event(event)
        self.previous_input_event = event

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
            print(f"{constants.ERROR}Error: Problemtype is not set properly: {self.current_problem}, provided algorithm: {algo}{constants.RESET}")
            self.state_machine.inc_num_help_lines()

    def step(self) -> None:
        """
        `step` is a wrapper that both calls `step_simulation` 
        and `update_screen` such that, essentially, the next 
        state of the algorithm is rendered.
        """
        self.step_simulation()

        self.update_screen()
    
    def step_simulation(self) -> None:
        """
        `step_simulation` calls the `next()` function on the currently
        active generator function. The screen is not updated automatically.
        """

        if self.current_problem == constants.problem_types.CH:
            if self.gen_CH is None:
                print(f"{constants.ERROR}Error: CH-generator not initialized.{constants.RESET}")
                self.state_machine.inc_num_help_lines()
                return

            try:
                self.latest_simulation_state = next(self.gen_CH)
            except StopIteration as e:
                self.state_machine.reset_state()
                self.res_CH = e.value
                self.render_result()

        elif self.current_problem == constants.problem_types.LSI:
            if self.gen_LSI is None:
                print(f"{constants.ERROR}Error: LSI-generator not initialized.{constants.RESET}")
                self.state_machine.inc_num_help_lines()
                return

            try:
                self.latest_simulation_state = next(self.gen_LSI)
            except StopIteration as e:
                self.state_machine.reset_state()
                self.res_LSI = e.value
                self.render_result()
            

    def reset_all(self) -> None:
        """
        `reset_all` deletes the entire graph and the associated
        result data of previous calculations.
        """
        self.reset_graph_calculations()
        self.G.reset_graph()

    def reset_graph_calculations(self) -> None:
        """
        `reset_graph` deletes all calcualted structures such as 
        convex hulls or MSTs. The graph structure itself stays
        unmodified.
        """
        self.res_CH.clear()
        self.res_LSI.clear()
        self.res_MST.clear()
        self.latest_simulation_state = GraphDrawContainer()

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
        self.reset_all()
        self.new_nodes(2 * num_segments);
        nodes: List[Node] = self.G.V.copy()
        for _ in range(num_segments):
            u: Node = random.choice(nodes)
            nodes.remove(u)
            v: Node = random.choice(nodes)
            nodes.remove(v)
            self.G.add_edge(u, v)

    # -------------------------------------------
    # ------------- Rendering -------------------
    # -------------------------------------------

    def clear_screen(self) -> None:
        self.window.clear()

    def render_state(self) -> None:
        items: List[Drawable] = self.latest_simulation_state.get_all_drawables()
        for d in items:
            d.draw(self.window.screen)

    def render_highlights(self) -> None:
        # Draw polygon nodes in lighter blue
        for p in self.G.polygon_map.values():
            for n in p:
                n.draw(self.window.screen, constants.PURPLE)

        # Render last selected node in different color
        if self.last_node_selected is not None:
            self.last_node_selected.draw(
                self.window.screen, 
                constants.ORANGE
            )

    def update_screen(self) -> None:
        self.clear_screen()
        # Draw the underlying graph
        self.G.draw(self.window.screen, constants.EDGE_COLOR, node_col=constants.BLUE)
        # Draw further highlighted nodes
        self.render_highlights()
        # Draw state of the algorithm
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

