import pyautogui
import time
import threading
import concurrent.futures
from GameController import GameController

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=640, y=405)
game_screen_furthest_location = gui.Point(x=1280, y=768)


class Looter:

    def __init__(self, game_controller_obj):
        self.GameController = game_controller_obj

    def loot(self):
        return self.locate_loot()


    def locate_loot(self):
        chest_location = self.find_chest()
        if chest_location is not None:

            self.GameController.check_wait_performing_action()

            pyautogui.leftClick(chest_location)
            time.sleep(self.calculate_travel_wait_time(chest_location))
            return True
        else:
            return False

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
