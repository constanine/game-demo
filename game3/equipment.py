# equipment.py
import random


class Equipment:
    def __init__(self, part, floor):
        self.part = part
        self.floor = floor
        self.attack_bonus = 0
        self.defense_bonus = 0
        self.hp_bonus = 0

        if part == "head":
            if random.random() < 0.5:
                self.defense_bonus = floor * random.randint(1, 3)
            else:
                self.hp_bonus = floor * random.randint(5, 10)
        elif part == "chest":
            self.hp_bonus = floor * random.randint(10, 20)
        elif part == "left_hand":
            self.attack_bonus = floor * random.randint(5, 10)
        elif part == "right_hand":
            self.defense_bonus = floor * random.randint(2, 5)
        elif part == "feet":
            self.defense_bonus = floor * random.randint(1, 3)

    def name(self):
        names = {
            "head": "头盔",
            "chest": "护甲",
            "left_hand": "长剑",
            "right_hand": "护盾",
            "feet": "靴子"
        }
        return f"{self.floor}层 {names[self.part]}"

    def get_type_name(self):
        """获取装备类型名称"""
        return self.part