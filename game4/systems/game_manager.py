# game4/systems/game_manager.py
import pygame
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Optional
from ..entities.player import Player
from ..entities.monster import Monster
from ..enums import GameState, Direction, MenuType  # 添加 MenuType 到这行
from ..constants import *
from ..utils.helpers import generate_monsters
from .battle_system import BattleSystem
from .menu_system import MenuSystem


class GameManager:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.state = GameState.EXPLORING
        self.floor = 1

        # 游戏对象
        self.player = Player()
        self.monsters: List[Monster] = []
        self.battle_system: Optional[BattleSystem] = None
        self.menu_system: Optional[MenuSystem] = None

        # 地图设置
        self.map_width = MAP_COLS
        self.map_height = MAP_ROWS
        self.entrance = (0, self.map_height // 2)  # 左侧中点
        self.exit = (self.map_width - 1, self.map_height // 2)  # 右侧中点

        # 初始化玩家位置
        self.player.x, self.player.y = self.entrance

        # 生成怪物
        self.generate_monsters()

        # 移动相关
        self.move_timer = 0
        self.move_direction = None

    def generate_monsters(self):
        self.monsters = generate_monsters(self.floor)
        # 设置怪物初始位置（简化处理）
        for i, monster in enumerate(self.monsters):
            monster.x = random.randint(5, self.map_width - 5)
            monster.y = random.randint(2, self.map_height - 2)

    def all_monsters_defeated(self):
        return all(not monster.is_alive() for monster in self.monsters)

    def can_exit(self):
        return self.all_monsters_defeated()

    def move_player(self, direction: Direction):
        dx, dy = 0, 0
        if direction == Direction.UP:
            dy = -1
        elif direction == Direction.DOWN:
            dy = 1
        elif direction == Direction.LEFT:
            dx = -1
        elif direction == Direction.RIGHT:
            dx = 1

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        # 边界检查
        if 0 <= new_x < self.map_width and 0 <= new_y < self.map_height:
            # 检查是否与怪物碰撞
            for monster in self.monsters:
                if monster.is_alive() and monster.x == new_x and monster.y == new_y:
                    # 触发战斗
                    self.start_battle([monster])
                    return

            # 检查是否到达出口
            if (new_x, new_y) == self.exit and self.can_exit():
                self.next_floor()
                return

            self.player.x = new_x
            self.player.y = new_y

    def start_battle(self, monsters: List[Monster]):
        self.state = GameState.BATTLE
        self.battle_system = BattleSystem(self.player, monsters, self.font)

    def next_floor(self):
        self.floor += 1
        self.player.x, self.player.y = self.entrance
        self.generate_monsters()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.EXPLORING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move_player(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.move_player(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.move_player(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.move_player(Direction.RIGHT)
                    elif event.key == pygame.K_i:
                        self.state = GameState.MENU
                        self.menu_system = MenuSystem(self.player, self.font)

            elif self.state == GameState.BATTLE:
                if self.battle_system:
                    # 简化事件处理
                    class MockEvent:
                        def __init__(self, type, key=None):
                            self.type = type
                            self.key = key

                    if event.type == pygame.KEYDOWN:
                        mock_event = MockEvent("KEYDOWN")
                        if event.key == pygame.K_UP:
                            mock_event.key = "UP"
                        elif event.key == pygame.K_DOWN:
                            mock_event.key = "DOWN"
                        elif event.key == pygame.K_RETURN:
                            mock_event.key = "RETURN"
                        elif event.key == pygame.K_ESCAPE:
                            mock_event.key = "ESCAPE"

                        self.battle_system.handle_input(mock_event)

                        # 检查战斗结果
                        if self.battle_system.battle_result == "victory":
                            self.state = GameState.EXPLORING
                            self.battle_system = None
                            # 给予奖励
                            self.give_battle_rewards()
                        elif self.battle_system.battle_result == "defeat":
                            self.state = GameState.GAME_OVER
                        elif self.battle_system.battle_result == "escape":
                            self.state = GameState.EXPLORING
                            self.battle_system = None
                        elif not self.battle_system.is_player_turn:
                            # 怪物回合
                            self.battle_system.start_monster_turn()
                            if self.battle_system.battle_result == "defeat":
                                self.state = GameState.GAME_OVER

            elif self.state == GameState.MENU:
                if self.menu_system:
                    # 简化事件处理
                    class MockEvent:
                        def __init__(self, type, key=None):
                            self.type = type
                            self.key = key

                    if event.type == pygame.KEYDOWN:
                        mock_event = MockEvent("KEYDOWN")
                        if event.key == pygame.K_UP:
                            mock_event.key = "UP"
                        elif event.key == pygame.K_DOWN:
                            mock_event.key = "DOWN"
                        elif event.key == pygame.K_LEFT:
                            mock_event.key = "LEFT"
                        elif event.key == pygame.K_RIGHT:
                            mock_event.key = "RIGHT"
                        elif event.key == pygame.K_RETURN:
                            mock_event.key = "RETURN"
                        elif event.key == pygame.K_ESCAPE:
                            mock_event.key = "ESCAPE"

                        self.menu_system.handle_input(mock_event)

                        # 检查是否退出菜单
                        if self.menu_system.current_menu is None:
                            self.state = GameState.EXPLORING
                            self.menu_system = None

        return True

    def give_battle_rewards(self):
        # 简化奖励系统
        self.player.gain_talent_point()

        # 随机给予道具和装备
        if random.random() < 0.8:  # 80% 概率获得苹果
            self.player.add_item("苹果", 1)
        if random.random() < 0.5:  # 50% 概率获得葡萄酒
            self.player.add_item("葡萄酒", 1)

    def update(self, dt):
        if self.state == GameState.EXPLORING:
            # 连续移动处理
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.move_timer += dt
                if self.move_timer >= 200:  # 每200ms移动一次
                    self.move_timer = 0
                    if keys[pygame.K_UP]:
                        self.move_player(Direction.UP)
                    elif keys[pygame.K_DOWN]:
                        self.move_player(Direction.DOWN)
                    elif keys[pygame.K_LEFT]:
                        self.move_player(Direction.LEFT)
                    elif keys[pygame.K_RIGHT]:
                        self.move_player(Direction.RIGHT)
            else:
                self.move_timer = 0

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == GameState.EXPLORING:
            self.draw_exploring()
        elif self.state == GameState.BATTLE:
            if self.battle_system:
                self.draw_battle()
        elif self.state == GameState.MENU:
            if self.menu_system:
                self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def draw_exploring(self):
        self.screen.fill(GRASS_GREEN)  # 使用草绿色填充背景
        # 绘制地图网格
        for x in range(self.map_width):
            for y in range(self.map_height):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # 绘制入口和出口
        entrance_rect = pygame.Rect(self.entrance[0] * GRID_SIZE, self.entrance[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, GREEN, entrance_rect)

        exit_color = YELLOW if self.can_exit() else GRAY
        exit_rect = pygame.Rect(self.exit[0] * GRID_SIZE, self.exit[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, exit_color, exit_rect)

        # 绘制怪物
        for monster in self.monsters:
            if monster.is_alive():
                monster_rect = pygame.Rect(monster.x * GRID_SIZE, monster.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                color = RED if monster.type == monster.type.NORMAL else (
                255, 165, 0) if monster.type == monster.type.ELITE else PURPLE
                pygame.draw.rect(self.screen, color, monster_rect)

                # 绘制血条
                bar_width = GRID_SIZE
                bar_height = 4
                hp_ratio = monster.current_health / monster.max_health
                hp_bar_width = int(bar_width * hp_ratio)

                bar_rect = pygame.Rect(monster.x * GRID_SIZE, monster.y * GRID_SIZE - 6, bar_width, bar_height)
                hp_bar_rect = pygame.Rect(monster.x * GRID_SIZE, monster.y * GRID_SIZE - 6, hp_bar_width, bar_height)

                pygame.draw.rect(self.screen, GRAY, bar_rect)
                pygame.draw.rect(self.screen, GREEN, hp_bar_rect)

        # 绘制玩家
        player_rect = pygame.Rect(self.player.x * GRID_SIZE, self.player.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, BLUE, player_rect)

        # 绘制状态栏
        status_rect = pygame.Rect(0, SCREEN_HEIGHT - STATUS_BAR_HEIGHT, SCREEN_WIDTH, STATUS_BAR_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, status_rect)

        # 绘制玩家状态信息
        status_text = f"楼层: {self.floor} | 生命: {self.player.current_health}/{self.player.total_health} | 攻击: {self.player.total_attack} | 防御: {self.player.total_defense} | 技力: {self.player.current_energy}/{self.player.total_energy} | 天赋点: {self.player.talent_points}"
        text_surface = self.font.render(status_text, True, WHITE)
        self.screen.blit(text_surface, (10, SCREEN_HEIGHT - STATUS_BAR_HEIGHT + 10))

    def draw_battle(self):
        if not self.battle_system:
            return

        # 左侧区域
        left_rect = pygame.Rect(0, 0, BATTLE_LEFT_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, DARK_GRAY, left_rect)

        # 动画区域
        animation_rect = pygame.Rect(0, 0, BATTLE_LEFT_WIDTH, BATTLE_ANIMATION_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_BLUE, animation_rect)

        # 显示怪物信息
        if self.battle_system.current_monster:
            monster = self.battle_system.current_monster
            monster_text = f"{monster.type.value} (等级 {self.floor})"
            text_surface = self.font.render(monster_text, True, BLACK)
            self.screen.blit(text_surface, (10, 10))

            # 血条
            bar_width = 200
            bar_height = 20
            hp_ratio = monster.current_health / monster.max_health
            hp_bar_width = int(bar_width * hp_ratio)

            bar_rect = pygame.Rect(10, 40, bar_width, bar_height)
            hp_bar_rect = pygame.Rect(10, 40, hp_bar_width, bar_height)

            pygame.draw.rect(self.screen, GRAY, bar_rect)
            pygame.draw.rect(self.screen, RED, hp_bar_rect)

            hp_text = f"{monster.current_health}/{monster.max_health}"
            hp_text_surface = self.font.render(hp_text, True, BLACK)
            self.screen.blit(hp_text_surface, (10, 42))

        # 玩家属性区域
        player_info_rect = pygame.Rect(0, BATTLE_ANIMATION_HEIGHT, BATTLE_LEFT_WIDTH, BATTLE_PLAYER_INFO_HEIGHT)
        pygame.draw.rect(self.screen, BROWN, player_info_rect)

        # 显示玩家信息
        player_stats = [
            f"生命: {self.player.current_health}/{self.player.total_health}",
            f"攻击: {self.player.total_attack}",
            f"防御: {self.player.total_defense}",
            f"技力: {self.player.current_energy}/{self.player.total_energy}"
        ]

        for i, stat in enumerate(player_stats):
            text_surface = self.font.render(stat, True, WHITE)
            self.screen.blit(text_surface, (10, BATTLE_ANIMATION_HEIGHT + 10 + i * 25))

        # BUFF状态
        buff_y = BATTLE_ANIMATION_HEIGHT + 120
        active_buffs = self.player.get_active_buffs()
        if active_buffs:
            buff_text = "状态: " + ", ".join([f"{buff.name}({buff.duration})" for buff in active_buffs])
            text_surface = self.font.render(buff_text, True, WHITE)
            self.screen.blit(text_surface, (10, buff_y))

        # 战斗选项区域
        menu_rect = pygame.Rect(0, BATTLE_ANIMATION_HEIGHT + BATTLE_PLAYER_INFO_HEIGHT, BATTLE_LEFT_WIDTH,
                                BATTLE_MENU_HEIGHT)
        pygame.draw.rect(self.screen, GRAY, menu_rect)

        # 绘制菜单
        menu_items = self.battle_system.get_current_menu_items()
        visible_items = menu_items[
                        self.battle_system.scroll_offset:self.battle_system.scroll_offset + self.battle_system.max_visible_items]

        for i, item in enumerate(visible_items):
            color = YELLOW if i + self.battle_system.scroll_offset == self.battle_system.selected_menu_index else WHITE
            text_surface = self.font.render(item, True, color)
            self.screen.blit(text_surface, (20, BATTLE_ANIMATION_HEIGHT + BATTLE_PLAYER_INFO_HEIGHT + 20 + i * 30))

        # 右侧日志区域
        log_rect = pygame.Rect(BATTLE_LEFT_WIDTH, 0, BATTLE_RIGHT_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, BLACK, log_rect)

        # 绘制战斗日志
        for i, log_entry in enumerate(self.battle_system.battle_log[:15]):  # 最多显示15条日志
            text_surface = self.font.render(log_entry, True, WHITE)
            self.screen.blit(text_surface, (BATTLE_LEFT_WIDTH + 10, 10 + i * 25))

    def draw_menu(self):
        if not self.menu_system:
            return

        # 绘制半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 绘制菜单标题
        title_text = "主菜单"
        if self.menu_system.current_menu == MenuType.ABILITY:
            title_text = "能力编辑"
        elif self.menu_system.current_menu == MenuType.EQUIPMENT:
            title_text = "装备编辑"
        elif self.menu_system.current_menu == MenuType.ITEM:
            title_text = "道具使用"
        elif self.menu_system.current_menu == MenuType.SYNTHESIS:
            title_text = "装备合成"

        title_surface = self.font.render(title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_surface, title_rect)

        # 绘制菜单项
        menu_items = self.menu_system.get_menu_items()
        visible_items = menu_items[
                        self.menu_system.scroll_offset:self.menu_system.scroll_offset + self.menu_system.max_visible_items]

        start_y = 100
        for i, item in enumerate(visible_items):
            color = YELLOW if i + self.menu_system.scroll_offset == self.menu_system.selected_index else WHITE
            text_surface = self.font.render(item, True, color)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text_surface, text_rect)

    def draw_game_over(self):
        self.screen.fill(BLACK)

        # 绘制游戏结束文字
        game_over_text = self.font.render("游戏结束", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        # 绘制最终信息
        final_text = self.font.render(f"你到达了第 {self.floor} 层", True, WHITE)
        final_rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_text, final_rect)

        # 绘制重新开始提示
        restart_text = self.font.render("按 R 重新开始，按 ESC 退出", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

        # 处理重新开始
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.__init__(self.screen, self.font)  # 重新初始化游戏

    def run(self, dt):
        if not self.handle_events():
            return False
        self.update(dt)
        self.draw()
        return True