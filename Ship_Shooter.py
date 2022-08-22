import numpy
import pyautogui
import time
import threading
from matplotlib import pyplot as plt
from PIL import Image
import pytesseract
from pytesseract import Output
from timeit import default_timer as timer
import re
import mss
from GameController import GameController
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=640, y=405)
game_screen_furthest_location = gui.Point(x=1280, y=768)


class ShipShooter:

    aggr_enemies_split_list = list()
    quest_enemies_split_list = list()
    other_enemies_split_list = list()

    def __init__(self, enemies_list, quest_enemies_list, aggressive_enemies_list, game_controller_obj):

        self.GameController = game_controller_obj

        self.screen_image = gui.screenshot()
        self.found_data_dict = dict()

        for enemy_name in enemies_list:
            name_list = enemy_name.strip().split(' ')
            self.other_enemies_split_list.append(name_list)

        for enemy_name in quest_enemies_list:
            name_list = enemy_name.strip().split(' ')
            self.quest_enemies_split_list.append(name_list)

        for enemy_name in aggressive_enemies_list:
            name_list = enemy_name.strip().split(' ')
            self.aggr_enemies_split_list.append(name_list)

        self.recognized_text_list = list()

    def battle(self):
        self.prepare_screen_data()

        battle_done = self.execute_fight()
        if not battle_done:
            return False
        gui.press('num2') # Repair
        return True

    def prepare_screen_data(self):
        monitor = {'top': 0, 'left': 0, 'width': 1366, 'height': 768}
        self.screen_image = numpy.asarray(mss.mss().grab(monitor))
        self.found_data_dict = pytesseract.image_to_data(self.screen_image, output_type=Output.DICT)
        # If ever you go with just snipping the name labels from game: # enemy_location = pyautogui.locateCenterOnScreen(img_dir + "abyss_pirate_label.png", confidence=0.5)
        # plt.imshow(image)
        # plt.show()


    def execute_fight(self, last_enemy_location=None):
        aggressive_fought = False
        ### 1 - Is somebody attacking us?
        # Agrresive enemies - get rid of all
        enemy_location = self.get_enemy_from_screen(self.aggr_enemies_split_list)
        while enemy_location:
            self.focus_on_enemy(enemy_location, self.aggr_enemies_split_list)
            aggressive_fought = True
            enemy_location = self.get_enemy_from_screen(self.aggr_enemies_split_list)

        if aggressive_fought:
            return True

        ### 2 Boss as most valuable enemy
        enemy_location = self.find_boss()
        if enemy_location:
            self.fight_boss(enemy_location)
            aggressive_fought = True

        ### Quest enemies
        #enemy_location = self.get_enemy_from_screen(self.quest_enemies_split_list)
        #if enemy_location:
        #    self.focus_on_enemy(enemy_location, self.quest_enemies_split_list)
        #    return True

        ### All other enemies
        enemy_location = self.get_enemy_from_screen(self.other_enemies_split_list)
        if enemy_location:
            self.focus_on_enemy(enemy_location, self.other_enemies_split_list)
            return True

        return False

    def focus_on_enemy(self, enemy_location, enemies_list):
        # try to double click found enemy 5 times
        locate_tries_count = 5
        chase_tries_count = 20
        new_enemy_location = enemy_location
        enemy_found = False

        self.GameController.check_wait_performing_action()

        gui.doubleClick(new_enemy_location)
        self.time_travel(new_enemy_location)

        while locate_tries_count > 0 and chase_tries_count > 0:
            if enemy_found:

                self.GameController.check_wait_performing_action()

                gui.leftClick(new_enemy_location)
                gui.press("space")
                self.time_travel(new_enemy_location)
            last_enemy_location = new_enemy_location
            self.prepare_screen_data()
            new_enemy_location = self.get_enemy_from_screen(enemies_list)

            # We are shooting enemy steady
            if new_enemy_location is not None and new_enemy_location == last_enemy_location:
                enemy_found = True
                continue
            # We are chasing enemy
            elif new_enemy_location is not None and new_enemy_location != last_enemy_location:
                chase_tries_count -= 1
                enemy_found = True
            # We can't find enemy
            elif new_enemy_location is None:
                enemy_found = False
                locate_tries_count -= 1

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

        #print("Focusing enemy: ", end="")
        #for i in all_name_positions_list:
        #    print(self.found_data_dict["text"][i], end=" ")
        #print()

        return gui.Point(x_center, y_center)

    def is_valid_click_location(self, x, y):
        # Battle utils menu
        if x > 535 and x < 830 and y > 667 and y < 769:
            return False

        # Battle shortcut utils menu
        if x > 480 and x < 885 and y > 720 and y < 769:
            return False

        return True

    def find_boss(self):
        boss_location = gui.locateCenterOnScreen(img_dir + "BossLabel.png", confidence=0.7)
        if boss_location:
            return gui.Point(boss_location.x, boss_location.y + 60)
        return boss_location

    def fight_boss(self, enemy_location):
        # try to double click found enemy 5 times
        locate_tries_count = 5
        chase_tries_count = 20
        new_enemy_location = enemy_location
        enemy_found = True

        self.GameController.check_wait_performing_action()

        gui.doubleClick(new_enemy_location)
        self.time_travel(new_enemy_location)

        while locate_tries_count > 0 and chase_tries_count > 0:
            if enemy_found:

                self.GameController.check_wait_performing_action()

                gui.leftClick(new_enemy_location)
                gui.press("space")
                self.time_travel(new_enemy_location)
            last_enemy_location = new_enemy_location
            self.prepare_screen_data()
            new_enemy_location = self.find_boss()

            # We are shooting enemy steady
            if new_enemy_location is not None and new_enemy_location == last_enemy_location:
                enemy_found = True
                continue
            # We are chasing enemy
            elif new_enemy_location is not None and new_enemy_location != last_enemy_location :
                chase_tries_count -= 1
                enemy_found = True
            # We can't find enemy
            elif new_enemy_location is None:
                enemy_found = False
                locate_tries_count -= 1

    def time_travel(self, point):
        time.sleep(float(round((abs(point.x - 683) + abs(point.y - 384)) * 0.0045, 3)))





