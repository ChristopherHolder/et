import math
import random
import pygame
from settings import (
    MAP_WIDTH, MAP_HEIGHT, PLAYER_SIZE,
    TREE_COUNT, TREE_SEED, TREE_MIN_RADIUS, TREE_MAX_RADIUS,
)


def _render_tree(radius, rng):
    """Pre-render one tree to a surface. Returns (surface, trunk_base_offset_y)."""
    trunk_w = max(6, int(radius * 0.3))
    trunk_h = max(10, int(radius * 0.6))
    canopy_r = radius
    # total size: canopy on top, trunk below
    w = canopy_r * 2 + 20
    h = canopy_r * 2 + trunk_h + 20
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    cx = w // 2
    trunk_top = canopy_r + 10
    trunk_bot = trunk_top + trunk_h

    # --- shadow on ground ---
    shadow_w = int(canopy_r * 1.2)
    shadow_h = int(canopy_r * 0.4)
    pygame.draw.ellipse(surf, (0, 0, 0, 35),
                        (cx - shadow_w, trunk_bot - shadow_h // 2,
                         shadow_w * 2, shadow_h))

    # --- trunk ---
    trunk_col = (110, 75, 45)
    trunk_dark = (85, 55, 30)
    trunk_rect = pygame.Rect(cx - trunk_w // 2, trunk_top, trunk_w, trunk_h)
    pygame.draw.rect(surf, trunk_col, trunk_rect, border_radius=3)
    # bark detail: a couple darker lines
    for i in range(2):
        bx = cx - trunk_w // 4 + rng.randint(0, trunk_w // 2)
        by1 = trunk_top + rng.randint(2, trunk_h // 3)
        by2 = by1 + rng.randint(4, trunk_h // 2)
        pygame.draw.line(surf, trunk_dark, (bx, by1), (bx, by2), 1)
    # small roots at base
    for side in (-1, 1):
        rx = cx + side * trunk_w // 2
        pygame.draw.line(surf, trunk_col,
                         (rx, trunk_bot - 2),
                         (rx + side * rng.randint(3, 6), trunk_bot + 1), 2)

    # --- canopy (layered circles for a lush look) ---
    base_green = (40, 160, 50)
    mid_green = (55, 185, 65)
    light_green = (90, 210, 90)
    highlight = (130, 230, 120)

    # big base shadow layer
    pygame.draw.circle(surf, (25, 110, 30),
                       (cx, trunk_top - int(canopy_r * 0.05)),
                       canopy_r + 2)

    # main canopy blobs — a few overlapping circles
    blobs = []
    blobs.append((cx, trunk_top - int(canopy_r * 0.1), canopy_r, base_green))
    for _ in range(5):
        bx = cx + rng.randint(-canopy_r // 2, canopy_r // 2)
        by = trunk_top - int(canopy_r * 0.1) + rng.randint(-canopy_r // 2, canopy_r // 3)
        br = rng.randint(int(canopy_r * 0.45), int(canopy_r * 0.75))
        blobs.append((bx, by, br, mid_green))

    for bx, by, br, col in blobs:
        pygame.draw.circle(surf, col, (bx, by), br)

    # lighter accent blobs on top
    for _ in range(3):
        bx = cx + rng.randint(-canopy_r // 3, canopy_r // 3)
        by = trunk_top - int(canopy_r * 0.2) + rng.randint(-canopy_r // 3, canopy_r // 4)
        br = rng.randint(int(canopy_r * 0.25), int(canopy_r * 0.45))
        pygame.draw.circle(surf, light_green, (bx, by), br)

    # small bright highlights
    for _ in range(2):
        bx = cx + rng.randint(-canopy_r // 4, canopy_r // 4)
        by = trunk_top - int(canopy_r * 0.3) + rng.randint(-canopy_r // 4, canopy_r // 6)
        br = rng.randint(int(canopy_r * 0.12), int(canopy_r * 0.22))
        pygame.draw.circle(surf, highlight, (bx, by), br)

    # canopy outline for definition
    pygame.draw.circle(surf, (25, 110, 30),
                       (cx, trunk_top - int(canopy_r * 0.1)),
                       canopy_r, 2)

    # trunk_base_offset_y = distance from top of surface to trunk bottom
    return surf, trunk_bot


class Trees:
    def __init__(self):
        rng = random.Random(TREE_SEED)
        self.trees = []  # list of (world_x, world_y, surface, y_sort)

        margin = TREE_MAX_RADIUS + 20
        spawn_margin = PLAYER_SIZE * 4  # keep trees away from spawn center
        spawn_cx, spawn_cy = MAP_WIDTH // 2, MAP_HEIGHT // 2

        for _ in range(TREE_COUNT):
            radius = rng.randint(TREE_MIN_RADIUS, TREE_MAX_RADIUS)
            surf, base_y_offset = _render_tree(radius, rng)

            # pick position, avoid map edges and player spawn
            for _attempt in range(20):
                wx = rng.randint(margin, MAP_WIDTH - margin)
                wy = rng.randint(margin, MAP_HEIGHT - margin)
                dx = wx - spawn_cx
                dy = wy - spawn_cy
                if math.hypot(dx, dy) > spawn_margin:
                    break

            # y_sort: the trunk base in world coords (for depth sorting)
            y_sort = wy + base_y_offset - surf.get_height() // 2
            self.trees.append((wx, wy, surf, y_sort))

        # sort by y so we can interleave with player later
        self.trees.sort(key=lambda t: t[3])

    def _draw_range(self, surface, camera, start, end):
        for i in range(start, end):
            wx, wy, tree_surf, y_sort = self.trees[i]
            sw, sh = tree_surf.get_size()
            world_rect = pygame.Rect(wx - sw // 2, wy - sh // 2, sw, sh)
            screen_rect = camera.apply(world_rect)
            surface.blit(tree_surf, screen_rect)

    def draw_behind(self, surface, camera, player_y):
        """Draw trees whose base is above (behind) the player. Returns split index."""
        split = len(self.trees)
        for i, (wx, wy, tree_surf, y_sort) in enumerate(self.trees):
            if y_sort > player_y:
                split = i
                break
        self._draw_range(surface, camera, 0, split)
        return split

    def draw_front(self, surface, camera, split):
        """Draw trees whose base is below (in front of) the player."""
        self._draw_range(surface, camera, split, len(self.trees))
