from enum import Enum
from typing import Any, Callable, Dict, Tuple

import pygame

import constants
from constants import convex_hull_algos, lsi_algos, problem_types


class State(Enum):
    NORMAL      = "NORMAL"
    DELETE      = "DELETE"
    DEL_NODES   = "DEL_NODES"
    DEL_EDGES   = "DEL_EDGES"
    GENERATE    = "GENERATE"
    INSERT      = "INSERT"
    INS_NODES   = "INS_NODES"
    INS_EDGE    = "INS_EDGE"
    INS_POLYGON = "INS_POLYGON"
    INS_SEGMENT = "INS_SEGMENT"
    RUN         = "RUN"
    CH          = "CONVEX HULL"
    LSI         = "LINE-SEGMENT INTERSECTION"
    T           = "TRIANGULATION"
    PAUSE       = "PAUSE"
    ANIMATE     = "ANIMATE"


class StateMachine:

    def __init__(self) -> None:
        self.current_state:State = State.NORMAL

        self._TRANSITIONS = {
            State.NORMAL: {
                pygame.K_d: State.DELETE,
                pygame.K_g: State.GENERATE,
                pygame.K_i: State.INSERT,
                pygame.K_r: State.RUN,
                pygame.K_q: State.NORMAL,
            },
            State.DELETE: {
                pygame.K_n: State.DEL_NODES,
                pygame.K_e: State.DEL_EDGES,
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.DEL_NODES: {
                pygame.K_a: State.DELETE, # action
                pygame.K_ESCAPE: State.DELETE,
                pygame.K_q: State.NORMAL,
            },
            State.DEL_EDGES: {
                pygame.K_a: State.DELETE, # action
                pygame.K_ESCAPE: State.DELETE,
                pygame.K_q: State.NORMAL,
            },
            State.GENERATE: {
                pygame.K_n: State.GENERATE, # action
                pygame.K_s: State.GENERATE, # action
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.INSERT: {
                pygame.K_n: State.INS_NODES,
                pygame.K_e: State.INS_EDGE,
                pygame.K_p: State.INS_POLYGON,
                pygame.K_s: State.INS_SEGMENT,
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.INS_NODES: {
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.INS_EDGE: {
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.INS_POLYGON: {
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.INS_SEGMENT: {
                pygame.K_ESCAPE: State.NORMAL,
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
                pygame.K_RETURN: State.PAUSE, # action
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
            State.ANIMATE: {
                pygame.K_SPACE: State.PAUSE,
                pygame.K_UP: State.ANIMATE, # action
                pygame.K_DOWN: State.ANIMATE, # action
                pygame.K_ESCAPE: State.NORMAL,
                pygame.K_q: State.NORMAL,
            },
        }
        self._ACTIONS: Dict[Tuple[State, int], Callable] = {}
        self._HELP = {
            State.NORMAL: ["NORMAL",
                           "  d : DELTE menu",
                           "  g : GENERATE menu",
                           "  i : INSERT menu",
                           "  r : RUN menu",
                           "  q : quit application"],
            State.DELETE: ["DELETE",
                           "  n   : DELETE_NODES menu",
                           "  e   : DELETE_EDGES menu",
                           "  ESC : NORMAL menu",
                           "  q   : quit application"],
            State.DEL_NODES: ["DELETE_NODES",
                              "  click : click a node to delete it",
                              "  a     : delete all edges",
                              "  ESC   : NORMAL menu",
                              "  q     : quit application"],
            State.DEL_EDGES: ["DELETE_EDGES",
                              "  click : click two nodes to delete their connecting edge",
                              "  a     : delete all edges",
                              "  ESC   : NORMAL menu",
                              "  q     : quit application"],
            State.GENERATE: ["GENERATE",
                             "  n   : generate random nodes",
                             "  s   : generate random segments",
                             "  ESC : NORMAL menu",
                             "  q   : quit application"],
            State.INSERT: ["INSERT",
                           "  n   : INSERT_NODES menu",
                           "  e   : INSERT_EDGES menu",
                           "  p   : INSERT_POLYGON menu",
                           "  s   : INSERT_SEGMENTS menu",
                           "  ESC : NORMAL menu",
                           "  q   : quit application"],
            State.INS_NODES: ["INSERT_NODES",
                              "  ESC : NORMAL menu",
                              "  q   : quit application"],
            State.INS_EDGE: ["INSERT_EDGES",
                             "  ESC : NORMAL menu",
                             "  q   : quit application"],
            State.INS_POLYGON: ["INSERT_POLYGON",
                                "  ESC : NORMAL menu",
                                "  q   : quit application"],
            State.INS_SEGMENT: ["INSERT_SEGMENTS",
                                "  ESC : NORMAL menu",
                                "  q   : quit application"],
            State.RUN: ["RUN",
                        "  c   : CONVEX HULL menu",
                        # "  t   : TRIANGULATION menu",
                        "  l   : LINE-SEGMENT INTERSECTION menu",
                        "  ESC : NORMAL menu",
                        "  q   : quit application"],
            State.CH: ["CONVEX HULL",
                       "  0   : Brute Force",
                       "  1   : Monotonous Chains",
                       "  2   : Jarvis' March",
                       "  ESC : NORMAL menu",
                       "  q   : quit application"],
            State.LSI: ["LINE-SEGMENT INTERSECTION",
                        "  0   : Brute Force",
                        "  ESC : NORMAL menu",
                        "  q   : quit application"],
            State.T: ["TRIANGULATION",
                      "  0   : Brute Force",
                      "  ESC : NORMAL menu",
                      "  q   : quit application"],
            State.PAUSE: ["PAUSE",
                          "  SPACE  : play",
                          "  RETURN : manual step",
                          "  ESC    : NORMAL menu",
                          "  q      : quit application"],
            State.ANIMATE: ["ANIMATE",
                            "  SPACE : pause",
                            "  UP    : increase FPS",
                            "  DOWN  : decrease FPS",
                            "  ESC   : NORMAL menu",
                            "  q     : quit application"],
        }

        self._print_help()

    def set_action(self, state: State, event: int, func: Callable):
        self._ACTIONS[(state, event)] = func

    def handle_event(self, event: pygame.event.Event) -> None:
        new_state = self._TRANSITIONS.get(self.current_state, {}).get(event.key)
        if new_state is None:
            return

        action = self._ACTIONS.get((self.current_state, event.key), None)
        if action is not None:
            action()

        if self.current_state != new_state:
            self.current_state = new_state
            self._print_help()

    def reset_state(self) -> None:
        self.current_state = State.NORMAL
        self._print_help()

    def _print_help(self):
        print("\n" + "=" * 48)
        for line in self._HELP.get(self.current_state, []):
            print(line)
