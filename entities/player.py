# entities/player.py
import pygame
from settings import TILE_SIZE

class Player:
    def __init__(self, grid_x, grid_y):

        self.grid_x = grid_x
        self.grid_y = grid_y

        self.pixel_x = grid_x * TILE_SIZE
        self.pixel_y = grid_y * TILE_SIZE

        self.sprite_sheet = pygame.image.load(
            "assets/sprites/player.png"
        ).convert_alpha()

        self.frame_width = TILE_SIZE
        self.frame_height = TILE_SIZE
        self.flip = False

        self.animations = {
            "idle_down": self.load_animation(row=0, frames=1),
            "walk_down": self.load_animation(row=0, frames=4),

            "idle_right": self.load_animation(row=1, frames=1),
            "walk_right": self.load_animation(row=1, frames=4),

            "idle_up": self.load_animation(row=2, frames=1),
            "walk_up": self.load_animation(row=2, frames=4),
        }


        self.state = "idle_down"
        self.image = self.animations[self.state][0]
        self.current_animation = self.state

        self.frame_index = 0
        self.animation_speed = 0.15

        self.rect = self.image.get_rect(
            topleft=(self.pixel_x, self.pixel_y)
        )

        self.base_speed = 4
        self.speed = self.base_speed

        self.base_damage = 10
        self.attack_damage = self.base_damage

        self.base_max_hp = 20
        self.max_hp = self.base_max_hp
        self.hp = self.max_hp

        self.moving = False
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.direction = "down"
        self.attack_cooldown = 0
        self.max_hp = 20
        self.hp = self.max_hp
        self.invul_timer = 0
        self.knockback_timer = 0
        self.knockback_dx = 0
        self.knockback_dy = 0
        self.knockback_speed = 6
        self.hurt_timer = 0
        self.hurt_duration = 15
        self.beast = None
        # ===== ATTACK ANIMATION =====
        self.attack_sheet = pygame.image.load(
            "assets/sprites/attack1.png"
        ).convert_alpha()
        # tamaño default ataque
        self.attack_frame_width = TILE_SIZE
        self.attack_frame_height = TILE_SIZE
        self.attack_frames = self.load_attack_animation(frames=4)
        self.attack_frame_index = 0
        self.attack_anim_speed = 0.25
        self.attacking = False

    def load_animation(self, row, frames):
        animation = []
        for i in range(frames):
            frame = pygame.Surface(
                (self.frame_width, self.frame_height),
                pygame.SRCALPHA
            )
            frame.blit(
                self.sprite_sheet,
                (0, 0),
                (i * self.frame_width, row * self.frame_height,
                self.frame_width, self.frame_height)
            )
            animation.append(frame)
        return animation

    def load_attack_animation(self, frames):
        animation = []

        for i in range(frames):
            frame = pygame.Surface(
                (self.attack_frame_width, self.attack_frame_height),
                pygame.SRCALPHA
            )

            frame.blit(
                self.attack_sheet,
                (0, 0),
                (
                    i * self.attack_frame_width,
                    0,
                    self.attack_frame_width,
                    self.attack_frame_height
                )
            )

            animation.append(frame)

        return animation



    def update(self, keys, world):

        # ---------------- KNOCKBACK ----------------
        if self.knockback_timer > 0:
            dx = self.knockback_dx * self.knockback_speed
            dy = self.knockback_dy * self.knockback_speed
            self.move_with_collision(dx, dy, world)
            self.knockback_timer -= 1

            # 🔒 apagar completamente el sistema tileado
            return

            # 🔴 SALIR DEL UPDATE




        # ---------------- TIMERS ----------------
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.invul_timer > 0:
            self.invul_timer -= 1
        # ===== ATTACK ANIMATION =====
        # ===== ATTACK ANIMATION =====
        if self.attacking:
            self.attack_frame_index += self.attack_anim_speed

            if self.attack_frame_index >= len(self.attack_frames):
                self.attacking = False
                self.attack_frame_index = 0

            return # bloquea movimiento mientras ataca

        # ---------------- INPUT ----------------
        can_move = self.knockback_timer == 0

        if can_move and not self.moving:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.direction = "up"
                self.start_move(0, -1, world)
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.direction = "down"
                self.start_move(0, 1, world)
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.direction = "left"
                self.start_move(-1, 0, world)
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.direction = "right"
                self.start_move(1, 0, world)

        # ---------------- ANIMATION ----------------
        state = "walk" if self.moving else "idle"

        anim_dir = "right" if self.direction == "left" else self.direction
        self.flip = self.direction == "left"

        anim_key = f"{state}_{anim_dir}"

        if anim_key != self.current_animation:
            self.current_animation = anim_key
            self.frame_index = 0

        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[anim_key]):
            self.frame_index = 0

        self.image = self.animations[anim_key][int(self.frame_index)]

        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            can_move = self.knockback_timer == 0
            if self.hurt_timer > 0:
                state = "idle"
            else:
                state = "walk" if self.moving else "idle"

        # ---------------- MOVEMENT ----------------
        self.move()


    def start_move(self, dx, dy, world):
        next_x = self.grid_x + dx
        next_y = self.grid_y + dy

        if world.is_blocked(next_x, next_y):
            return

        self.grid_x = next_x
        self.grid_y = next_y
        self.target_x = self.grid_x * TILE_SIZE
        self.target_y = self.grid_y * TILE_SIZE
        self.moving = True


    def move(self):
        if self.moving:
            if self.pixel_x < self.target_x:
                self.pixel_x += self.speed
            if self.pixel_x > self.target_x:
                self.pixel_x -= self.speed
            if self.pixel_y < self.target_y:
                self.pixel_y += self.speed
            if self.pixel_y > self.target_y:
                self.pixel_y -= self.speed

            if (
                abs(self.pixel_x - self.target_x) <= self.speed and
                abs(self.pixel_y - self.target_y) <= self.speed
            ):
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False


            self.rect.topleft = (self.pixel_x, self.pixel_y)

    def attack(self):
        if self.attack_cooldown > 0 or self.knockback_timer > 0:
            return None, 0

        self.attacking = True
        self.attack_frame_index = 0

        size = getattr(self, "attack_hitbox_size", 30)
        x, y = self.rect.center


        if self.direction == "up":
            hitbox = pygame.Rect(x - size//2, y - TILE_SIZE, size, size)
        elif self.direction == "down":
            hitbox = pygame.Rect(x - size//2, y + TILE_SIZE//2, size, size)
        elif self.direction == "left":
            hitbox = pygame.Rect(x - TILE_SIZE, y - size//2, size, size)
        else:
            hitbox = pygame.Rect(x + TILE_SIZE//2, y - size//2, size, size)

        self.attack_cooldown = 20
        return hitbox, self.attack_damage
    
    def move_with_collision(self, dx, dy, world):
        # Movimiento X
        if dx != 0:
            next_rect = self.rect.move(dx, 0)
            grid_x = next_rect.centerx // TILE_SIZE
            grid_y = next_rect.centery // TILE_SIZE

            if not world.is_blocked(grid_x, grid_y):
                self.rect = next_rect
                self.pixel_x = self.rect.x

        # Movimiento Y
        if dy != 0:
            next_rect = self.rect.move(0, dy)
            grid_x = next_rect.centerx // TILE_SIZE
            grid_y = next_rect.centery // TILE_SIZE

            if not world.is_blocked(grid_x, grid_y):
                self.rect = next_rect
                self.pixel_y = self.rect.y

    def take_damage(self, amount, source_rect=None):
        if self.invul_timer > 0:
            return

        self.hp -= amount
        self.invul_timer = 30
        self.hurt_timer = self.hurt_duration

        # 🔧 resetear movimiento tileado
        self.moving = False

        if source_rect:
            dx = self.rect.centerx - source_rect.centerx
            dy = self.rect.centery - source_rect.centery
            distance = (dx**2 + dy**2) ** 0.5 or 1

            self.knockback_dx = dx / distance
            self.knockback_dy = dy / distance
            self.knockback_timer = 10

            # 🔧 enganchar grilla al inicio del knockback
            self.grid_x = self.rect.centerx // TILE_SIZE
            self.grid_y = self.rect.centery // TILE_SIZE
            self.target_x = self.grid_x * TILE_SIZE
            self.target_y = self.grid_y * TILE_SIZE

    def set_attack_sprite(self, path, frames,frame_w=None, frame_h=None):

        self.attack_sheet = pygame.image.load(path).convert_alpha()

        if frame_w:
            self.attack_frame_width = frame_w
        if frame_h:
            self.attack_frame_height = frame_h

        self.attack_frames = self.load_attack_animation(frames)
        self.attack_frame_index = 0


    def draw_beast_near_player(self, surface, offset_x=0, offset_y=0):
        self.beast.draw(surface, self, offset_x, offset_y)

    def draw(self, surface, offset_x=0, offset_y=0):
        if self.invul_timer > 0 and self.invul_timer % 6 < 3:
            return

        surface.blit(
            self.image,
            (self.rect.x + offset_x, self.rect.y + offset_y)
        )
        if self.attacking:
            frame = self.attack_frames[int(self.attack_frame_index)]

            cx, cy = self.rect.center

            if self.direction == "up":
                pos = (cx - frame.get_width()//2,
                    self.rect.top - frame.get_height())

            elif self.direction == "down":
                pos = (cx - frame.get_width()//2,
                    self.rect.bottom)

            elif self.direction == "left":
                frame = pygame.transform.flip(frame, True, False)
                pos = (self.rect.left - frame.get_width(),
                    cy - frame.get_height()//2)

            else:  # right
                pos = (self.rect.right,
                    cy - frame.get_height()//2)

            surface.blit(frame, (pos[0] + offset_x, pos[1] + offset_y))

        if self.beast:
            self.beast.update()
            self.beast.draw(surface, self, offset_x, offset_y)



        
