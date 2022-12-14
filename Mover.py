import pyautogui
import time
import threading
import concurrent.futures
from random import seed
from random import randint

gui = pyautogui
img_dir = 'img/'
top_gamescreen_first_pixel = 63
game_screen_center_location = gui.Point(x=683, y=410)
seed(1)


class Mover(threading.Thread):

    def __init__(self, thread_name, thread_ID, game_controller_obj):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.GameController = game_controller_obj
        self.moved_previously = False

    # Overrriding of run() method in the subclass
    def run(self):
        print("Thread name: " + str(self.thread_name) + "  " + "Thread id: " + str(self.thread_ID));
        # We can't sleep at startup program
        while not self.GameController.game_exited:
            self.move()

    def move(self):
        if self.moved_previously:
            self.moved_previously = False
        else:
            time.sleep(3)
        x_magnifier = randint(-430, 430)
        y_magnifier = randint(-245, 245)
        random_dir_location = gui.Point(game_screen_center_location.x + x_magnifier,
                                        game_screen_center_location.y + y_magnifier)
        if not self.GameController.shooting_boss and not self.GameController.need_healing and not self.GameController.is_fighting and not self.GameController.is_looting and not self.GameController.is_refilling and time.time() - self.GameController.last_fought > 5:
            if not self.we_are_dead():
                gui.leftClick(random_dir_location)
                self.time_travel(random_dir_location)
                self.moved_previously = True

    def time_travel(self, point):
        time.sleep(float(round((abs(point.x - 683) + abs(point.y - 384)) * 0.0045, 3)))

    # Prevent clicking 500 diamonds repair by any means
    def we_are_dead(self):
        restore_icon = gui.locateCenterOnScreen(img_dir + "restore_ship_icon.png", confidence=0.8)
        if restore_icon:
            return True
