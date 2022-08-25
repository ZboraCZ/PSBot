import threading
import keyboard
from random import seed
from random import randint

img_dir = 'img/'
seed(1)


class ExitWaiter(threading.Thread):

    def __init__(self, thread_name, thread_ID, game_controller_obj):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.GameController = game_controller_obj

    # Overrriding of run() method in the subclass
    def run(self):
        print("Thread name: " + str(self.thread_name) + "  " + "Thread id: " + str(self.thread_ID));
        # We can't sleep at startup program
        while not self.GameController.game_exited:
            keyboard.wait('esc')
            print("====== END GAME - Esc pressed =========")
            self.GameController.game_exited = True
