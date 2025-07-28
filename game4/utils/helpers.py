# game4/utils/helpers.py
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..entities.monster import Monster
from ..entities.equipment import Equipment
from ..enums import MonsterType, EquipmentType


def generate_monsters(floor: int):
    """生成指定楼层的怪物"""
    monsters = []

    # 生成普通怪物
    normal_count = random.randint(7, 10)
    for _ in range(normal_count):
        monsters.append(Monster(MonsterType.NORMAL, floor))

    # 生成精英怪物
    elite_count = random.randint(2, 3)
    for _ in range(elite_count):
        monsters.append(Monster(MonsterType.ELITE, floor))

    # 生成Boss怪物
    monsters.append(Monster(MonsterType.BOSS, floor))

    return monsters


def generate_random_equipment(floor: int) -> Equipment:
    """生成随机装备"""
    part = random.choice(list(EquipmentType))
    return Equipment(floor, part)


def calculate_damage(attacker_attack, defender_defense):
    """计算伤害"""
    return max(1, attacker_attack - defender_defense)


def wrap_text(text, font, max_width):
    """文本换行处理"""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines