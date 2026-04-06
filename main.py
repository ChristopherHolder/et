import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, MAP_WIDTH, MAP_HEIGHT
from camera import Camera
from player import Player
from world import World


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.world = World()
        self.camera = Camera()
        self.player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self, dt):
        self.player.handle_input(dt)
        self.camera.update(self.player.rect)

    def draw(self):
        self.world.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
