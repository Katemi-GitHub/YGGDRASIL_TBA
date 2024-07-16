# project started 12/02/2023

import base64
code = base64.b64encode(b"""

import tkinter as tk
import sys
import json
import time
import random
from items import *
from room import *

class Skill:
    def __init__(self, name, damage, mana_cost, effect=None):
        self.name = name
        self.damage = damage
        self.mana_cost = mana_cost
        self.effect = effect  # Additional effects like stun, heal, etc.

    def use(self, user, target):
        if user.mp >= self.mana_cost:
            user.mp -= self.mana_cost
            target.hp -= self.damage
            tgaPrint(0, 0, f'{user.name} uses {self.name} on {target.name} for {self.damage} damage.')
            if self.effect:
                self.apply_effect(target)
        else:
            tgaPrint(0, 0, f'Not enough MP to use {self.name}')

    def apply_effect(self, target):
        # Placeholder for effects like stun, burn, etc.
        if self.effect == 'stun':
            target.stunned = True
            tgaPrint(0, 0, f'{target.name} is stunned!')

class Entity:
    def __init__(self, name, level, race, x=0, y=0):
        self.name = name
        self.level = level
        self.xp = 0
        self.job_points = level
        self.race = race
        self.base_stats = {
            'HP': 10,
            'MP': 10,
            'P_ATK': 10,
            'P_DEF': 10,
            'M_ATK': 10,
            'M_DEF': 10,
            'RES': 10,
        }
        self.x = x
        self.y = y
        self.jobs = []
        self.racial_jobs = []
        self.inventory = []  # Initialize empty inventory for the Entity
        self.weapon = None  # Slot for weapon
        self.armor = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
        }
        self.stats = self.calculate_stats()
        self.hp = self.calculate_hp()
        self.mp = self.calculate_mp()
        self.skills = []
        self.isStunned = False
    
    def learn_skill(self, skill):
        self.skills.append(skill)

    def show_skills(self):
        tgaPrint(0, f"{self.name}'s Skills:")
        for skill in self.skills:
            tgaPrint(0, f' - {skill.name}: {skill.damage} damage, {skill.mana_cost} MP')

    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
            'xp': self.xp,
            'job_points': self.job_points,
            'race': self.race,
            'base_stats': self.base_stats,
            'x': self.x,
            'y': self.y,
            'jobs': [job.to_dict() for job in self.jobs],
            'racial_jobs': [job.to_dict() for job in self.racial_jobs],
            'inventory': [item.JSON_serialize() for item in self.inventory],
            'weapon': self.weapon.JSON_serialize() if self.weapon else None,
            'armor': {slot: piece.JSON_serialize() if piece else None for slot, piece in self.armor.items()},
            'stats': self.stats,
            'hp': self.hp,
            'mp': self.mp,
            'skills': [skill.to_dict() for skill in self.skills]  # Add this line
        }

    @classmethod
    def from_dict(cls, data):
        entity = cls(data['name'], data['level'], data['race'], data['x'], data['y'])
        entity.xp = data['xp']
        entity.job_points = data['job_points']
        entity.base_stats = data['base_stats']
        entity.jobs = [Job.from_dict(job) for job in data['jobs']]
        entity.racial_jobs = [Job.from_dict(job) for job in data['racial_jobs']]
        entity.inventory = [ygg_item(**item) for item in data['inventory']]
        entity.weapon = ygg_item(**data['weapon']) if data['weapon'] else None
        entity.armor = {slot: ygg_item(**piece) if piece else None for slot, piece in data['armor'].items()}
        entity.stats = data['stats']
        entity.hp = data['hp']
        entity.mp = data['mp']
        entity.skills = [Skill.from_dict(skill) for skill in data['skills']]  # Add this line
        return entity

    def add_job(self, job):
        if self.job_points > 0:
            self.jobs.append(job)
            self.job_points -= 1

    def add_racial_job(self, racial_job):
        if self.job_points > 0:
            self.racial_jobs.append(racial_job)
            self.job_points -= 1

    def level_up_job(self, job_name):
        if self.job_points > 0:
            for job in self.jobs:
                if job.name == job_name:
                    job.level_up()
                    self.job_points -= 1
                    break
            else:  # If job not found in jobs list, check racial jobs
                for racial_job in self.racial_jobs:
                    if racial_job.name == job_name:
                        racial_job.level_up()
                        self.job_points -= 1
                        break
                else:
                    tgaPrint(0, f'Job {job_name} not found.')
                    return
            self.stats = self.calculate_stats()
            self.hp = self.calculate_hp()
            self.mp = self.calculate_mp()
        else:
            tgaPrint(0, f'Not Enough Job Points.')

    def calculate_growth_rates(self):
        growth_rates = {
            'HP': 0.25,
            'MP': 0.25,
            'P_ATK': 0.25,
            'P_DEF': 0.25,
            'M_ATK': 0.25,
            'M_DEF': 0.25,
            'RES': 0.25,
        }
        for job in self.jobs:
            for stat, base_rate in job.base_growth_rates.items():
                growth_rates[stat] += base_rate
        for racial_job in self.racial_jobs:
            for stat, base_rate in racial_job.base_growth_rates.items():
                growth_rates[stat] += base_rate
        return growth_rates

    def calculate_stat(self, base, level, rate):
        return base + int(level * rate)

    def calculate_stats(self):
        growth_rates = self.calculate_growth_rates()
        stats = {stat: self.calculate_stat(base, self.level, growth_rates.get(stat, 0)) for stat, base in self.base_stats.items()}
        # Adjust stats based on equipped items
        if self.weapon:
            for stat, value in self.weapon.stats.items():
                stats[stat] += value
        for armor_piece in self.armor.values():
            if armor_piece:
                for stat, value in armor_piece.stats.items():
                    stats[stat] += value
        return stats

    def calc_level(self):
        while self.xp >= 10 * (self.level ** 2):
            self.xp -= 10 * (self.level ** 2)
            self.level += 1
            self.update_growth_rates()
            self.stats = self.calculate_stats()
            self.hp = self.calculate_hp()
            self.mp = self.calculate_mp()

    def gain_xp(self, amount):
        self.xp += amount
        self.calc_level()

    def calculate_hp(self):
        base_hp = 10
        return base_hp + self.stats['HP'] * self.level

    def calculate_mp(self):
        base_mp = 10
        return base_mp + self.stats['MP'] * self.level

    def print_stats(self):
        tgaPrint(0, f'Name: {self.name}')
        tgaPrint(0, f'Level: {self.level}')
        for stat, value in self.stats.items():
            tgaPrint(0, f'{stat}: {value}')
        tgaPrint(0, f'Current HP: {self.hp}')
        tgaPrint(0, f'Current MP: {self.mp}')
        tgaPrint(0, 'Jobs:')
        for job in self.jobs:
            job.print_info()
        tgaPrint(0, 'Racial Jobs:')
        for racial_job in self.racial_jobs:
            racial_job.print_info()

    def add_to_inventory(self, item):
        self.inventory.append(item)
        tgaPrint(0, f'Added {item.name} to inventory.')

    def remove_from_inventory(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            tgaPrint(0, f'Removed {item.name} from inventory.')
        else:
            tgaPrint(0, f'{item.name} is not in inventory.')

    def list_inventory(self):
        tgaPrint(0, f'Inventory for {self.name}:')
        for item in self.inventory:
            tgaPrint(0, f'{item.name}')

    def equip_weapon(self, weapon):
        if isinstance(weapon, ygg_item) and weapon.item_type == 'weapon':
            self.weapon = weapon
            tgaPrint(0, f'Equipped {weapon.name} as weapon.')
            self.stats = self.calculate_stats()  # Update stats
        else:
            tgaPrint(0, f'{weapon.name} is not a valid weapon.')

    def equip_armor(self, armor_piece, slot):
        if isinstance(armor_piece, ygg_item) and armor_piece.item_type == 'armor' and slot in self.armor:
            self.armor[slot] = armor_piece
            tgaPrint(0, f'Equipped {armor_piece.name} as {slot} armor.')
            self.stats = self.calculate_stats()  # Update stats
        else:
            tgaPrint(0, f'{armor_piece.name} is not a valid armor piece for slot {slot}.')

    def unequip_weapon(self):
        if self.weapon:
            tgaPrint(0, f'Unequipped {self.weapon.name} from weapon slot.')
            self.weapon = None
            self.stats = self.calculate_stats()  # Update stats
        else:
            tgaPrint(0, 'No weapon to unequip.')

    def unequip_armor(self, slot):
        if self.armor[slot]:
            tgaPrint(0, f'Unequipped {self.armor[slot].name} from {slot} slot.')
            self.armor[slot] = None
            self.stats = self.calculate_stats()  # Update stats
        else:
            tgaPrint(0, f'No armor in {slot} slot to unequip.')

# Example usage
class Job:
    def __init__(self, name, rarity, growth_rates):
        self.name = name
        self.rarity = rarity
        self.level = 1
        self.max_level = self.set_max_level()
        self.temp_growth_rates = growth_rates
        self.base_growth_rates = self.update_job_growth_rate()

    def set_max_level(self):
        if self.rarity == 'base':
            return 15
        elif self.rarity == 'high':
            return 10
        elif self.rarity == 'rare':
            return 5
        else:
            raise ValueError('Invalid rarity specified')

    def level_up(self):
        if self.level < self.max_level:
            self.level += 1
            self.base_growth_rates = self.update_job_growth_rate()
        else:
            tgaPrint(0, f'{self.name} has reached its max level.')

    def update_job_growth_rate(self):
        growth_rates = {
            'HP': 0,
            'MP': 0,
            'P_ATK': 0,
            'P_DEF': 0,
            'M_ATK': 0,
            'M_DEF': 0,
            'RES': 0,
        }
        for stat, rate in self.temp_growth_rates.items():
            growth_rates[stat] = rate / self.max_level * self.level
        
        return growth_rates

    def print_info(self):
        tgaPrint(0, f'Job: {self.name} (Rarity: {self.rarity}, Level: {self.level}/{self.max_level})')
        tgaPrint(0, f'Base Growth Rates: {self.base_growth_rates}')

class RacialJob(Job):
    pass

# Load and read player save and settings
def save_files():
    save['player'] = player.to_dict()
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4, separators=(',', ':'))
    with open('save.json', 'w') as file:
        json.dump(save, file, indent=4, separators=(',', ':'))

def load_files():
    try:
        with open('settings.json', 'r') as file:
            settings = json.load(file)
    except json.decoder.JSONDecodeError:
        with open('settings.json', 'w') as file:
            json.dump({}, file)
            settings = json.load(file)

    try:
        with open('save.json', 'r') as file:
            save = json.load(file)
    except json.decoder.JSONDecodeError:
        with open('save.json', 'w') as file:
            json.dump({}, file)
            save = json.load(file)

    if 'player' in save:
        global player
        player = Entity.from_dict(save['player'])
    else:
        player = None

    return settings, save

settings, save = load_files()

running = True
def on_close():
    global running, user_last_input
    running = False
    user_last_input.set(1)

# Window initializer
version = 'Alpha 0.6'
name = 'YGGDRASIL'
sizeWnd = '800x600'

frame = tk.Tk()
frame.protocol('WM_DELETE_WINDOW', on_close)
frame.title(name)
frame.geometry(sizeWnd)
frame.resizable(False, False)

# Set the custom icon
icon_path = 'icon.ico'
frame.iconbitmap(icon_path)

# Initialize file settings if missing
settings.setdefault('first_time', 'True')
save.setdefault('name', '')
save.setdefault('location', '')
save.setdefault('inventory', [])

# Game variables outside the 'settings.json' file
chat_history = []
user_last_input = tk.StringVar()
start_time = time.time()

command_list = [
    {
        'name': 'craft',
        'info': "Command used for crafting items, add \'custom\' after \'craft\' for creating new items. Custom syntax: craft custom [name] [lore] [slots] [recipe], use _ instead of spaces."
    }
]

def tgaPrint(msgType, msg):
    chat_history.append(msg)
    typeTag = 'SYSTEM' if msgType == 0 else 'WORLD'
    text_area.config(state='normal')
    text_area.insert(tk.END, '[' + typeTag + '] ', typeTag)
    text_area.insert(tk.END, msg + '\\n')
    text_area.config(state='disabled')
    text_area.tag_config('SYSTEM', foreground='#5555ff')
    text_area.tag_config('WORLD', foreground='green')

def append_message(Event=None):
    global user_last_input
    user_last_input.set(text_input.get())
    text_input.delete(0, tk.END)

def getUserInput(user_input):
    frame.update()
    frame.wait_variable(user_input)

def smooth(number):
    return int(number) if number == int(number) else int(number) + 1

def get_item(item, quantity):
    inv_name = 0
    item_found = False

    for items in yggdrasil_itemList:
        if item == items.name:
            item_found = True
            if not save['inventory']:
                save['inventory'].append(items.JSON_serialize())
                save['inventory'][-1]['quantity'] = quantity
                if save['inventory'][-1]['quantity'] <= 0:
                    save['inventory'].remove(save['inventory'][-1])
            else:
                for items_i in save['inventory']:
                    if items_i['name'] == item:
                        items_i['quantity'] += quantity
                        if items_i['quantity'] <= 0:
                            save['inventory'].remove(items_i)
                    else:
                        inv_name += 1
                if inv_name == len(save['inventory']):
                    save['inventory'].append(items.JSON_serialize())
                    save['inventory'][-1]['quantity'] = quantity
                    if save['inventory'][-1]['quantity'] <= 0:
                        save['inventory'].remove(save['inventory'][-1])

    if not item_found:
        print(f'{item} not found in yggdrasil_itemList')

    save_files()

def inventory():
    tgaPrint(0, 'Inventory')
    if not save['inventory']:
        tgaPrint(0, 'Your inventory is empty')
    else:
        for item in save['inventory']:
            tgaPrint(0, '   ' + str(item['name']) + ' ' + str(item['quantity']))

def craft_item(item):
    for items in yggdrasil_itemList:
        if items.name == item:
            total_i = len(items.recipe.items())
            i = 0
            for ingredient, required_quantity in items.recipe.items():
                for item_i in save['inventory']:
                    if item_i['name'] == ingredient and item_i['quantity'] >= required_quantity:
                        i += 1
            if i == total_i:
                for ingredient, required_quantity in items.recipe.items():
                    for item_i in save['inventory']:
                        if item_i['name'] == ingredient and item_i['quantity'] >= required_quantity:
                            get_item(ingredient, -required_quantity)
                get_item(item, 1)
                tgaPrint(0, 'You successfully crafted a ' + str(item))
                break
            else:
                tgaPrint(0, 'Not enough ingredients')
                break
    save_files()

def custom_crafting(custom_name, custom_lore, item_slots, recipe):
    chance = 0
    recipe_items = recipe.split('_')
    for item in recipe_items:
        for item_name in yggdrasil_itemList:
            if item_name.name == item:
                chance += item_name.rarity
    calc_rarity = smooth(chance / len(recipe))
    gen_chance = random.randint(0, 10000)
    new_item = ygg_item(custom_name, custom_lore, item_slots, calc_rarity, None)
    if gen_chance <= smooth(((10000 - chance) / 100) * 100):
        save['inventory'].append(new_item.JSON_serialize())
        tgaPrint(0, 'Custom item ' + custom_name + ' was successfully created')
    else:
        tgaPrint(0, 'Custom item ' + custom_name + ' failed to create')
    print(smooth(((10000 - chance) / 100) * 100), gen_chance)

class Ygg_place:
    def __init__(self, id, map):
        self.id = id
        self.map = map[1]
        self.player_x = map[0][0]
        self.player_y = map[0][1]

    def move_player(self, additive_player_x, additive_player_y):
        if self.map[self.player_y + additive_player_y][self.player_x + additive_player_x] == 1:
            tgaPrint(0, 'Invalid movement')
        else:
            self.player_x += additive_player_x
            self.player_y += additive_player_y
            tgaPrint(0, 'X: ' + str(self.player_x) + ', Y: ' + str(self.player_y))
            update_map_display()

def update_map_display():
    if current_room:
        map_display.config(state='normal')
        map_display.delete('1.0', tk.END)
        map_size = 11  # Display size: 11x11 characters (player centered)
        half_size = map_size // 2

        for y in range(current_room.player_y - half_size, current_room.player_y + half_size + 1):
            row = ''
            for x in range(current_room.player_x - half_size, current_room.player_x + half_size + 1):
                if y == current_room.player_y and x == current_room.player_x:
                    row += '@'
                elif 0 <= y < len(current_room.map) and 0 <= x < len(current_room.map[0]):
                    row += '#' if current_room.map[y][x] == 1 else ' '
                else:
                    row += ' '
            map_display.insert(tk.END, row + '\\n')
        map_display.config(state='disabled')

rooms = [Ygg_place('test', map_1), Ygg_place('test_2', map_2)]
current_room = next((room for room in rooms if room.id == save['location']), None)

# GUI elements
bottom_bar = tk.Frame(frame, bg='grey90', height=20)
bottom_bar.pack(side='bottom', fill='x')

version_display = tk.Label(bottom_bar, text=version)
version_display.config(bd=2, relief='sunken')
version_display.pack(side=tk.LEFT)

text_input = tk.Entry(frame)
text_input.config(bd=1, relief='raised')
text_input.pack(side=tk.BOTTOM, fill=tk.X)
text_input.bind('<Return>', append_message)

# Frame to contain both text_area, map_display, and the new box
game_frame = tk.Frame(frame)
game_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

text_area = tk.Text(game_frame, state='disabled')
text_area.grid(row=0, column=0, sticky='NWS')  # Use grid for text_area
text_area.config(bg='black', fg='white', bd=1, relief='sunken')

map_display = tk.Text(game_frame, state='disabled', font=('Courier', 12),  width=20, height=10)
map_display.grid(row=0, column=1, sticky='NE')  # Use grid for map_display
map_display.config(bg='black', fg='white', bd=1, relief='sunken')

# New box below map_display
new_box = tk.Text(game_frame, state='disabled')
new_box.grid(row=0, column=1, sticky='SE')
new_box.config(bg='black', fg='white', bd=1, relief='sunken')

game_frame.columnconfigure(1, weight=1)
game_frame.rowconfigure(0, weight=1)

# Game logic (not functions)
tgaPrint(0, 'Welcome to YGGDRASIL')

if settings['first_time'] == 'True':
    tgaPrint(0, 'Log-in, type NEW to create your new game')
    getUserInput(user_last_input)
    command = ((user_last_input.get()).lower()).split(' ')

    if command[0] == 'new':
        tgaPrint(0, 'Please adventurer, type your name')
        getUserInput(user_last_input)
        player_name = user_last_input.get()
        available_races = ['Human', 'Elf', 'Dwarf']  # List of available races
        tgaPrint(1, f"Choose your race ({\', \'.join(available_races)}):")
        getUserInput(user_last_input)
        race = user_last_input.get().capitalize()
        while race not in available_races:
            tgaPrint(0, f"Invalid race. Choose from {\', \'.join(available_races)}:")
            getUserInput(user_last_input)
            race = user_last_input.get().capitalize()
        player = Entity(player_name, 1, race)
        tgaPrint(1, f'Be welcome {player_name} to Yggdrasil, the almighty tree of life and creation!')
        tgaPrint(1, "In this Text Adventure Game you don\'t have to be a hero to play, but just yourself")
        settings['first_time'] = 'False'
        save_files()

def gameLoop():
    global current_room
    while running:
        getUserInput(user_last_input)
        command = ((user_last_input.get()).lower()).split(' ')

        if len(command) < 2:
            command.append('')

        # Command handling
        if command[0] == 'help':
            if command[1] == '':
                tgaPrint(0, 'Print commands help, use help [command] or help list to show available commands')
            if command[1] == 'list':
                tgaPrint(0, 'Craft')
            elif command[1] == 'craft':
                for commands in command_list:
                    if commands['name'] == 'craft':
                        tgaPrint(0, commands['info'])
        elif command[0] == 'craft':
            if command[1] == 'custom' and len(command) > 1:
                custom_crafting(command[2], command[3], command[4], command[5])
            else:
                craft_item(command[1])
            save_files()
        elif command[0] == 'goto':
            for room in rooms:
                if room.id == command[1]:
                    current_room = room
                    save['location'] = command[1]
            save_files()
        elif command[0] == 'move':
            if command[1] in ['down', 's']:
                current_room.move_player(0, 1)
            elif command[1] in ['up', 'w']:
                current_room.move_player(0, -1)
            elif command[1] in ['left', 'a']:
                current_room.move_player(-1, 0)
            elif command[1] in ['right', 'd']:
                current_room.move_player(1, 0)
        elif command[0] == 'get':
            if len(command) > 2:
                get_item(command[1], int(command[2]))
                tgaPrint(0, f'Got {command[2]} {command[1]}')
            else:
                get_item(command[1], 1)
                tgaPrint(0, f'Got 1 {command[1]}')
        elif command[0] in ['inv', 'inventory']:
            inventory()

if current_room:
    update_map_display()
gameLoop()
frame.destroy()
save_files()
sys.exit()

# uncomment this while compiling
""")
exec(base64.b64decode(code))