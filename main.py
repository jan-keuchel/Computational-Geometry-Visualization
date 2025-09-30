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
    g.init_graph()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.clear()
        g.draw(window.screen)
        window.render()

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
