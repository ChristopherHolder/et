import pygame
from settings import (
    MAP_WIDTH, MAP_HEIGHT, MAP_COLOR,
    GRID_COLOR, GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
)


class World:
    def __init__(self):
        pass

    def draw(self, surface, camera):
        surface.fill(MAP_COLOR)

        ox, oy = int(camera.offset.x), int(camera.offset.y)

        # draw grid lines visible on screen
        start_x = -(ox % GRID_SIZE)
        start_y = -(oy % GRID_SIZE)

        for x in range(start_x, SCREEN_WIDTH + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(start_y, SCREEN_HEIGHT + GRID_SIZE, GRID_SIZE):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

        # map border (white outline)
        border = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        drawn = camera.apply(border)
        pygame.draw.rect(surface, (255, 255, 255), drawn, 2)
