# map.py
import random
import pygame
from monster import Monster

GRID_SIZE = 40
MAP_WIDTH = 800 // GRID_SIZE
MAP_HEIGHT = 600 // GRID_SIZE


class GameMap:
    def __init__(self, player):
        self.player = player
        self.monsters = []
        self.generate_monsters()
        self.player.heal_full()  # 进入新层时恢复体力

    def generate_monsters(self):
        self.monsters.clear()

        # 固定生成7个普通怪,2个精英,1个boss
        monster_types = ["normal"] * 7 + ["elite"] * 2 + ["boss"] * 1

        for i, monster_type in enumerate(monster_types):
            monster = Monster(monster_type, self.player.floor)

            # 确保怪物不重叠
            attempts = 0
            while attempts < 50:  # 最多尝试50次
                # 生成随机位置（避开入口和出口区域）
                monster.x = 80 + (640) * random.random()
                monster.y = 80 + (440) * random.random()

                # 检查是否与其他怪物重叠
                overlap = False
                for existing_monster in self.monsters:
                    distance = ((monster.x - existing_monster.x) ** 2 +
                                (monster.y - existing_monster.y) ** 2) ** 0.5
                    min_distance = (monster.size + existing_monster.size) / 2 + 10
                    if distance < min_distance:
                        overlap = True
                        break

                if not overlap:
                    break
                attempts += 1

            self.monsters.append(monster)

    def update(self):
        """检查玩家与怪物的碰撞，以及出口碰撞"""
        # 检查怪物碰撞
        for i, monster in enumerate(self.monsters):
            if self.player.check_collision(monster.x - monster.size // 2,
                                           monster.y - monster.size // 2,
                                           monster.size, monster.size):
                # 触发战斗
                return "battle", monster

        # 检查出口碰撞（怪物清光后才能进入）
        if not self.monsters:
            # 出口位置：右边界中点
            exit_x, exit_y = 760, 280
            if self.player.check_collision(exit_x, exit_y, GRID_SIZE, GRID_SIZE):
                # 进入下一层
                self.player.floor += 1
                self.generate_monsters()
                # 将玩家送回入口
                self.player.x = 0
                self.player.y = 320 - GRID_SIZE // 2
                return "next_floor", None

        return None, None

    def remove_monster(self, monster):
        """移除被击败的怪物"""
        if monster in self.monsters:
            self.monsters.remove(monster)

    def draw(self, screen):
        # 绘制网格
        for x in range(0, 800, GRID_SIZE):
            for y in range(0, 600, GRID_SIZE):
                rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

        # 绘制怪物
        for monster in self.monsters:
            monster.draw(screen)

        # 绘制入口和出口
        entry = pygame.Rect(0, 280, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, (0, 0, 0), entry)  # 黑色入口

        exit_color = (128, 128, 128) if self.monsters else (255, 255, 0)
        exit_rect = pygame.Rect(760, 280, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, exit_color, exit_rect)