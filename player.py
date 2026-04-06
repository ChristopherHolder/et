import pygame
from settings import (
    PLAYER_SIZE, PLAYER_COLOR, PLAYER_SPEED,
    MAP_WIDTH, MAP_HEIGHT,
)


class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            direction.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            direction.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            direction.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            direction.x += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        self.pos += direction * PLAYER_SPEED * dt
        # clamp to map
        self.pos.x = max(0, min(self.pos.x, MAP_WIDTH - PLAYER_SIZE))
        self.pos.y = max(0, min(self.pos.y, MAP_HEIGHT - PLAYER_SIZE))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface, camera):
        drawn_rect = camera.apply(self.rect)
        pygame.draw.rect(surface, PLAYER_COLOR, drawn_rect)
        # small direction dot in center
        pygame.draw.circle(
            surface, (180, 180, 30),
            drawn_rect.center, PLAYER_SIZE // 6,
        )
