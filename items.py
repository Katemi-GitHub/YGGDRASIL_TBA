class ygg_item():
    def __init__(self, name, lore, slots, rarity, recipe = None):
        self.name = name
        self.lore = lore
        self.recipe = recipe
        self.quantity = 1
        self.rarity = rarity
        self.slots = slots
        self.item_slots = []
    
    def add_item(self, item):
        if len(self.item_slots) >= self.slots:
            return False
        else:
            self.slots.append(item)
            return True
    
    def JSON_serialize(self):
        return {"name":self.name, "lore":self.lore, "quantity:":self.quantity, "item_slots":self.item_slots, "slots":self.slots, "rarity":self.rarity}
    
yggdrasil_itemList = [
    ygg_item("test", "Test item, you shouldn't have this", 0, 13, None)
    ]