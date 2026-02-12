import pygame
import math
from entities.beast import Beast

class HellCat(Beast):
    def __init__(self):
        super().__init__()
        self.name = "Hell Cat"
        self.attack_bonus = 2
        self.attack_color = (255, 120, 40)

        # ========= SPRITESHEET =========
        self.sprite_sheet = pygame.image.load(
            "assets/sprites/beasts/hell_cat.png"
        ).convert_alpha()

        self.frame_width = 98
        self.frame_height = 56

        self.frames = self.load_frames()
        self.frame_index = 0
        self.animation_speed = 0.18
        self.image = self.frames[0]

    def load_frames(self):
        frames = []
        sheet_w = self.sprite_sheet.get_width()
        frame_count = sheet_w // self.frame_width

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

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def draw(self, surface, player, offset_x=0, offset_y=0):
        self.update()

        float_y = int(math.sin(pygame.time.get_ticks() * 0.006) * 3)

        x = player.rect.centerx - 24 + offset_x
        y = player.rect.centery - 18 + offset_y + float_y

        surface.blit(self.image, (x, y))
