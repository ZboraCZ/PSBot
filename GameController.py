import pyautogui
import time
import threading
from LifeKeeper import LifeKeeper

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=640, y=405)
game_screen_furthest_location = gui.Point(x=1280, y=768)


class GameController(threading.Thread):

    performing_action = False

    def __init__(self, thread_name, thread_ID, Life_Keeper):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.Life_Keeper = Life_Keeper
        self.performing_action = False
        self.game_exited = False

    # Overrriding of run() method in the subclass
    def run(self):
        print("Thread name: " + str(self.thread_name) + "  " + "Thread id: " + str(self.thread_ID));
        # We can't sleep at startup program
        while not self.game_exited:
            #self.check_health()
            self.check_ammo()
            self.check_respawn()
            self.check_miscellaneous()
            time.sleep(30)

    #def start(self):

    def check_ammo(self):
        # 2K cannonballs left
        cannon_balls_location1 = gui.locateCenterOnScreen(img_dir + "cannonballs_icon_2K.png")
        if cannon_balls_location1:
            self.performing_action = True
            self.refill_cannonballs(cannon_balls_location1)
            self.performing_action = False

        # 1K cannonballs left
        cannon_balls_location2 = gui.locateCenterOnScreen(img_dir + "cannonballs_icon_1K.png")
        if cannon_balls_location2:
            self.performing_action = True
            self.refill_cannonballs(cannon_balls_location2)
            self.performing_action = False

        # 2K harpoons left
        harpoons_location1 = gui.locateCenterOnScreen(img_dir + "harpoons_icon_2K.png")
        if harpoons_location1:
            self.performing_action = True
            self.refill_harpoons(harpoons_location1)
            self.performing_action = False

        # 1K harpoons left
        harpoons_location2 = gui.locateCenterOnScreen(img_dir + "harpoons_icon_1K.png")
        if harpoons_location2:
            self.performing_action = True
            self.refill_harpoons(harpoons_location2)
            self.performing_action = False


    def refill_cannonballs(self, cannonballs_location):
        # Open menu
        gui.leftClick(cannonballs_location.x, cannonballs_location.y)
        gui.moveTo(cannonballs_location.x, cannonballs_location.y - 44)
        # Click buy button
        gui.leftClick(786, 725)
        # Close menu
        gui.leftClick(cannonballs_location.x, cannonballs_location.y)

    def refill_harpoons(self, harpoons_location):
        # Open menu
        gui.leftClick(harpoons_location.x, harpoons_location.y)
        gui.moveTo(harpoons_location.x, harpoons_location.y - 44)
        # Click buy button
        gui.leftClick(826, 725)
        # Close menu
        gui.leftClick(harpoons_location.x, harpoons_location.y)

    def check_wait_performing_action(self):
        while self.performing_action:
            continue
        return

    def check_health(self):
        self.performing_action = True
        locs_list1 = pyautogui.locateAllOnScreen(img_dir+'low_health_indicator.png', confidence=0.7)
        low_health = False
        for location in locs_list1:
            if location.left > 621 and location.top > 325 and location.left < 747 and location.top < 437:
                low_health = True
                break
        if not low_health:
            self.performing_action = False
            return

        # Low health state
        self.Life_Keeper.survive()

        self.performing_action = False

    def check_respawn(self):
        restore_icon = gui.locateCenterOnScreen(img_dir + "restore_ship_icon.png", confidence=0.8)
        if restore_icon:
            self.performing_action = True
            gui.moveTo(restore_icon.x, restore_icon.y + 82)
            gui.leftClick()
            time.sleep(5)
            gui.press('num2')  # Start Repair
            time.sleep(60)
            gui.leftClick(683,510) # SET SAIL button
            self.performing_action = False
            return True

        # Accidentally got into Harbour?
        set_sail_icon = gui.locateCenterOnScreen(img_dir + "set_sail_icon.png")
        if set_sail_icon:
            self.performing_action = True
            gui.press('num2')  # Start Repair
            time.sleep(30)
            gui.leftClick(set_sail_icon)
            self.performing_action = False
            return True

    def check_miscellaneous(self):
        okay_button = gui.locateCenterOnScreen(img_dir + "okay_icon.png")
        if okay_button:
            self.performing_action = True
            gui.leftClick(okay_button)
            self.performing_action

