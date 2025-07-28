# game4/enums.py
from enum import Enum

class GameState(Enum):
    EXPLORING = 1
    BATTLE = 2
    MENU = 3
    GAME_OVER = 4

class EquipmentType(Enum):
    HEAD = 1
    CHEST = 2
    LEFT_HAND = 3
    RIGHT_HAND = 4
    FEET = 5

class ItemType(Enum):
    APPLE = "苹果"
    BREAD = "面包"
    WINE = "葡萄酒"

class MonsterType(Enum):
    NORMAL = "普通怪物"
    ELITE = "精英怪物"
    BOSS = "Boss怪物"

class MenuType(Enum):
    MAIN = 1
    ABILITY = 2
    EQUIPMENT = 3
    ITEM = 4
    SYNTHESIS = 5

class BattleMenuType(Enum):
    MAIN = 1
    SKILL = 2
    ITEM = 3

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4