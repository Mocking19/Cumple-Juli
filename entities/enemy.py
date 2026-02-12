import pygame
from settings import TILE_SIZE

BOSS_PHASES = {
    1: {
        "max_hp": 40,
        "speed": 0.7,
        "damage": 1,
        "idle_sheet": "assets/sprites/enemy1.png",
        "move_sheet": "assets/sprites/enemy1.png",
        "frame_width": 64,
        "frame_height": 64,
        "draw_scale": 3,   
        "regen": False,
        "aggro_enter": TILE_SIZE * 3,
        "aggro_exit": TILE_SIZE * 7,
    },
    2: {
        "max_hp": 80,
        "speed": 2,
        "damage": 2,
        "idle_sheet": "assets/sprites/enemy2_idle.png",
        "move_sheet": "assets/sprites/enemy2_run.png",
        "frame_width": 160,
        "frame_height": 96,
        "draw_scale": 2,
        "regen": False,
        "aggro_enter": TILE_SIZE * 4,
        "aggro_exit": TILE_SIZE * 8,
    },
    3: {
        "max_hp": 150,
        "speed": 0.7,
        "damage": 3,
        "idle_sheet": "assets/sprites/enemy3_idle.png",
        "move_sheet": "assets/sprites/enemy3_idle.png",
        "frame_width": 160,
        "frame_height": 144,
        "draw_scale": 1.5,
        "regen": True,
        "aggro_enter": TILE_SIZE * 5,
        "aggro_exit": TILE_SIZE * 10,

    }
}


class Enemy:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.aggro = False
    
        self.pixel_x = grid_x * TILE_SIZE
        self.pixel_y = grid_y * TILE_SIZE
        
        self.rect = pygame.Rect(
            self.pixel_x,
            self.pixel_y,
            TILE_SIZE,
            TILE_SIZE
        )
        self.phase = 1
        self.damage = 1
        self.spawn_x = self.rect.centerx
        self.spawn_y = self.rect.centery
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y
        self.alive = True
        self.hit_timer = 0
        self.aggro_range = TILE_SIZE * 2
        self.knockback_timer = 0
        self.knockback_dx = 0
        self.knockback_dy = 0
        self.knockback_speed = 4
        # =========================
        # =========================
    
        self.state = "idle"
        self.frame_index = 0
        self.anim_speed = 0.12

        self.enter_phase(1)

    def at_spawn(self):
        return (
            abs(self.rect.centerx - self.spawn_x) <= 1 and
            abs(self.rect.centery - self.spawn_y) <= 1
        )

    def load_animations(self):
        for state, sheet in self.sprite_sheets.items():
            sheet_width = sheet.get_width()
            total_frames = sheet_width // self.frame_width

            for i in range(total_frames):
                frame = pygame.Surface(
                    (self.frame_width, self.frame_height),
                    pygame.SRCALPHA
                )
                frame.blit(
                    sheet,
                    (0, 0),
                    (i * self.frame_width, 0,
                    self.frame_width, self.frame_height)
                )

                if self.draw_scale != 1:
                    frame = pygame.transform.scale(
                        frame,
                        (
                            int(self.frame_width * self.draw_scale),
                            int(self.frame_height * self.draw_scale)
                        )
                    )

                self.animations[state].append(frame)

    def enter_phase(self, phase):
        self.phase = phase
        data = BOSS_PHASES[phase]
        HITBOX_WIDTH = 24
        HITBOX_HEIGHT = 24
        self.rect = pygame.Rect(
            0, 0,
            HITBOX_WIDTH,
            HITBOX_HEIGHT
        )
        self.rect.center = (self.spawn_x, self.spawn_y)
        self.aggro_enter = data.get("aggro_enter", TILE_SIZE * 3)
        self.aggro_exit = data.get("aggro_exit", TILE_SIZE * 6)

        self.max_hp = data["max_hp"]
        self.hp = self.max_hp
        self.speed = data["speed"]
        self.damage = data["damage"]
        self.regen = data["regen"]

        self.frame_width = data["frame_width"]
        self.frame_height = data["frame_height"]
        self.draw_scale = data.get("draw_scale", 1)

        self.sprite_sheets = {
            "idle": pygame.image.load(data["idle_sheet"]).convert_alpha(),
            "move": pygame.image.load(data["move_sheet"]).convert_alpha(),
        }

        self.animations = {"idle": [], "move": []}
        self.load_animations()

        self.state = "idle"
        self.frame_index = 0

        self.rect.center = (self.spawn_x, self.spawn_y)
        self.rect.width = self.frame_width
        self.rect.height = self.frame_height
        self.rect.center = (self.spawn_x, self.spawn_y)


    def take_damage(self, amount, source_rect=None):
        self.hp -= amount
        self.hit_timer = 10

        if source_rect:
            dx = self.rect.centerx - source_rect.centerx
            dy = self.rect.centery - source_rect.centery
            distance = (dx**2 + dy**2) ** 0.5 or 1
            self.knockback_dx = dx / distance
            self.knockback_dy = dy / distance
            self.knockback_timer = 8

        if self.hp <= 0:
            if self.phase < 3:
                self.hp = 0  
            else:
                self.alive = False


    def move_with_collision(self, dx, dy, world):
        # X
        if dx != 0:
            next_rect = self.rect.move(dx, 0)
            grid_x = next_rect.centerx // TILE_SIZE
            grid_y = next_rect.centery // TILE_SIZE
            if not world.is_blocked(grid_x, grid_y):
                self.rect = next_rect

        # Y
        if dy != 0:
            next_rect = self.rect.move(0, dy)
            grid_x = next_rect.centerx // TILE_SIZE
            grid_y = next_rect.centery // TILE_SIZE
            if not world.is_blocked(grid_x, grid_y):
                self.rect = next_rect

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0


    def update(self, player, world):
        if not self.alive:
            return

        # ==============================
        # KNOCKBACK 
        # ==============================
        if self.knockback_timer > 0:
            dx = self.knockback_dx * self.knockback_speed
            dy = self.knockback_dy * self.knockback_speed
            self.move_with_collision(dx, dy, world)
            self.knockback_timer -= 1
            return

        # ==============================
        # HIT VISUAL
        # ==============================
        if self.hit_timer > 0:
            self.hit_timer -= 1

        # ==============================
        # CHASE
        # ==============================
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx**2 + dy**2) ** 0.5

        

        # ==============================
        # AGGRO LOGIC
        # ==============================
        if not self.aggro and distance <= self.aggro_enter:
            self.aggro = True

        if self.aggro and distance >= self.aggro_exit:
            self.aggro = False

        if self.aggro and distance > 0:
            move_x = round(self.speed * dx / distance)
            move_y = round(self.speed * dy / distance)
            self.move_with_collision(move_x, move_y, world)

        else:
            # volver al spawn
            dx = self.spawn_x - self.rect.centerx
            dy = self.spawn_y - self.rect.centery
            dist = (dx**2 + dy**2) ** 0.5

            if dist > 1:
                move_x = round(self.speed * dx / dist)
                move_y = round(self.speed * dy / dist)

                if move_x != 0 or move_y != 0:
                    self.move_with_collision(move_x, move_y, world)

            else:
                # snap final al spawn
                self.rect.centerx = self.spawn_x
                self.rect.centery = self.spawn_y
                self.frame_index += self.anim_speed

            if self.frame_index >= len(self.animations[self.state]):
                self.frame_index = 0
        # ==============================
        # STATE LOGIC 
        # ==============================
        if self.at_spawn():
            self.set_state("idle")
        else:
            self.set_state("move")
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        if distance < TILE_SIZE * 0.8:
            return
        if self.at_spawn():
            self.aggro = False




    def draw(self, surface, offset_x=0, offset_y=0):
        if not self.alive:
            return

        frame = self.animations[self.state][int(self.frame_index)]

        frame = self.animations[self.state][int(self.frame_index)]

        x = self.rect.centerx - frame.get_width() // 2 + offset_x

    
        y = self.rect.bottom - frame.get_height() + offset_y

        surface.blit(frame, (x, y))

        # =========================
        # HP BAR
        # =========================
        bar_width = 40
        bar_height = 5
        hp_ratio = self.hp / self.max_hp

        bar_x = x + frame.get_width() // 2 - bar_width // 2
        bar_y = y - 10

        pygame.draw.rect(
            surface,
            (60, 60, 60),
            (bar_x, bar_y, bar_width, bar_height)
        )

        pygame.draw.rect(
            surface,
            (200, 50, 50),
            (bar_x, bar_y, bar_width * hp_ratio, bar_height)
        )

