import pygame
import random
import json
import os

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
GRID_SIZE = 40
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("网格冒险游戏")

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# 游戏时钟
clock = pygame.time.Clock()

# 分数记录文件
HIGH_SCORE_FILE = "high_scores.json"


# 加载最高分
def load_high_scores():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            return json.load(f)
    return []


# 保存最高分
def save_high_scores(high_scores):
    with open(HIGH_SCORE_FILE, "w") as f:
        json.dump(high_scores, f)


# 添加新分数到最高分列表
def add_score_to_high_scores(score, high_scores):
    high_scores.append(score)
    high_scores.sort(reverse=True)
    if len(high_scores) > 5:
        high_scores.pop()
    save_high_scores(high_scores)


# 玩家类
class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.power = 5
        self.score = 0
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BLUE)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        # 限制在屏幕范围内
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# 怪物类
class Monster:
    def __init__(self, wave, monster_type):
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.x = random.randint(0, (SCREEN_WIDTH - self.width) // GRID_SIZE) * GRID_SIZE
        self.y = random.randint(0, (SCREEN_HEIGHT - self.height) // GRID_SIZE) * GRID_SIZE

        # 根据类型设置战力
        base = wave * wave  # 波次平方
        if monster_type == "low":
            self.power = base * random.randint(1, 5)
        elif monster_type == "medium":
            self.power = base * random.randint(10, 50)
        else:  # high
            self.power = base * random.randint(100, 200)

        self.image = pygame.Surface((self.width, self.height))
        pygame.draw.circle(self.image, RED, (self.width // 2, self.height // 2), self.width // 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# 宝物类
class Treasure:
    def __init__(self, wave):
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.x = random.randint(0, (SCREEN_WIDTH - self.width) // GRID_SIZE) * GRID_SIZE
        self.y = random.randint(0, (SCREEN_HEIGHT - self.height) // GRID_SIZE) * GRID_SIZE

        # 随机宝物类型（2倍加成概率为5%）
        if random.random() < 0.95:  # 90%概率获得加成宝物
            self.type = "add"
            self.value = wave * random.randint(1, 5)
        else:  # 10%概率获得翻倍宝物
            self.type = "50%power"
            self.value = 1.5

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(YELLOW)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


# 检查碰撞
def check_collision(rect1, rect2):
    # 计算碰撞区域
    collision_rect = rect1.colliderect(rect2)
    if not collision_rect:
        return False

    # 获取实际碰撞区域
    collision_rect = rect1.clip(rect2)

    # 计算碰撞面积
    collision_area = collision_rect.width * collision_rect.height

    # 计算两个矩形的面积
    area1 = rect1.width * rect1.height
    area2 = rect2.width * rect2.height

    # 判断超过20%重合
    return collision_area > (min(area1, area2) * 0.2)


# 显示游戏结束画面
def show_game_over(screen, score, high_scores):
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))

    font = pygame.font.Font(None, 36)
    text = font.render("Press Enter to play again", True, BLACK)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    # 显示最高分
    high_scores_text = font.render("Top Scores:", True, BLACK)
    screen.blit(high_scores_text, (SCREEN_WIDTH // 2 - high_scores_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

    for i, high_score in enumerate(high_scores):
        score_text = font.render(f"{i + 1}. {high_score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 140 + i * 30))

    pygame.display.flip()


# 能力编辑菜单
def show_ability_menu(screen, player, monsters, wave):
    menu_items = [
        "Increase Power (+5) - 10 points",
        "Refresh Treasure - 10 points",
        "Weaken Monsters - 20 points",
        "Cancel"
    ]
    selected_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if selected_index == 0:  # 增加战力
                        if player.score >= 10:
                            player.power += 5
                            player.score -= 10
                            return True
                    elif selected_index == 1:  # 刷新宝物
                        if player.score >= 10:
                            player.score -= 10
                            treasures = [Treasure(wave) for _ in range(5)]
                            return treasures
                    elif selected_index == 2:  # 减弱怪物
                        if player.score >= 20:
                            player.score -= 20
                            for monster in monsters:
                                monster.power = max(1, monster.power // 2)
                            return True
                    elif selected_index == 3:  # 取消
                        return True
                elif event.key == pygame.K_ESCAPE:
                    return True

        screen.fill(WHITE, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 400))
        show_menu(screen, menu_items, selected_index, "Ability Menu")

        # 显示玩家信息
        font = pygame.font.Font(None, 28)
        power_text = font.render(f"Player Power: {player.power}", True, BLACK)
        score_text = font.render(f"Score: {player.score}", True, BLACK)
        screen.blit(power_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 80))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 50))

        pygame.display.flip()
        clock.tick(30)

# 主游戏函数
def main_game():
    # 初始化游戏元素
    player = Player()
    wave = 1

    # 确保怪物数量固定为 5+3+2
    def generate_monsters(wave):
        monsters = []
        for _ in range(5):
            monsters.append(Monster(wave, "low"))
        for _ in range(3):
            monsters.append(Monster(wave, "medium"))
        for _ in range(2):
            monsters.append(Monster(wave, "high"))
        return monsters

    monsters = generate_monsters(wave)
    treasures = [Treasure(wave) for _ in range(5)]

    running = True
    game_over = False
    moving = False
    move_direction = None
    move_speed = GRID_SIZE / 2  # 每帧移动距离

    high_scores = load_high_scores()

    # 持续移动计时器
    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, 100)

    # 菜单状态
    in_menu = False
    menu_stack = []

    while running:
        if game_over:
            show_game_over(screen, player.score, high_scores)
        else:
            # 正常游戏画面
            screen.fill(WHITE)

            # 显示玩家
            screen.blit(player.image, (player.x, player.y))
            power_text = pygame.font.Font(None, 24).render(f"{player.power}", True, BLACK)
            screen.blit(power_text, (player.x, player.y - 20))

            # 显示怪物
            for monster in monsters:
                screen.blit(monster.image, (monster.x, monster.y))
                power_text = pygame.font.Font(None, 24).render(f"{monster.power}", True, BLACK)
                screen.blit(power_text, (monster.x, monster.y - 20))

            # 显示宝物
            for treasure in treasures:
                screen.blit(treasure.image, (treasure.x, treasure.y))
                value_text = pygame.font.Font(None, 24).render(
                    f"+{treasure.value}" if treasure.type == "add" else "x2", True, BLACK)
                screen.blit(value_text, (treasure.x, treasure.y - 20))

            # 显示战力和分数
            info_font = pygame.font.Font(None, 36)
            screen.blit(info_font.render(f"Power: {player.power}", True, BLACK), (10, 10))
            screen.blit(info_font.render(f"Score: {player.score}", True, BLACK), (10, 40))
            screen.blit(info_font.render(f"Wave: {wave}", True, BLACK), (10, 70))

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_RETURN:
                        # 重新开始游戏
                        player = Player()
                        wave = 1
                        monsters = generate_monsters(wave)
                        treasures = [Treasure(wave) for _ in range(5)]
                        game_over = False


        if not game_over and not in_menu:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move(-move_speed, 0)
            elif keys[pygame.K_RIGHT]:
                player.move(move_speed, 0)
            elif keys[pygame.K_UP]:
                player.move(0, -move_speed)
            elif keys[pygame.K_DOWN]:
                player.move(0, move_speed)

        if not game_over and not in_menu:
            player_rect = player.get_rect()

            # 玩家与怪物碰撞
            for monster in monsters[:]:
                if check_collision(player_rect, monster.get_rect()):
                    if player.power > monster.power:
                        player.power += monster.power
                        player.score += 1
                        monsters.remove(monster)
                    else:
                        game_over = True
                        add_score_to_high_scores(player.score, high_scores)
                    break

            # 玩家与宝物碰撞
            for treasure in treasures[:]:
                if check_collision(player_rect, treasure.get_rect()):
                    if treasure.type == "add":
                        player.power += treasure.value
                    elif treasure.type == "double":
                        player.power *= treasure.value
                    treasures.remove(treasure)

            # 所有怪物被击败，进入下一波
            if len(monsters) == 0:
                wave += 1
                player.power = max(1, int(player.power * 0.5))  # 减少 50% 战力
                monsters = generate_monsters(wave)
                treasures = [Treasure(wave) for _ in range(5)]

        # 菜单逻辑
        if not game_over and menu_stack:
            in_menu = True
            current_menu = menu_stack[-1]

            if current_menu == "main":
                menu_items = ["Ability Edit", "Equipment Edit", "Cancel"]
                selected_index = 0
                while True:
                    show_menu(screen, menu_items, selected_index, "Menu")
                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected_index = (selected_index - 1) % len(menu_items)
                        elif event.key == pygame.K_DOWN:
                            selected_index = (selected_index + 1) % len(menu_items)
                        elif event.key == pygame.K_RETURN:
                            if selected_index == 0:  # 能力编辑
                                menu_stack.append("ability")
                            elif selected_index == 1:  # 装备编辑（暂未实现）
                                pass
                            elif selected_index == 2:  # 取消
                                menu_stack.pop()
                                in_menu = False
                            break
                        elif event.key == pygame.K_ESCAPE:
                            menu_stack.pop()
                            in_menu = False
                            break

            elif current_menu == "ability":
                menu_items = [
                    "Increase Power (+10%) - 10 points",
                    "Refresh Treasure - 10 points",
                    "Weaken Monsters - 20 points",
                    "Cancel"
                ]
                selected_index = 0
                while True:
                    # 显示玩家信息在菜单顶部
                    screen.fill(WHITE, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100, 300, 400))
                    show_menu(screen, menu_items, selected_index, "Ability Menu")
                    power_text = pygame.font.Font(None, 28).render(f"Power: {player.power}", True, BLACK)
                    score_text = pygame.font.Font(None, 28).render(f"Score: {player.score}", True, BLACK)
                    screen.blit(power_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 90))
                    screen.blit(score_text, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 60))

                    event = pygame.event.wait()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            selected_index = (selected_index - 1) % len(menu_items)
                        elif event.key == pygame.K_DOWN:
                            selected_index = (selected_index + 1) % len(menu_items)
                        elif event.key == pygame.K_RETURN:
                            if selected_index == 0 and player.score >= 10:  # 增加10%战力
                                player.power = int(player.power * 1.1)
                                player.score -= 10
                            elif selected_index == 1 and player.score >= 10:  # 刷新宝物
                                player.score -= 10
                                treasures = [Treasure(wave) for _ in range(5)]
                            elif selected_index == 2 and player.score >= 20:  # 怪物战力减半
                                player.score -= 20
                                for monster in monsters:
                                    monster.power = max(1, monster.power // 2)
                            elif selected_index == 3:  # 取消
                                menu_stack.pop()
                            break
                        elif event.key == pygame.K_ESCAPE:
                            menu_stack.pop()
                            break

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main_game()