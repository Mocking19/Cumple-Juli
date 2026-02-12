#shadow_beast.py
import pygame
import math

class ShadowBeast:
    def __init__(self):
        # =========================
        # VISUAL
        # =========================
        self.sprite_sheet = pygame.image.load(
            "assets/sprites/beasts/shadow_beast.png"
        ).convert_alpha()

        self.frame_width = 64
        self.frame_height = 48
        self.frames = self.load_frames()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.frames[0]

        # =========================
        # FLOATING MOTION
        # =========================
        self.float_timer = 0
        self.float_amplitude = 6
        self.follow_offset = (-20, -24)

        # =========================
        # COMBAT MODIFIERS
        # =========================
        self.attack_color = (120, 80, 200)
        self.attack_bonus = 1

    def load_frames(self):
        frames = []
        sheet_width = self.sprite_sheet.get_width()
        frame_count = sheet_width // self.frame_width

        for i in range(frame_count):
            frame = pygame.Surface(
                (self.frame_width, self.frame_height),
                pygame.SRCALPHA
            )
            frame.blit(
                self.sprite_sheet,
                (0, 0),
                (i * self.frame_width, 0,
                 self.frame_width, self.frame_height)
            )
            frames.append(frame)

        return frames

    # =========================
    # APPLY / REMOVE
    # =========================
    def apply(self, player):
        player.attack_damage += self.attack_bonus

    def remove(self, player):
        player.attack_damage -= self.attack_bonus

    # =========================
    # UPDATE
    # =========================
    def update(self):
        self.float_timer += 0.1

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    # =========================
    # DRAW
    # =========================
    def draw(self, surface, player, offset_x=0, offset_y=0):
        offset_x = 8     # al costado
        offset_y = -4    # un poco arriba

        float_y = int(math.sin(pygame.time.get_ticks() * 0.005) * 3)

        x = player.rect.centerx + offset_x
        y = player.rect.centery + offset_y + float_y

        surface.blit(
            self.image,
            (x + offset_x, y + offset_y)
        )
