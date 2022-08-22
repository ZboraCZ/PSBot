# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Resolution: 1366 x 768

import pyautogui
import time
import threading
import concurrent.futures
import keyboard
import os

from Looter import Looter
from Ship_Shooter import ShipShooter
from Mover import Mover
from GameController import GameController
from LifeKeeper import LifeKeeper


gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=640, y=405)
game_screen_furthest_location = gui.Point(x=1280, y=768)

enemies_list = list()
quest_enemies_list = list()
aggressive_enemies_list = list()

load_step = 1
still_comment = True

print("Bot starting up: 20 seconds.")

try:
    with open('map_settings.txt') as f:
        for line in f:
            line = line.strip()
            start_char = line[0]
            #Start enemy comments
            if load_step == 1 and start_char == '#' and still_comment:
                continue
            # Store enemy names
            elif load_step == 1 and start_char != '#':
                if line.split('=')[1] != "":
                    enemies_list.append(line.split('=')[1])
                still_comment = False

            # Switch to quest enemies section
            if load_step == 1 and start_char == '#' and still_comment == False:
                load_step = 2
                still_comment = True

            # Still quest enemies comments
            if load_step == 2 and start_char == '#' and still_comment:
                continue

            # Store quest enemy names
            elif load_step == 2 and start_char != '#':
                if line.split('=')[1] != "":
                    quest_enemies_list.append(line.split('=')[1])
                still_comment = False

            # Switch to aggressive enemies section
            if load_step == 2 and start_char == '#' and still_comment == False:
                load_step = 3
                still_comment = True

            # Still aggressive enemies comments
            if load_step == 3 and start_char == '#' and still_comment:
                continue

            # Store quest enemy names
            elif load_step == 3 and start_char != '#':
                if line.split('=')[1] != "":
                    aggressive_enemies_list.append(line.split('=')[1])
                still_comment = False

    f.close()
except IndexError:
    print("Blank lines in map_settings.txt")


time.sleep(20)

#Game_Controller = GameController()

#game_controller_function = threading.Thread(target=GameController.start())
#game_controller_function.start()

Life_Keeper = LifeKeeper(aggressive_enemies_list)

Game_Controller_Thread = GameController("Game_Controller_Thread", 1, Life_Keeper)

Game_Controller_Thread.start()

Loot_Manager = Looter(Game_Controller_Thread)
Ship_Shooter = ShipShooter(enemies_list, quest_enemies_list, aggressive_enemies_list, Game_Controller_Thread)
Mover = Mover(Game_Controller_Thread)

loot_found = False
battle_executed = False

game_exited = False

def exit_game_key_listener_thread(Game_Controller_Thread):
    keyboard.wait('esc')
    print("====== END GAME - Esc pressed =========")
    global game_exited
    game_exited = True
    Game_Controller_Thread.game_exited = True
    exit()

game_exit_thread = threading.Thread(target=exit_game_key_listener_thread, args=(Game_Controller_Thread,))
game_exit_thread.start()

while not game_exited:

    if not loot_found and not battle_executed:
        Mover.move()

    # Loot first - fastest money
    loot_found = Loot_Manager.loot()
    if loot_found:
        continue

    # Kill and survive first place
    battle_executed = Ship_Shooter.battle()


del Mover
del Loot_Manager
del Ship_Shooter
Game_Controller_Thread.join()

