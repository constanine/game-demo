import pygame
import random
import sys
import math
from enum import Enum
from collections import defaultdict

# 初始化pygame
pygame.init()

# 设置中文字体
try:
    # 尝试使用系统中文字体
    font_path = "C:/Windows/Fonts/msyh.ttc"  # Windows微软雅黑
    FONT = pygame.font.Font(font_path, 24)
    SMALL_FONT = pygame.font.Font(font_path, 20)
    LARGE_FONT = pygame.font.Font(font_path, 36)
    BATTLE_FONT = pygame.font.Font(font_path, 20)  # 战斗界面专用字体
except:
    try:
        # 如果没有找到中文字体，使用系统默认字体
        FONT = pygame.font.SysFont('simhei', 24)  # 黑体
        SMALL_FONT = pygame.font.SysFont('simhei', 20)
        LARGE_FONT = pygame.font.SysFont('simhei', 36)
        BATTLE_FONT = pygame.font.SysFont('simhei', 20)
    except:
        # 最后回退到默认字体
        FONT = pygame.font.Font(None, 24)
        SMALL_FONT = pygame.font.Font(None, 20)
        LARGE_FONT = pygame.font.Font(None, 36)
        BATTLE_FONT = pygame.font.Font(None, 20)

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
GRID_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 40) // GRID_SIZE  # 为底部信息栏留出空间

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
LIGHT_GREEN = (144, 238, 144)
DARK_GREEN = (0, 100, 0)
LIGHT_YELLOW = (255, 255, 224)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)


# 游戏状态枚举
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    BATTLE = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
    SKILL_SELECT = 5  # 新增技能选择状态


# 装备类型枚举
class EquipmentType(Enum):
    HEAD = 1
    CHEST = 2
    LEFT_HAND = 3
    RIGHT_HAND = 4
    FEET = 5


# 怪物类型枚举
class MonsterType(Enum):
    NORMAL = 1
    ELITE = 2
    BOSS = 3


# 道具类型枚举
class ItemType(Enum):
    APPLE = 1
    BREAD = 2
    GRAPE = 3  # 新增葡萄道具


# BUFF类型枚举
class BuffType(Enum):
    STRONG = 1  # 强壮
    RECOVERY = 2  # 恢复


# DEBUFF类型枚举
class DebuffType(Enum):
    BLEED = 1  # 割裂
    POISON = 2  # 中毒


# 技能类型枚举
class SkillType(Enum):
    DOUBLE_ATTACK = 1  # 二连击
    BLEED_ATTACK = 2  # 割裂攻击
    BATTLE_CRY = 3  # 战吼
    BLESS = 4  # 祝福


# BUFF类
class Buff:
    def __init__(self, buff_type, duration=3):
        self.type = buff_type
        self.duration = duration
        self.name = self.get_name()
        self.description = self.get_description()

    def get_name(self):
        names = {
            BuffType.STRONG: "强壮",
            BuffType.RECOVERY: "恢复"
        }
        return names[self.type]

    def get_description(self):
        descriptions = {
            BuffType.STRONG: "攻击力增加30%",
            BuffType.RECOVERY: "每回合恢复20%体力"
        }
        return descriptions[self.type]

    def apply_effect(self, player):
        if self.type == BuffType.RECOVERY:
            heal_amount = int(player.get_total_health() * 0.2)
            player.current_health = min(player.get_total_health(), player.current_health + heal_amount)
            return f"恢复了{heal_amount}点体力"
        return ""


# DEBUFF类
class Debuff:
    def __init__(self, debuff_type, duration=3):
        self.type = debuff_type
        self.duration = duration
        self.name = self.get_name()
        self.description = self.get_description()

    def get_name(self):
        names = {
            DebuffType.BLEED: "割裂",
            DebuffType.POISON: "中毒"
        }
        return names[self.type]

    def get_description(self):
        descriptions = {
            DebuffType.BLEED: "每回合损失20点体力",
            DebuffType.POISON: "每回合损失10%最大体力"
        }
        return descriptions[self.type]

    def apply_effect(self, target):
        if self.type == DebuffType.BLEED:
            damage = min(20, target.current_health)
            target.current_health -= damage
            return f"受到{damage}点割裂伤害"
        elif self.type == DebuffType.POISON:
            damage = int(target.get_total_health() * 0.1)
            damage = min(damage, target.current_health)
            target.current_health -= damage
            return f"受到{damage}点毒素伤害"
        return ""


# 技能类
class Skill:
    def __init__(self, skill_type):
        self.type = skill_type
        self.name = self.get_name()
        self.description = self.get_description()
        self.cost = 5  # 消耗5点技力

    def get_name(self):
        names = {
            SkillType.DOUBLE_ATTACK: "二连击",
            SkillType.BLEED_ATTACK: "割裂",
            SkillType.BATTLE_CRY: "战吼",
            SkillType.BLESS: "祝福"
        }
        return names[self.type]

    def get_description(self):
        descriptions = {
            SkillType.DOUBLE_ATTACK: "连续攻击2次",
            SkillType.BLEED_ATTACK: "攻击并施加割裂效果",
            SkillType.BATTLE_CRY: "获得强壮BUFF",
            SkillType.BLESS: "获得恢复BUFF"
        }
        return descriptions[self.type]


# 装备类
class Equipment:
    def __init__(self, floor, eq_type):
        self.floor = floor
        self.type = eq_type
        self.name = self.generate_name()
        self.attack_bonus = 0
        self.defense_bonus = 0
        self.health_bonus = 0
        self.generate_stats()

    def generate_name(self):
        type_names = {
            EquipmentType.HEAD: "头盔",
            EquipmentType.CHEST: "护甲",
            EquipmentType.LEFT_HAND: "长剑",
            EquipmentType.RIGHT_HAND: "护盾",
            EquipmentType.FEET: "靴子"
        }
        return f"{self.floor}楼 {type_names[self.type]}"

    def generate_stats(self):
        if self.type == EquipmentType.HEAD:
            if random.random() < 0.5:
                self.defense_bonus = self.floor * random.randint(1, 3)
            else:
                self.health_bonus = self.floor * random.randint(5, 10)
        elif self.type == EquipmentType.CHEST:
            self.health_bonus = self.floor * random.randint(10, 20)
        elif self.type == EquipmentType.LEFT_HAND:
            self.attack_bonus = self.floor * random.randint(5, 10)
        elif self.type == EquipmentType.RIGHT_HAND:
            self.defense_bonus = self.floor * random.randint(2, 5)
        elif self.type == EquipmentType.FEET:
            self.defense_bonus = self.floor * random.randint(1, 3)


# 道具类
class Item:
    def __init__(self, item_type):
        self.type = item_type
        if item_type == ItemType.APPLE:
            self.name = "苹果"
        elif item_type == ItemType.BREAD:
            self.name = "面包"
        elif item_type == ItemType.GRAPE:
            self.name = "葡萄"


# 怪物类
class Monster:
    def __init__(self, monster_type, floor):
        self.type = monster_type
        self.floor = floor
        self.x = 0
        self.y = 0
        self.generate_stats()
        self.generate_size()
        self.debuffs = {}  # 存储DEBUFF
        self.current_health = self.max_health

    def generate_stats(self):
        if self.type == MonsterType.NORMAL:
            self.attack = 2 * self.floor
            self.max_health = 20 * self.floor
            self.defense = 1 * self.floor
        elif self.type == MonsterType.ELITE:
            self.attack = 5 * self.floor
            self.max_health = 50 * self.floor
            self.defense = 2 * self.floor
        elif self.type == MonsterType.BOSS:
            self.attack = 15 * self.floor
            self.max_health = 150 * self.floor
            self.defense = 5 * self.floor
        self.current_health = self.max_health

    def generate_size(self):
        if self.type == MonsterType.NORMAL:
            self.size = 40
        elif self.type == MonsterType.ELITE:
            self.size = 60
        elif self.type == MonsterType.BOSS:
            self.size = 80

    def add_debuff(self, debuff):
        self.debuffs[debuff.type] = debuff

    def update_buffs_debuffs(self):
        effects = []
        # 更新DEBUFF
        debuff_types_to_remove = []
        for debuff_type, debuff in self.debuffs.items():
            effect = debuff.apply_effect(self)
            if effect:
                effects.append(f"{self.type.name}受到{debuff.name}效果: {effect}")
            debuff.duration -= 1
            if debuff.duration <= 0:
                debuff_types_to_remove.append(debuff_type)

        # 移除过期的DEBUFF
        for debuff_type in debuff_types_to_remove:
            del self.debuffs[debuff_type]

        return effects


# 玩家类
class Player:
    def __init__(self):
        # 基础属性
        self.base_attack = 10
        self.base_health = 100
        self.base_defense = 5
        self.base_energy = 20  # 新增技力属性，默认20点
        self.current_health = self.base_health
        self.current_energy = self.base_energy
        self.talent_points = 0

        # 装备
        self.equipment = {
            EquipmentType.HEAD: None,
            EquipmentType.CHEST: None,
            EquipmentType.LEFT_HAND: None,
            EquipmentType.RIGHT_HAND: None,
            EquipmentType.FEET: None
        }

        # 道具
        self.inventory = []

        # BUFF和技能
        self.buffs = {}  # 存储BUFF
        self.skills = [
            Skill(SkillType.DOUBLE_ATTACK),
            Skill(SkillType.BLEED_ATTACK),
            Skill(SkillType.BATTLE_CRY),
            Skill(SkillType.BLESS)
        ]

        # 位置
        self.x = 0
        self.y = GRID_HEIGHT // 2
        self.floor = 1

    def get_total_attack(self):
        total = self.base_attack
        for eq in self.equipment.values():
            if eq:
                total += eq.attack_bonus
        # 应用强壮BUFF加成
        if BuffType.STRONG in self.buffs:
            total = int(total * 1.3)
        return total

    def get_total_defense(self):
        total = self.base_defense
        for eq in self.equipment.values():
            if eq:
                total += eq.defense_bonus
        return total

    def get_total_health(self):
        total = self.base_health
        for eq in self.equipment.values():
            if eq:
                total += eq.health_bonus
        return total

    def get_total_energy(self):
        total = self.base_energy
        return total

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        # 边界检查
        if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
            self.x = new_x
            self.y = new_y

    def use_item(self, item):
        if item.type == ItemType.APPLE:
            heal_amount = min(20, self.get_total_health() - self.current_health)
            self.current_health += heal_amount
            return f"使用了{item.name}，恢复了{heal_amount}点体力"
        elif item.type == ItemType.BREAD:
            max_health = self.get_total_health()
            heal_amount = min(int(max_health * 0.2), max_health - self.current_health)
            self.current_health += heal_amount
            return f"使用了{item.name}，恢复了{heal_amount}点体力"
        elif item.type == ItemType.GRAPE:
            energy_heal = min(20, self.get_total_energy() - self.current_energy)
            self.current_energy += energy_heal
            return f"使用了{item.name}，恢复了{energy_heal}点技力"
        return ""

    def add_buff(self, buff):
        self.buffs[buff.type] = buff

    def update_buffs_debuffs(self):
        effects = []
        # 更新BUFF
        buff_types_to_remove = []
        for buff_type, buff in self.buffs.items():
            effect = buff.apply_effect(self)
            if effect:
                effects.append(f"玩家受到{buff.name}效果: {effect}")
            buff.duration -= 1
            if buff.duration <= 0:
                buff_types_to_remove.append(buff_type)

        # 移除过期的BUFF
        for buff_type in buff_types_to_remove:
            del self.buffs[buff_type]

        return effects

    def use_skill(self, skill, target=None):
        if self.current_energy < skill.cost:
            return "技力不足！"

        self.current_energy -= skill.cost
        effects = []

        if skill.type == SkillType.DOUBLE_ATTACK:
            effects.append("使用了二连击！")
            # 二连击逻辑在战斗系统中处理
        elif skill.type == SkillType.BLEED_ATTACK:
            if target:
                target.add_debuff(Debuff(DebuffType.BLEED))
                effects.append(f"对{target.type.name}施加了割裂效果！")
        elif skill.type == SkillType.BATTLE_CRY:
            self.add_buff(Buff(BuffType.STRONG))
            effects.append("获得了强壮BUFF！")
        elif skill.type == SkillType.BLESS:
            self.add_buff(Buff(BuffType.RECOVERY))
            effects.append("获得了恢复BUFF！")

        return " ".join(effects)


# 战斗系统类
class BattleSystem:
    def __init__(self, player, monster):
        self.player = player
        self.monster = monster
        self.log_messages = []
        self.player_turn = True
        self.selected_skill = None

    def add_log(self, message):
        self.log_messages.append(message)
        if len(self.log_messages) > 10:  # 保留最多10条日志
            self.log_messages.pop(0)

    def player_attack(self):
        damage = max(1, self.player.get_total_attack() - self.monster.defense)
        self.monster.current_health -= damage
        self.add_log(f"玩家对{self.get_monster_name()}造成了{damage}点伤害")

        if self.monster.current_health <= 0:
            self.monster.current_health = 0
            self.add_log(f"击败了{self.get_monster_name()}！")
            return True
        return False

    def player_double_attack(self):
        # 二连击 - 造成两次攻击伤害
        for i in range(2):
            damage = max(1, self.player.get_total_attack() - self.monster.defense)
            self.monster.current_health -= damage
            self.add_log(f"玩家第{i + 1}次攻击对{self.get_monster_name()}造成了{damage}点伤害")

            if self.monster.current_health <= 0:
                self.monster.current_health = 0
                self.add_log(f"击败了{self.get_monster_name()}！")
                return True
        return False

    def get_monster_name(self):
        names = {
            MonsterType.NORMAL: "普通怪物",
            MonsterType.ELITE: "精英怪物",
            MonsterType.BOSS: "Boss怪物"
        }
        return names[self.monster.type]

    def monster_attack(self):
        damage = max(1, self.monster.attack - self.player.get_total_defense())
        self.player.current_health -= damage
        self.add_log(f"{self.get_monster_name()}对玩家造成了{damage}点伤害")

        if self.player.current_health <= 0:
            self.player.current_health = 0
            self.add_log("玩家被击败了！")
            return True
        return False


# 菜单系统类
class MenuSystem:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.font = LARGE_FONT
        self.small_font = FONT
        self.battle_font = BATTLE_FONT
        self.selected = 0
        self.menu_stack = []
        self.current_menu = "main"
        self.battle_menu_options = ["战斗", "技能", "物品", "逃跑"]
        self.skill_menu_options = [skill.name for skill in player.skills] + ["返回"]
        self.main_menu_options = ["能力编辑", "装备编辑", "装备合成", "道具使用", "返回"]
        self.stat_menu_options = ["增加5点攻击", "增加15点体力", "增加2点防御", "增加2点技力", "返回"]
        self.equipment_menu_options = ["头", "胸", "左手", "右手", "足", "返回"]
        self.selected_equipment_type = None
        self.battle_action = None
        self.show_message = None
        self.message_timer = 0
        self.temp_player = None
        self.skill_selected = False
        self.selected_skill_index = 0

    def draw_battle_menu(self, battle_system):
        # 绘制战斗动画区域
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, 600, 400))

        # 绘制战斗选项区域
        pygame.draw.rect(self.screen, GRAY, (0, 400, 600, 200))  # 增加到200px高度

        # 绘制选项（垂直排列）
        for i, option in enumerate(self.battle_menu_options):
            color = YELLOW if i == self.selected else WHITE
            text = self.battle_font.render(option, True, color)
            # 垂直排列，每个选项间隔50px
            self.screen.blit(text, (50, 420 + i * 50))
            # 添加三角标识
            if i == self.selected:
                triangle_points = [
                    (30, 420 + i * 50 + text.get_height() // 2),
                    (40, 420 + i * 50),
                    (40, 420 + i * 50 + text.get_height())
                ]
                pygame.draw.polygon(self.screen, YELLOW, triangle_points)

        # 绘制日志区域
        pygame.draw.rect(self.screen, BLACK, (0, 600, 600, 40))
        pygame.draw.rect(self.screen, WHITE, (0, 600, 600, 40), 2)

        # 绘制日志消息
        if battle_system.log_messages:
            latest_message = battle_system.log_messages[-1]  # 显示最新消息
            text = self.battle_font.render(latest_message, True, WHITE)
            self.screen.blit(text, (10, 610))

    def draw_skill_menu(self, battle_system):
        # 绘制技能选择菜单
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, 600, 400))

        # 绘制技能选项区域
        pygame.draw.rect(self.screen, GRAY, (0, 400, 600, 200))

        # 绘制标题
        title = self.battle_font.render("选择技能", True, WHITE)
        self.screen.blit(title, (50, 410))

        # 绘制技能选项（垂直排列）
        skill_options = self.skill_menu_options
        for i, option in enumerate(skill_options):
            color = YELLOW if i == self.selected else WHITE
            text = self.battle_font.render(option, True, color)
            self.screen.blit(text, (50, 450 + i * 40))
            # 添加三角标识
            if i == self.selected:
                triangle_points = [
                    (30, 450 + i * 40 + text.get_height() // 2),
                    (40, 450 + i * 40),
                    (40, 450 + i * 40 + text.get_height())
                ]
                pygame.draw.polygon(self.screen, YELLOW, triangle_points)

        # 绘制日志区域
        pygame.draw.rect(self.screen, BLACK, (0, 600, 600, 40))
        pygame.draw.rect(self.screen, WHITE, (0, 600, 600, 40), 2)

        # 绘制日志消息
        if battle_system.log_messages:
            latest_message = battle_system.log_messages[-1]
            text = self.battle_font.render(latest_message, True, WHITE)
            self.screen.blit(text, (10, 610))

    def draw_main_menu(self):
        # 绘制半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(128)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))

        # 绘制菜单
        menu_width = 300
        menu_height = len(self.main_menu_options) * 50 + 20
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, DARK_GREEN, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)

        # 绘制标题
        title = self.font.render("游戏菜单", True, YELLOW)
        self.screen.blit(title, (menu_x + (menu_width - title.get_width()) // 2, menu_y + 10))

        # 绘制选项
        for i, option in enumerate(self.main_menu_options):
            color = RED if (i == self.selected and option == "返回") else (YELLOW if i == self.selected else WHITE)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (menu_x + 20, menu_y + 50 + i * 50))

        # 绘制玩家属性
        attr_x = menu_x + menu_width + 20
        attr_y = menu_y
        attrs = [
            f"攻击力: {self.player.get_total_attack()}",
            f"体力: {self.player.current_health}/{self.player.get_total_health()}",
            f"防御力: {self.player.get_total_defense()}",
            f"技力: {self.player.current_energy}/{self.player.get_total_energy()}",
            f"天赋点: {self.player.talent_points}"
        ]

        for i, attr in enumerate(attrs):
            text = self.small_font.render(attr, True, WHITE)
            self.screen.blit(text, (attr_x, attr_y + i * 30))

    def draw_stat_menu(self):
        # 绘制半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(128)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))

        # 绘制菜单
        menu_width = 300
        menu_height = len(self.stat_menu_options) * 50 + 20
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, DARK_GREEN, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)

        # 绘制标题
        title = self.font.render("能力编辑", True, YELLOW)
        self.screen.blit(title, (menu_x + (menu_width - title.get_width()) // 2, menu_y + 10))

        # 绘制选项
        for i, option in enumerate(self.stat_menu_options):
            color = RED if (i == self.selected and option == "返回") else (YELLOW if i == self.selected else WHITE)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (menu_x + 20, menu_y + 50 + i * 50))

        # 绘制右侧属性预览
        preview_x = menu_x + menu_width + 20
        preview_y = menu_y

        # 创建临时玩家对象用于预览
        if self.temp_player is None:
            self.temp_player = Player()
            self.temp_player.base_attack = self.player.base_attack
            self.temp_player.base_health = self.player.base_health
            self.temp_player.base_defense = self.player.base_defense
            self.temp_player.base_energy = self.player.base_energy
            self.temp_player.talent_points = self.player.talent_points
            # 复制装备
            for eq_type, eq in self.player.equipment.items():
                self.temp_player.equipment[eq_type] = eq

        preview_title = self.font.render("属性预览", True, YELLOW)
        self.screen.blit(preview_title, (preview_x, preview_y))

        # 显示当前选择的属性变化
        if 0 <= self.selected < len(self.stat_menu_options) - 1:  # 不包括"返回"
            preview_attrs = [
                f"攻击力: {self.temp_player.get_total_attack()}",
                f"体力: {self.temp_player.get_total_health()}",
                f"防御力: {self.temp_player.get_total_defense()}",
                f"技力: {self.temp_player.get_total_energy()}",
                f"天赋点: {self.temp_player.talent_points}"
            ]

            for i, attr in enumerate(preview_attrs):
                text = self.small_font.render(attr, True, WHITE)
                self.screen.blit(text, (preview_x, preview_y + 40 + i * 30))

    def draw_equipment_menu(self):
        # 绘制半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(128)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))

        # 绘制左侧面板(装备部位选择)
        left_width = 200
        pygame.draw.rect(self.screen, DARK_GREEN, (50, 50, left_width, 300))
        pygame.draw.rect(self.screen, WHITE, (50, 50, left_width, 300), 2)

        title = self.font.render("装备部位", True, YELLOW)
        self.screen.blit(title, (50 + (left_width - title.get_width()) // 2, 60))

        for i, option in enumerate(self.equipment_menu_options):
            color = RED if (i == self.selected and option == "返回") else (YELLOW if i == self.selected else WHITE)
            text = self.font.render(option, True, color)
            self.screen.blit(text, (70, 100 + i * 40))

        # 绘制右侧面板(装备列表)
        if self.selected_equipment_type is not None and self.selected_equipment_type != "返回":
            right_width = 300
            pygame.draw.rect(self.screen, DARK_GREEN, (300, 50, right_width, 300))
            pygame.draw.rect(self.screen, WHITE, (300, 50, right_width, 300), 2)

            eq_type_map = {
                "头": EquipmentType.HEAD,
                "胸": EquipmentType.CHEST,
                "左手": EquipmentType.LEFT_HAND,
                "右手": EquipmentType.RIGHT_HAND,
                "足": EquipmentType.FEET
            }

            eq_type = eq_type_map[self.selected_equipment_type]
            title = self.font.render(f"{self.selected_equipment_type}部装备", True, YELLOW)
            self.screen.blit(title, (300 + (right_width - title.get_width()) // 2, 60))

            # 显示已装备的装备
            equipped = self.player.equipment[eq_type]
            if equipped:
                equip_text = self.small_font.render(f"已装备: {equipped.name}", True, CYAN)
                self.screen.blit(equip_text, (320, 100))

            # 显示可装备的装备列表
            available_eq = [eq for eq in self.player.inventory if isinstance(eq, Equipment) and eq.type == eq_type]
            for i, eq in enumerate(available_eq[:5]):  # 最多显示5个
                text = self.small_font.render(eq.name, True, YELLOW)
                self.screen.blit(text, (320, 140 + i * 30))

    def draw_item_menu(self):
        # 绘制半透明背景
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(128)
        s.fill(BLACK)
        self.screen.blit(s, (0, 0))

        # 绘制菜单
        menu_width = 400
        menu_height = 300
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2

        pygame.draw.rect(self.screen, DARK_GREEN, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height), 2)

        # 绘制标题
        title = self.font.render("道具使用", True, YELLOW)
        self.screen.blit(title, (menu_x + (menu_width - title.get_width()) // 2, menu_y + 10))

        # 显示道具列表
        items = [item for item in self.player.inventory if isinstance(item, Item)]
        if not items:
            no_item_text = self.font.render("没有道具", True, WHITE)
            self.screen.blit(no_item_text, (menu_x + (menu_width - no_item_text.get_width()) // 2, menu_y + 100))
        else:
            for i, item in enumerate(items[:8]):  # 最多显示8个道具
                color = YELLOW if i == self.selected else WHITE
                text = self.font.render(f"{item.name}", True, color)
                self.screen.blit(text, (menu_x + 20, menu_y + 60 + i * 30))

        # 返回选项
        return_color = RED if (len(items) <= self.selected or self.selected < 0) else WHITE
        return_text = self.font.render("返回", True, return_color)
        self.screen.blit(return_text, (menu_x + 20, menu_y + 60 + len(items[:8]) * 30))

    def draw_message(self, message):
        # 绘制消息提示框
        text = self.font.render(message, True, WHITE)
        text_width = text.get_width()
        text_height = text.get_height()

        box_width = text_width + 40
        box_height = text_height + 40
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2

        pygame.draw.rect(self.screen, DARK_GREEN, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, WHITE, (box_x, box_y, box_width, box_height), 2)
        self.screen.blit(text, (box_x + 20, box_y + 20))

    def handle_battle_input(self, keys):
        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.battle_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.battle_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            self.battle_action = self.battle_menu_options[self.selected]
            return self.battle_action
        return None

    def handle_skill_input(self, keys):
        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.skill_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.skill_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            if self.selected < len(self.player.skills):
                # 选择技能
                return self.player.skills[self.selected]
            else:
                # 返回
                return "返回"
        return None

    def handle_main_menu_input(self, keys):
        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.main_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.main_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            selected_option = self.main_menu_options[self.selected]
            if selected_option == "能力编辑":
                self.current_menu = "stat"
                self.selected = 0
                # 初始化临时玩家对象
                self.temp_player = Player()
                self.temp_player.base_attack = self.player.base_attack
                self.temp_player.base_health = self.player.base_health
                self.temp_player.base_defense = self.player.base_defense
                self.temp_player.base_energy = self.player.base_energy
                self.temp_player.talent_points = self.player.talent_points
                # 复制装备
                for eq_type, eq in self.player.equipment.items():
                    self.temp_player.equipment[eq_type] = eq
            elif selected_option == "装备编辑":
                self.current_menu = "equipment"
                self.selected = 0
                self.selected_equipment_type = None
            elif selected_option == "道具使用":
                self.current_menu = "item"
                self.selected = 0
            elif selected_option == "返回":
                return "close"
        return None

    def handle_stat_menu_input(self, keys):
        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.stat_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.stat_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            selected_option = self.stat_menu_options[self.selected]
            if selected_option == "增加5点攻击" and self.temp_player.talent_points > 0:
                self.temp_player.base_attack += 5
                self.temp_player.talent_points -= 1
                self.show_message = "攻击力增加了5点"
                self.message_timer = 180  # 3秒
            elif selected_option == "增加15点体力" and self.temp_player.talent_points > 0:
                self.temp_player.base_health += 15
                self.temp_player.talent_points -= 1
                self.show_message = "体力增加了15点"
                self.message_timer = 180
            elif selected_option == "增加2点防御" and self.temp_player.talent_points > 0:
                self.temp_player.base_defense += 2
                self.temp_player.talent_points -= 1
                self.show_message = "防御力增加了2点"
                self.message_timer = 180
            elif selected_option == "增加2点技力" and self.temp_player.talent_points > 0:
                self.temp_player.base_energy += 2
                self.temp_player.talent_points -= 1
                self.show_message = "技力增加了2点"
                self.message_timer = 180
            elif selected_option == "返回":
                # 确认属性更改
                if self.temp_player:
                    self.player.base_attack = self.temp_player.base_attack
                    self.player.base_health = self.temp_player.base_health
                    self.player.base_defense = self.temp_player.base_defense
                    self.player.base_energy = self.temp_player.base_energy
                    self.player.talent_points = self.temp_player.talent_points
                self.current_menu = "main"
                self.selected = 0
                self.temp_player = None
        return None

    def handle_equipment_menu_input(self, keys):
        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) % len(self.equipment_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) % len(self.equipment_menu_options)
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            selected_option = self.equipment_menu_options[self.selected]
            if selected_option == "返回":
                self.current_menu = "main"
                self.selected = 0
                self.selected_equipment_type = None
            else:
                self.selected_equipment_type = selected_option
        return None

    def handle_item_menu_input(self, keys):
        items = [item for item in self.player.inventory if isinstance(item, Item)]
        max_selection = len(items)

        if keys[pygame.K_UP]:
            self.selected = (self.selected - 1) if self.selected > 0 else max_selection
            pygame.time.wait(150)
        elif keys[pygame.K_DOWN]:
            self.selected = (self.selected + 1) if self.selected < max_selection else 0
            pygame.time.wait(150)
        elif keys[pygame.K_RETURN]:
            if self.selected < len(items):
                # 使用道具
                item = items[self.selected]
                result = self.player.use_item(item)
                if item in self.player.inventory:
                    self.player.inventory.remove(item)
                self.show_message = result
                self.message_timer = 180
                self.current_menu = "main"
                self.selected = 0
                return "used"
            else:
                # 返回
                self.current_menu = "main"
                self.selected = 0
        return None


# 主游戏类
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("冒险游戏")
        self.clock = pygame.time.Clock()
        self.font = FONT
        self.small_font = SMALL_FONT
        self.large_font = LARGE_FONT
        self.battle_font = BATTLE_FONT

        # 游戏对象
        self.player = Player()
        self.monsters = []
        self.battle_system = None
        self.menu_system = MenuSystem(self.screen, self.player)

        # 游戏状态
        self.state = GameState.PLAYING
        self.exit_locked = True
        self.log_messages = []

        # 初始化第一层
        self.generate_level()

    def generate_level(self):
        self.monsters = []
        self.player.current_health = self.player.get_total_health()
        self.player.current_energy = self.player.get_total_energy()  # 恢复技力

        # 生成怪物
        # 7个普通怪物
        for _ in range(7):
            monster = Monster(MonsterType.NORMAL, self.player.floor)
            self.place_monster(monster)
            self.monsters.append(monster)

        # 2个精英怪物
        for _ in range(2):
            monster = Monster(MonsterType.ELITE, self.player.floor)
            self.place_monster(monster)
            self.monsters.append(monster)

        # 1个Boss怪物
        boss = Monster(MonsterType.BOSS, self.player.floor)
        self.place_monster(boss)
        self.monsters.append(boss)

        self.exit_locked = True
        self.player.x = 0
        self.player.y = GRID_HEIGHT // 2

    def place_monster(self, monster):
        # 确保怪物不重叠
        while True:
            # 避开玩家初始位置和出口位置
            monster.x = random.randint(2, GRID_WIDTH - 3)
            monster.y = random.randint(1, GRID_HEIGHT - 2)

            # 检查是否与其他怪物重叠
            overlap = False
            for other in self.monsters:
                if (abs(monster.x - other.x) < 2 and abs(monster.y - other.y) < 2):
                    overlap = True
                    break

            if not overlap:
                break

    def check_collision(self, obj1_x, obj1_y, obj1_size, obj2_x, obj2_y, obj2_size):
        # 检查两个矩形是否碰撞（20%重合就算触碰）
        rect1 = pygame.Rect(obj1_x * GRID_SIZE, obj1_y * GRID_SIZE, obj1_size, obj1_size)
        rect2 = pygame.Rect(obj2_x * GRID_SIZE, obj2_y * GRID_SIZE, obj2_size, obj2_size)

        # 计算交集面积
        intersection = rect1.clip(rect2)
        if intersection.width * intersection.height > 0:
            # 计算最小矩形的面积
            min_area = min(obj1_size * obj1_size, obj2_size * obj2_size)
            # 如果交集面积大于最小面积的20%，则认为碰撞
            if intersection.width * intersection.height > min_area * 0.2:
                return True
        return False

    def check_monster_collisions(self):
        player_rect = pygame.Rect(self.player.x * GRID_SIZE, self.player.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

        for monster in self.monsters:
            monster_rect = pygame.Rect(monster.x * GRID_SIZE, monster.y * GRID_SIZE, monster.size, monster.size)

            if player_rect.colliderect(monster_rect):
                # 开始战斗
                self.battle_system = BattleSystem(self.player, monster)
                self.battle_system.add_log("玩家回合开始")
                self.state = GameState.BATTLE
                self.menu_system.selected = 0
                return monster
        return None

    def update_battle(self):
        if self.battle_system and self.menu_system.battle_action:
            action = self.menu_system.battle_action
            self.menu_system.battle_action = None

            if action == "战斗":
                # 玩家攻击
                defeated = self.battle_system.player_attack()
                if defeated:
                    # 战斗胜利
                    self.handle_battle_victory()
                    return

                # 更新BUFF/DEBUFF效果
                player_effects = self.player.update_buffs_debuffs()
                for effect in player_effects:
                    self.battle_system.add_log(effect)

                monster_effects = self.battle_system.monster.update_buffs_debuffs()
                for effect in monster_effects:
                    self.battle_system.add_log(effect)

                # 检查是否死亡
                if self.player.current_health <= 0:
                    self.state = GameState.GAME_OVER
                    return
                if self.battle_system.monster.current_health <= 0:
                    self.handle_battle_victory()
                    return

                # 怪物攻击
                self.battle_system.add_log("怪物回合开始")
                game_over = self.battle_system.monster_attack()
                if game_over:
                    self.state = GameState.GAME_OVER
                    return

                self.battle_system.add_log("玩家回合开始")
                self.menu_system.selected = 0

            elif action == "技能":
                # 进入技能选择状态
                self.state = GameState.SKILL_SELECT
                self.menu_system.selected = 0
                self.menu_system.current_menu = "skill"

            elif action == "物品":
                # 打开物品菜单
                items = [item for item in self.player.inventory if isinstance(item, Item)]
                if items:
                    # 使用第一个物品作为示例
                    item = items[0]
                    result = self.player.use_item(item)
                    if item in self.player.inventory:
                        self.player.inventory.remove(item)
                    self.battle_system.add_log(result)

                    # 更新BUFF/DEBUFF效果
                    player_effects = self.player.update_buffs_debuffs()
                    for effect in player_effects:
                        self.battle_system.add_log(effect)

                    monster_effects = self.battle_system.monster.update_buffs_debuffs()
                    for effect in monster_effects:
                        self.battle_system.add_log(effect)

                    # 检查是否死亡
                    if self.player.current_health <= 0:
                        self.state = GameState.GAME_OVER
                        return
                    if self.battle_system.monster.current_health <= 0:
                        self.handle_battle_victory()
                        return

                    # 怪物攻击
                    self.battle_system.add_log("怪物回合开始")
                    game_over = self.battle_system.monster_attack()
                    if game_over:
                        self.state = GameState.GAME_OVER
                        return

                    self.battle_system.add_log("玩家回合开始")
                else:
                    self.battle_system.add_log("没有可用的道具！")
                self.menu_system.selected = 0

            elif action == "逃跑":
                if random.random() < 0.5:
                    self.state = GameState.PLAYING
                    self.battle_system = None
                    self.player.x = 0  # 回到入口
                    self.player.y = GRID_HEIGHT // 2
                else:
                    self.battle_system.add_log("逃跑失败！")
                    # 怪物攻击
                    self.battle_system.add_log("怪物回合开始")
                    game_over = self.battle_system.monster_attack()
                    if game_over:
                        self.state = GameState.GAME_OVER
                        return
                    self.battle_system.add_log("玩家回合开始")
                    self.menu_system.selected = 0

    def update_skill_select(self):
        keys = pygame.key.get_pressed()
        result = self.menu_system.handle_skill_input(keys)

        if result:
            if result == "返回":
                # 返回战斗菜单
                self.state = GameState.BATTLE
                self.menu_system.current_menu = "battle"
                self.menu_system.selected = 0
            elif isinstance(result, Skill):
                # 使用选中的技能
                skill = result
                if self.player.current_energy < skill.cost:
                    self.battle_system.add_log("技力不足！")
                else:
                    self.battle_system.add_log(f"使用了{skill.name}！")

                    # 根据技能类型执行不同效果
                    if skill.type == SkillType.DOUBLE_ATTACK:
                        # 二连击 - 造成两次攻击伤害
                        for i in range(2):
                            damage = max(1, self.player.get_total_attack() - self.battle_system.monster.defense)
                            self.battle_system.monster.current_health -= damage
                            self.battle_system.add_log(f"第{i + 1}次攻击造成了{damage}点伤害")

                            if self.battle_system.monster.current_health <= 0:
                                self.battle_system.monster.current_health = 0
                                self.battle_system.add_log(f"击败了{self.battle_system.get_monster_name()}！")
                                self.handle_battle_victory()
                                return

                    elif skill.type == SkillType.BLEED_ATTACK:
                        # 割裂攻击 - 施加割裂DEBUFF
                        self.battle_system.monster.add_debuff(Debuff(DebuffType.BLEED))
                        self.battle_system.add_log(f"对{self.battle_system.get_monster_name()}施加了割裂效果！")
                        damage = max(1, self.player.get_total_attack() - self.battle_system.monster.defense)
                        self.battle_system.monster.current_health -= damage
                        self.battle_system.add_log(f"造成了{damage}点伤害")

                        if self.battle_system.monster.current_health <= 0:
                            self.battle_system.monster.current_health = 0
                            self.battle_system.add_log(f"击败了{self.battle_system.get_monster_name()}！")
                            self.handle_battle_victory()
                            return

                    elif skill.type == SkillType.BATTLE_CRY:
                        # 战吼 - 获得强壮BUFF
                        self.player.add_buff(Buff(BuffType.STRONG))
                        self.battle_system.add_log("获得了强壮BUFF！")

                    elif skill.type == SkillType.BLESS:
                        # 祝福 - 获得恢复BUFF
                        self.player.add_buff(Buff(BuffType.RECOVERY))
                        self.battle_system.add_log("获得了恢复BUFF！")

                    # 消耗技力
                    self.player.current_energy -= skill.cost

                    # 更新BUFF/DEBUFF效果
                    player_effects = self.player.update_buffs_debuffs()
                    for effect in player_effects:
                        self.battle_system.add_log(effect)

                    monster_effects = self.battle_system.monster.update_buffs_debuffs()
                    for effect in monster_effects:
                        self.battle_system.add_log(effect)

                    # 检查是否死亡
                    if self.player.current_health <= 0:
                        self.state = GameState.GAME_OVER
                        return
                    if self.battle_system.monster.current_health <= 0:
                        self.handle_battle_victory()
                        return

                    # 怪物攻击
                    self.battle_system.add_log("怪物回合开始")
                    game_over = self.battle_system.monster_attack()
                    if game_over:
                        self.state = GameState.GAME_OVER
                        return

                    self.battle_system.add_log("玩家回合开始")

                # 返回战斗菜单
                self.state = GameState.BATTLE
                self.menu_system.current_menu = "battle"
                self.menu_system.selected = 0

    def handle_battle_victory(self):
        # 移除被击败的怪物
        self.monsters.remove(self.battle_system.monster)

        # 给予奖励
        self.player.talent_points += 1

        # 掉落物品
        monster = self.battle_system.monster
        if monster.type == MonsterType.NORMAL:
            if random.random() < 0.8:
                self.player.inventory.append(Item(ItemType.APPLE))
            if random.random() < 0.2:
                eq_type = random.choice(list(EquipmentType))
                self.player.inventory.append(Equipment(monster.floor, eq_type))
            # 50%概率掉落葡萄
            if random.random() < 0.5:
                self.player.inventory.append(Item(ItemType.GRAPE))
        elif monster.type == MonsterType.ELITE:
            self.player.inventory.append(Item(ItemType.BREAD))
            eq_type = random.choice(list(EquipmentType))
            self.player.inventory.append(Equipment(monster.floor, eq_type))
            # 100%掉落葡萄
            self.player.inventory.append(Item(ItemType.GRAPE))
        elif monster.type == MonsterType.BOSS:
            self.player.inventory.append(Item(ItemType.BREAD))
            # 给予两个当前楼层装备
            for _ in range(2):
                eq_type = random.choice(list(EquipmentType))
                self.player.inventory.append(Equipment(monster.floor, eq_type))
            # 50%概率给予下一层装备
            if random.random() < 0.5:
                eq_type = random.choice(list(EquipmentType))
                self.player.inventory.append(Equipment(monster.floor + 1, eq_type))
            # 100%掉落葡萄
            self.player.inventory.append(Item(ItemType.GRAPE))

        self.state = GameState.PLAYING
        self.battle_system = None

        # 检查是否所有怪物都被击败
        if len(self.monsters) == 0:
            self.exit_locked = False

    def check_exit_collision(self):
        exit_x = GRID_WIDTH - 1
        exit_y = GRID_HEIGHT // 2

        if not self.exit_locked:
            if (abs(self.player.x - exit_x) < 1 and abs(self.player.y - exit_y) < 1):
                # 进入下一层
                self.player.floor += 1
                self.generate_level()
                return True
        return False

    def update(self):
        if self.state == GameState.PLAYING:
            keys = pygame.key.get_pressed()

            # 玩家移动
            if keys[pygame.K_LEFT]:
                self.player.move(-0.5, 0)
                pygame.time.wait(50)
            elif keys[pygame.K_RIGHT]:
                self.player.move(0.5, 0)
                pygame.time.wait(50)
            elif keys[pygame.K_UP]:
                self.player.move(0, -0.5)
                pygame.time.wait(50)
            elif keys[pygame.K_DOWN]:
                self.player.move(0, 0.5)
                pygame.time.wait(50)

            # 检查碰撞
            self.check_monster_collisions()
            self.check_exit_collision()

            # 检查是否所有怪物都被击败
            if len(self.monsters) == 0:
                self.exit_locked = False
        elif self.state == GameState.SKILL_SELECT:
            self.update_skill_select()

    def draw(self):
        # 绘制背景
        if self.state == GameState.GAME_OVER:
            self.screen.fill(BLACK)
        else:
            self.screen.fill(LIGHT_GREEN)

        if self.state == GameState.PLAYING:
            # 绘制网格
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(self.screen, DARK_GREEN, (x, 0), (x, SCREEN_HEIGHT - 40))
            for y in range(0, SCREEN_HEIGHT - 40, GRID_SIZE):
                pygame.draw.line(self.screen, DARK_GREEN, (0, y), (SCREEN_WIDTH, y))

            # 绘制入口（黑色）
            pygame.draw.rect(self.screen, BLACK, (0, (GRID_HEIGHT // 2) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

            # 绘制出口
            exit_color = GRAY if self.exit_locked else YELLOW
            pygame.draw.rect(self.screen, exit_color,
                             ((GRID_WIDTH - 1) * GRID_SIZE, (GRID_HEIGHT // 2) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

            # 绘制玩家
            pygame.draw.rect(self.screen, BLUE,
                             (self.player.x * GRID_SIZE, self.player.y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

            # 绘制怪物
            for monster in self.monsters:
                color = RED if monster.type == MonsterType.NORMAL else (
                    ORANGE if monster.type == MonsterType.ELITE else PURPLE)
                pygame.draw.rect(self.screen, color,
                                 (monster.x * GRID_SIZE, monster.y * GRID_SIZE, monster.size, monster.size))

            # 绘制底部信息栏
            pygame.draw.rect(self.screen, BLACK, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
            pygame.draw.line(self.screen, WHITE, (0, SCREEN_HEIGHT - 40), (SCREEN_WIDTH, SCREEN_HEIGHT - 40), 2)

            # 显示玩家信息
            info_text = f"楼层: {self.player.floor} | 生命: {self.player.current_health}/{self.player.get_total_health()} | 攻击: {self.player.get_total_attack()} | 防御: {self.player.get_total_defense()} | 技力: {self.player.current_energy}/{self.player.get_total_energy()}"
            text = self.font.render(info_text, True, WHITE)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 30))

            # 显示出口状态
            exit_status = "出口: 锁定" if self.exit_locked else "出口: 开放"
            status_text = self.font.render(exit_status, True, YELLOW if not self.exit_locked else GRAY)
            self.screen.blit(status_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30))

            # 在左上角显示当前楼层
            floor_text = self.large_font.render(f"第 {self.player.floor} 层", True, WHITE)
            self.screen.blit(floor_text, (10, 10))

        elif self.state == GameState.BATTLE:
            self.draw_battle_interface()

        elif self.state == GameState.SKILL_SELECT:
            self.menu_system.draw_skill_menu(self.battle_system)

        elif self.state == GameState.GAME_OVER:
            # 显示游戏结束信息
            game_over_text = self.large_font.render("游戏结束", True, RED)
            self.screen.blit(game_over_text,
                             (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

            restart_text = self.font.render("按R键重新开始", True, WHITE)
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # 绘制菜单
        if self.state == GameState.MENU:
            if self.menu_system.current_menu == "main":
                self.menu_system.draw_main_menu()
            elif self.menu_system.current_menu == "stat":
                self.menu_system.draw_stat_menu()
            elif self.menu_system.current_menu == "equipment":
                self.menu_system.draw_equipment_menu()
            elif self.menu_system.current_menu == "item":
                self.menu_system.draw_item_menu()

        # 绘制消息
        if self.menu_system.show_message and self.menu_system.message_timer > 0:
            self.menu_system.draw_message(self.menu_system.show_message)

    def draw_battle_interface(self):
        # 左侧区域（600px × 640px）
        left_width = 600
        left_height = 640
        left_x = 0
        left_y = 0

        # 右侧区域（200px × 640px）
        right_width = 200
        right_height = 640
        right_x = 600
        right_y = 0

        # 左侧区域：战斗动画区（600px × 400px）
        battle_animation_area = pygame.Rect(left_x, left_y, left_width, 400)
        pygame.draw.rect(self.screen, BLACK, battle_animation_area)
        pygame.draw.rect(self.screen, WHITE, battle_animation_area, 2)

        # 显示怪物图形和血量
        monster = self.battle_system.monster
        monster_x = left_x + (left_width - monster.size) // 2
        monster_y = left_y + (400 - monster.size) // 2
        pygame.draw.rect(self.screen, RED, (monster_x, monster_y, monster.size, monster.size))  # 怪物图形

        # 显示怪物血量（使用较小字体）
        health_text = self.battle_font.render(f"血量: {monster.current_health}/{monster.max_health}", True, WHITE)
        self.screen.blit(health_text, (left_x + (left_width - health_text.get_width()) // 2, left_y + 400 - 30))

        # 显示怪物DEBUFF（使用较小字体）
        if monster.debuffs:
            debuff_y = left_y + 10
            for debuff in monster.debuffs.values():
                debuff_text = self.battle_font.render(f"{debuff.name}({debuff.duration})", True, RED)
                self.screen.blit(debuff_text, (left_x + 10, debuff_y))
                debuff_y += 25

        # 显示怪物个数（如果有多个怪物）（使用较小字体）
        monsters_count = len([m for m in self.monsters if m.current_health > 0])
        if monsters_count > 1:
            count_text = self.battle_font.render(f"当前有 {monsters_count} 只怪物", True, WHITE)
            self.screen.blit(count_text, (left_x + (left_width - count_text.get_width()) // 2, left_y + 10))

        # 左侧区域：玩家属性区（600px × 200px）（使用较小字体）
        player_stats_area = pygame.Rect(left_x, left_y + 400, left_width, 200)
        pygame.draw.rect(self.screen, GRAY, player_stats_area)
        pygame.draw.rect(self.screen, WHITE, player_stats_area, 2)

        # 显示玩家属性（使用较小字体）
        player_stats = [
            f"剩余体力: {self.player.current_health}/{self.player.get_total_health()}",
            f"攻击力: {self.player.get_total_attack()}",
            f"防御力: {self.player.get_total_defense()}",
            f"技力: {self.player.current_energy}/{self.player.get_total_energy()}"
        ]
        for i, stat in enumerate(player_stats):
            text = self.battle_font.render(stat, True, WHITE)
            self.screen.blit(text, (left_x + 20, left_y + 420 + i * 40))  # 调整行间距

        # 显示玩家BUFF（使用较小字体）
        if self.player.buffs:
            buff_y = left_y + 420
            for buff in self.player.buffs.values():
                buff_text = self.battle_font.render(f"{buff.name}({buff.duration})", True, GREEN)
                self.screen.blit(buff_text, (left_x + 300, buff_y))
                buff_y += 25

        # 左侧区域：战斗选项区（600px × 200px）（垂直排列选项）
        battle_options_area = pygame.Rect(left_x, left_y + 600, left_width, 40)
        pygame.draw.rect(self.screen, DARK_GRAY, battle_options_area)
        pygame.draw.rect(self.screen, WHITE, battle_options_area, 2)

        # 显示战斗选项（垂直排列）
        options = ["战斗", "技能", "物品", "逃跑"]
        for i, option in enumerate(options):
            color = RED if i == self.menu_system.selected else WHITE
            text = self.battle_font.render(option, True, color)
            # 垂直排列，每个选项间隔50px
            self.screen.blit(text, (left_x + 50, left_y + 610 + i * 50))
            # 添加三角标识
            if i == self.menu_system.selected:
                triangle_points = [
                    (left_x + 30, left_y + 610 + i * 50 + text.get_height() // 2),
                    (left_x + 40, left_y + 610 + i * 50),
                    (left_x + 40, left_y + 610 + i * 50 + text.get_height())
                ]
                pygame.draw.polygon(self.screen, YELLOW, triangle_points)

        # 右侧区域：日志区（200px × 640px）
        log_area = pygame.Rect(right_x, right_y, right_width, right_height)
        pygame.draw.rect(self.screen, LIGHT_GREEN, log_area)
        pygame.draw.rect(self.screen, WHITE, log_area, 2)

        # 显示战斗日志（最新消息在最上方）（使用较小字体）
        log_messages = self.battle_system.log_messages[::-1]  # 反转列表，最新消息在最上方
        for i, message in enumerate(log_messages[:10]):  # 最多显示10条日志
            text = self.battle_font.render(message, True, BLACK)
            self.screen.blit(text, (right_x + 10, right_y + 10 + i * 30))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_i:
                        self.state = GameState.MENU
                        self.menu_system.selected = 0
                        self.menu_system.current_menu = "main"

            elif self.state == GameState.MENU:
                keys = pygame.key.get_pressed()
                if self.menu_system.current_menu == "main":
                    result = self.menu_system.handle_main_menu_input(keys)
                    if result == "close":
                        self.state = GameState.PLAYING
                elif self.menu_system.current_menu == "stat":
                    self.menu_system.handle_stat_menu_input(keys)
                elif self.menu_system.current_menu == "equipment":
                    self.menu_system.handle_equipment_menu_input(keys)
                elif self.menu_system.current_menu == "item":
                    self.menu_system.handle_item_menu_input(keys)

            elif self.state == GameState.BATTLE:
                keys = pygame.key.get_pressed()
                self.menu_system.handle_battle_input(keys)

            elif self.state == GameState.SKILL_SELECT:
                # 技能选择状态已经在update_skill_select中处理
                pass

            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # 重新开始游戏
                        self.__init__()

        # 更新消息计时器
        if self.menu_system.message_timer > 0:
            self.menu_system.message_timer -= 1
        else:
            self.menu_system.show_message = None

        return True

    def run(self):
        running = True
        while running:
            running = self.handle_events()

            if self.state == GameState.PLAYING:
                self.update()
            elif self.state == GameState.BATTLE:
                self.update_battle()
            elif self.state == GameState.SKILL_SELECT:
                self.update_skill_select()

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()