# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Resolution: 1366 x 768

import pyautogui
import time

from GameController import GameController

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=683, y=384)
game_screen_furthest_location = gui.Point(x=1280, y=768)

print("Bot starting up: 20 seconds.")
#time.sleep(20)

Game_Controller = GameController()

Game_Controller.run()



