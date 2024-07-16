class ygg_item():
    def __init__(self, name, lore, rarity, recipe=None, stats=None, item_type=None):
        self.name = name
        self.lore = lore
        self.recipe = recipe
        self.quantity = 1
        self.rarity = rarity
        self.stats = stats if stats else {}  # Dictionary to hold stat modifications
        self.item_type = item_type  # Type of item: "weapon", "armor", or None for other items

    def JSON_serialize(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "item_slots": [item.JSON_serialize() for item in self.item_slots]
        }

yggdrasil_itemList = [
    ygg_item("test", "Test item, you shouldn't have this", 13, None),
    ygg_item("stick", "Just a stick...", 0, None),
    ygg_item("leather", "It's just leather, nothing special", 0, None),
    ygg_item("sword", "A basic sword.", 1, None, {"P_ATK": 5}, "weapon"),
    ygg_item("helmet", "A basic helmet.", 1, None, {"P_DEF": 3}, "armor")
]
