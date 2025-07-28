# game4/entities/monster.py
import random
import sys
import os

from .buff import Buff

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..enums import MonsterType


class Monster:
    def __init__(self, monster_type: MonsterType, floor: int):
        self.type = monster_type
        self.floor = floor
        self.image = self._get_image_path()
        self.size = self._get_size()

        self.attack = self._calc_attack()
        self.max_health = self._calc_health()
        self.current_health = self.max_health
        self.defense = self._calc_defense()

        # 位置
        self.x = 0
        self.y = 0

        # BUFF状态
        self.buffs = []

    def _get_image_path(self):
        paths = {
            MonsterType.NORMAL: "monster.png",
            MonsterType.ELITE: "oldmonster.png",
            MonsterType.BOSS: "boss.png"
        }
        return paths[self.type]

    def _get_size(self):
        sizes = {
            MonsterType.NORMAL: (40, 40),
            MonsterType.ELITE: (60, 60),
            MonsterType.BOSS: (80, 80)
        }
        return sizes[self.type]

    def _calc_attack(self):
        multipliers = {
            MonsterType.NORMAL: 2,
            MonsterType.ELITE: 5,
            MonsterType.BOSS: 15
        }
        return multipliers[self.type] * self.floor

    def _calc_health(self):
        multipliers = {
            MonsterType.NORMAL: 20,
            MonsterType.ELITE: 50,
            MonsterType.BOSS: 150
        }
        return multipliers[self.type] * self.floor

    def _calc_defense(self):
        multipliers = {
            MonsterType.NORMAL: 1,
            MonsterType.ELITE: 2,
            MonsterType.BOSS: 5
        }
        return multipliers[self.type] * self.floor

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.current_health -= actual_damage
        if self.current_health < 0:
            self.current_health = 0
        return actual_damage

    def is_alive(self):
        return self.current_health > 0

    def attack_player(self, player):
        damage = max(1, self.attack - player.total_defense)
        return damage

    def add_buff(self, buff):
        # 简化版buff系统
        self.buffs.append(buff)

    def update_buffs(self):
        # 更新buff持续时间
        for buff in self.buffs[:]:
            buff.duration -= 1
            if buff.duration <= 0:
                self.buffs.remove(buff)

    def add_buff(self, buff: Buff):
        """添加或刷新 Buff/Debuff"""
        # 检查是否已有相同类型的buff
        for existing_buff in self.buffs:
            if existing_buff.buff_type == buff.buff_type:
                # 刷新持续时间和/或数值 (取最大值)
                existing_buff.duration = max(existing_buff.duration, buff.duration)
                # 如果新 buff 的数值更大，也可以更新数值
                # existing_buff.value = max(existing_buff.value, buff.value)
                return
        self.buffs.append(buff)

    def update_buffs(self):
        """更新 Buff/Debuff 持续时间并应用效果"""
        for buff in self.buffs[:]:  # 使用副本避免迭代时修改
            buff.duration -= 1

            # 应用每回合效果
            if buff.buff_type == BuffType.BLEED:  # 割裂 DEBUFF
                self.take_damage(buff.value)  # 直接掉血，不计入日志（可在日志中添加）
                self.add_buff_log(f"{self.type.value} 受到 {buff.value} 点割裂伤害")  # 假设有一个 add_buff_log 方法

            # 可以在这里添加其他 Buff/Debuff 效果

            if buff.duration <= 0:
                self.buffs.remove(buff)
                # 可以添加 Buff 消失的日志

    def add_buff_log(self, message):
        """为了简化，Monster 类本身不直接管理日志，
           但可以在 BattleSystem 中调用此方法或直接处理。
           这里提供一个接口，实际由 BattleSystem 调用。
        """
        # 实际实现将在 BattleSystem 中处理
        pass  # 占位符