# pyright: reportMissingImports=false
import pygame
pygame.init()
pygame.font.init()

from visualizer import Visualizer
import constants


def main():

    vis = Visualizer()

    vis.new_segments(10)

    vis.line_segment_intersection(constants.line_segment_intersection_algos.BRUTE_FORCE, animate=True)

    vis.clear_screen()

    vis.render_edges()
    vis.render_nodes(compact=True)
    vis.render_intersects(compact=True, color=constants.GREEN)
    
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
