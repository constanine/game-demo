# item.py
class Item:
    def __init__(self, name, item_type, effect_value=0):
        self.name = name
        self.type = item_type  # "apple", "bread", "equipment"
        self.effect_value = effect_value
        self.equipment = None  # 如果是装备类型，存储装备对象

    def use(self, player):
        """使用道具，返回使用效果描述"""
        if self.type == "apple":
            # 恢复20点体力，不超过最大值
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + 20)
            restored = player.hp - old_hp
            return f"恢复了{restored}点体力"
        elif self.type == "bread":
            # 恢复当前体力最大值的20%，不超过最大值
            restore_amount = int(player.max_hp * 0.2)
            old_hp = player.hp
            player.hp = min(player.max_hp, player.hp + restore_amount)
            restored = player.hp - old_hp
            return f"恢复了{int(player.max_hp * 0.2)}点体力({int(20)}%)"
        elif self.type == "equipment":
            # 装备物品需要特殊处理
            return None
        return None