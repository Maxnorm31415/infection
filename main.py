import pygame, random
import numpy as np
from person import Human, Infected

BLACK = (0, 0, 0)

FRAMES_PER_SECOND = 60

def on_the_land(x,y,mask1):
    if mask1.get_at((x,y)):
        return True
    else:
        return False

def main():
    pygame.init()
    screen = pygame.display.set_mode((1600, 821))
    pygame.display.set_caption("Human Infection")
    mask = pygame.mask.from_surface(pygame.image.load('mask.png').convert_alpha())
    world = pygame.image.load('world.png').convert()
    clock = pygame.time.Clock()
    mouse_pos = pygame.mouse.get_pos()
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
        print(on_the_land(mouse_pos[0], mouse_pos[1], mask))
        screen.fill(BLACK)
        screen.blit(world, (0, 0))
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)

if __name__ == "__main__":
    main()