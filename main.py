# pyright: reportMissingImports=false
import pygame
pygame.init()
pygame.font.init()

from state_machine import State
from visualizer import Visualizer
import constants


def main():

    vis = Visualizer()
    clock = pygame.time.Clock()

    running = True
    while running:

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                vis.clear_screen()
                vis.display_screen()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                    vis.clear_screen()
                    vis.display_screen()
                else:
                    vis.process_input(event)


        if vis.get_state() == State.ANIMATE:
            vis.step_simulation()
            # vis.update_screen()
            clock.tick(vis.fps)

        if vis.get_state() == State.PAUSE:
            clock.tick()


        vis.update_screen()

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
