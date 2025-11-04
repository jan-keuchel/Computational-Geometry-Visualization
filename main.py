# pyright: reportMissingImports=false
import pygame
pygame.init()
pygame.font.init()

from visualizer import Visualizer
import constants


def main():

    vis = Visualizer()

    vis.clear_screen()
    vis.render_screen()

    # vis.new_segments(10)
    # vis.new_custom_nodes()
    vis.new_custom_polygon()

    # vis.line_segment_intersection(constants.line_segment_intersection_algos.BRUTE_FORCE, animate=True)
    vis.convex_hull(constants.convex_hull_algos.JARVIS_MARCH,animate=True)

    vis.clear_screen()

    vis.render_edges()
    # vis.render_intersects(compact=True, color=constants.GREEN)
    vis.render_convex_hull(constants.GREEN,edge_width=3)
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
