import pygame
import os

class DialogueManager:
    def __init__(self):
        self.active = False
        self.lines = []
        self.index = 0
        self.font = pygame.font.Font(None, 24)

        # cache de retratos
        self.portraits = {}

    # =========================
    # PORTRAIT LOADER
    # =========================
    def get_portrait(self, name):
        if name is None:
            return None

        if name not in self.portraits:
            path = f"assets/portraits/{name}.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (256, 256))
                self.portraits[name] = img
            else:
                self.portraits[name] = None

        return self.portraits[name]

    # =========================
    def start(self, lines):
        """
        lines = [
            (speaker, text, portrait_name)
        ]
        """
        self.lines = lines
        self.index = 0
        self.active = True

    # =========================
    def update(self, events):
        if not self.active:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.index += 1
                    if self.index >= len(self.lines):
                        self.active = False

    # =========================
    def draw(self, surface):
        if not self.active:
            return

        speaker, text, portrait_name = self.lines[self.index]

        screen_w, screen_h = surface.get_size()

        # =========================
        # PORTRAIT
        # =========================
        portrait = self.get_portrait(portrait_name)
        if portrait:
            surface.blit(
                portrait,
                (40, screen_h - 256 - 140)
            )

        # =========================
        # BOX
        # =========================
        box_rect = pygame.Rect(
            20, screen_h - 120,
            screen_w - 40, 100
        )

        pygame.draw.rect(surface, (10, 10, 10), box_rect)
        pygame.draw.rect(surface, (200, 200, 200), box_rect, 2)

        # speaker
        speaker_text = self.font.render(
            speaker,
            True,
            (255, 220, 120)
        )
        surface.blit(speaker_text, (box_rect.x + 20, box_rect.y + 8))

        # text
        rendered = self.font.render(
            text,
            True,
            (230, 230, 230)
        )
        surface.blit(rendered, (box_rect.x + 20, box_rect.y + 40))
