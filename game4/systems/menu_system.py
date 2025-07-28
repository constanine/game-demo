# game4/systems/menu_system.py
from typing import List, Tuple, Dict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..entities.player import Player
from ..entities.equipment import Equipment
from ..enums import MenuType, EquipmentType


class MenuSystem:
    def __init__(self, player: Player, font):
        self.player = player
        self.font = font
        self.current_menu = MenuType.MAIN
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible_items = 10

        # 装备菜单专用变量
        self.equipment_selected_part = None
        self.equipment_list = []

        # 合成菜单专用变量
        self.synthesis_selected_items = []

    def handle_input(self, event):
        if event.type == "KEYDOWN":
            if event.key == "UP":
                self.navigate(-1)
            elif event.key == "DOWN":
                self.navigate(1)
            elif event.key == "RETURN":
                self.select()
            elif event.key == "ESCAPE":
                self.back()
            elif event.key == "LEFT" and self.current_menu == MenuType.EQUIPMENT:
                if self.equipment_selected_part is not None:
                    self.equipment_selected_part = None
                    self.selected_index = 0
                    self.scroll_offset = 0
            elif event.key == "RIGHT" and self.current_menu == MenuType.EQUIPMENT:
                if self.equipment_selected_part is None and self.selected_index < len(list(EquipmentType)):
                    self.equipment_selected_part = list(EquipmentType)[self.selected_index]
                    self.refresh_equipment_list()
                    self.selected_index = 0
                    self.scroll_offset = 0

    def navigate(self, direction):
        menu_items = self.get_menu_items()
        if menu_items:
            self.selected_index = (self.selected_index + direction) % len(menu_items)

            # 处理滚动
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
            elif self.selected_index >= self.scroll_offset + self.max_visible_items:
                self.scroll_offset = self.selected_index - self.max_visible_items + 1

    def select(self):
        menu_items = self.get_menu_items()
        if not menu_items:
            return

        if self.current_menu == MenuType.MAIN:
            if self.selected_index == 0:  # 能力编辑
                self.current_menu = MenuType.ABILITY
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index == 1:  # 装备编辑
                self.current_menu = MenuType.EQUIPMENT
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index == 2:  # 道具使用
                self.current_menu = MenuType.ITEM
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index == 3:  # 装备合成
                self.current_menu = MenuType.SYNTHESIS
                self.selected_index = 0
                self.scroll_offset = 0
            elif self.selected_index == 4:  # 返回
                self.current_menu = None

        elif self.current_menu == MenuType.ABILITY:
            # 检查是否有天赋点
            if self.player.talent_points > 0:
                if 0 <= self.selected_index < 4:  # 属性提升选项
                    self.upgrade_attribute(self.selected_index)
                    # 升级后刷新菜单项以显示新数值
                    # 或者简单地在下一次绘制时会自动更新
                elif self.selected_index == 4:  # "取消" 或 "返回" 选项
                    self.current_menu = MenuType.MAIN
                    self.selected_index = 0  # 回到主菜单第一项
                    self.scroll_offset = 0
            else:
                # 如果没有天赋点，点击任何选项（除了返回）都无效或给出提示
                if self.selected_index == 4 or (self.player.talent_points == 0 and self.selected_index == 4):  # "返回"
                    self.current_menu = MenuType.MAIN
                    self.selected_index = 0
                    self.scroll_offset = 0
                else:
                    # 可以添加一个短暂的提示，比如闪烁 "天赋点不足"
                    pass  # 暂时不做处理

        elif self.current_menu == MenuType.EQUIPMENT:
            if self.equipment_selected_part is None:
                # 选择装备部位
                if self.selected_index < len(list(EquipmentType)):
                    self.equipment_selected_part = list(EquipmentType)[self.selected_index]
                    self.refresh_equipment_list()
                    self.selected_index = 0
                    self.scroll_offset = 0
                else:  # 取消
                    self.current_menu = MenuType.MAIN
                    self.selected_index = 1
                    self.scroll_offset = 0
            else:
                # 选择具体装备
                if self.selected_index < len(self.equipment_list):
                    equipment = self.equipment_list[self.selected_index]
                    old_equipment = self.player.equip(equipment)
                    # 这里应该有一个装备库存系统，暂时简化处理
                    self.equipment_selected_part = None
                    self.selected_index = 0
                    self.scroll_offset = 0
                else:  # 取消
                    self.equipment_selected_part = None
                    self.selected_index = 0
                    self.scroll_offset = 0

        elif self.current_menu == MenuType.ITEM:
            available_items = [(name, count) for name, count in self.player.inventory.items() if count > 0]
            if self.selected_index < len(available_items):
                item_name, _ = available_items[self.selected_index]
                success, message = self.player.use_item(item_name)
                # 这里应该显示使用结果
                if success:
                    pass  # 使用成功
            else:  # 取消
                self.current_menu = MenuType.MAIN
                self.selected_index = 2
                self.scroll_offset = 0

        elif self.current_menu == MenuType.SYNTHESIS:
            # 简化处理
            if self.selected_index == 0:  # 取消
                self.current_menu = MenuType.MAIN
                self.selected_index = 3
                self.scroll_offset = 0

    def back(self):
        if self.current_menu == MenuType.MAIN:
            self.current_menu = None
        elif self.current_menu == MenuType.ABILITY:
            self.current_menu = MenuType.MAIN
            self.selected_index = 0
        elif self.current_menu == MenuType.EQUIPMENT:
            if self.equipment_selected_part is not None:
                self.equipment_selected_part = None
                self.selected_index = 0
            else:
                self.current_menu = MenuType.MAIN
                self.selected_index = 1
        elif self.current_menu == MenuType.ITEM:
            self.current_menu = MenuType.MAIN
            self.selected_index = 2
        elif self.current_menu == MenuType.SYNTHESIS:
            self.current_menu = MenuType.MAIN
            self.selected_index = 3

    def upgrade_attribute(self, index):
        if self.player.spend_talent_point():
            if index == 0:  # 攻击力
                self.player.base_attack += 3
            elif index == 1:  # 体力
                self.player.base_health += 10
                # 同步当前血量
                self.player.current_health = self.player.total_health
            elif index == 2:  # 防御力
                self.player.base_defense += 1
            elif index == 3:  # 技力
                self.player.base_energy += 3
                # 同步当前技力
                self.player.current_energy = self.player.total_energy

    def refresh_equipment_list(self):
        # 简化处理，实际应该从装备库存中获取
        self.equipment_list = []
        # 生成一些测试装备
        for i in range(5):
            part = self.equipment_selected_part
            if part:
                equipment = Equipment(1, part)
                self.equipment_list.append(equipment)

    def get_menu_items(self) -> List[str]:
        if self.current_menu == MenuType.MAIN:
            return ["能力编辑", "装备编辑", "道具使用", "装备合成", "返回"]
        elif self.current_menu == MenuType.ABILITY:
            items = [
                f"提升攻击力 (+3) - 消耗1点天赋 (当前: {self.player.base_attack})",
                f"提升体力 (+10) - 消耗1点天赋 (当前: {self.player.base_health})",
                f"提升防御力 (+1) - 消耗1点天赋 (当前: {self.player.base_defense})",
                f"提升技力 (+3) - 消耗1点天赋 (当前: {self.player.base_energy})",
            ]
            # 只有当天赋点大于0时才显示升级选项
            if self.player.talent_points > 0:
                return items + ["取消"]  # 或者 "返回"
            else:
                return items + ["天赋点不足", "返回"]  # 禁用选项或提供提示
        elif self.current_menu == MenuType.EQUIPMENT:
            if self.equipment_selected_part is None:
                parts = ["头部", "胸部", "左手", "右手", "足部"]
                equipped_names = []
                for i, part_type in enumerate(EquipmentType):
                    equipment = self.player.equipped.get(part_type)
                    if equipment:
                        equipped_names.append(f"{parts[i]}: {equipment.name}")
                    else:
                        equipped_names.append(f"{parts[i]}: 无")
                return equipped_names + ["取消"]
            else:
                equipment_names = [e.name for e in self.equipment_list]
                return equipment_names + ["取消"]
        elif self.current_menu == MenuType.ITEM:
            items = []
            for name, count in self.player.inventory.items():
                if count > 0:
                    items.append(f"{name} x{count}")
            return items + ["取消"]
        elif self.current_menu == MenuType.SYNTHESIS:
            return ["功能暂未实现", "取消"]
        return []