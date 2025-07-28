# game4/entities/equipment.py
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..enums import EquipmentType


class Equipment:
    def __init__(self, floor: int, part: EquipmentType):
        self.floor = floor
        self.part = part
        self.attack = 0
        self.health = 0
        self.defense = 0
        self.energy = 0

        self._generate_stats()

    def _generate_stats(self):
        f = self.floor
        if self.part == EquipmentType.HEAD:
            if random.random() < 0.5:
                self.defense = f * random.randint(1, 3)
            else:
                self.health = f * random.randint(5, 10)
        elif self.part == EquipmentType.CHEST:
            self.health = f * random.randint(10, 20)
        elif self.part == EquipmentType.LEFT_HAND:
            self.attack = f * random.randint(5, 10)
        elif self.part == EquipmentType.RIGHT_HAND:
            self.defense = f * random.randint(2, 5)
        elif self.part == EquipmentType.FEET:
            self.defense = f * random.randint(1, 3)

    @property
    def name(self):
        names = {
            EquipmentType.HEAD: f"{self.floor}号头盔",
            EquipmentType.CHEST: f"{self.floor}号护甲",
            EquipmentType.LEFT_HAND: f"{self.floor}号长剑",
            EquipmentType.RIGHT_HAND: f"{self.floor}号护盾",
            EquipmentType.FEET: f"{self.floor}号靴子"
        }
        return names[self.part]

    def get_stats_string(self):
        stats = []
        if self.attack > 0:
            stats.append(f"攻击+{self.attack}")
        if self.health > 0:
            stats.append(f"体力+{self.health}")
        if self.defense > 0:
            stats.append(f"防御+{self.defense}")
        if self.energy > 0:
            stats.append(f"技力+{self.energy}")
        return ", ".join(stats) if stats else "无属性"