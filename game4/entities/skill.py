# game4/entities/skill.py
"""Skill entity."""
from game4.enums import SkillType

class Skill:
    def __init__(self, skill_type):
        self.type = skill_type
        self.name = self.get_name()
        self.description = self.get_description()
        self.cost = 5

    def get_name(self):
        names = {
            SkillType.DOUBLE_ATTACK: "二连击",
            SkillType.BLEED_ATTACK: "割裂",
            SkillType.BATTLE_CRY: "战吼",
            SkillType.BLESS: "祝福",
        }
        return names[self.type]

    def get_description(self):
        descriptions = {
            SkillType.DOUBLE_ATTACK: "连续攻击2次",
            SkillType.BLEED_ATTACK: "攻击并施加割裂效果",
            SkillType.BATTLE_CRY: "获得强壮BUFF",
            SkillType.BLESS: "获得恢复BUFF",
        }
        return descriptions[self.type]