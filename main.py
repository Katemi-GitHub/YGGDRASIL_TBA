# Project started 12/2/23

import pygame
import json
from pygame.locals import *

with open("settings.json", "r") as f:
    settings = json.load(f)

with open("save.json", "r") as f:
    save = json.load(f)

pygame.init()
window = pygame.display.set_mode((800, 600))
pygame.display.set_caption("YGGDRASIL || BUILD 0.1DEV")
font = pygame.font.Font(None, 20)

entry_text = ""
entry_text_render = font.render("> " + entry_text, True, (255, 255, 255))
chat = []
scroll = 0
tags = ""

def TBA_print(type, message):
    if type == 1:
        end_message = "[SYSTEM] " + message
    message_text = font.render(end_message, True, (255, 255, 255))
    text_width = message_text.get_rect().width
    lines = text_width // 75 + 1
    for i in range(lines):
        line = end_message[i * 75:(i + 1) * 75]
        chat.append(line)
    for i, text in enumerate(chat):
        if text == "":
            chat.pop(i)

TBA_print(1, "Wellcome to YGGDRASIL BETA 1.0")

if settings["first_time"] == "True":
    TBA_print(1, "Please enter your name")
else:
    TBA_print(1, "Wellcome " + save["name"])

def game_logic(list, message):
    if settings["first_time"]:
        if save["name"] == "":
            save["name"] = message
            save["tags"].append(message)
            settings["first_time"] = "False"
            with open("save.json", "w") as f:
                json.dump(save, f)
            with open("settings.json", "w") as f:
                json.dump(settings, f)
            TBA_print(1, "Wellcome " + save["name"])
    if message == "":
        return

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalnum() or event.unicode == " ":
                entry_text += event.unicode
            elif event.key == pygame.K_BACKSPACE:
                entry_text = entry_text[:-1]
            elif event.key == K_RETURN:
                if scroll <= len(chat)*20:
                    scroll == len(chat)*20
                if entry_text != "" and len(chat)*20 > 520:
                    scroll += 20
                for tag in save["tags"]:
                    tags = "[" + tag + "]"
                chat_text = font.render(entry_text, True, (255, 255, 255))
                text_width = chat_text.get_rect().width
                lines = text_width // 75 + 1
                for i in range(lines):
                    line = tags + " " + entry_text[i * 75:(i + 1) * 75]
                    chat.append(line)
                game_logic(chat, entry_text)
                entry_text = ""
            entry_text_render = font.render("> " + entry_text, True, (255, 255, 255))
        if event.type == MOUSEWHEEL:
            if event.y == -1:
                if scroll <= (len(chat)*20 - 600):
                    scroll += 20
            elif event.y == 1:
                if scroll >= 20:
                    scroll -= 20

    window.fill((0, 0, 0))
    pygame.draw.rect(window, (55, 55, 55), (0, 540, 800, 60), width=5)
    window.blit(entry_text_render, (10, 550))
    for i, text in enumerate(chat):
        if text == "":
            chat.pop(i)
    for i, text in enumerate(chat):
        chat_text = font.render(text, True, (255, 255, 255))
        window.blit(chat_text, (10, 20*(i+1) - scroll))
    pygame.display.update()
