import math
import pygame
from settings import (
    PLAYER_SIZE, PLAYER_SPEED,
    SKIN_COLOR, SHIRT_COLOR, PANTS_COLOR, HAIR_COLOR, SHOE_COLOR,
    MAP_WIDTH, MAP_HEIGHT,
)


class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.facing = pygame.math.Vector2(0, 1)  # default facing down

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
            self.facing = direction.copy()

        self.pos += direction * PLAYER_SPEED * dt
        self.pos.x = max(0, min(self.pos.x, MAP_WIDTH - PLAYER_SIZE))
        self.pos.y = max(0, min(self.pos.y, MAP_HEIGHT - PLAYER_SIZE))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface, camera):
        drawn_rect = camera.apply(self.rect)
        cx, cy = drawn_rect.center
        r = PLAYER_SIZE // 2

        angle = math.atan2(self.facing.y, self.facing.x)

        # --- legs / feet (drawn behind body) ---
        leg_offset = r * 0.3
        leg_dist = r * 0.55
        for side in (-1, 1):
            perp_x = -math.sin(angle) * side * leg_offset
            perp_y = math.cos(angle) * side * leg_offset
            # leg extends backward from facing direction
            lx = cx + perp_x - math.cos(angle) * leg_dist
            ly = cy + perp_y - math.sin(angle) * leg_dist
            # thigh (pants)
            pygame.draw.circle(surface, PANTS_COLOR, (int(lx), int(ly)), int(r * 0.25))
            # shoe a bit further back
            sx = lx - math.cos(angle) * r * 0.25
            sy = ly - math.sin(angle) * r * 0.25
            pygame.draw.circle(surface, SHOE_COLOR, (int(sx), int(sy)), int(r * 0.2))

        # --- body (torso) ---
        pygame.draw.circle(surface, SHIRT_COLOR, (cx, cy), int(r * 0.6))

        # --- arms ---
        arm_dist = r * 0.35
        for side in (-1, 1):
            perp_x = -math.sin(angle) * side * (r * 0.6)
            perp_y = math.cos(angle) * side * (r * 0.6)
            ax = cx + perp_x - math.cos(angle) * arm_dist
            ay = cy + perp_y - math.sin(angle) * arm_dist
            pygame.draw.circle(surface, SKIN_COLOR, (int(ax), int(ay)), int(r * 0.2))

        # --- head ---
        head_dist = r * 0.5
        hx = cx + math.cos(angle) * head_dist
        hy = cy + math.sin(angle) * head_dist
        head_r = int(r * 0.45)
        pygame.draw.circle(surface, SKIN_COLOR, (int(hx), int(hy)), head_r)

        # hair (semicircle on the back of the head)
        hair_cx = hx - math.cos(angle) * head_r * 0.3
        hair_cy = hy - math.sin(angle) * head_r * 0.3
        pygame.draw.circle(surface, HAIR_COLOR, (int(hair_cx), int(hair_cy)), int(head_r * 0.85))
        # redraw front of head over hair to make it a half-coverage
        fore_cx = hx + math.cos(angle) * head_r * 0.2
        fore_cy = hy + math.sin(angle) * head_r * 0.2
        pygame.draw.circle(surface, SKIN_COLOR, (int(fore_cx), int(fore_cy)), int(head_r * 0.7))
