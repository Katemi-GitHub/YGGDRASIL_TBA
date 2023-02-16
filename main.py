# project started 12/02/2023

#import base64
#code = base64.b64encode(b"""

import tkinter as tk
import json
import time
import random
from items import *

# load and read player save and settings
with open("settings.json", "r") as file:
    settings = json.load(file)

with open("save.json", "r") as file:
    save = json.load(file)

# window initializer

version = "Alpha-0.3" # version of the project
name = "YGGDRASIL"
sizeWnd = "800x600" # window size
frame = tk.Tk()
frame.title(name) # window name display
frame.geometry(sizeWnd)
logged_in = False
loggingLoopId = None

# game var outside the "settings.json" file

chat_history = [] # stores the text displayed on the window
user_last_input = tk.StringVar()
start_time = time.time() # initialization time
end_time = 0

command_list = [
    {
        "name": "craft",
        "info": "Command used for crafting items, add \"custom\" after \"craft\" for creating new items \nCustom syntax: craft custom [name] [lore] [slots] [recipe], instead of spaces use _ to add several items or lore"
    }
]

# TODO:
# 1- Icon for the window    
# 2- Crafting system        FINISHED
# 3- Map and map syntax     
# 3.5- Goto function        

# there goes the functions used through the game

def tgaPrint(msgType=int, msg=str):
    chat_history.append(msg)
    typeTag = "" # typeTag defines which kind of message will be sent
    if msgType == 0: # type 0 for system messages
        typeTag = "SYSTEM"
    if msgType == 1: # type 1 for world notifications
        typeTag = "WORLD"
    text_area.config(state="normal")
    text_area.insert(tk.END, "["+typeTag+"] "+msg+"\n") # print into the text_area the desired message
    text_area.config(state="disabled")

def append_message(Event=None):
    global user_last_input
    user_last_input.set(text_input.get())
    text_input.delete(0, tk.END)

def saveFiles():
    with open("settings.json", "w") as file:
        json.dump(settings, file)

    with open("save.json", "w") as file:
        json.dump(save, file)

def getUserInput(user_input):
    frame.update()
    frame.wait_variable(user_input)

def smooth(number):
    if number == int(number):
        return int(number)
    else:
        return int(number) + 1

def craft_item(item):
    global save
    for ingredient, required_quantity in item.recipe.items():
        if save["inventory"].get(ingredient, 0) < required_quantity:
            tgaPrint(0, "Not enough ingredients")
            return False
    for ingredient, required_quantity in item.recipe.items():
        save["inventory"][ingredient] -= required_quantity
    save["inventory"][item.name] = save["inventory"].get(item.name, 0) + item.quantity
    saveFiles()
    return True


def custom_crafting(custom_name, custom_lore, item_slots, recipe):
    chance = 0
    recipe_items = recipe.split("_")
    for item in recipe_items:
        for item_name in yggdrasil_itemList:
            if item_name.name == item:
                chance += item_name.rarity
    calc_rarity = smooth(chance / len(recipe))
    gen_chance = random.randint(0, 10000)
    new_item = ygg_item(custom_name, custom_lore, item_slots, calc_rarity, None)
    if gen_chance <= smooth(((10000-chance)/100)*100):
        save["inventory"].append(new_item.JSON_serialize())
        tgaPrint(0, "Custom item "+custom_name+" was successfully created")
    else:
        tgaPrint(0, "Custom item "+custom_name+" failed to create")
    print(smooth(((10000-chance)/100)*100), gen_chance)

# there goes the GUI elements

bottom_bar = tk.Frame(frame, bg="grey90", height=20)
bottom_bar.pack(side="bottom", fill="x")

version_display = tk.Label(bottom_bar, text=version)
version_display.config(bd=2, relief="sunken")
version_display.pack(side=tk.LEFT)

text_input = tk.Entry(frame)
text_input.config(bd=1, relief="raised")
text_input.pack(side=tk.BOTTOM, fill=tk.X)
text_input.bind("<Return>", append_message)

text_area = tk.Text(frame, state="disabled")
text_area.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
text_area.config(bg="black", fg="white", bd=1, relief="sunken")

# there goes the game logic (NOT FUNCTIONS)

tgaPrint(0, "Wellcome to YGGDRASIL")

if settings["first_time"] == "True":
    tgaPrint(0, "Log-in, type NEW to create your new game")
    getUserInput(user_last_input)
    command = ((user_last_input.get()).lower()).split(" ")

    if command[0] == "new":

        tgaPrint(0, "Please adventurer, type your name")
        getUserInput(user_last_input)
        save["name"] = user_last_input.get()
        tgaPrint(0, "Be welcome "+save["name"]+" to Yggdrasil, the almighty tree of life and creation!")
        tgaPrint(0, "In this Text Adventure Game you don't have to be a hero to play, but just yourself")
        settings["first_time"] = "False"
        saveFiles()

def gameLoop():
    getUserInput(user_last_input)
    command = ((user_last_input.get()).lower()).split(" ")

    if len(command) < 2:
        command.append("")

    print(command)

    if command[0] == "help":
        tgaPrint(0, "Print commands help, use help [command] or help list to show available commands")
        if command[1] == "list":
            tgaPrint(0, "Craft")
        elif command[1] == "craft":
            for commands in command_list:
                if commands["name"] == "craft":
                    tgaPrint(0, commands["info"])
    elif command[0] == "craft":
        if command[1] == "custom" and len(command) > 1:
            custom_crafting(command[2], command[3], command[4], command[5])
        else:
            tgaPrint(0, "crafting list")
        saveFiles()
    elif command[0] == "goto":
        tgaPrint(0, "goto")
    
    frame.after(500, gameLoop)

frame.after(500, gameLoop)
frame.mainloop()

#""")
#exec(base64.b64decode(code))
