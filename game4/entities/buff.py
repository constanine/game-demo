# game4/entities/buff.py
from enum import Enum

class BuffType(Enum):
    STRENGTH = "强壮"      # 增加攻击 (通常是 BUFF)
    REGENERATION = "恢复"  # 每回合回血 (通常是 BUFF)
    BLEED = "割裂"        # 每回合掉血 (通常是 DEBUFF)
    POISON = "中毒"        # 按比例掉血 (通常是 DEBUFF)

class Buff:
    def __init__(self, buff_type: BuffType, value: int, duration: int):
        self.buff_type = buff_type
        self.value = value
        self.duration = duration
        self.name = buff_type.value

# DEBUFF 本质上是具有负面效果的 Buff 实例。
# 例如：Buff(BuffType.BLEED, 5, 3) 就是一个 DEBUFF。
# 可以根据 buff_type 来区分是 BUFF 还是 DEBUFF。