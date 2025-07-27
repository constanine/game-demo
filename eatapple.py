import pygame
import random
import time
import os

# 初始化
pygame.init()

# 屏幕设置
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
GRID_SIZE = 40
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("吃苹果小游戏")

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
HIGHLIGHT = (100, 100, 255)

# 字体（优先使用中文字体）
try:
    font = pygame.font.SysFont('SimHei', 36)  # 支持中文
except:
    font = pygame.font.SysFont('arial', 36, bold=True)  # 备用字体

menu_font = pygame.font.SysFont('SimHei', 48)

# 加载苹果图片（可选）
USE_IMAGE = True
apple_image = None
if USE_IMAGE:
    try:
        apple_image = pygame.image.load("apple.png")
        apple_image = pygame.transform.scale(apple_image, (GRID_SIZE, GRID_SIZE))
        player_image = pygame.image.load("player.png")
        player_image = pygame.transform.scale(player_image, (GRID_SIZE*2, GRID_SIZE*2))
    except FileNotFoundError:
        print("未找到 apple.png，将使用红色矩形替代。")
        USE_IMAGE = False

# 小人类
class Player:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.base_speed = 1  # 初始速度
        self.speed_factor = 1.0   # 速度倍率（每次+20%）
        self.direction = None
        self.enlarge_step = 0     # 放大等级，每级 +5px

    def move(self):
        if self.direction == "UP":
            self.y -= self.base_speed * self.speed_factor
        elif self.direction == "DOWN":
            self.y += self.base_speed * self.speed_factor
        elif self.direction == "LEFT":
            self.x -= self.base_speed * self.speed_factor
        elif self.direction == "RIGHT":
            self.x += self.base_speed * self.speed_factor

        self.x = max(0, min(SCREEN_WIDTH - self.width(), self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height(), self.y))

    def width(self):
        return GRID_SIZE*2 + self.enlarge_step * 10

    def height(self):
        return GRID_SIZE*2 + self.enlarge_step * 10

    def draw(self):
        rect = pygame.Rect(int(self.x), int(self.y), self.width(), self.height())
        pygame.draw.rect(screen, BLUE, rect)

        if USE_IMAGE and player_image:
            screen.blit(player_image, rect)
        else:
            pygame.draw.rect(screen, RED, rect)
    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width(), self.height())

# 苹果类
class Apple:
    def __init__(self):
        self.x = random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        self.y = random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.spawn_time = time.time()
        self.lifetime = 15  # 存在时间15秒

    def is_alive(self):
        return time.time() - self.spawn_time < self.lifetime

    def draw(self):
        if USE_IMAGE and apple_image:
            screen.blit(apple_image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, GRID_SIZE, GRID_SIZE))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE)

    def check_collision(self, player_rect):
        intersect = self.get_rect().clip(player_rect)
        intersect_area = intersect.width * intersect.height
        total_area = GRID_SIZE * GRID_SIZE
        return intersect_area > 0.2 * total_area


# 读取历史最高分
def load_high_scores():
    if os.path.exists("high_scores.txt"):
        with open("high_scores.txt", "r") as f:
            return sorted([int(line.strip()) for line in f.readlines()], reverse=True)
    return []

# 保存新分数
def save_high_score(score):
    scores = load_high_scores()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:5]
    with open("high_scores.txt", "w") as f:
        for s in scores:
            f.write(f"{s}\n")

# 创建玩家和苹果
player = Player()
apples = [Apple() for _ in range(10)]

score = 0
running = True
clock = pygame.time.Clock()
show_menu = False
show_ability_menu = False
menu_selection = 0  # 当前选中项: 0=大小+5px, 1=水果+5, 2=速度+20%, 3=取消
show_not_enough = False  # 是否显示分数不足提示
game_over = False
start_time = time.time()
total_game_time = 300  # 300秒 = 5分钟

# 菜单绘制函数
def draw_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    title = menu_font.render("功能菜单", True, WHITE)
    option = menu_font.render("→ 增加能力", True, GREEN)
    screen.blit(title, (SCREEN_WIDTH // 2 - 100, 100))
    screen.blit(option, (SCREEN_WIDTH // 2 - 120, 200))

# 能力菜单绘制
def draw_ability_menu():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    title = menu_font.render("选择能力", True, WHITE)

    opt_texts = [
        "1. 大小+5px (-5分)",
        "2. +5水果 (-10分)",
        "3. 加快速度 (-5分)",
        "4. 取消"
    ]
    colors = [
        GREEN if score >= 5 else RED,
        GREEN if score >= 10 else RED,
        GREEN if score >= 5 else RED,
        WHITE
    ]

    screen.blit(title, (SCREEN_WIDTH // 2 - 100, 100))

    for i, text in enumerate(opt_texts):
        color = HIGHLIGHT if i == menu_selection else colors[i]
        rect_color = (50, 50, 150) if i == menu_selection else (30, 30, 30)
        pygame.draw.rect(screen, rect_color, (SCREEN_WIDTH//2 - 200, 170 + i * 90, 400, 60))
        label = menu_font.render(text, True, color)
        screen.blit(label, (SCREEN_WIDTH // 2 - 160, 180 + i * 90))

    if show_not_enough:
        warn = menu_font.render("No enough score!", True, RED)
        screen.blit(warn, (SCREEN_WIDTH // 2 - 200, 550))

# 结局界面
def show_game_over():
    screen.fill(BLACK)
    save_high_score(score)

    title = menu_font.render(f"游戏结束! 得分: {score}", True, GREEN)
    replay = menu_font.render("按 Enter 再来一局", True, WHITE)

    screen.blit(title, (SCREEN_WIDTH // 2 - 250, 200))
    screen.blit(replay, (SCREEN_WIDTH // 2 - 220, 300))

    # 显示历史最高分
    scores = load_high_scores()
    y = 400
    for i, s in enumerate(scores[:5]):
        line = font.render(f"{i+1}. {s}", True, GRAY)
        screen.blit(line, (SCREEN_WIDTH // 2 - 50, y + i * 40))

# 主循环
while running:
    current_time = time.time()
    time_left = max(0, int(total_game_time - (current_time - start_time)))

    if game_over:
        show_game_over()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # 重新开始
                player = Player()
                apples = [Apple() for _ in range(10)]
                score = 0
                start_time = time.time()
                game_over = False
        continue

    screen.fill(WHITE)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                show_menu = not show_menu
                show_ability_menu = False
                menu_selection = 0
                show_not_enough = False

            elif show_menu and not show_ability_menu and event.key == pygame.K_RETURN:
                show_ability_menu = True
                show_not_enough = False

            elif event.key == pygame.K_ESCAPE:
                show_menu = False
                show_ability_menu = False
                menu_selection = 0
                show_not_enough = False

            elif show_ability_menu and event.key == pygame.K_UP:
                menu_selection = (menu_selection - 1) % 4
            elif show_ability_menu and event.key == pygame.K_DOWN:
                menu_selection = (menu_selection + 1) % 4

            elif show_ability_menu and event.key == pygame.K_RETURN:
                if menu_selection == 0:
                    if score >= 5:
                        player.enlarge_step += 1
                        score -= 5
                        show_ability_menu = False
                        show_menu = False
                    else:
                        show_not_enough = True
                elif menu_selection == 1:
                    if score >= 10:
                        for _ in range(5):
                            apples.append(Apple())
                        score -= 10
                        show_ability_menu = False
                        show_menu = False
                    else:
                        show_not_enough = True
                elif menu_selection == 2:
                    if score >= 5:
                        player.speed_factor *= 1.2
                        score -= 5
                        show_ability_menu = False
                        show_menu = False
                    else:
                        show_not_enough = True
                elif menu_selection == 3:
                    show_ability_menu = False

    # 键盘输入处理
    keys = pygame.key.get_pressed()
    if not (show_menu or show_ability_menu):  # 菜单打开时不控制角色
        if keys[pygame.K_UP]:
            player.direction = "UP"
        elif keys[pygame.K_DOWN]:
            player.direction = "DOWN"
        elif keys[pygame.K_LEFT]:
            player.direction = "LEFT"
        elif keys[pygame.K_RIGHT]:
            player.direction = "RIGHT"
        else:
            player.direction = None

    # 移动玩家
    player.move()

    # 绘制苹果并检查碰撞
    player_rect = player.get_rect()
    for apple in apples[:]:
        if not apple.is_alive():
            apples.remove(apple)
        elif apple.check_collision(player_rect):
            score += 1
            apples.remove(apple)
        else:
            apple.draw()

    # 如果苹果数量不足，可以补充新的苹果
    while len(apples) < 10:
        apples.append(Apple())

    # 绘制玩家
    player.draw()

    # 显示分数
    score_text = font.render(f"Score: {score}", True, GREEN)
    screen.blit(score_text, (10, 10))

    # 显示倒计时
    time_text = font.render(f"剩余时间: {time_left} 秒", True, RED)
    screen.blit(time_text, (SCREEN_WIDTH - 250, 10))

    # 显示菜单
    if show_menu:
        draw_menu()
    if show_ability_menu:
        draw_ability_menu()

    # 判断是否时间到
    if current_time - start_time >= total_game_time:
        game_over = True

    pygame.display.flip()
    clock.tick(60)  # 60 FPS

pygame.quit()