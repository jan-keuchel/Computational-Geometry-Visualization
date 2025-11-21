# pyright: reportMissingImports=false
import pygame
from enum import Enum

font = pygame.font.SysFont('Hack Nerd Font', 16)

WIN_WIDTH = 1000
WIN_HEIGHT = 800
BORDER_OFFSET = 30

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (239, 118, 122)
BLUE    = (107, 164, 255)
PURPLE  = (79, 43, 255)
GREEN   = (35, 240, 199)
ORANGE  = (255, 172, 70)

FOREGROUND = (255, 240, 250)
BACKGROUND = (6, 17, 21)

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

# Warnings output
FONT_ORANGE = "\033[38;5;208m"
FONT_RED = "\033[91m"
WARNING = f"{BOLD}{FONT_ORANGE}"
ERROR = f"{BOLD}{FONT_RED}"

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
