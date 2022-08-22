import pyautogui
import time
import numpy
import mss
import pytesseract
from pytesseract import Output
import re
from random import seed
from random import randint

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=683, y=384)
game_screen_furthest_location = gui.Point(x=1280, y=768)
seed(1)


class LifeKeeper:
    aggr_enemies_split_list = list()

    def __init__(self, aggressive_enemies_list):
        for enemy_name in aggressive_enemies_list:
            name_list = enemy_name.strip().split(' ')
            self.aggr_enemies_split_list.append(name_list)

        self.found_data_dict = dict()

    # Run away from aggr enemies and heal yourself
    def survive(self):
        while self.still_on_fire:
            #Run for 40 seconds
            t_end = time.time() + 60
            t_heal_start = time.time() + 15
            healing_started = False

            while time.time() < t_end:
                if not healing_started and time.time() >= t_heal_start:
                    gui.press('num2')  # Start Repair
                    healing_started = True

                self.prepare_screen_data()
                enemy_location = self.get_enemy_from_screen(self.aggr_enemies_split_list)
                if not enemy_location: continue

                self.move_from_enemy(enemy_location.x, enemy_location.y)


    def still_on_fire(self):
        locs_list1 = pyautogui.locateAllOnScreen(img_dir + 'low_health_indicator.png', confidence=0.7)
        low_health = False
        for location in locs_list1:
            if location.left > 621 and location.top > 325 and location.left < 747 and location.top < 437:
                return True
        return False


    def move_from_enemy(self, posX, posY):
        # Click away from enemy - 4 quadrants principle
        # Left top
        if posX <= game_screen_center_location.x and posY <= game_screen_center_location.y:
            for i in range(2):
                x_magnifier = randint(200, 430)
                y_magnifier = randint(100, 245)
                random_dir_location = gui.Point(game_screen_center_location.x + x_magnifier,
                                                game_screen_center_location.y + y_magnifier)
                gui.leftClick(random_dir_location)
                self.time_travel(random_dir_location)
                return True

        # Right top
        elif posX >= game_screen_center_location.x and posY <= game_screen_center_location.y:
            for i in range(2):
                x_magnifier = randint(-430, -200)
                y_magnifier = randint(100, 245)
                random_dir_location = gui.Point(game_screen_center_location.x + x_magnifier,
                                                game_screen_center_location.y + y_magnifier)

                gui.leftClick(random_dir_location)
                self.time_travel(random_dir_location)
                return True

        # Left bottom
        if posX <= game_screen_center_location.x and posY >= game_screen_center_location.y:
            for i in range(2):
                x_magnifier = randint(200, 430)
                y_magnifier = randint(-245, -100 )
                random_dir_location = gui.Point(game_screen_center_location.x + x_magnifier,
                                                game_screen_center_location.y + y_magnifier)
                gui.leftClick(random_dir_location)
                self.time_travel(random_dir_location)
                return True

        # Right bottom
        if posX >= game_screen_center_location.x and posY >= game_screen_center_location.y:
            for i in range(2):
                x_magnifier = randint(-430, -200 )
                y_magnifier = randint(-245, -100 )
                random_dir_location = gui.Point(game_screen_center_location.x + x_magnifier,
                                                game_screen_center_location.y + y_magnifier)
                gui.leftClick(random_dir_location)
                self.time_travel(random_dir_location)
                return True

        return True


    def time_travel(self, point):
        time.sleep(float(round((abs(point.x - 683) + abs(point.y - 384)) * 0.0045, 3)))


    def prepare_screen_data(self):
        monitor = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}
        self.screen_image = numpy.asarray(mss.mss().grab(monitor))
        self.found_data_dict = pytesseract.image_to_data(self.screen_image, output_type=Output.DICT)
        # If ever you go with just snipping the name labels from game: # enemy_location = pyautogui.locateCenterOnScreen(img_dir + "abyss_pirate_label.png", confidence=0.5)
        # plt.imshow(image)
        # plt.show()

    def get_enemy_from_screen(self, enemies_list):
        texts_list = self.found_data_dict["text"]
        #print(self.found_data_dict["text"])
        all_name_positions_list = list()
        found = False

        for dict_pos in range(len(texts_list)-1):
            if not texts_list[dict_pos].strip() or len(texts_list[dict_pos].strip() ) < 4:
                continue

            label_found = False
            for enemy_name_list in enemies_list:
                if texts_list[dict_pos] in enemy_name_list:
                    # Check if there is a Level label in previous column
                    if re.search(r'\([0-9]+\)', texts_list[dict_pos-1]):
                        all_name_positions_list.append(dict_pos-1)
                        label_found = True
                    elif re.search(r'\([0-9]+\)', texts_list[dict_pos-2]):
                        all_name_positions_list.append(dict_pos - 2)
                        all_name_positions_list.append(dict_pos-1)
                        label_found = True
                    if not label_found:
                        continue
                    all_name_positions_list.append(dict_pos)
                    i = dict_pos + 1
                    while i < len(texts_list) and texts_list[i] in enemy_name_list:
                        all_name_positions_list.append(i)
                        i += 1
                    found = True
                    break
            if found:
                break
        # No enemy found
        if not found:
            #print("No enemy found")
            return None

        x_left = self.found_data_dict['left'][all_name_positions_list[0]]
        x_right = self.found_data_dict['left'][ all_name_positions_list[len(all_name_positions_list)-1] ] + self.found_data_dict['width'][ all_name_positions_list[len(all_name_positions_list)-1] ]

        x_center = x_left + ( (x_right-x_left) / 2 )
        y_top = self.found_data_dict['top'][all_name_positions_list[0]]
        y_center = y_top + 40

        if not self.is_valid_click_location(x_center, y_center):
            return None

        return gui.Point(x_center, y_center)

    def is_valid_click_location(self, x, y):
        # Battle utils menu
        if x > 535 and x < 830 and y > 667 and y < 769:
            return False

        # Battle shortcut utils menu
        if x > 480 and x < 885 and y > 720 and y < 769:
            return False

        return True
