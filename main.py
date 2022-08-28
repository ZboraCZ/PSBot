# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Resolution: 1366 x 768

import pyautogui
import time

from GameController import GameController

gui = pyautogui
img_dir = 'img/'
top_gamescreen_first_pixel = 63
game_screen_center_location = gui.Point(x=683, y=(768/2)+top_gamescreen_first_pixel-1)

print("Bot starting up: 20 seconds.")
time.sleep(20)

Game_Controller = GameController()

Game_Controller.run()



