# game4/systems/battle_system.py
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Tuple
from ..entities.player import Player
from ..entities.monster import Monster
from ..entities.buff import Buff, BuffType
from ..utils.helpers import calculate_damage, wrap_text
from ..constants import BATTLE_LEFT_WIDTH, BATTLE_RIGHT_WIDTH, BATTLE_ANIMATION_HEIGHT, BATTLE_PLAYER_INFO_HEIGHT, \
    BATTLE_MENU_HEIGHT


class BattleSystem:
    def __init__(self, player: Player, monsters: List[Monster], font):
        self.player = player
        self.monsters = monsters
        self.font = font
        self.current_monster_index = 0
        self.battle_log = []
        self.is_player_turn = True
        self.battle_result = None  # None, "victory", "defeat"

        # 战斗菜单状态
        self.menu_state = "main"  # "main", "skill", "item"
        self.selected_menu_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 5

        # 初始化战斗日志
        monster_names = [m.type.value for m in monsters]
        self.add_log(f"遭遇了 {', '.join(monster_names)}!")

    @property
    def current_monster(self):
        if 0 <= self.current_monster_index < len(self.monsters):
            return self.monsters[self.current_monster_index]
        return None

    def add_log(self, message):
        self.battle_log.insert(0, message)
        # 限制日志数量
        if len(self.battle_log) > 50:
            self.battle_log = self.battle_log[:50]

    def player_attack(self):
        if not self.current_monster or not self.current_monster.is_alive():
            return

        damage = calculate_damage(self.player.total_attack, self.current_monster.defense)
        self.current_monster.take_damage(damage)
        self.add_log(f"你对 {self.current_monster.type.value} 造成了 {damage} 点伤害")

        if not self.current_monster.is_alive():
            self.add_log(f"{self.current_monster.type.value} 被击败了!")
            self.check_victory()

    def player_use_skill(self, skill_name):
        # 简化技能系统
        if skill_name == "二连击":
            if self.player.use_energy(10):
                self.add_log("使用了二连击!")
                self.player_attack()
                if self.current_monster and self.current_monster.is_alive():
                    self.player_attack()
            else:
                self.add_log("技力不足!")
        elif skill_name == "割裂":
            if self.player.use_energy(15):
                self.add_log("使用了割裂!")
                if self.current_monster:
                    # 1. 先进行一次普通攻击
                    damage = calculate_damage(self.player.total_attack, self.current_monster.defense)
                    actual_damage = self.current_monster.take_damage(damage)
                    self.add_log(f"你对 {self.current_monster.type.value} 造成了 {actual_damage} 点伤害 (割裂攻击)")

                    # 2. 然后施加割裂 DEBUFF
                    buff = Buff(BuffType.BLEED, 5, 3)  # 3回合，每回合掉5血
                    self.current_monster.add_buff(buff)
                    self.add_log(f"对 {self.current_monster.type.value} 施加了割裂效果 (持续3回合)")
            else:
                self.add_log("技力不足!")
        elif skill_name == "战吼":
            if self.player.use_energy(20):
                self.add_log("使用了战吼!")
                # 假设战吼提供 30% 攻击力加成，持续 2 回合
                # 注意：这里的 value 应该是基础攻击力的百分比或者固定值
                # 为了简化，我们使用固定攻击力加成
                bonus_attack = int(self.player.base_attack * 0.3)  # 基础攻击的30%
                buff = Buff(BuffType.STRENGTH, bonus_attack, 2)  # 2回合
                self.player.add_buff(buff)
                self.add_log(f"攻击力提升了 {bonus_attack} 点! (持续2回合)")
            else:
                self.add_log("技力不足!")
        elif skill_name == "祝福":
            if self.player.use_energy(25):
                self.add_log("使用了祝福!")
                buff = Buff(BuffType.REGENERATION, 10, 3)
                self.player.add_buff(buff)
                self.add_log("获得了恢复效果!")
            else:
                self.add_log("技力不足!")

    def player_use_item(self, item_name):
        success, message = self.player.use_item(item_name)
        self.add_log(message)
        return success

    def try_escape(self):
        if random.random() < 0.5:  # 50% 逃跑成功率
            self.add_log("成功逃跑了!")
            self.battle_result = "escape"
        else:
            self.add_log("逃跑失败!")
            self.end_player_turn()

    def monster_attack(self):
        if not self.current_monster or not self.current_monster.is_alive():
            return

            # 1. 怪物回合开始时，先更新自身 Buff/Debuff
        self.update_monster_buffs()  # 新增方法调用

        # 2. 然后进行攻击
        damage = self.current_monster.attack_player(self.player)
        self.player.take_damage(damage)
        self.add_log(f"{self.current_monster.type.value} 对你造成了 {damage} 点伤害")

        # 3. 更新玩家 Buff/Debuff (原逻辑)
        # self.current_monster.update_buffs() # 这行移到了上面
        if self.player.current_health <= 0:
            self.add_log("你被击败了!")
            self.battle_result = "defeat"

    def update_monster_buffs(self):
        """更新当前怪物的 Buff/Debuff 并记录日志"""
        if not self.current_monster:
            return

        for buff in self.current_monster.buffs[:]:  # 使用副本避免迭代时修改
            buff.duration -= 1

            # 应用每回合效果
            if buff.buff_type == BuffType.BLEED:  # 割裂 DEBUFF
                initial_health = self.current_monster.current_health
                self.current_monster.take_damage(buff.value)  # 直接掉血
                damage_dealt = initial_health - self.current_monster.current_health
                self.add_log(f"{self.current_monster.type.value} 受到 {damage_dealt} 点割裂伤害")

            # 可以在这里添加其他 Buff/Debuff 效果

            if buff.duration <= 0:
                self.current_monster.buffs.remove(buff)
                self.add_log(f"{self.current_monster.type.value} 身上的 {buff.name} 效果消失了")

    def end_player_turn(self):
        self.is_player_turn = False
        # 更新玩家buff
        self.player.update_buffs()

    def start_monster_turn(self):
        self.monster_attack()
        if self.battle_result != "defeat":
            self.is_player_turn = True
            self.add_log("你的回合开始了")

    def check_victory(self):
        alive_monsters = [m for m in self.monsters if m.is_alive()]
        if not alive_monsters:
            self.add_log("所有敌人都被击败了!")
            self.battle_result = "victory"
        else:
            # 切换到下一个活着的怪物
            for i, monster in enumerate(self.monsters):
                if monster.is_alive():
                    self.current_monster_index = i
                    break

    def handle_input(self, event):
        if self.battle_result is not None:
            return

        if self.is_player_turn:
            if event.type == "KEYDOWN":
                if event.key == "UP":
                    self.navigate_menu(-1)
                elif event.key == "DOWN":
                    self.navigate_menu(1)
                elif event.key == "RETURN":
                    self.select_menu_item()
                elif event.key == "ESCAPE":
                    if self.menu_state != "main":
                        self.menu_state = "main"
                        self.selected_menu_index = 0
                        self.scroll_offset = 0

    def navigate_menu(self, direction):
        max_items = self.get_menu_item_count()
        self.selected_menu_index = (self.selected_menu_index + direction) % max_items

        # 处理滚动
        if self.selected_menu_index < self.scroll_offset:
            self.scroll_offset = self.selected_menu_index
        elif self.selected_menu_index >= self.scroll_offset + self.max_visible_items:
            self.scroll_offset = self.selected_menu_index - self.max_visible_items + 1

    def get_menu_item_count(self):
        if self.menu_state == "main":
            return 4  # 战斗、技能、物品、逃跑
        elif self.menu_state == "skill":
            return 5  # 4个技能 + 取消
        elif self.menu_state == "item":
            # 只显示有数量的道具
            item_count = sum(1 for count in self.player.inventory.values() if count > 0)
            return item_count + 1  # +1 for 取消
        return 0

    def select_menu_item(self):
        if self.menu_state == "main":
            if self.selected_menu_index == 0:  # 战斗
                self.player_attack()
                self.end_player_turn()
            elif self.selected_menu_index == 1:  # 技能
                self.menu_state = "skill"
                self.selected_menu_index = 0
                self.scroll_offset = 0
            elif self.selected_menu_index == 2:  # 物品
                self.menu_state = "item"
                self.selected_menu_index = 0
                self.scroll_offset = 0
            elif self.selected_menu_index == 3:  # 逃跑
                self.try_escape()
        elif self.menu_state == "skill":
            skills = ["二连击", "割裂", "战吼", "祝福", "取消"]
            if self.selected_menu_index < len(skills) - 1:
                skill_name = skills[self.selected_menu_index]
                self.player_use_skill(skill_name)
                self.end_player_turn()
                self.menu_state = "main"
                self.selected_menu_index = 0
                self.scroll_offset = 0
            else:  # 取消
                self.menu_state = "main"
                self.selected_menu_index = 1  # 回到技能选项
                self.scroll_offset = 0
        elif self.menu_state == "item":
            # 获取可用道具列表
            available_items = [(name, count) for name, count in self.player.inventory.items() if count > 0]
            if self.selected_menu_index < len(available_items):
                item_name, _ = available_items[self.selected_menu_index]
                if self.player_use_item(item_name):
                    self.end_player_turn()
                self.menu_state = "main"
                self.selected_menu_index = 0
                self.scroll_offset = 0
            else:  # 取消
                self.menu_state = "main"
                self.selected_menu_index = 2  # 回到物品选项
                self.scroll_offset = 0

    def get_current_menu_items(self):
        if self.menu_state == "main":
            return ["战斗", "技能", "物品", "逃跑"]
        elif self.menu_state == "skill":
            return ["二连击", "割裂", "战吼", "祝福", "取消"]
        elif self.menu_state == "item":
            items = [(name, count) for name, count in self.player.inventory.items() if count > 0]
            return [f"{name} x{count}" for name, count in items] + ["取消"]
        return []