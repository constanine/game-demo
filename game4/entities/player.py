# game4/entities/player.py
from typing import Dict, List, Optional
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..enums import EquipmentType, ItemType
from .equipment import Equipment
from .buff import Buff, BuffType


class Player:
    def __init__(self):
        # 装备和道具
        self.equipped: Dict[EquipmentType, Optional[Equipment]] = {
            EquipmentType.HEAD: None,
            EquipmentType.CHEST: None,
            EquipmentType.LEFT_HAND: None,
            EquipmentType.RIGHT_HAND: None,
            EquipmentType.FEET: None
        }

        self.inventory: Dict[str, int] = {
            "苹果": 3,
            "面包": 1,
            "葡萄酒": 2
        }

        # 基础属性
        self.base_attack = 10
        self.base_health = 100
        self.base_defense = 5
        self.base_energy = 50

        # 当前状态
        self.current_health = self.total_health
        self.current_energy = self.total_energy

        # 等级和天赋
        self.level = 1
        self.talent_points = 0

        # BUFF状态
        self.buffs: List[Buff] = []

        # 位置
        self.x = 0
        self.y = 0

    @property
    def total_attack(self):
        attack = self.base_attack
        for equipment in self.equipped.values():
            if equipment:
                attack += equipment.attack

        # 应用 Buff 效果
        for buff in self.buffs:
            if buff.buff_type == BuffType.STRENGTH:
                attack += buff.value

        return attack

    @property
    def total_health(self):
        health = self.base_health
        for equipment in self.equipped.values():
            if equipment:
                health += equipment.health
        return health

    @property
    def total_defense(self):
        defense = self.base_defense
        for equipment in self.equipped.values():
            if equipment:
                defense += equipment.defense
        return defense

    @property
    def total_energy(self):
        energy = self.base_energy
        for equipment in self.equipped.values():
            if equipment:
                energy += equipment.energy
        return energy

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # 边界检查
        if 0 <= new_x < 20 and 0 <= new_y < 18:  # 假设地图是 20x18
            self.x = new_x
            self.y = new_y

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.total_defense)
        self.current_health -= actual_damage
        if self.current_health < 0:
            self.current_health = 0
        return actual_damage

    def heal(self, amount):
        self.current_health = min(self.total_health, self.current_health + amount)

    def restore_energy(self, amount):
        self.current_energy = min(self.total_energy, self.current_energy + amount)

    def use_energy(self, amount):
        if self.current_energy >= amount:
            self.current_energy -= amount
            return True
        return False

    def add_buff(self, buff: Buff):
        # 检查是否已有相同类型的buff
        for existing_buff in self.buffs:
            if existing_buff.buff_type == buff.buff_type:
                # 刷新持续时间
                existing_buff.duration = max(existing_buff.duration, buff.duration)
                return
        self.buffs.append(buff)

    def update_buffs(self):
        # 更新所有buff的持续时间
        for buff in self.buffs[:]:  # 使用切片复制列表以避免在迭代时修改
            buff.duration -= 1
            if buff.duration <= 0:
                self.buffs.remove(buff)

            # 应用每回合效果
            if buff.buff_type == BuffType.REGENERATION:
                self.heal(buff.value)
            elif buff.buff_type == BuffType.BLEED:
                self.take_damage(buff.value)

    def get_active_buffs(self):
        return [buff for buff in self.buffs if buff.duration > 0]

    def equip(self, equipment: Equipment):
        if equipment.part in self.equipped:
            old_equipment = self.equipped[equipment.part]
            self.equipped[equipment.part] = equipment
            return old_equipment
        return None

    def unequip(self, part: EquipmentType):
        if part in self.equipped:
            equipment = self.equipped[part]
            self.equipped[part] = None
            return equipment
        return None

    def add_item(self, item_type: str, quantity: int = 1):
        if item_type in self.inventory:
            self.inventory[item_type] += quantity
        else:
            self.inventory[item_type] = quantity

    def use_item(self, item_type: str):
        if item_type in self.inventory and self.inventory[item_type] > 0:
            self.inventory[item_type] -= 1

            if item_type == "苹果":
                self.heal(20)
                return True, "恢复了20点体力"
            elif item_type == "面包":
                heal_amount = int(self.total_health * 0.2)
                self.heal(heal_amount)
                return True, f"恢复了{heal_amount}点体力"
            elif item_type == "葡萄酒":
                self.restore_energy(20)
                return True, "恢复了20点技力"

        return False, "无法使用该道具"

    def gain_talent_point(self):
        self.talent_points += 1

    def spend_talent_point(self):
        if self.talent_points > 0:
            self.talent_points -= 1
            return True
        return False