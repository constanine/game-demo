import pygame
import random
from equipment import Equipment
from item import Item

GRID_SIZE = 40


class Player:
    def __init__(self):
        self.x = 0
        self.y = 320 - GRID_SIZE // 2  # 修改为640屏幕的中点
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.speed = GRID_SIZE * 0.5  # 半格每帧
        self.attack = 10
        self.defense = 5
        self.hp = 100
        self.max_hp = 100
        self.talent_points = 0
        self.floor = 1
        self.equipment = {
            "head": None,
            "chest": None,
            "left_hand": None,
            "right_hand": None,
            "feet": None
        }
        self.inventory = []

        # 添加一些初始道具用于测试
        self.inventory.append(Item("苹果", "apple"))
        self.inventory.append(Item("面包", "bread"))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        self.x += dx
        self.y += dy

        # 边界限制 (600高度)
        self.x = max(0, min(self.x, 800 - self.width))
        self.y = max(0, min(self.y, 600 - self.height))  # 修改为600

    def update(self, dt):
        """更新玩家状态"""
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, self.width, self.height))

    def get_total_stats(self):
        total_attack = self.attack
        total_defense = self.defense
        total_hp = self.hp
        for item in self.equipment.values():
            if item:
                total_attack += item.attack_bonus
                total_defense += item.defense_bonus
                total_hp += item.hp_bonus
        return total_attack, total_defense, total_hp

    def gain_exp(self, points):
        self.talent_points += points

    def heal_full(self):
        self.hp = self.max_hp

    def check_collision(self, other_x, other_y, other_width, other_height):
        """检查与另一个矩形的碰撞（20%重合就算触碰）"""
        # 矩形碰撞检测
        if (self.x < other_x + other_width and
                self.x + self.width > other_x and
                self.y < other_y + other_height and
                self.y + self.height > other_y):
            # 计算重叠面积
            overlap_x = max(0, min(self.x + self.width, other_x + other_width) - max(self.x, other_x))
            overlap_y = max(0, min(self.y + self.height, other_y + other_height) - max(self.y, other_y))
            overlap_area = overlap_x * overlap_y

            # 计算最小矩形面积的20%
            min_area = min(self.width * self.height, other_width * other_height)
            threshold = min_area * 0.2

            return overlap_area >= threshold
        return False

    def add_item(self, item):
        """添加道具到背包"""
        self.inventory.append(item)
        print(f"获得了 {item.name}")

    # player.py 中添加装备管理方法
    def get_equipment_by_part(self, part):
        """根据部位获取装备"""
        return self.equipment.get(part)

    def set_equipment(self, part, equipment):
        """设置某个部位的装备"""
        self.equipment[part] = equipment

    def get_all_equipment(self):
        """获取所有装备"""
        return [equip for equip in self.equipment.values() if equip is not None]

    # player.py 中添加装备合成相关方法
    def get_equipment_groups_for_synthesis(self):
        """获取可用于合成的装备组"""
        # 按楼层和部位分组
        equipment_groups = {}

        # 检查装备栏中的装备
        for part, equipment in self.equipment.items():
            if equipment:
                key = (equipment.floor, equipment.part)
                if key not in equipment_groups:
                    equipment_groups[key] = []
                equipment_groups[key].append(equipment)

        # 检查背包中的装备道具
        for item in self.inventory:
            if item.type == "equipment" and item.equipment:
                key = (item.equipment.floor, item.equipment.part)
                if key not in equipment_groups:
                    equipment_groups[key] = []
                equipment_groups[key].append(item.equipment)

        # 筛选出有3个或以上相同装备的组
        synthesis_groups = []
        for key, equipments in equipment_groups.items():
            if len(equipments) >= 3:
                synthesis_groups.append((key[0], key[1], len(equipments)))

        return synthesis_groups

    def synthesize_equipment(self, floor, part):
        """合成装备"""
        from equipment import Equipment

        # 消耗3个相同装备
        consumed_count = 0

        # 从装备栏中移除
        if self.equipment[part] and self.equipment[part].floor == floor:
            self.equipment[part] = None
            consumed_count += 1

        # 从背包中移除
        items_to_remove = []
        for item in self.inventory:
            if (item.type == "equipment" and item.equipment and
                    item.equipment.floor == floor and item.equipment.part == part):
                items_to_remove.append(item)
                consumed_count += 1
                if consumed_count >= 3:
                    break

        for item in items_to_remove:
            if item in self.inventory:
                self.inventory.remove(item)

        if consumed_count >= 3:
            # 创建新装备（等级+1）
            new_equipment = Equipment(part, floor + 1)
            # 将新装备添加到背包
            from item import Item
            new_item = Item(new_equipment.name(), "equipment")
            new_item.equipment = new_equipment
            self.inventory.append(new_item)
            return True
        return False