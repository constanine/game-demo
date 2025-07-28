# game4/entities/item.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ..enums import ItemType


class Item:
    def __init__(self, item_type: ItemType):
        self.type = item_type
        self.name = item_type.value
        self.description = self._get_description()

    def _get_description(self):
        descriptions = {
            ItemType.APPLE: "恢复20点体力",
            ItemType.BREAD: "恢复当前体力最大值的20%",
            ItemType.WINE: "恢复20点技力"
        }
        return descriptions[self.type]