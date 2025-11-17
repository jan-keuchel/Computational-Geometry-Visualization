from enum import Enum

import pygame


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

    _TRANSITIONS = {
        #   KEYSTROKE           NEW STATE           FUNCTION TO CALL                                        ARGS TO FUNCTION
        State.NORMAL: {
            pygame.K_d:         (State.DELETE,      None,                                                   []),
            pygame.K_g:         (State.GENERATE,    None,                                                   []),
            pygame.K_i:         (State.INSERT,      None,                                                   []),
            pygame.K_r:         (State.RUN,         None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.DELETE: {
            pygame.K_n:         (State.DEL_NODES,   None,                                                   []),
            pygame.K_e:         (State.DEL_EDGES,   None,                                                   []),
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.DEL_NODES: {
            pygame.K_a:         (State.DELETE,      lambda: print("[Deleting all nodes (vertices)]"),       []),
            pygame.K_ESCAPE:    (State.DELETE,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.DEL_EDGES: {
            pygame.K_a:         (State.DELETE,      lambda: print("[Deleting all edges (links)]"),          []),
            pygame.K_ESCAPE:    (State.DELETE,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.GENERATE: {
            pygame.K_n:         (State.GENERATE,    lambda: print("[Generating nodes]"),                    []),
            pygame.K_s:         (State.GENERATE,    lambda: print("[Generating segments]"),                 []),
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.INSERT: {
            pygame.K_n:         (State.INS_NODES,   None,                                                   []),
            pygame.K_e:         (State.INS_EDGE,    None,                                                   []),
            pygame.K_p:         (State.INS_POLYGON, None,                                                   []),
            pygame.K_s:         (State.INS_SEGMENT, None,                                                   []),
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.INS_NODES: {
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.INS_EDGE: {
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.INS_POLYGON: {
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.INS_SEGMENT: {
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.RUN: {
            pygame.K_c:         (State.CH,          None,                                                   []),
            pygame.K_t:         (State.T,           None,                                                   []),
            pygame.K_l:         (State.LSI,         None,                                                   []),
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.CH: {
            pygame.K_0:         (State.PAUSE,       lambda: print("[Running algo 0]"),                      []),
            pygame.K_1:         (State.PAUSE,       lambda: print("[Running algo 1]"),                      []),
            pygame.K_2:         (State.PAUSE,       lambda: print("[Running algo 2]"),                      []),
            pygame.K_ESCAPE:    (State.RUN,         None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.LSI: {
            pygame.K_0:         (State.PAUSE,       lambda: print("[Running algo 0]"),                      []),
            pygame.K_1:         (State.PAUSE,       lambda: print("[Running algo 1]"),                      []),
            pygame.K_ESCAPE:    (State.RUN,         None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.T: {
            pygame.K_0:         (State.PAUSE,       lambda: print("[Running algo 0]"),                      []),
            pygame.K_ESCAPE:    (State.RUN,         None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.PAUSE: {
            pygame.K_SPACE:     (State.ANIMATE,     None,                                                   []),
            pygame.K_RETURN:    (State.PAUSE,       lambda: print("[Manual step]"),                         []),
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
        State.ANIMATE: {
            pygame.K_SPACE:     (State.PAUSE,       None,                                                   []),
            pygame.K_UP:        (State.ANIMATE,     lambda: print("[Inc. FPS]"),                            []),
            pygame.K_DOWN:      (State.ANIMATE,     lambda: print("[Dec. FPS]"),                            []),
            pygame.K_ESCAPE:    (State.NORMAL,      None,                                                   []),
            pygame.K_q:         (State.NORMAL,      lambda: print("[quit]"),                                []),
        },
    }

    _HELP = {
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
                    "  t   : TRIANGULATION menu",
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
                  "  1   : Bentley-Ottmann",
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

    def __init__(self) -> None:
        self.current_state = State.NORMAL
        self._print_help()

    def handle_event(self, event: pygame.event.Event) -> None:
        transition = self._TRANSITIONS.get(self.current_state, {}).get(event.key)
        if transition is None:
            return

        new_state, action, args = transition
        self.current_state = new_state

        # TODO: call function on visualizer

    def reset_state(self) -> None:
        self.current_state = State.NORMAL
        self._print_help()

    def _print_help(self):
        print("\n" + "=" * 48)
        for line in self._HELP.get(self.current_state, []):
            print(line)
