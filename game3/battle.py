import pygame
import random
from item import Item
from equipment import Equipment


class BattleSystem:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player

        # 尝试加载中文字体
        try:
            self.font = pygame.font.SysFont('simhei,arial,helvetica', 36)
        except:
            self.font = pygame.font.Font(None, 36)

        self.small_font = pygame.font.SysFont('simhei,arial,helvetica', 24)
        self.log_messages = []  # 日志消息队列，保留最后3条

    def add_log_message(self, message):
        """添加日志消息，最多保留5条"""
        self.log_messages.append(message)
        if len(self.log_messages) > 5:
            self.log_messages.pop(0)

    def run(self, monster):
        """运行战斗系统"""
        selected_option = 0
        options = ["战斗", "物品", "逃跑"]

        # 添加初始日志
        self.add_log_message("玩家回合开始")

        # 主战斗循环
        while True:
            # 绘制战斗界面
            self.draw_battle_screen(monster, selected_option, options)
            pygame.display.flip()

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "flee"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        selected_option = (selected_option - 1) % len(options)
                    elif event.key == pygame.K_RIGHT:
                        selected_option = (selected_option + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # 战斗
                            result = self.battle(monster)
                            if result != "continue":
                                return result
                        elif selected_option == 1:  # 物品
                            result = self.use_item(monster)
                            if result != "continue":
                                return result
                        elif selected_option == 2:  # 逃跑
                            result = self.flee(monster)
                            if result != "continue":
                                return result

            pygame.time.Clock().tick(60)

    def draw_battle_screen(self, monster, selected_option, options):
        """绘制战斗界面"""
        # 600*400px战斗动画区域 (0到600px宽度, 0到400px高度)
        battle_area = pygame.Rect(0, 0, 600, 400)
        pygame.draw.rect(self.screen, (50, 50, 50), battle_area)

        # 显示怪物信息
        monster_text = self.font.render(f"{monster.type}怪物", True, (255, 255, 255))
        self.screen.blit(monster_text, (50, 50))

        hp_text = self.small_font.render(f"HP: {monster.hp}/{monster.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_text, (50, 100))

        # 显示玩家信息
        player_attack, player_defense, player_hp = self.player.get_total_stats()
        player_text = self.small_font.render(f"玩家 HP: {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255))
        self.screen.blit(player_text, (50, 150))

        attack_text = self.small_font.render(f"攻击: {player_attack} 防御: {player_defense}", True, (255, 255, 255))
        self.screen.blit(attack_text, (50, 180))

        # 600px宽度, 120px高度战斗选项界面 (400到480px高度)
        options_area = pygame.Rect(0, 400, 600, 80)
        pygame.draw.rect(self.screen, (100, 100, 100), options_area)

        # 显示选项 - 居中显示
        option_width = 150
        total_width = len(options) * option_width + (len(options) - 1) * 50
        start_x = (600 - total_width) // 2
        start_y = 430

        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected_option else (255, 255, 255)
            text = self.font.render(option, True, color)
            x_pos = start_x + i * (option_width + 50)
            self.screen.blit(text, (x_pos, start_y))

        # 底部120px日志信息输出界面 (480到640px高度)
        log_area = pygame.Rect(0, 480, 600, 160)
        pygame.draw.rect(self.screen, (0, 0, 0), log_area)
        pygame.draw.rect(self.screen, (255, 255, 255), log_area, 1)

        # 显示最近3条日志消息
        for i, message in enumerate(self.log_messages):
            message_text = self.small_font.render(message, True, (255, 255, 255))
            self.screen.blit(message_text, (10, 490 + i * 30))

    def battle(self, monster):
        """战斗逻辑"""
        # 玩家攻击
        player_attack, player_defense, player_hp = self.player.get_total_stats()
        damage = max(1, player_attack - monster.defense)
        monster.hp -= damage
        self.add_log_message(f"玩家造成 {damage} 点伤害")
        print(f"玩家造成 {damage} 点伤害")

        if monster.hp <= 0:
            monster.hp = 0
            self.add_log_message("战斗胜利!")
            print("战斗胜利!")
            # 给予奖励
            self.give_rewards(monster)
            return "win"
        else:
            # 怪物反击
            self.add_log_message("怪物回合开始")
            monster_damage = max(1, monster.attack - player_defense)
            self.player.hp -= monster_damage
            self.add_log_message(f"怪物造成 {monster_damage} 点伤害")
            print(f"怪物造成 {monster_damage} 点伤害")

            if self.player.hp <= 0:
                self.player.hp = 0
                self.add_log_message("战斗失败!")
                print("战斗失败!")
                return "lose"

            self.add_log_message("玩家回合开始")
            return "continue"

    def use_item(self, monster):
        """使用物品逻辑"""
        if not self.player.inventory:
            self.add_log_message("没有可用物品!")
            print("没有可用物品!")
            pygame.time.wait(1000)
            return "continue"

        # 让玩家选择物品
        result = self.select_and_use_item()
        if result == "used":
            # 物品使用后怪物反击
            self.add_log_message("怪物回合开始")
            player_attack, player_defense, player_hp = self.player.get_total_stats()
            monster_damage = max(1, monster.attack - player_defense)
            self.player.hp -= monster_damage
            self.add_log_message(f"怪物造成 {monster_damage} 点伤害")
            print(f"怪物造成 {monster_damage} 点伤害")

            if self.player.hp <= 0:
                self.player.hp = 0
                self.add_log_message("战斗失败!")
                print("战斗失败!")
                return "lose"

            self.add_log_message("玩家回合开始")
            return "continue"
        elif result == "cancelled":
            return "continue"

        return "continue"

    # battle.py 中 select_and_use_item 方法的修改部分
    def select_and_use_item(self):
        """选择并使用物品"""
        selected = 0
        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("选择物品", True, (255, 255, 255))
            self.screen.blit(title, (300, 50))

            # 显示物品列表（只显示非装备物品）
            non_equipment_items = [item for item in self.player.inventory if item.type != "equipment"]

            if not non_equipment_items:
                no_item_text = self.small_font.render("没有可用物品", True, (255, 255, 255))
                self.screen.blit(no_item_text, (100, 150))

                cancel_text = self.small_font.render("返回", True, (255, 0, 0))
                self.screen.blit(cancel_text, (100, 200))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "cancelled"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return "cancelled"
            else:
                for i, item in enumerate(non_equipment_items):
                    color = (255, 255, 0) if i == selected else (255, 255, 255)
                    text = self.small_font.render(f"{item.name}", True, color)
                    self.screen.blit(text, (100, 150 + i * 40))

                # 取消选项（红色）
                cancel_color = (255, 0, 0) if selected == len(non_equipment_items) else (255, 255, 255)
                cancel_text = self.small_font.render("取消", True, cancel_color)
                self.screen.blit(cancel_text, (100, 150 + len(non_equipment_items) * 40))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "cancelled"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected = (selected - 1) % (len(non_equipment_items) + 1)
                        elif event.key == pygame.K_DOWN:
                            selected = (selected + 1) % (len(non_equipment_items) + 1)
                        elif event.key == pygame.K_RETURN:
                            if selected < len(non_equipment_items):
                                # 使用物品
                                item = non_equipment_items[selected]
                                if item in self.player.inventory:  # 确保道具还在背包中
                                    use_result = item.use(self.player)
                                    if use_result:
                                        # 安全地从背包中移除道具
                                        if item in self.player.inventory:
                                            self.player.inventory.remove(item)
                                        self.add_log_message(f"使用了 {item.name}, {use_result}")
                                        print(f"使用了 {item.name}, {use_result}")
                                        pygame.time.wait(1500)
                                        return "used"
                                    else:
                                        self.add_log_message("无法使用此物品!")
                                        print("无法使用此物品!")
                                        pygame.time.wait(1500)
                                        return "continue"
                                else:
                                    self.add_log_message("道具已使用!")
                                    print("道具已使用!")
                                    pygame.time.wait(1500)
                                    return "continue"
                            else:
                                return "cancelled"

            pygame.time.Clock().tick(60)

    def flee(self, monster):
        """逃跑逻辑"""
        if random.random() < 0.5:
            self.add_log_message("逃跑成功!")
            print("逃跑成功!")
            return "flee"
        else:
            self.add_log_message("逃跑失败!")
            print("逃跑失败!")
            # 怪物反击
            self.add_log_message("怪物回合开始")
            player_attack, player_defense, player_hp = self.player.get_total_stats()
            monster_damage = max(1, monster.attack - player_defense)
            self.player.hp -= monster_damage
            self.add_log_message(f"怪物造成 {monster_damage} 点伤害")
            print(f"怪物造成 {monster_damage} 点伤害")

            if self.player.hp <= 0:
                self.player.hp = 0
                self.add_log_message("战斗失败!")
                print("战斗失败!")
                return "lose"

            self.add_log_message("玩家回合开始")
            return "continue"

    def give_rewards(self, monster):
        """给予战斗奖励"""
        if monster.type == "normal":
            # 80%概率获得苹果
            if random.random() < 0.8:
                apple = Item("苹果", "apple")
                self.player.add_item(apple)
                self.add_log_message("获得了苹果!")
                print("获得了苹果!")

            # 20%概率获得当前楼层装备
            if random.random() < 0.2:
                parts = ["head", "chest", "left_hand", "right_hand", "feet"]
                part = random.choice(parts)
                equipment = Equipment(part, self.player.floor)
                # 装备直接添加到装备栏
                self.player.equipment[part] = equipment
                self.add_log_message(f"获得了{equipment.name()}!")
                print(f"获得了{equipment.name()}!")

        elif monster.type == "elite":
            # 100%获得当前楼层装备
            parts = ["head", "chest", "left_hand", "right_hand", "feet"]
            part = random.choice(parts)
            equipment = Equipment(part, self.player.floor)
            self.player.equipment[part] = equipment
            self.add_log_message(f"获得了{equipment.name()}!")
            print(f"获得了{equipment.name()}!")

            # 100%获得面包
            bread = Item("面包", "bread")
            self.player.add_item(bread)
            self.add_log_message("获得了面包!")
            print("获得了面包!")

        elif monster.type == "boss":
            # 100%获得当前楼层装备(2个)
            for i in range(2):
                parts = ["head", "chest", "left_hand", "right_hand", "feet"]
                part = random.choice(parts)
                equipment = Equipment(part, self.player.floor)
                self.player.equipment[part] = equipment
                self.add_log_message(f"获得了{equipment.name()}!")
                print(f"获得了{equipment.name()}!")

            # 100%获得面包
            bread = Item("面包", "bread")
            self.player.add_item(bread)
            self.add_log_message("获得了面包!")
            print("获得了面包!")

            # 50%概率获得下层装备
            if random.random() < 0.5:
                parts = ["head", "chest", "left_hand", "right_hand", "feet"]
                part = random.choice(parts)
                equipment = Equipment(part, self.player.floor + 1)
                self.player.equipment[part] = equipment
                self.add_log_message(f"获得了{equipment.name()}!")
                print(f"获得了{equipment.name()}!")