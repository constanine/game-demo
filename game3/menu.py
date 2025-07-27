# menu.py
import pygame
import random
from equipment import Equipment
from item import Item


class Menu:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        # 加载中文字体
        try:
            self.font = pygame.font.SysFont('simhei,arial,helvetica', 36)
        except:
            self.font = pygame.font.Font(None, 36)

        self.small_font = pygame.font.SysFont('simhei,arial,helvetica', 24)
        self.show_message = None
        self.message_timer = 0

    def show_temp_message(self, message, duration=2000):
        """显示临时消息"""
        self.show_message = message
        self.message_timer = pygame.time.get_ticks() + duration

    def draw_temp_message(self):
        """绘制临时消息框"""
        if self.show_message and pygame.time.get_ticks() < self.message_timer:
            # 绘制半透明背景
            s = pygame.Surface((400, 100), pygame.SRCALPHA)
            s.fill((0, 0, 0, 200))
            self.screen.blit(s, (200, 270))

            # 绘制消息文本
            text = self.font.render(self.show_message, True, (255, 255, 255))
            text_rect = text.get_rect(center=(400, 320))
            self.screen.blit(text, text_rect)
            return True
        else:
            self.show_message = None
            return False

    def run(self):
        options = ["能力编辑", "装备编辑", "装备合成", "道具使用", "返回地图"]
        selected = 0

        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("游戏菜单", True, (255, 255, 255))
            self.screen.blit(title, (350, 50))

            # 显示玩家当前属性（右边）
            self.draw_player_stats(500, 100)

            # 显示菜单选项（左边）
            for i, option in enumerate(options):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                self.screen.blit(text, (100, 150 + i * 50))

            # 绘制临时消息
            if self.draw_temp_message():
                pygame.display.flip()
                pygame.time.Clock().tick(60)
                continue

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == len(options) - 1:
                            return "back"  # 返回地图
                        else:
                            # 处理各个菜单选项
                            result = self.handle_menu_option(selected)
                            if result == "back_to_main":
                                return "handled"

    def draw_player_stats(self, x, y):
        """在指定位置绘制玩家属性"""
        title = self.small_font.render("当前属性:", True, (255, 255, 255))
        self.screen.blit(title, (x, y))

        # 计算总属性
        total_attack, total_defense, total_hp = self.player.get_total_stats()

        stats = [
            f"攻击力: {total_attack}",
            f"体力: {self.player.hp}/{self.player.max_hp}",
            f"防御力: {total_defense}"
        ]

        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, (255, 255, 255))
            self.screen.blit(text, (x, y + 40 + i * 30))

    def handle_menu_option(self, option_index):
        """处理菜单选项"""
        if option_index == 0:
            return self.ability_edit()
        elif option_index == 1:
            return self.equipment_edit()
        elif option_index == 2:
            return self.equipment_synthesis()
        elif option_index == 3:
            return self.item_use()
        return "handled"

    def ability_edit(self):
        """能力编辑"""
        options = ["消耗1点天赋增加5点攻击",
                   "消耗1点天赋增加15点体力",
                   "消耗1点天赋增加2点防御",
                   "返回"]
        selected = 0

        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("能力编辑", True, (255, 255, 255))
            self.screen.blit(title, (300, 50))

            # 显示当前属性
            stats = [
                f"攻击: {self.player.attack}",
                f"体力: {self.player.hp}/{self.player.max_hp}",
                f"防御: {self.player.defense}",
                f"天赋点: {self.player.talent_points}"
            ]

            for i, stat in enumerate(stats):
                text = self.small_font.render(stat, True, (255, 255, 255))
                self.screen.blit(text, (100, 100 + i * 30))

            # 显示选项
            for i, option in enumerate(options):
                # "返回"选项显示为红色
                if i == len(options) - 1:
                    color = (255, 0, 0) if i == selected else (255, 255, 255)
                else:
                    color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.small_font.render(option, True, color)
                self.screen.blit(text, (100, 250 + i * 40))

            # 绘制临时消息
            if self.draw_temp_message():
                pygame.display.flip()
                pygame.time.Clock().tick(60)
                continue

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "back_to_main"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected == 0 and self.player.talent_points > 0:  # 增加攻击
                            self.player.attack += 5
                            self.player.talent_points -= 1
                            self.show_temp_message("攻击+5")
                        elif selected == 1 and self.player.talent_points > 0:  # 增加体力
                            self.player.max_hp += 15
                            self.player.hp = min(self.player.hp + 15, self.player.max_hp)
                            self.player.talent_points -= 1
                            self.show_temp_message("体力+15")
                        elif selected == 2 and self.player.talent_points > 0:  # 增加防御
                            self.player.defense += 2
                            self.player.talent_points -= 1
                            self.show_temp_message("防御+2")
                        elif selected == 3:  # 返回
                            return "handled"
            pygame.time.Clock().tick(60)

    def equipment_edit(self):
        """装备编辑 - 左边是部位和已穿戴装备，右边是装备列表"""
        parts = ["head", "chest", "left_hand", "right_hand", "feet"]
        part_names = ["头部", "胸部", "左手", "右手", "足部"]
        selected_part = 0
        selected_equipment = 0
        choosing_equipment = False

        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("装备编辑", True, (255, 255, 255))
            self.screen.blit(title, (300, 50))

            # 左边显示部位和已穿戴装备
            left_title = self.small_font.render("装备部位:", True, (255, 255, 255))
            self.screen.blit(left_title, (50, 100))

            for i, part_name in enumerate(part_names):
                # 部位名称
                color = (255, 255, 0) if i == selected_part and not choosing_equipment else (255, 255, 255)
                text = self.small_font.render(part_name, True, color)
                self.screen.blit(text, (50, 140 + i * 60))

                # 对应的已穿戴装备
                current_equipment = self.player.equipment[parts[i]]
                if current_equipment:
                    equip_text = self.small_font.render(f"  → {current_equipment.name()}", True, (200, 200, 200))
                    self.screen.blit(equip_text, (50, 170 + i * 60))
                else:
                    none_text = self.small_font.render("  → 无装备", True, (150, 150, 150))
                    self.screen.blit(none_text, (50, 170 + i * 60))

            # 右边显示该部位的所有可装备物品
            right_title = self.small_font.render("可装备物品:", True, (255, 255, 255))
            self.screen.blit(right_title, (350, 100))

            # 查找该部位的装备（这里简化为显示当前装备）
            current_equipment = self.player.equipment[parts[selected_part]]
            if current_equipment:
                equip_text = self.small_font.render(current_equipment.name(), True, (255, 255, 0))  # 选中为黄色
                bonus_text = self.small_font.render(
                    f"攻击+{current_equipment.attack_bonus} 防御+{current_equipment.defense_bonus} 体力+{current_equipment.hp_bonus}",
                    True, (200, 200, 200))
                self.screen.blit(equip_text, (350, 140))
                self.screen.blit(bonus_text, (350, 170))
            else:
                none_text = self.small_font.render("无装备", True, (255, 255, 0))  # 选中为黄色
                self.screen.blit(none_text, (350, 140))

            # 显示操作提示
            if not choosing_equipment:
                hint = self.small_font.render("↑↓选择部位 Enter装备 ESC返回", True, (255, 255, 255))
                self.screen.blit(hint, (50, 500))
            else:
                hint = self.small_font.render("Enter确认装备 ESC取消", True, (255, 255, 255))
                self.screen.blit(hint, (50, 500))

            # "返回菜单"显示为红色
            return_text = self.small_font.render("返回菜单", True, (255, 0, 0))
            self.screen.blit(return_text, (50, 550))

            # 绘制临时消息
            if self.draw_temp_message():
                pygame.display.flip()
                pygame.time.Clock().tick(60)
                continue

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "back_to_main"
                elif event.type == pygame.KEYDOWN:
                    if not choosing_equipment:
                        if event.key == pygame.K_UP:
                            selected_part = (selected_part - 1) % len(parts)
                        elif event.key == pygame.K_DOWN:
                            selected_part = (selected_part + 1) % len(parts)
                        elif event.key == pygame.K_RETURN:
                            choosing_equipment = True
                            selected_equipment = 0
                        elif event.key == pygame.K_ESCAPE:
                            return "handled"
                    else:
                        # 在选择装备状态下
                        if event.key == pygame.K_ESCAPE:
                            choosing_equipment = False
                        elif event.key == pygame.K_RETURN:
                            # 这里可以添加装备逻辑
                            self.show_temp_message("装备成功!")
                            choosing_equipment = False

            pygame.time.Clock().tick(60)

    def equipment_synthesis(self):
        """装备合成 - 3个相同楼层N阶级的装备合成N+1阶级的装备"""
        self.screen.fill((0, 0, 0))
        title = self.font.render("装备合成", True, (255, 255, 255))
        self.screen.blit(title, (300, 50))

        info_text = self.small_font.render("选择3个相同楼层的装备进行合成", True, (255, 255, 255))
        self.screen.blit(info_text, (100, 100))

        # "返回"显示为红色
        back_text = self.small_font.render("按任意键返回", True, (255, 0, 0))
        self.screen.blit(back_text, (300, 500))

        # 绘制临时消息
        if self.draw_temp_message():
            pygame.display.flip()
            pygame.time.Clock().tick(60)
            return "handled"

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "back_to_main"
                elif event.type == pygame.KEYDOWN:
                    waiting = False
        return "handled"

    # menu.py 中 item_use 方法的修改部分
    def item_use(self):
        """道具使用"""
        # 只显示非装备类型的道具
        non_equipment_items = [item for item in self.player.inventory if item.type != "equipment"]

        if not non_equipment_items:
            self.screen.fill((0, 0, 0))
            title = self.font.render("没有可用道具", True, (255, 255, 255))
            self.screen.blit(title, (300, 200))

            # "返回"显示为红色
            back_text = self.small_font.render("按任意键返回", True, (255, 0, 0))
            self.screen.blit(back_text, (300, 300))

            # 绘制临时消息
            if self.draw_temp_message():
                pygame.display.flip()
                pygame.time.Clock().tick(60)
                return "handled"

            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "back_to_main"
                    elif event.type == pygame.KEYDOWN:
                        waiting = False
            return "handled"

        # 显示道具列表
        selected = 0
        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("道具使用", True, (255, 255, 255))
            self.screen.blit(title, (300, 50))

            # 重新获取非装备道具列表
            non_equipment_items = [item for item in self.player.inventory if item.type != "equipment"]

            if not non_equipment_items:
                # 如果道具用完了，显示提示并返回
                no_item_text = self.small_font.render("没有可用道具", True, (255, 255, 255))
                self.screen.blit(no_item_text, (100, 150))
                # "返回"显示为红色
                return_text = self.small_font.render("返回", True, (255, 0, 0))
                self.screen.blit(return_text, (100, 200))

                # 绘制临时消息
                if self.draw_temp_message():
                    pygame.display.flip()
                    pygame.time.Clock().tick(60)
                    continue

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "back_to_main"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return "handled"
                pygame.time.Clock().tick(60)
                continue

            # 显示道具
            for i, item in enumerate(non_equipment_items):
                color = (255, 255, 0) if i == selected else (255, 255, 255)
                text = self.small_font.render(f"{item.name}", True, color)
                self.screen.blit(text, (100, 150 + i * 40))

            # "返回"选项显示为红色
            return_text = self.small_font.render("返回", True,
                                                 (255, 0, 0) if selected == len(non_equipment_items) else (
                                                 255, 255, 255))
            self.screen.blit(return_text, (100, 150 + len(non_equipment_items) * 40))

            # 绘制临时消息
            if self.draw_temp_message():
                pygame.display.flip()
                pygame.time.Clock().tick(60)
                continue

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "back_to_main"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % (len(non_equipment_items) + 1)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % (len(non_equipment_items) + 1)
                    elif event.key == pygame.K_RETURN:
                        if selected < len(non_equipment_items):  # 使用道具
                            item = non_equipment_items[selected]
                            if item in self.player.inventory:  # 确保道具还在背包中
                                use_result = item.use(self.player)
                                if use_result:
                                    # 安全地从背包中移除道具
                                    if item in self.player.inventory:
                                        self.player.inventory.remove(item)
                                    self.show_temp_message(f"使用了 {item.name}, {use_result}")
                                    pygame.time.wait(2000)
                                else:
                                    self.show_temp_message("无法使用此物品!")
                                    pygame.time.wait(2000)
                            else:
                                self.show_temp_message("道具已使用!")
                                pygame.time.wait(2000)
                        else:  # 返回
                            return "handled"
            pygame.time.Clock().tick(60)