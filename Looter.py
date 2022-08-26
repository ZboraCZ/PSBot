import pyautogui
import time
import threading
import concurrent.futures
#from GameController import GameController

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=683, y=384)
game_screen_furthest_location = gui.Point(x=1280, y=768)


class Looter(threading.Thread):

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
            self.loot()

    def loot(self):
        self.locate_loot()


    def locate_loot(self):
        chest_location = self.find_chest()
        if chest_location is not None:
            self.GameController.is_looting = True
            if self.GameController.need_healing or self.GameController.is_fighting or self.GameController.is_refilling:
                return

            pyautogui.leftClick(chest_location)
            time.sleep(self.calculate_travel_wait_time(chest_location))

            return
        else:
            self.GameController.is_looting = False
            return

    def find_chest(self):
        locs_list1 = pyautogui.locateAllOnScreen(img_dir + "LootBox1.png", confidence=0.7)
        locs_list2 = pyautogui.locateAllOnScreen(img_dir + "LootBox2.png", confidence=0.7)
        locs_list3 = pyautogui.locateAllOnScreen(img_dir + "LootBox3.png", confidence=0.7)
        locs_list_appended = [locs_list1, locs_list2, locs_list3]

        min_chest_locations = list()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(locs_list_appended)) as executor:
            for returned_fastest_specific_chest_location in executor.map(self.find_closest_chest_thread, locs_list_appended):
                if returned_fastest_specific_chest_location:
                    min_chest_locations.append(returned_fastest_specific_chest_location)

        return self.find_closest_chest_thread(min_chest_locations)


    def calculate_travel_wait_time(self, point):
        try:
            posX = point.left + (point.width / 2)
            posY = point.top + (point.height / 2)
            return float(round((abs(posX - 683) + abs(posY - 384)) * 0.0045, 3))
        except AttributeError:
            1 == 1

    def find_closest_chest_thread(self, chest_locations_list):
        if chest_locations_list:
            min_travel_time = 999  # seconds
            fastest_location = None
            for location in chest_locations_list:
                temp_travel_time = self.calculate_travel_wait_time(location)
                if temp_travel_time < min_travel_time:
                    min_travel_time = temp_travel_time
                    fastest_location = location
            return fastest_location
        else:
            return None
