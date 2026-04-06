import math
import pygame
from settings import (
    PLAYER_SIZE, PLAYER_SPEED,
    SKIN_COLOR, HAIR_COLOR, OVERALL_COLOR, OVERALL_BUCKLE,
    SHIRT_COLOR, HAT_STRAW, HAT_BAND, SHOE_COLOR, CHEEK_COLOR,
    WALK_CYCLE_SPEED, MAP_WIDTH, MAP_HEIGHT,
)


class Player:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.facing = pygame.math.Vector2(0, 1)
        self.walk_timer = 0.0
        self.moving = False

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
            self.moving = True
            self.walk_timer += dt * WALK_CYCLE_SPEED
        else:
            self.moving = False
            self.walk_timer = 0.0

        self.pos += direction * PLAYER_SPEED * dt
        self.pos.x = max(0, min(self.pos.x, MAP_WIDTH - PLAYER_SIZE))
        self.pos.y = max(0, min(self.pos.y, MAP_HEIGHT - PLAYER_SIZE))
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface, camera):
        drawn_rect = camera.apply(self.rect)
        cx, cy = drawn_rect.center
        r = PLAYER_SIZE // 2
        angle = math.atan2(self.facing.y, self.facing.x)

        # walk swing: oscillates between -1 and 1
        swing = math.sin(self.walk_timer * math.pi * 2) if self.moving else 0
        # gentle body bob
        bob = abs(swing) * 1.5 if self.moving else 0

        # perpendicular direction helpers
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)
        fwd_x = math.cos(angle)
        fwd_y = math.sin(angle)

        # --- shadow ---
        shadow_w = int(r * 1.4)
        shadow_h = int(r * 0.5)
        shadow_surf = pygame.Surface((shadow_w * 2, shadow_h * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40),
                            (0, 0, shadow_w * 2, shadow_h * 2))
        surface.blit(shadow_surf, (cx - shadow_w, cy - shadow_h + int(r * 0.6)))

        # --- legs (animated) ---
        for side, leg_swing in ((-1, swing), (1, -swing)):
            # leg extends behind body, swings forward/back
            leg_fwd = leg_swing * r * 0.4
            lx = cx + perp_x * side * r * 0.25 - fwd_x * r * 0.2 + fwd_x * leg_fwd
            ly = cy + perp_y * side * r * 0.25 - fwd_y * r * 0.2 + fwd_y * leg_fwd - bob
            # overall leg
            pygame.draw.circle(surface, OVERALL_COLOR, (int(lx), int(ly)), int(r * 0.22))
            # boot at end
            bx = lx - fwd_x * r * 0.3
            by = ly - fwd_y * r * 0.3
            pygame.draw.circle(surface, SHOE_COLOR, (int(bx), int(by)), int(r * 0.2))

        # --- body (torso) ---
        body_y_offset = -bob
        bx = cx
        by = cy + body_y_offset

        # red shirt (slightly behind)
        shirt_x = bx - fwd_x * r * 0.1
        shirt_y = by - fwd_y * r * 0.1
        pygame.draw.circle(surface, SHIRT_COLOR, (int(shirt_x), int(shirt_y)), int(r * 0.5))

        # overalls on top
        pygame.draw.circle(surface, OVERALL_COLOR, (int(bx), int(by)), int(r * 0.45))

        # overall buckles (two little dots on the front)
        for side in (-1, 1):
            buckle_x = bx + perp_x * side * r * 0.2 + fwd_x * r * 0.25
            buckle_y = by + perp_y * side * r * 0.2 + fwd_y * r * 0.25
            pygame.draw.circle(surface, OVERALL_BUCKLE,
                               (int(buckle_x), int(buckle_y)), int(r * 0.08))

        # --- arms (animated, swing opposite to legs, gentler than legs) ---
        arm_swing = swing * 0.5
        for side, a_swing in ((-1, -arm_swing), (1, arm_swing)):
            arm_fwd = a_swing * r * 0.35
            ax = bx + perp_x * side * r * 0.55 + fwd_x * arm_fwd
            ay = by + perp_y * side * r * 0.55 + fwd_y * arm_fwd
            # shirt sleeve
            pygame.draw.circle(surface, SHIRT_COLOR, (int(ax), int(ay)), int(r * 0.2))
            # hand
            hx = ax - fwd_x * r * 0.15
            hy = ay - fwd_y * r * 0.15
            pygame.draw.circle(surface, SKIN_COLOR, (int(hx), int(hy)), int(r * 0.15))

        # --- head ---
        head_dist = r * 0.5
        hx = bx + fwd_x * head_dist
        hy = by + fwd_y * head_dist
        head_r = int(r * 0.45)

        # hair behind head
        hair_x = hx - fwd_x * head_r * 0.3
        hair_y = hy - fwd_y * head_r * 0.3
        pygame.draw.circle(surface, HAIR_COLOR, (int(hair_x), int(hair_y)), int(head_r * 0.9))

        # head
        pygame.draw.circle(surface, SKIN_COLOR, (int(hx), int(hy)), head_r)

        # rosy cheeks
        for side in (-1, 1):
            cheek_x = hx + perp_x * side * head_r * 0.5 + fwd_x * head_r * 0.15
            cheek_y = hy + perp_y * side * head_r * 0.5 + fwd_y * head_r * 0.15
            pygame.draw.circle(surface, CHEEK_COLOR,
                               (int(cheek_x), int(cheek_y)), int(head_r * 0.25))

        # little eyes
        for side in (-1, 1):
            ex = hx + perp_x * side * head_r * 0.3 + fwd_x * head_r * 0.45
            ey = hy + perp_y * side * head_r * 0.3 + fwd_y * head_r * 0.45
            pygame.draw.circle(surface, (30, 30, 30),
                               (int(ex), int(ey)), int(head_r * 0.18))
            # eye shine
            sx = ex + fwd_x * head_r * 0.05 + perp_x * side * head_r * 0.05
            sy = ey + fwd_y * head_r * 0.05 + perp_y * side * head_r * 0.05
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(sx), int(sy)), int(head_r * 0.08))

        # --- straw hat (big and distinctive) ---
        hat_x = hx + fwd_x * head_r * 0.05
        hat_y = hy + fwd_y * head_r * 0.05
        deg = -math.degrees(angle) + 90
        outline_col = (90, 70, 30)
        straw_light = (245, 225, 160)
        straw_dark = (210, 185, 115)
        ol = 3  # outline width

        # --- wide brim ---
        brim_w = int(head_r * 2.6)
        brim_h = int(head_r * 2.2)
        bsz = ((brim_w + ol) * 2, (brim_h + ol) * 2)
        brim_surf = pygame.Surface(bsz, pygame.SRCALPHA)
        # dark outline ellipse
        pygame.draw.ellipse(brim_surf, outline_col, (0, 0, bsz[0], bsz[1]))
        # main straw fill
        inner = (ol, ol, brim_w * 2, brim_h * 2)
        pygame.draw.ellipse(brim_surf, HAT_STRAW, inner)
        # straw weave: alternating light/dark concentric rings
        cx_b, cy_b = bsz[0] // 2, bsz[1] // 2
        for ring in range(3, max(brim_w, brim_h), 5):
            col = straw_dark if (ring // 5) % 2 == 0 else straw_light
            rect = (cx_b - ring, cy_b - ring, ring * 2, int(ring * 2 * brim_h / brim_w))
            pygame.draw.ellipse(brim_surf, col, rect, 1)
        # clip weave to inner ellipse by redrawing outline on top
        pygame.draw.ellipse(brim_surf, outline_col, (0, 0, bsz[0], bsz[1]), ol)

        brim_surf = pygame.transform.rotate(brim_surf, deg)
        surface.blit(brim_surf, brim_surf.get_rect(center=(int(hat_x), int(hat_y))))

        # --- hat crown (dome on top) ---
        crown_w = int(head_r * 1.3)
        crown_h = int(head_r * 1.1)
        csz = (crown_w * 2 + ol * 2, crown_h * 2 + ol * 2)
        crown_surf = pygame.Surface(csz, pygame.SRCALPHA)
        pygame.draw.ellipse(crown_surf, outline_col, (0, 0, csz[0], csz[1]))
        pygame.draw.ellipse(crown_surf, HAT_STRAW, (ol, ol, crown_w * 2, crown_h * 2))
        # subtle highlight on crown
        pygame.draw.ellipse(crown_surf, straw_light,
                            (ol + crown_w // 3, ol + crown_h // 3,
                             crown_w, crown_h), 0)
        # hat band (thick ribbon stripe)
        band_h = max(4, int(crown_h * 0.4))
        band_y = crown_h + ol - band_h // 2
        pygame.draw.rect(crown_surf, HAT_BAND, (ol, band_y, crown_w * 2, band_h))
        # ribbon bow knot on the side
        bow_x = ol + crown_w * 2 - int(crown_w * 0.15)
        bow_y = band_y + band_h // 2
        for dy in (-4, 4):
            pygame.draw.ellipse(crown_surf, HAT_BAND,
                                (bow_x - 4, bow_y + dy - 3, 8, 6))
        pygame.draw.circle(crown_surf, (140, 65, 40), (bow_x, bow_y), 2)

        crown_surf = pygame.transform.rotate(crown_surf, deg)
        surface.blit(crown_surf, crown_surf.get_rect(center=(int(hat_x), int(hat_y))))
