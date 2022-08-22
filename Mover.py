import pyautogui
import time
import threading
import concurrent.futures
from random import seed
from random import randint

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=640, y=405)
game_screen_furthest_location = gui.Point(x=1280, y=768)
seed(1)


class Mover:

    def __init__(self, game_controller_obj):
        self.GameController = game_controller_obj


    def move(self):
        x_magnifier = randint(-430, 430)
        y_magnifier = randint(-245, 245)
        random_dir_location = gui.Point(game_screen_center_location.x + x_magnifier,
                                        game_screen_center_location.y + y_magnifier)

        self.GameController.check_wait_performing_action()

        gui.leftClick(random_dir_location)
        self.time_travel(random_dir_location)
        return True

    def time_travel(self, point):
        time.sleep(float(round((abs(point.x - 683) + abs(point.y - 384)) * 0.0045, 3)))





