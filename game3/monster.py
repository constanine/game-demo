import pygame
import random

MONSTER_TYPES = {
    "normal": {"attack": 2, "hp": 20, "defense": 1, "size": 40},
    "elite": {"attack": 5, "hp": 50, "defense": 2, "size": 60},
    "boss": {"attack": 15, "hp": 150, "defense": 5, "size": 80},
}

class Monster:
    def __init__(self, monster_type, floor):
        self.type = monster_type
        base = MONSTER_TYPES[monster_type]
        self.attack = base["attack"] * floor
        self.hp = base["hp"] * floor
        self.max_hp = self.hp
        self.defense = base["defense"] * floor
        self.size = base["size"]
        self.x = 100 + (800 - 200) * random.random()
        self.y = 100 + (800 - 200) * random.random()

    def draw(self, screen):
        color = (255, 0, 0) if self.type == "normal" else \
                (255, 165, 0) if self.type == "elite" else (255, 0, 255)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size // 2)