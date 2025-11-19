from enum import Enum
from typing import Any, Callable, Dict, Tuple

import pygame
import pygame.mouse

import constants
from constants import convex_hull_algos, lsi_algos, problem_types


class State(Enum):
    NORMAL          = "NORMAL"
    MANUAL_MOD      = "MANUAL MODIFICATION"
    MANUAL_NODES    = "NODES MANUAL MODIFICATION"
    MANUAL_EDGES    = "EDGES MANUAL MODIFICATION"
    MANUAL_SEGMENTS = "SEGMENTS MANUAL MODIFICATION"
    MANUAL_POLYGONS = "POLYGONS MANUAL MODIFICATION"
    GENERATE        = "GENERATE"
    GEN_NODES       = "GENERATE_NODES"
    GEN_SEGMENTS    = "GENERATE_SEGMENTS"
    RUN             = "RUN"
    CH              = "CONVEX HULL"
    LSI             = "LINE-SEGMENT INTERSECTION"
    T               = "TRIANGULATION"
    PAUSE           = "PAUSE"
    ANIMATE         = "ANIMATE"


class StateMachine:

    def __init__(self) -> None:
        self.current_state:State = State.NORMAL

        self._TRANSITIONS = {
            State.NORMAL: {
                pygame.K_g: State.GENERATE,
                pygame.K_m: State.MANUAL_MOD,
                pygame.K_r: State.RUN,
                pygame.K_q: State.NORMAL,
            },
            State.MANUAL_MOD: {
                pygame.K_n: State.MANUAL_NODES,
                pygame.K_e: State.MANUAL_EDGES,
                pygame.K_s: State.MANUAL_SEGMENTS,
                pygame.K_p: State.MANUAL_POLYGONS,
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.MANUAL_NODES: {
                pygame.K_ESCAPE: State.MANUAL_MOD,
                pygame.K_q: State.NORMAL,
            },
            State.MANUAL_EDGES: {
                pygame.K_ESCAPE: State.MANUAL_MOD,
                pygame.K_q: State.NORMAL,
            },
            State.MANUAL_SEGMENTS: {
                pygame.K_ESCAPE: State.MANUAL_MOD,
                pygame.K_q: State.NORMAL,
            },
            State.MANUAL_POLYGONS: {
                pygame.K_ESCAPE: State.MANUAL_MOD,
                pygame.K_q: State.NORMAL,
            },
            State.GENERATE: {
                pygame.K_n: State.GEN_NODES,
                pygame.K_s: State.GEN_SEGMENTS,
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.GEN_NODES: {
                pygame.K_ESCAPE: State.GENERATE,
                pygame.K_q: State.NORMAL,
            },
            State.GEN_SEGMENTS: {
                pygame.K_ESCAPE: State.GENERATE,
                pygame.K_q: State.NORMAL,
            },
            State.RUN: {
                pygame.K_c: State.CH, # action
                # pygame.K_t: State.T, # action
                pygame.K_l: State.LSI, # action
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.CH: {
                pygame.K_0: State.PAUSE, # action
                pygame.K_1: State.PAUSE, # action
                pygame.K_2: State.PAUSE, # action
                pygame.K_ESCAPE: State.RUN,
                pygame.K_q: State.NORMAL,
            },
            State.LSI: {
                pygame.K_0: State.PAUSE, # action
                pygame.K_ESCAPE: State.RUN,
                pygame.K_q: State.NORMAL,
            },
            # State.T: {
            #     pygame.K_0: State.PAUSE, # action
            #     pygame.K_ESCAPE: State.RUN,
            #     pygame.K_q: State.NORMAL,
            # },
            State.PAUSE: {
                pygame.K_SPACE: State.ANIMATE,
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.ANIMATE: {
                pygame.K_SPACE: State.PAUSE,
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
        }
        self._ACTIONS: Dict[Tuple[State, int], Callable] = {}
        self._HELP = {
            State.NORMAL: ["NORMAL",
                           "  m : MANUAL MODIFICATION menu",
                           "  g : GENERATE menu",
                           "  r : RUN menu",
                           "  d : delete all",
                           "  - : toggle compact node rendering",
                           "  q : quit application"],
            State.MANUAL_MOD: ["MANUAL MODIFICATION",
                               "  n   : NODES MANUAL MODIFICATION",
                               "  e   : EDGES MANUAL MODIFICATION",
                               "  s   : SEGMENTS MANUAL MODIFICATION",
                               "  p   : POLYGONS MANUAL MODIFICATION",
                               "  -   : toggle compact node rendering",
                               "  ESC : NORMAL menu",
                               "  q   : quit application"],
            State.MANUAL_NODES: ["NODES MANUAL MODIFICATION",
                                 "  left click  : add a node",
                                 "  right click : remove a node",
                                 "  d           : delete all nodes",
                                 "  -           : toggle compact node rendering",
                                 "  ESC         : MANUAL MODIFICATION menu",
                                 "  q           : quit application"],
            State.MANUAL_EDGES: ["EDGES MANUAL MODIFICATION",
                                 "  left click  : click onto 2 nodes to add an edge",
                                 "  right click : click onto 2 nodes to remove an existing edge",
                                 "  d           : delete all edges",
                                 "  -           : toggle compact node rendering",
                                 "  ESC         : MANUAL MODIFICATION menu",
                                 "  q           : quit application"],
            State.MANUAL_SEGMENTS: ["SEGMENTS MANUAL MODIFICATION",
                                    "  left click  : click twice to add a segment",
                                    "  right click : click onto 2 nodes to remove an existing segment",
                                    "  d           : delete all segments (pairs of nodes and edges)",
                                    "  -           : toggle compact node rendering",
                                    "  ESC         : MANUAL MODIFICATION menu",
                                    "  q           : quit application"],
            State.MANUAL_POLYGONS: ["POLYGONS MANUAL MODIFICATION",
                                    "  left click  : add a new node to the current chain of nodes",
                                    "  right click : remove the last node from the current chain of nodes",
                                    "  RETURN      : connect the last placed node with the first placed node to form a polygon",
                                    "  -           : toggle compact node rendering",
                                    "  ESC         : MANUAL MODIFICATION menu",
                                    "  q           : quit application"],
            State.GENERATE: ["GENERATE",
                             "  n   : GENERATE NODES",
                             "  s   : GENERATE SEGMENTS",
                             "  -   : toggle compact node rendering",
                             "  ESC : NORMAL menu",
                             "  q   : quit application"],
            State.GEN_NODES: ["GENERATE NODES",
                              "  RETURN : generate random rondes",
                              "  UP     : increment number of nodes",
                              "  DOWN   : decrement number of nodes",
                              "  -      : toggle compact node rendering",
                              "  ESC    : NORMAL menu",
                              "  q      : quit application"],
            State.GEN_SEGMENTS: ["GENERATE SEGMENTS",
                                 "  RETURN : generate random segments",
                                 "  UP     : increment number of segments",
                                 "  DOWN   : decrement number of segments",
                                 "  -      : toggle compact node rendering",
                                 "  ESC    : NORMAL menu",
                                 "  q      : quit application"],
            State.RUN: ["RUN",
                        "  c   : CONVEX HULL menu",
                        # "  t   : TRIANGULATION menu",
                        "  l   : LINE-SEGMENT INTERSECTION menu",
                        "  -   : toggle compact node rendering",
                        "  ESC : NORMAL menu",
                        "  q   : quit application"],
            State.CH: ["CONVEX HULL",
                       "  0   : Brute Force",
                       "  1   : Monotonous Chains",
                       "  2   : Jarvis' March",
                       "  -   : toggle compact node rendering",
                       "  ESC : NORMAL menu",
                       "  q   : quit application"],
            State.LSI: ["LINE-SEGMENT INTERSECTION",
                        "  0   : Brute Force",
                        "  -   : toggle compact node rendering",
                        "  ESC : NORMAL menu",
                        "  q   : quit application"],
            State.T: ["TRIANGULATION",
                      "  0   : Brute Force",
                      "  -   : toggle compact node rendering",
                      "  ESC : NORMAL menu",
                      "  q   : quit application"],
            State.PAUSE: ["PAUSE",
                          "  SPACE  : play",
                          "  RETURN : manual step",
                          "  -      : toggle compact node rendering",
                          "  ESC    : NORMAL menu",
                          "  q      : quit application"],
            State.ANIMATE: ["ANIMATE",
                            "  SPACE : pause",
                            "  UP    : increase FPS",
                            "  DOWN  : decrease FPS",
                            "  -     : toggle compact node rendering",
                            "  ESC   : NORMAL menu",
                            "  q     : quit application"],
        }

        self._print_help()

    def set_action(self, state: State, event: int, func: Callable):
        self._ACTIONS[(state, event)] = func

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            action = self._ACTIONS.get((self.current_state, event.key), None)
            if action is not None:
                action()

            new_state = self._TRANSITIONS.get(self.current_state, {}).get(event.key)
            if new_state is None:
                return

            if self.current_state != new_state:
                self.current_state = new_state
                self._print_help()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            action = self._ACTIONS.get((self.current_state, event.button), None)
            if action is not None:
                action()

    def reset_state(self) -> None:
        self.current_state = State.NORMAL
        self._print_help()

    def _print_help(self):
        print("\n" + "=" * 48)
        for line in self._HELP.get(self.current_state, []):
            print(line)
