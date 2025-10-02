# pyright: reportMissingImports=false
import pygame
pygame.init()
pygame.font.init()

import constants
from graph import Graph
from window import Window


def main():

    window = Window(800, 600)
    g = Graph()
    g.generate_graph(constants.graph_type.MST_NO_DEG_1, 30)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.clear()
        g.draw_edges(window.screen, constants.ORANGE, 2)
        g.draw_nodes(window.screen, draw_compact=False)
        window.render()

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
