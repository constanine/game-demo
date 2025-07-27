import pygame
import sys
from player import Player
from map import GameMap
from battle import BattleSystem
from menu import Menu
from game_over import show_game_over_screen

# 初始化Pygame
pygame.init()

# 设置屏幕大小为800*640
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("冒险游戏")

clock = pygame.time.Clock()
FPS = 60

# 初始化对象
player = Player()
game_map = GameMap(player)
battle_system = BattleSystem(screen, player)
menu = Menu(screen, player)

# 游戏状态管理
game_state = "playing"  # "playing", "battle", "menu", "game_over"
current_monster = None

# 主循环
running = True
while running:
    dt = clock.tick(FPS) / 1000.0  # delta time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i and game_state == "playing":
                game_state = "menu"
            elif event.key == pygame.K_ESCAPE:
                if game_state == "menu":
                    game_state = "playing"
                elif game_state == "battle":
                    game_state = "playing"

    # 根据状态更新和渲染
    if game_state == "playing":
        player.handle_input()

        # 检查碰撞
        collision_result, monster = game_map.update()
        if collision_result == "battle":
            current_monster = monster
            game_state = "battle"
        elif collision_result == "next_floor":
            # 已经在map.update()中处理了进入下一层的逻辑
            pass

        # 绘制地图与角色 - 使用浅绿色背景
        screen.fill((144, 238, 144))  # 浅绿色
        game_map.draw(screen)
        player.draw(screen)

    elif game_state == "battle":
        if current_monster:
            result = battle_system.run(current_monster)
            if result == "win":
                player.gain_exp(1)
                game_map.remove_monster(current_monster)
                current_monster = None
                game_state = "playing"
            elif result == "lose":
                game_state = "game_over"
            elif result == "flee":
                player.x = 0  # 回到入口
                player.y = 320 - player.height // 2
                current_monster = None
                game_state = "playing"
            elif result == "continue":
                # 继续战斗，保持battle状态
                pass

    elif game_state == "menu":
        menu_result = menu.run()
        if menu_result in ["back", "handled", "quit"]:
            game_state = "playing"
            if menu_result == "quit":
                running = False

    elif game_state == "game_over":
        show_game_over_screen(screen, player.floor)
        running = False  # 可以改为重新开始逻辑

    pygame.display.flip()

pygame.quit()
#sys.exit()