# pyright: reportMissingImports=false
import pygame
from enum import Enum

font = pygame.font.SysFont('Hack Nerd Font', 16)

WIN_WIDTH = 800
WIN_HEIGHT = 600
BORDER_OFFSET = 30

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (244, 103, 110)
BLUE    = (67, 97, 238)
GREEN   = (150, 218, 47)
ORANGE  = (255, 181, 5)

FOREGROUND = (255, 240, 250)
BACKGROUND = (30, 30, 35)

EDGE_COLOR = (180, 160, 190)

FPS = 20

# Rendering
NODE_COMPACT_SIZE = 8
NODE_FULL_SIZE = 15

# Menu output
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
SS = f"{BOLD}{UNDERLINE}"
RESET = "\033[0m"

# -----------------------------------
# --------- Graph Generation --------
# -----------------------------------

MIN_NODE_OFFSET = 30

class mst_algos(Enum):
    PRIMS                       = 0

class graph_type(Enum):
    FULLY_CONNECTED             = 0
    MST_NO_DEG_1                = 1
    MST                         = 2

class convex_hull_algos(Enum):
    BRUTE_FORCE                 = 0
    GRAHAM_SCAN                 = 1
    JARVIS_MARCH                = 2


class lsi_algos(Enum):
    BRUTE_FORCE                 = 0


class problem_types(Enum):
    CH      = "Convex Hull"
    LSI     = "Line-segment Intersection"
    T       = "Triangulation"
