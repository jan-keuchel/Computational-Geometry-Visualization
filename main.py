# pyright: reportMissingImports=false
import pygame
pygame.init()
pygame.font.init()

from visualizer import Visualizer
import constants


def main():

    vis = Visualizer()
    vis.new_nodes(20)
    vis.convex_hull(constants.convex_hull_algos.BRUTE_FORCE)

    vis.clear_screen()

    vis.render_convex_hull()
    vis.render_nodes(compact=False)
    vis.render_screen()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
