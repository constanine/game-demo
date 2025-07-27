import pygame
import random
import sys

# 初始化 Pygame
pygame.init()

# 常量设置
SCREEN_SIZE = 800
GRID_SIZE = 40
GRID_WIDTH = SCREEN_SIZE // GRID_SIZE  # 20
GRID_HEIGHT = SCREEN_SIZE // GRID_SIZE  # 20
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("地牢冒险")
clock = pygame.time.Clock()

# 字体
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 28)

# 游戏状态
GAME_STATE = "map"  # map, battle, menu
FLOOR = 1
TalentPoints = 0

# 装备类型
EQUIP_SLOTS = ["head", "chest", "left_hand", "right_hand", "feet"]

# 道具库存
inventory = []

# 怪物列表
monsters = []

# ------------------ 角色类 ------------------
class Player:
    def __init__(self):
        self.x = 0
        self.y = GRID_HEIGHT // 2
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.atk = 10
        self.hp = 100
        self.max_hp = 100
        self.defense = 5
        self.equipment = {slot: None for slot in EQUIP_SLOTS}
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(BLUE)

    def move(self, dx, dy):
        new_x = self.x + dx * 0.5
        new_y = self.y + dy * 0.5
        # 边界检测
        if 0 <= new_x <= GRID_WIDTH - 1 and 0 <= new_y <= GRID_HEIGHT - 1:
            self.x = new_x
            self.y = new_y

    def get_total_atk(self):
        bonus = sum(equip.atk_bonus if equip else 0 for equip in self.equipment.values())
        return self.atk + bonus

    def get_total_def(self):
        bonus = sum(equip.def_bonus if equip else 0 for equip in self.equipment.values())
        return self.defense + bonus

    def get_total_hp(self):
        bonus = sum(equip.hp_bonus if equip else 0 for equip in self.equipment.values())
        return self.hp + bonus

    def draw(self, surface):
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, self.width, self.height)
        surface.blit(self.image, rect.topleft)

player = Player()

# ------------------ 装备类 ------------------
class Equipment:
    def __init__(self, floor, slot):
        self.floor = floor
        self.slot = slot
        self.name = ""
        self.atk_bonus = 0
        self.def_bonus = 0
        self.hp_bonus = 0
        self.generate_stats()

    def generate_stats(self):
        if self.slot == "head":
            choice = random.choice(["def", "hp"])
            if choice == "def":
                self.def_bonus = self.floor * random.randint(1, 3)
            else:
                self.hp_bonus = self.floor * random.randint(5, 10)
            self.name = f"{self.floor} 头盔"
        elif self.slot == "chest":
            self.hp_bonus = self.floor * random.randint(10, 20)
            self.name = f"{self.floor} 护甲"
        elif self.slot == "left_hand":
            self.atk_bonus = self.floor * random.randint(5, 10)
            self.name = f"{self.floor} 长剑"
        elif self.slot == "right_hand":
            self.def_bonus = self.floor * random.randint(2, 5)
            self.name = f"{self.floor} 护盾"
        elif self.slot == "feet":
            self.def_bonus = self.floor * random.randint(1, 3)
            self.name = f"{self.floor} 靴子"

    def __str__(self):
        return f"{self.name} (+{self.atk_bonus}atk, +{self.def_bonus}def, +{self.hp_bonus}hp)"

# ------------------ 道具类 ------------------
class Item:
    def __init__(self, name, heal_amount):
        self.name = name
        self.heal = heal_amount

    def use(self, target):
        target.hp = min(target.max_hp, target.hp + self.heal)
        return f"{target} 使用了 {self.name}，恢复 {self.heal} 生命值"

# 苹果和面包
apple = Item("苹果", 20)
bread = Item("面包", 50)

# ------------------ 怪物类 ------------------
class Monster:
    def __init__(self, floor, mtype="normal"):
        self.floor = floor
        self.mtype = mtype
        self.width = GRID_SIZE
        self.height = GRID_SIZE
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(RED)
        self.atk = 0
        self.hp = 0
        self.defense = 0
        self.max_hp = 0
        self.x = random.randint(0, GRID_WIDTH - 1)
        self.y = random.randint(0, GRID_HEIGHT - 1)
        self.generate_stats(mtype)
        self.dead = False

    def generate_stats(self, mtype):
        if mtype == "normal":
            self.atk = 2 * self.floor
            self.hp = 20 * self.floor
            self.defense = 1 * self.floor
        elif mtype == "elite":
            self.atk = 5 * self.floor
            self.hp = 50 * self.floor
            self.defense = 2 * self.floor
        elif mtype == "boss":
            self.atk = 15 * self.floor
            self.hp = 150 * self.floor
            self.defense = 5 * self.floor
        self.max_hp = self.hp

    def draw(self, surface):
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, self.width, self.height)
        surface.blit(self.image, rect.topleft)

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
        return actual_damage

    def attack(self, player):
        damage = max(1, self.atk - player.get_total_def())
        player.hp = max(0, player.hp - damage)
        return damage

# ------------------ 战斗系统 ------------------
current_monster = None
battle_log = []
battle_options = ["战斗", "物品", "逃跑"]
battle_selected = 0

def start_battle(monster):
    global GAME_STATE, current_monster, battle_log, battle_selected
    current_monster = monster
    battle_log = [f"遭遇了 {monster.mtype} 怪物！"]
    battle_selected = 0
    GAME_STATE = "battle"

def end_battle(victory=False):
    global GAME_STATE, current_monster
    if victory:
        global TalentPoints
        TalentPoints += 1
        drop_loot(current_monster)
    current_monster = None
    GAME_STATE = "map"

def drop_loot(monster):
    drops = []
    if monster.mtype == "normal":
        if random.random() < 0.8:
            drops.append(apple)
        if random.random() < 0.2:
            slot = random.choice(EQUIP_SLOTS)
            drops.append(Equipment(FLOOR, slot))
    elif monster.mtype == "elite":
        slot = random.choice(EQUIP_SLOTS)
        drops.append(Equipment(FLOOR, slot))
        drops.append(bread)
    elif monster.mtype == "boss":
        drops.append(bread)
        drops.append(Equipment(FLOOR, random.choice(EQUIP_SLOTS)))
        drops.append(Equipment(FLOOR, random.choice(EQUIP_SLOTS)))
        if random.random() < 0.5:
            drops.append(Equipment(FLOOR + 1, random.choice(EQUIP_SLOTS)))
    for item in drops:
        if isinstance(item, Equipment):
            inventory.append(item)
        elif isinstance(item, Item):
            found = False
            for inv_item in inventory:
                if inv_item.name == item.name:
                    # 可堆叠？简单处理：不堆叠，直接加
                    pass
            inventory.append(item)
    battle_log.append("获得了战利品！")

# ------------------ 菜单系统 ------------------
menu_stack = []
menu_actions = {}

def open_menu():
    global GAME_STATE, menu_stack
    main_menu = {
        "title": "功能菜单",
        "options": ["能力编辑", "装备编辑", "道具使用", "装备合成", "取消"],
        "action": [
            open_ability_menu,
            open_equip_menu,
            open_item_menu,
            open_combine_menu,
            lambda: menu_stack.pop()
        ]
    }
    menu_stack = [main_menu]
    GAME_STATE = "menu"

def run_menu_action():
    selected = menu_stack[-1].get("selected", 0)
    action = menu_stack[-1]["action"][selected]
    action()

def draw_menu():
    menu = menu_stack[-1]
    screen.fill(GRAY)
    title_surf = font.render(menu["title"], True, BLACK)
    screen.blit(title_surf, (50, 50))

    for i, option in enumerate(menu["options"]):
        color = YELLOW if i == menu.get("selected", 0) else WHITE
        surf = small_font.render(option, True, color)
        screen.blit(surf, (100, 120 + i * 50))

def open_ability_menu():
    menu = {
        "title": "能力编辑 (1天赋=)",
        "options": [
            f"攻击力 +5 (当前:{player.atk})",
            f"体力 +15 (当前:{player.hp})",
            f"防御力 +2 (当前:{player.defense})",
            "返回"
        ],
        "action": [
            lambda: upgrade_stat("atk", 5, 1),
            lambda: upgrade_stat("hp", 15, 1),
            lambda: upgrade_stat("defense", 2, 1),
            lambda: menu_stack.pop()
        ]
    }
    menu_stack.append(menu)

def upgrade_stat(stat, value, cost):
    global TalentPoints
    if TalentPoints >= cost:
        setattr(player, stat, getattr(player, stat) + value)
        TalentPoints -= cost
        menu_stack.pop()
        # 更新最大血量
        if stat == "hp":
            player.max_hp = player.get_total_hp()

def open_equip_menu():
    options = []
    actions = []
    for slot in EQUIP_SLOTS:
        eq_list = [e for e in inventory if isinstance(e, Equipment) and e.slot == slot]
        names = [e.name for e in eq_list] or ["无可用装备"]
        options.append(f"{slot}: {'/'.join(names)}")
        actions.append(lambda s=slot, lst=eq_list: select_equip_for_slot(s, lst))
    options.append("返回")
    actions.append(lambda: menu_stack.pop())
    menu = {
        "title": "装备穿戴",
        "options": options,
        "action": actions
    }
    menu_stack.append(menu)

def select_equip_for_slot(slot, equip_list):
    if not equip_list:
        return
    options = [e.name for e in equip_list] + ["返回"]
    actions = []
    for e in equip_list:
        def action(eq=e):
            old = player.equipment[eq.slot]
            if old in inventory:
                inventory.remove(old)
            player.equipment[eq.slot] = eq
            inventory.remove(eq)
            menu_stack.pop()
        actions.append(action)
    actions.append(lambda: menu_stack.pop())
    menu = {
        "title": f"选择{slot}装备",
        "options": options,
        "action": actions
    }
    menu_stack.append(menu)

def open_item_menu():
    usable_items = [i for i in inventory if isinstance(i, Item)]
    if not usable_items:
        menu_stack.append({
            "title": "没有可使用道具",
            "options": ["返回"],
            "action": [lambda: menu_stack.pop()]
        })
        return
    options = [f"{i.name}" for i in usable_items] + ["返回"]
    actions = [lambda x=i: use_item(x) for i in usable_items] + [lambda: menu_stack.pop()]
    menu = {
        "title": "选择道具",
        "options": options,
        "action": actions
    }
    menu_stack.append(menu)

def use_item(item):
    msg = item.use(player)
    battle_log.append(msg)
    if item in inventory:
        inventory.remove(item)
    menu_stack.pop()

def open_combine_menu():
    floors = {}
    for e in inventory:
        if isinstance(e, Equipment):
            fl = e.floor
            if fl not in floors:
                floors[fl] = []
            floors[fl].append(e)
    candidates = [(f, es) for f, es in floors.items() if len(es) >= 3]
    if not candidates:
        menu_stack.append({
            "title": "无可合成装备",
            "options": ["返回"],
            "action": [lambda: menu_stack.pop()]
        })
        return
    options = [f"合成 {f+1}阶装备 ({len(es)}个{f}阶)" for f, es in candidates] + ["返回"]
    actions = []
    for f, es in candidates:
        def action(floor=f, equips=es):
            # 选3个相同楼层的装备
            selected = equips[:3]
            new_slot = random.choice(EQUIP_SLOTS)
            new_equip = Equipment(floor + 1, new_slot)
            for e in selected:
                inventory.remove(e)
            inventory.append(new_equip)
            menu_stack.pop()
        actions.append(action)
    actions.append(lambda: menu_stack.pop())
    menu = {
        "title": "装备合成",
        "options": options,
        "action": actions
    }
    menu_stack.append(menu)

# ------------------ 地图与游戏逻辑 ------------------
def spawn_monsters():
    global monsters
    monsters = []
    types = ["normal"]*7 + ["elite"]*2 + ["boss"]
    for mtype in types:
        m = Monster(FLOOR, mtype)
        # 避免重叠出生点或出口
        while (m.x == 0 and abs(m.y - GRID_HEIGHT//2) < 2) or \
              (m.x == GRID_WIDTH-1 and abs(m.y - GRID_HEIGHT//2) < 2):
            m.x = random.randint(0, GRID_WIDTH - 1)
            m.y = random.randint(0, GRID_HEIGHT - 1)
        monsters.append(m)

def reset_floor():
    global FLOOR, monsters
    player.x = 0
    player.y = GRID_HEIGHT // 2
    player.hp = player.get_total_hp()
    player.max_hp = player.get_total_hp()
    spawn_monsters()

def check_collision(rect1, rect2):
    overlap = rect1.clip(rect2).width * rect1.clip(rect2).height
    area1 = rect1.width * rect1.height
    return overlap / area1 > 0.2

# ------------------ 主循环 ------------------
def main():
    global GAME_STATE, FLOOR, battle_selected

    reset_floor()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if GAME_STATE == "map":
                    if event.key == pygame.K_i:
                        open_menu()
                elif GAME_STATE == "battle":
                    if event.key == pygame.K_UP:
                        battle_selected = (battle_selected - 1) % len(battle_options)
                    elif event.key == pygame.K_DOWN:
                        battle_selected = (battle_selected + 1) % len(battle_options)
                    elif event.key == pygame.K_RETURN:
                        option = battle_options[battle_selected]
                        if option == "战斗":
                            dmg = current_monster.take_damage(player.get_total_atk())
                            battle_log.append(f"造成 {dmg} 伤害")
                            if current_monster.dead:
                                battle_log.append("怪物被击败！")
                                pygame.time.wait(1000)
                                end_battle(victory=True)
                            else:
                                # 怪物攻击
                                pdmg = current_monster.attack(player)
                                battle_log.append(f"受到 {pdmg} 伤害")
                                if player.hp <= 0:
                                    battle_log.append("你被击败了……游戏结束")
                                    pygame.time.wait(2000)
                                    running = False
                        elif option == "物品":
                            open_item_menu()
                        elif option == "逃跑":
                            if random.random() < 0.5:
                                battle_log.append("逃跑成功！")
                                player.x = 0
                                player.y = GRID_HEIGHT // 2
                                end_battle()
                            else:
                                battle_log.append("逃跑失败！")
                                pdmg = current_monster.attack(player)
                                battle_log.append(f"受到 {pdmg} 伤害")
                                if player.hp <= 0:
                                    battle_log.append("你被击败了……游戏结束")
                                    pygame.time.wait(2000)
                                    running = False
                elif GAME_STATE == "menu":
                    if event.key == pygame.K_UP:
                        menu_stack[-1]["selected"] = (menu_stack[-1].get("selected", 0) - 1) % len(menu_stack[-1]["options"])
                    elif event.key == pygame.K_DOWN:
                        menu_stack[-1]["selected"] = (menu_stack[-1].get("selected", 0) + 1) % len(menu_stack[-1]["options"])
                    elif event.key == pygame.K_RETURN:
                        run_menu_action()
                    elif event.key == pygame.K_ESCAPE:
                        menu_stack.pop()
                        if not menu_stack:
                            GAME_STATE = "map"

        # 地图状态下的输入处理
        if GAME_STATE == "map":
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx = -1
            if keys[pygame.K_RIGHT]:
                dx = 1
            if keys[pygame.K_UP]:
                dy = -1
            if keys[pygame.K_DOWN]:
                dy = 1
            if dx != 0 or dy != 0:
                player.move(dx, dy)

            # 检测是否触碰怪物
            player_rect = pygame.Rect(player.x * GRID_SIZE, player.y * GRID_SIZE, player.width, player.height)
            for m in monsters:
                if m.dead:
                    continue
                m_rect = pygame.Rect(m.x * GRID_SIZE, m.y * GRID_SIZE, m.width, m.height)
                if check_collision(player_rect, m_rect):
                    start_battle(m)
                    break

            # 检测是否到达出口
            exit_x = GRID_WIDTH - 1
            exit_y = GRID_HEIGHT // 2
            if int(player.x) == exit_x and int(player.y) == exit_y:
                FLOOR += 1
                reset_floor()

        # 绘制
        screen.fill(WHITE)

        if GAME_STATE == "map":
            # 绘制入口和出口
            pygame.draw.rect(screen, GREEN, (0, (GRID_HEIGHT//2)*GRID_SIZE, GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BLUE, ((GRID_WIDTH-1)*GRID_SIZE, (GRID_HEIGHT//2)*GRID_SIZE, GRID_SIZE, GRID_SIZE))

            player.draw(screen)
            for m in monsters:
                if not m.dead:
                    m.draw(screen)

            # UI信息
            hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, BLACK)
            atk_text = font.render(f"ATK: {player.get_total_atk()}", True, BLACK)
            def_text = font.render(f"DEF: {player.get_total_def()}", True, BLACK)
            floor_text = font.render(f"楼层: {FLOOR}", True, BLACK)
            talent_text = font.render(f"天赋点: {TalentPoints}", True, BLACK)
            screen.blit(hp_text, (10, 10))
            screen.blit(atk_text, (10, 50))
            screen.blit(def_text, (10, 90))
            screen.blit(floor_text, (10, 130))
            screen.blit(talent_text, (10, 170))

        elif GAME_STATE == "battle":
            # 战斗界面：左上600x600动画区，底部200px选项
            pygame.draw.rect(screen, GRAY, (0, 0, 800, 600))  # 动画区
            pygame.draw.rect(screen, BLACK, (0, 600, 800, 200))  # 选项区

            # 显示怪物
            if current_monster:
                mx = 300
                my = 300
                screen.blit(current_monster.image, (mx, my))
                hp_bar = current_monster.hp / current_monster.max_hp
                pygame.draw.rect(screen, RED, (mx, my + 45, 40 * hp_bar, 5))

            # 绘制选项
            for i, opt in enumerate(battle_options):
                color = YELLOW if i == battle_selected else WHITE
                text = font.render(opt, True, color)
                screen.blit(text, (100 + i * 200, 650))

            # 日志
            for i, log in enumerate(battle_log[-5:]):
                log_surf = small_font.render(log, True, WHITE)
                screen.blit(log_surf, (100, 700 + i * 30))

        elif GAME_STATE == "menu":
            draw_menu()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()