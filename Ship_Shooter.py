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
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'

gui = pyautogui
img_dir = 'img/'
game_screen_center_location = gui.Point(x=683, y=384)
game_screen_furthest_location = gui.Point(x=1280, y=768)
nearby_coordinates = (395,175, 515, 415)


class ShipShooter(threading.Thread):

    def __init__(self, thread_name, thread_ID, game_controller_obj):
        threading.Thread.__init__(self)
        self.GameController = game_controller_obj
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.ability_num = 0

    # Overrriding of run() method in the subclass
    def run(self):
        print("Thread name: " + str(self.thread_name) + "  " + "Thread id: " + str(self.thread_ID));
        # We can't sleep at startup program
        while not self.GameController.game_exited:
            self.battle()

    def battle(self):

        if self.GameController.is_refilling:
            return

        # If low health, only kill aggr necessary and just stand still
        if self.GameController.need_healing:

            batteled = False
            enemy_location = self.locate_aggressive_enemy_nearby()
            if enemy_location:
                self.GameController.is_fighting = True
                batteled = True

            while enemy_location:
                battle_done = self.execute_aggr_fight(enemy_location)
                enemy_location = self.locate_aggressive_enemy_nearby()

            if batteled:
                gui.press('num2')  # Repair
                self.GameController.last_fought = time.time()
                self.GameController.is_fighting = False

            return

        fought_nearby = self.fight_nearby()

        if fought_nearby:
            return

        fought_far = self.fight_far()


    def fight_nearby(self):
        # Fight aggr enemies
        batteled = False
        enemy_location = self.locate_aggressive_enemy_nearby()
        if enemy_location:
            self.GameController.is_fighting = True
            batteled = True

        while enemy_location:
            battle_done = self.execute_aggr_fight(enemy_location)
            enemy_location = self.locate_aggressive_enemy_nearby()

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True

        # Fight boss
        enemy_location = self.find_boss_nearby()
        if enemy_location:
            batteled = True
            self.GameController.is_fighting = True
            gui.doubleClick(enemy_location)
            battle_done = self.execute_aggr_fight(enemy_location)

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True


        # Locate and fight passive enemy
        # Here not while because we fight only once and better check again for things
        enemy_location = self.locate_passive_enemy_nearby()
        if enemy_location:
            batteled = True
            self.GameController.is_fighting = True
            self.shoot(enemy_location)
            battle_done = self.execute_aggr_fight(enemy_location)

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True

    def fight_far(self):
        # Fight aggr enemies
        batteled = False
        enemy_location = self.locate_aggressive_enemy()
        if enemy_location:
            self.GameController.is_fighting = True
            batteled = True

        while enemy_location:
            battle_done = self.execute_aggr_fight(enemy_location)
            enemy_location = self.locate_aggressive_enemy()

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True

        # Fight boss
        enemy_location = self.find_boss()
        if enemy_location:
            batteled = True
            self.GameController.is_fighting = True
            enemy_location = self.find_boss_nearby()
            gui.doubleClick(enemy_location)
            if enemy_location:
                battle_done = self.execute_aggr_fight(enemy_location)

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True

        # Locate and fight passive enemy far away - just get to him and loop again
        # Here not while because we fight only once and better check again for things
        enemy_location = self.locate_passive_enemy()
        if enemy_location:
            batteled = True
            self.GameController.is_fighting = True
            gui.doubleClick(enemy_location)
            self.time_travel(enemy_location)

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True


    def locate_aggressive_enemy_nearby(self):
        enemy_location = gui.locateCenterOnScreen(img_dir + "Aggr_enemy_start_icon.png", region=nearby_coordinates, confidence=0.9)
        return enemy_location

    def locate_passive_enemy_nearby(self): #910, 590
        enemy_location = gui.locateCenterOnScreen(img_dir + "Passive_enemy_start_icon.png", region=nearby_coordinates, confidence=0.9)
        return enemy_location

    def locate_aggressive_enemy(self):
        enemy_location = gui.locateCenterOnScreen(img_dir + "Aggr_enemy_start_icon.png", confidence=0.9)
        return enemy_location


    def locate_passive_enemy(self):
        enemy_location = gui.locateCenterOnScreen(img_dir + "Passive_enemy_start_icon.png", confidence=0.9)
        return enemy_location


    def execute_aggr_fight(self, enemy_location):
        self.shoot(enemy_location)
        self.use_ability()

        # Check if we still have enemy near last position and continue fighting
        enemy_loc_list = gui.locateAllOnScreen(img_dir + "Aggr_enemy_start_icon.png", confidence=0.9)
        enemy_lives = False
        if enemy_loc_list:
            enemy_lives = True
        while enemy_lives:
            enemy_lives = False
            for enemy_loc in enemy_loc_list:
                posX = enemy_loc.left + (enemy_loc.width / 2)
                posY = enemy_loc.top + (enemy_loc.height / 2)
                if ( abs((posX - enemy_location.x)) + abs((posY - enemy_location.y)) ) < 80:
                    enemy_lives = True
                    self.shoot(gui.Point(posX, posY))
                    break
            if enemy_lives:
                time.sleep(1)
                enemy_loc_list = gui.locateAllOnScreen(img_dir + "Aggr_enemy_start_icon.png", confidence=0.9)
                continue
            else:
                break

    def execute_pass_fight(self, enemy_location):
        # First move to enemy location as he can be far away
        gui.leftClick(enemy_location)
        self.time_travel(enemy_location)
        # Now check if he is aggressive because we couldn't determine before
        enemy_location = self.locate_aggressive_enemy_nearby()
        if enemy_location:
            while enemy_location:
                battle_done = self.execute_aggr_fight(enemy_location)
                enemy_location = self.locate_aggressive_enemy_nearby()
        # No aggressive enemy, shoot passive enemy
        else:
            enemy_location = self.locate_passive_enemy_nearby()
            if enemy_location:
                self.shoot(enemy_location)
                # Now he became aggressive after shooting, so aggressive fight began
                while enemy_location:
                    battle_done = self.execute_aggr_fight(enemy_location)
                    enemy_location = self.locate_aggressive_enemy_nearby()
                    if not enemy_location:
                        enemy_location = self.locate_passive_enemy_nearby()
                        if enemy_location:
                            self.shoot(enemy_location)


    def shoot(self, enemy_location):
        center_x = enemy_location.x + 60
        center_y = enemy_location.y + 37

        if self.is_valid_click_location(center_x, center_y):
            gui.doubleClick(center_x, center_y)


    def is_valid_click_location(self, x, y):
        # Bottom Battle utils menu
        if x > 476 and x < 887 and y > 658 and y < 769:
            return False

        return True

    def find_boss(self):
        boss_location = gui.locateCenterOnScreen(img_dir + "BossLabel.png", confidence=0.7)
        if boss_location:
            gui.leftClick(boss_location)
            return gui.Point(boss_location.x, boss_location.y + 60)
        return None

    def find_boss_nearby(self):
        boss_location = gui.locateCenterOnScreen(img_dir + "BossLabel.png", region=nearby_coordinates, confidence=0.7)
        if boss_location:
            return gui.Point(boss_location.x, boss_location.y + 60)
        return None


    def time_travel(self, point):
        time.sleep(float(round((abs(point.x - 683) + abs(point.y - 384)) * 0.0045, 3)))

    def use_ability(self):
        if self.ability_num == 6:
            self.ability_num = 1
        else:
            self.ability_num += 1
        # Davy Jones - Give damage
        if self.ability_num == 1:
            pyautogui.keyDown('ctrl')  # hold down the shift key
            pyautogui.press('num1')
            pyautogui.keyUp('ctrl')
        # Gremlin - dmg per second
        elif self.ability_num == 2:
            pyautogui.keyDown('ctrl')  # hold down the shift key
            pyautogui.press('num3')
            pyautogui.keyUp('ctrl')
        # Morgans storm - dmg +7%
        elif self.ability_num == 3:
            pyautogui.keyDown('ctrl')  # hold down the shift key
            pyautogui.press('num4')
            pyautogui.keyUp('ctrl')

        # Lafities +dmg
        elif self.ability_num == 4:
            pyautogui.keyDown('ctrl')  # hold down the shift key
            pyautogui.press('num5')
            pyautogui.keyUp('ctrl')
        # Hawkins - reload -10%
        elif self.ability_num == 5:
            pyautogui.keyDown('ctrl')  # hold down the shift key
            pyautogui.press('num6')
            pyautogui.keyUp('ctrl')

        # Sirens Song - dmg sustained -8%
        elif self.ability_num == 6:
            pyautogui.keyDown('ctrl')  # hold down the shift key
            pyautogui.press('num9')
            pyautogui.keyUp('ctrl')