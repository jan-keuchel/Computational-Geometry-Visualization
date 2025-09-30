# pyright: reportMissingImports=false
from node import Node
import pygame
from window import Window

def main():
    pygame.init()
    pygame.font.init()

    window = Window(800, 600)

    n = Node(9, 100, 100)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        window.clear()
        n.draw(window.screen, window.font)
        window.render()

    pygame.font.quit()
    pygame.quit()

if __name__ == "__main__":
    main()
