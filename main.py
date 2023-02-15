# project started 12/02/2023

import tkinter as tk
import json
import time

# load and read player save and settings
with open("settings.json", "r") as file:
    settings = json.load(file)

with open("save.json", "r") as file:
    save = json.load(file)

# window initializer

version = "Alpha-0.1" # version of the project
name = "YGGDRASIL"
sizeWnd = "800x600" # window size
frame = tk.Tk()
frame.title(name) # window name display
frame.geometry(sizeWnd)

# game var outside the "settings.json" file

chat_history = [] # stores the text displayed on the window
user_last_input = tk.StringVar()
start_time = time.time() # initialization time
end_time = 0

# TODO:
# 1- Icon for the window
# 2- Crafting system
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

# there goes the GUI elements

bottom_bar = tk.Frame(frame, bg="grey90", height=20)
bottom_bar.pack(side="bottom", fill="x")

version_display = tk.Label(bottom_bar, text=version)
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
    tgaPrint(0, "Please adventurer, type your name")
    getUserInput(user_last_input)
    save["name"] = user_last_input.get()
    tgaPrint(0, "Be welcome "+save["name"]+" to Yggdrasil, the almighty tree of life and creation!")
    settings["first_time"] = "False"
    saveFiles()

getUserInput(user_last_input)
command = user_last_input.get()

frame.mainloop()
