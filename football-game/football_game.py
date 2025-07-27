import pygame
import sys
from pygame.locals import *

# 初始化 Pygame
pygame.init()

# 游戏屏幕大小
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

# 图标大小
ICON_SIZE = 40
CIRCLE_SIZE = 120

# 加载图像
football_img = pygame.image.load('images/football.png')
football_img = pygame.transform.scale(football_img, (ICON_SIZE, ICON_SIZE))

red_student_img = pygame.image.load('images/red_student.png')
red_student_img = pygame.transform.scale(red_student_img, (ICON_SIZE, ICON_SIZE))

yellow_student_img = pygame.image.load('images/yellow_student.png')
yellow_student_img = pygame.transform.scale(yellow_student_img, (ICON_SIZE, ICON_SIZE))

blue_student_img = pygame.image.load('images/blue_student.png')
blue_student_img = pygame.transform.scale(blue_student_img, (ICON_SIZE, ICON_SIZE))

green_student_img = pygame.image.load('images/green_student.png')
green_student_img = pygame.transform.scale(green_student_img, (ICON_SIZE, ICON_SIZE))


red_student_wait_img = pygame.image.load('images/red_student_w.png')
red_student_wait_img = pygame.transform.scale(red_student_wait_img, (ICON_SIZE, ICON_SIZE))

yellow_student_wait_img = pygame.image.load('images/yellow_student_w.png')
yellow_student_wait_img = pygame.transform.scale(yellow_student_wait_img, (ICON_SIZE, ICON_SIZE))

blue_student_wait_img = pygame.image.load('images/blue_student_w.png')
blue_student_wait_img = pygame.transform.scale(blue_student_wait_img, (ICON_SIZE, ICON_SIZE))

green_student_wait_img = pygame.image.load('images/green_student_w.png')
green_student_wait_img = pygame.transform.scale(green_student_wait_img, (ICON_SIZE, ICON_SIZE))

# 颜色
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
DARK_BACKGROUND = (30, 30, 30)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('招球进宝')

# 帧率
FPS = 60
clock = pygame.time.Clock()


font_name = pygame.font.match_font('SimHei ')
#显示中文
game_font = pygame.font.Font(font_name, 36)
# 学生类
class Student(pygame.sprite.Sprite):
    def __init__(self, id, image_active, image_waitting, x, y, circle_color, is_player=False):
        super().__init__()
        self.id = id

        self.image_active = image_active
        self.image_waitting = image_waitting
        self.image = self.image_active
        self.original_speed = 4
        self.speed = self.original_speed
        self.rect = self.image.get_rect(center=(x, y))
        self.circle_color = circle_color
        self.circle_center = (x, y)
        self.has_ball = False
        self.cooldown = 0
        self.is_player = is_player
        self.target_ball = None
        self.score = 0
        self.balls_in_circle = []
        self.waitting = False;
        self.waittingCount = 0;

        if self.is_player:
            self.speed = self.original_speed + 1
    def draw_circle(self):
        pygame.draw.circle(screen, self.circle_color, self.circle_center, CIRCLE_SIZE // 2, 2)

    # 跟新每个学生移动动画
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        # 如果是玩家
        if self.is_player:
            keys = pygame.key.get_pressed()
            if keys[K_LEFT]:
                self.rect.x -= self.speed
            if keys[K_RIGHT]:
                self.rect.x += self.speed
            if keys[K_UP]:
                self.rect.y -= self.speed
            if keys[K_DOWN]:
                self.rect.y += self.speed
            self.player_drop_ball()
            if waiting:
                if self.waittingCount == 0:
                     self.waitting = False
                     self.image = self.image_active
                else:
                    self.waitting -= 2
        else:
            # 如果是程序
            if not waiting:
                if not self.has_ball:
                    self.find_closest_ball()
                else:
                    self.move_towards_circle()

                if self.target_ball and not self.has_ball:
                    self.move_towards_ball()
            else:
                if self.waittingCount == 0:
                     self.waitting = False
                     self.image = self.image_active
                else:
                    self.waitting -= 1
        self.rect.clamp_ip(screen.get_rect())

    def find_closest_ball(self):
        min_distance = float('inf')
        closest_ball = None
        for ball in footballs:
            if ball.owner != self:
                distance = pygame.math.Vector2(ball.rect.center).distance_to(self.rect.center)
                if distance < min_distance:
                    min_distance = distance
                    closest_ball = ball
        self.target_ball = closest_ball

    def move_towards_ball(self):
        if self.target_ball and not self.has_ball:
            ball_pos = pygame.math.Vector2(self.target_ball.rect.center)
            student_pos = pygame.math.Vector2(self.rect.center)
            if ball_pos != student_pos:
                direction = (ball_pos - student_pos).normalize()
                self.rect.x += int(direction.x * self.speed)
                self.rect.y += int(direction.y * self.speed)

    def move_towards_circle(self):
        if self.has_ball:
            circle_pos = pygame.math.Vector2(self.circle_center)
            student_pos = pygame.math.Vector2(self.rect.center)
            if student_pos.distance_to(circle_pos) > 1:
                direction = (circle_pos - student_pos).normalize()
                self.rect.x += int(direction.x * self.speed)
                self.rect.y += int(direction.y * self.speed)
            else:
                self.drop_ball()

    def player_drop_ball(self):
        if self.has_ball:
            circle_pos = pygame.math.Vector2(self.circle_center)
            student_pos = pygame.math.Vector2(self.rect.center)
            if student_pos.distance_to(circle_pos) <= 40:
                self.drop_ball()
    def pick_up_ball(self, ball):
        if not self.has_ball:
            self.has_ball = True
            self.speed = self.original_speed // 2
            ball.rect.center = self.rect.center
            if ball.carried_by is None and ball.owner is not None:
                ball.owner.balls_in_circle.remove(ball)
                ball.owner.update_score()
            if ball.carried_by is not None:
                ball.carried_by.be_waitting()
            ball.carried_by = self
            ball.changeOwner(self)
            self.target_ball = None

    def drop_ball(self):
        if self.has_ball:
            self.has_ball = False
            self.speed = self.original_speed
            for ball in footballs:
                if ball.carried_by == self:
                    ball.rect.center = self.circle_center
                    ball.carried_by = None
                    self.balls_in_circle.append(ball)
            self.update_score()

    def update_score(self):
        num_balls = len(self.balls_in_circle)
        self.score = num_balls

    def be_waitting(self):
        self.waitting = True;
        self.waittingCount = 5;
        self.image = self.image_waitting


# 足球类
class Football(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = football_img
        self.rect = self.image.get_rect(center=(x, y))
        self.carried_by = None
        self.owner = None

    def update(self):
        if self.carried_by:
            self.rect.center = self.carried_by.rect.center

    def changeOwner(self, owner):
        self.owner = owner

def create_honeycomb_pattern():
    positions = [
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH // 2 - ICON_SIZE, SCREEN_HEIGHT // 2 - ICON_SIZE),
        (SCREEN_WIDTH // 2 + ICON_SIZE, SCREEN_HEIGHT // 2 - ICON_SIZE),
        (SCREEN_WIDTH // 2 - ICON_SIZE, SCREEN_HEIGHT // 2 + ICON_SIZE),
        (SCREEN_WIDTH // 2 + ICON_SIZE, SCREEN_HEIGHT // 2 + ICON_SIZE),
        (SCREEN_WIDTH // 2 - ICON_SIZE * 2, SCREEN_HEIGHT // 2),
        (SCREEN_WIDTH // 2 + ICON_SIZE * 2, SCREEN_HEIGHT // 2)
    ]
    return [Football(x, y) for x, y in positions]


def check_for_winner():
    for student in students:
        if student.score >= 3:
            return student
    return None

def draw_all():
    screen.fill(DARK_BACKGROUND)
    for student in students:
        student.draw_circle()
        screen.blit(student.image, student.rect)

        # 在圈的底部显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"{student.score}", True, WHITE)
        score_position = (
        student.circle_center[0] - score_text.get_width() // 2, student.circle_center[1] + CIRCLE_SIZE // 2)
        screen.blit(score_text, score_position)

    footballs.draw(screen)
    pygame.display.flip()

def restart_game():
    show_instructions()
    global footballs, students, player
    # 初始化对象
    footballs = pygame.sprite.Group(*create_honeycomb_pattern())

    # 创建学生对象
    red_student = Student(1001, red_student_img, red_student_wait_img, SCREEN_WIDTH // 2, SCREEN_HEIGHT - CIRCLE_SIZE, RED,
                          is_player=True)
    yellow_student = Student(1002, yellow_student_img, yellow_student_wait_img, CIRCLE_SIZE, SCREEN_HEIGHT // 2, YELLOW)
    blue_student = Student(1003, blue_student_img, blue_student_wait_img, SCREEN_WIDTH // 2, CIRCLE_SIZE, BLUE)
    green_student = Student(1004, green_student_img, green_student_wait_img, SCREEN_WIDTH - CIRCLE_SIZE, SCREEN_HEIGHT // 2, GREEN)

    students = pygame.sprite.Group(red_student, yellow_student, blue_student, green_student)
    player = red_student


def main_game():
    restart_game()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        students.update()
        footballs.update()

        for student in students:
            if student.has_ball or student.waitting:
                continue
            for ball in footballs:
                if student.rect.colliderect(ball.rect) and ball.owner != student:
                    if(student.is_player):
                        student.pick_up_ball(ball)
                    else:
                        student.pick_up_ball(ball)
        winner = check_for_winner()
        if winner:
            screen.fill(DARK_BACKGROUND)
            font = pygame.font.Font(font_name, 48)
            win_color = winner.circle_color
            if win_color == RED:
                text = font.render(f"恭喜你获胜！", True, WHITE)
            else:
                if win_color == YELLOW:
                    color_name = "黄色"
                elif win_color == BLUE:
                    color_name = "蓝色"
                else:
                    color_name = "绿色"
                text = font.render(f"{color_name} 学生获胜！", True, WHITE)

            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(3000)

            restart_game()

        draw_all()
        clock.tick(FPS)


def show_instructions():
    font = pygame.font.Font(None, 36)
    instructions = [
        "招球进宝",
        "通过方向键控制红色学生移动",
        "将足球带回自己的圈内",
        "率先收集3个足球的学生获胜",
        "按任意键开始"
    ]
    screen.fill(DARK_BACKGROUND)
    for i, line in enumerate(instructions):
        text = game_font.render(line, True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + i * 40))
    pygame.display.flip()


show_instructions()
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            waiting = False

main_game()
