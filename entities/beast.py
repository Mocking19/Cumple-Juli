class Beast:
    def __init__(self):
        self.name = "Bestia"
        self.attack_bonus = 0
        self.attack_color = (255, 255, 255)
        self.float_offset = (0, -20)

    def apply(self, player):
        player.attack_damage = player.base_damage + self.attack_bonus
        player.beast = self

    def remove(self, player):
        player.attack_damage = player.base_damage
        player.beast = None

    def update(self):
        pass

    def draw(self, surface, player, offset_x=0, offset_y=0):
        pass
