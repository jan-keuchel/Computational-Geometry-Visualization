# pyright: reportMissingImports=false
import pygame
pygame.init()
pygame.font.init()

import constants
from graph import Graph
from window import Window
import algorithms


def main():

    window = Window(800, 600)
    g = Graph()
    g.generate_fully_connected(30)

    mst = algorithms.mst_prims(g)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.clear()
        g.draw_edges(window.screen)
        for e in mst:
            e.draw(window.screen, constants.ORANGE, width=5)
        g.draw_nodes(window.screen)
        window.render()

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
