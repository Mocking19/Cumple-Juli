# world/map.py
import pygame
from settings import TILE_SIZE

MAP_DATA = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

PHASE_TILES = {
    1: "assets/tiles/tile_floor.png",
    2: "assets/tiles/tile_floor2.png",
    3: "assets/tiles/tile_floor3.png",
}

class WorldMap:
    def __init__(self):
        self.map = MAP_DATA
        self.phase = 1
        self.set_phase(1)

    def set_phase(self, phase):
        self.phase = phase
        path = PHASE_TILES.get(phase, PHASE_TILES[1])
        self.floor_tile = pygame.image.load(path).convert_alpha()
        
    def is_blocked(self, grid_x, grid_y):
        if grid_y < 0 or grid_y >= len(self.map):
            return True
        if grid_x < 0 or grid_x >= len(self.map[0]):
            return True
        return self.map[grid_y][grid_x] == 1

    def draw(self, surface, offset_x=0, offset_y=0):
        rows = len(self.map)
        cols = len(self.map[0])

        # 🔹 dibujar piso
        for y in range(rows):
            for x in range(cols):
                surface.blit(
                    self.floor_tile,
                    (
                        x * TILE_SIZE + offset_x,
                        y * TILE_SIZE + offset_y
                    )
                )

        # 🔹 dibujar paredes / colisiones
        for y, row in enumerate(self.map):
            for x, tile in enumerate(row):
                if tile == 1:
                    rect = pygame.Rect(
                        x * TILE_SIZE + offset_x,
                        y * TILE_SIZE + offset_y,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                    pygame.draw.rect(surface, (90, 50, 90), rect)

