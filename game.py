# game.py
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from entities.player import Player
from world.map import WorldMap
from entities.enemy import Enemy
import random
from ui.dialogue import DialogueManager
from entities.beasts.shadow_beast import ShadowBeast
from entities.beasts.hell_cat import HellCat
from entities.beasts.werewolf import WereWolf

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        pygame.display.set_caption("RPG Fantasía Oscura")
        self.clock = pygame.time.Clock()
        self.running = True
        self.world = WorldMap()
        self.player = Player(1, 1)
        self.attack_hitbox = None
        self.attack_timer = 0
        self.enemy = Enemy(10, 8)
        self.attack_applied = False
        self.hit_stop = 0
        self.shake_timer = 0
        self.shake_intensity = 4
        self.game_state = "dialogue"  # "dialogue" | "combat"
        self.attack_damage = 1
        self.ending_shown = False
        self.final_text = ""
        self.dialogue = DialogueManager()
        self.dialogue.start([
        ("Narrador","En un mundo cubierto por sombras...", None),
        ("Narrador","...una heroína y su más reciente compañero Nilo dan un paso al frente.", None),
        ("Juli","No está sola.","juli"),
        ("Narrador","Una bestia oscura se ha unido a su causa.", None),
        ("Nilo","Estoy contigo.","nilo"),
        ("Narrador","Se enfrentan al Cambiaformas, comandante N° 32+2 del Rey Demonio", None),
        ("Narrador","El destino del reino pende de un hilo...", None),
        ("Juli","Bueno, otro año más acá... ", "juli"),
        ("Juli","¿Me vas a prestar tu poder?", "juli"),
        ("Nilo","Siempre y cuando no hayan escaleras oscuras, cuenta conmigo.","nilo"),
        ("Juli","Vamos Nilo!", "juli"),
        ("Nilo","Vamos SAPAYA!", "nilo"),
        ("Narrador","W A S D (movimiento) | Space (golpear)", None),
        ])
        self.pending_final_dialogue = False
        self.player.beast = ShadowBeast()
        self.player.beast.apply(self.player)
        ##self.player.beast.remove(self.player)
        self.pending_phase_change = False
        self.revived_once = False


    def run(self):
        while self.running:
            self.clock.tick(FPS)
            events = pygame.event.get()
            self.handle_events(events)
            self.update(events)
            self.draw()

        pygame.quit()

    def handle_events(self, events):
        if self.game_state == "ending":
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.__init__()   # reinicia juego completo
            return

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            if self.game_state != "combat":
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    hitbox, damage = self.player.attack()
                    if hitbox:
                        self.attack_hitbox = hitbox
                        self.attack_damage = damage
                        self.attack_timer = 10
                        self.attack_applied = False

    def start_phase_transition(self):
        self.game_state = "dialogue"
        self.pending_phase_change = True

        if self.enemy.phase == 1:
            self.dialogue.start([
            ("Narrador","La criatura se retuerce entre sombras...", None),
            ("Narrador","...sufre una transformación grotesca", None),
            ("Nilo","AAAAAA una escalera oscura me caí","nilo"),
            ("Juli","Aguanta conmigo gordito.","juli"),
            ("Nilo","No puedo moverme, tambien me mordió un CHow Chow","nilo"),
            ("Juli","Nooo, ¿ahora que voy a hacer?.","juli"),
            ("Frida","Yo tomaré el relevo.","frida"),
            ("Juli","Frida! al final si me querías o.o.","juli"),
            ("Frida","Siempre y cuando sea alimentada","frida"),
            ("Juli","Vamos Frida!","juli"),
            ("Frida","Vamos sepiyo! digo waaaaw","frida"),
            ])


        elif self.enemy.phase == 2:
            self.dialogue.start([
                ("Frida","Ya no puedo seguir...","frida"),
                ("Juli","¿Que paso Frida? Ya casi lo tenemos!.","juli"),
                ("Frida","Me pegue un atracón! :C","frida"),
                ("Juli","No importa, se que puedo...","juli"),
                ("Juli","...pero ojalá...","juli"),
                ("Juli","...hubiera alguien más.","juli"),
                ("Narrador","Un viejo recuerdo despierta.", None),
            ])


    def apply_phase_changes(self):
        next_phase = self.enemy.phase + 1

        if next_phase > 3:
            return

        # boss
        self.enemy.enter_phase(next_phase)

        # map visual
        self.world.set_phase(next_phase)

        # quitar bestia actual
        if self.player.beast:
            self.player.beast.remove(self.player)

        # =====================
        # fase 2
        # =====================
        if next_phase == 2:
            self.player.speed += 1
            self.player.beast = HellCat()
            self.player.beast.apply(self.player)

        # =====================
        # fase 3
        # =====================
        elif next_phase == 3:
            self.player.speed = self.player.base_speed
            # WereWolf entra después por evento revive


    def update(self, events):
        if self.game_state == "ending":
            return
        # =========================
        # DIALOGUE MODE
        # =========================
        if self.game_state == "combat":
            if self.enemy.hp <= 0 and self.enemy.phase < 3:
                self.start_phase_transition()
                return

        if self.game_state == "dialogue":
            self.dialogue.update(events)
            if self.dialogue.active:
                return

           # diálogo terminó
        if self.pending_phase_change:
            self.apply_phase_changes()
            self.pending_phase_change = False

        self.game_state = "combat"

        # ===== FINAL DIALOGUE DONE =====
        if self.pending_final_dialogue:
            self.pending_final_dialogue = False
            self.game_state = "ending"
            return

            # ⚠️ NO return aquí

        # =========================
        # PLAYER
        # =========================
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.world)

        # =========================
        # ATTACK HITBOX TIMER
        # =========================
        if self.attack_timer > 0:
            self.attack_timer -= 1
        else:
            self.attack_hitbox = None

        # =========================
        # ENEMY
        # =========================
        self.enemy.update(self.player, self.world)

        # =========================
        # ATTACK COLLISION
        # =========================
        if (
            self.attack_hitbox and
            self.enemy.alive and
            not self.attack_applied and
            self.attack_hitbox.colliderect(self.enemy.rect)
        ):
            damage = self.attack_damage

            if self.enemy.phase == 3 and not isinstance(self.player.beast, WereWolf):
                damage = 1   # daño simbólico → imposible matarlo

            self.enemy.take_damage(damage, self.player.rect)
            self.attack_applied = True
            self.hit_stop = 3
            self.shake_timer = 6
        # ===== FINAL BOSS =====
        if not self.enemy.alive and self.enemy.phase == 3 and not self.ending_shown:
            self.ending_shown = True
            self.game_state = "dialogue"
            self.pending_final_dialogue = True

            if self.revived_once:
                    self.final_text = """FINAL: Pacto de Sangre
                    Porque vos salvas mi mundo, 
                    todos los dias sos mi heroína 
                    y nunca fue mi elección 
                    Te amo, Feliz Cumpleaños.
                    """                
                    self.dialogue.start([
                    ("Juli","Terminó... pero el precio fue alto, usé mucho de tu poder.","juli"),
                    ("Astor","El poder siempre exige algo a cambio.","astor"),
                    ("Juli","Gracias por volver.","juli"),
                    ("Astor","Nunca me fui, aunque quizá me lleve tiempo recuperarme...","astor"),
                    ("Astor","...pero siempre que necesites mi poder, estaré para tí.","astor"),
                    ("Juli","Lo sé, y lo agradezco. Espero ser lo suficientemente fuerte...","juli"),
                    ("Juli","Para proteger a los que quiero por mi cuenta","juli"),
                    ("Astor","Hasta la Próxima Juli, Feliz Cumpleaños","astor"),
                    ("Nilo","Feliz Cumpleaños sanaoria!","nilo"),
                    ("Frida","gwaaaw... digo Feliz Cumpleaños esclava","frida"),
                    ("Juli",":)","juli"),
                    ("Narrador","La heroína se aleja con sus compañeros, dejando atrás un reino en ruinas.", None),
                    ("Narrador","Y la prueba feaciente de que ha salvado el mundo una vez más...", None),
                    ("Narrador","...", None),
                    ("Narrador","..", None),
                    ("Narrador",".", None),
                    ("Narrador","¿Tendrá que hacerlo el siguiente año?", None),
                ])
            else:
                self.final_text = "FINAL: Voluntad Inquebrantable"
                self.dialogue.start([
                    ("Juli","Lo logré... sola.","juli"),
                    ("Juli","Nadie más tuvo que caer.","juli"),
                    ("Narrador","La voluntad también es poder.", None),
                    ("Narrador","La heroína no vuelve a dejarnos maravillados.", None),
                ])

            return

        # =========================
        # PLAYER DAMAGE
        # =========================
        if self.enemy.alive and self.enemy.rect.colliderect(self.player.rect):
            self.player.take_damage(1, self.enemy.rect)

        if self.player.hp <= 0:

    # ===== REVIVE WEREWOLF =====
            if self.enemy.phase == 3 and not self.revived_once:
                self.revived_once = True
                self.game_state = "dialogue"

                self.dialogue.start([
                    ("Narrador","La heroína cae...", None),
                    ("Juli","Aghh...por qué...","juli"),
                    ("Juli","...si tan solo...","juli"),
                    ("Juli","...no, ya es muy tarde...","juli"),
                    ("Narrador","Una presencia antigua responde al llamado.", None),
                    ("Astor","No volverás a luchar sola.","astor"),
                    ("Juli","¿Astor? Pensé que te habías ido","juli"),
                    ("Astor","Tu nunca me dejaste, yo tampoco te dejaría sola.","astor"),
                    ("Astor","Voy a dejarte usar mi poder","astor"),
                    ("Juli","Gracias, Astor.","juli"),
                    ("Astor","No hay nada que agradecer, levántate y "
                    "terminemos con esto","astor"),
                    ("Juli","Vamos!","juli"),
                    ("Astor","Que caiga!","astor"),
                ])

                # buff revive
                self.player.max_hp += 30
                self.player.hp = self.player.max_hp

                if self.player.beast:
                    self.player.beast.remove(self.player)

                self.player.beast = WereWolf()
                self.player.beast.apply(self.player)

                return

            # ===== MUERTE NORMAL =====
            else:
                self.running = False

    def draw_multiline_centered(self, text, font, color, center_x, start_y, line_spacing=10):
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip() == "":
                continue  # permite líneas vacías

            surface = font.render(line.strip(), True, color)
            rect = surface.get_rect(center=(center_x, start_y + i * (font.get_height() + line_spacing)))
            self.screen.blit(surface, rect)



    def draw(self):
        self.screen.fill((0, 0, 0))
        offset_x = 0
        offset_y = 0

        # =========================
        # SCREEN SHAKE
        # =========================
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        # =========================
        # WORLD & ENTITIES
        # =========================
        self.world.draw(self.screen, offset_x, offset_y)
        self.player.draw(self.screen, offset_x, offset_y)
        self.enemy.draw(self.screen, offset_x, offset_y)

        # =========================
        # ATTACK HITBOX (UNA SOLA VEZ)
        # =========================
        if self.attack_hitbox:
            color = (200, 50, 50)  # color base

            if self.player.beast:
                color = self.player.beast.attack_color

            hitbox = self.attack_hitbox.move(offset_x, offset_y)

            ##pygame.draw.rect(
            ##    self.screen,
            ##    color,
            ##    hitbox,
            ##    2
            ##)

        # =========================
        # PLAYER HP BAR
        # =========================
        bar_width = 200
        bar_height = 20
        hp_ratio = self.player.hp / self.player.max_hp

        pygame.draw.rect(
            self.screen,
            (60, 60, 60),
            (20, 20, bar_width, bar_height)
        )

        pygame.draw.rect(
            self.screen,
            (200, 50, 50),
            (20, 20, bar_width * hp_ratio, bar_height)
        )

        # =========================
        # DIALOGUE
        # =========================
        if self.game_state == "dialogue":
            self.dialogue.draw(self.screen)
        # =========================
        # ENDING SCREEN
        # =========================
        if self.game_state == "ending":
            self.screen.fill((0,0,0))

            font_big = pygame.font.Font(None, 64)
            font_small = pygame.font.Font(None, 28)

            # Dibujar texto multilínea centrado
            self.draw_multiline_centered(
                self.final_text,
                font_big,
                (220,220,220),
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 80
            )

            hint = font_small.render("Presiona ENTER para volver a jugar", True, (160,160,160))

            self.screen.blit(
                hint,
                (SCREEN_WIDTH//2 - hint.get_width()//2,
                SCREEN_HEIGHT//2 + 100)
            )


        pygame.display.flip()

