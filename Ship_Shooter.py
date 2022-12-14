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
top_gamescreen_first_pixel = 46
game_screen_center_location = gui.Point(x=683, y=410)
nearby_coordinates = (395,175, 515, 415)
perfect_shooting_distance = 297 # abs(mine.x - enemy.x) + abs(mine.y - enemy.y)
perfect_x_dist = 210
perfect_y_dist = 150


class ShipShooter(threading.Thread):

    def __init__(self, thread_name, thread_ID, game_controller_obj):
        threading.Thread.__init__(self)
        self.GameController = game_controller_obj
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.ability_num = 0
        self.healing_movement = "up"
        self.preventively_moved_while_healing = False
        self.last_time_boss_spotted = 999.0

    # Overrriding of run() method in the subclass
    def run(self):
        print("Thread name: " + str(self.thread_name) + "  " + "Thread id: " + str(self.thread_ID));
        # We can't sleep at startup program
        while not self.GameController.game_exited:
            self.battle()

    def battle(self):

        if self.GameController.is_refilling:
            return

        # If low health, only kill aggr necessary and just stand still if not looting
        if self.GameController.need_healing:
            self.fight_in_heal_state()
            return

        self.preventively_moved_while_healing = False
        fought_nearby = self.fight_nearby()

        if fought_nearby:
            return

        fought_far = self.fight_far()


    def fight_in_heal_state(self):
        batteled = False

        if self.GameController.shooting_boss:
            boss_location = self.find_boss()
            if boss_location:
                batteled = True
                self.GameController.is_fighting = True
                self.GameController.shooting_boss = True
                self.last_time_boss_spotted = time.time()
                if self.is_valid_click_location(boss_location.x, boss_location.y):
                    gui.doubleClick(boss_location)
                    gui.press('num3')  # Shoot Thunder rocket
                    # Davy Jones - Give damage
                    pyautogui.keyDown('ctrl')  # hold down the shift key
                    pyautogui.press('num1')
                    pyautogui.keyUp('ctrl')
                    time.sleep(0.2)
                    self.use_ability()
                    battle_done = self.execute_boss_fight(boss_location)
            else:
                self.GameController.is_fighting = False
                self.GameController.shooting_boss = False

        if self.GameController.shooting_boss or time.time() - self.last_time_boss_spotted <= 5:
            return

        enemy_location = self.locate_aggressive_enemy_nearby()

        if enemy_location:
            self.GameController.is_fighting = True
            batteled = True
            self.preventively_moved_while_healing = False

        while enemy_location:
            battle_done = self.execute_aggr_fight(enemy_location)
            enemy_location = self.locate_aggressive_enemy_nearby()

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False
        # There can be a enemy hidden in our ship - Move a bit up, next time down
        else:
            if time.time() - self.GameController.last_fought > 3 and not self.GameController.is_looting:
                if self.preventively_moved_while_healing:
                    time.sleep(5)
                if self.healing_movement == "up":
                    gui.leftClick(game_screen_center_location.x, game_screen_center_location.y - 210)
                    self.healing_movement = "down"
                    self.preventively_moved_while_healing = True
                else:
                    gui.leftClick(game_screen_center_location.x, game_screen_center_location.y + 210)
                    self.healing_movement = "up"
                    self.preventively_moved_while_healing = True


    def fight_nearby(self):
        batteled = False

        # Fight boss
        enemy_location = self.find_boss()
        if enemy_location:
            batteled = True
            self.GameController.is_fighting = True
            self.GameController.shooting_boss = True
            self.last_time_boss_spotted = time.time()
            if self.is_valid_click_location(enemy_location.x, enemy_location.y):
                gui.doubleClick(enemy_location)
                gui.press('num3')  # Shoot Thunder rocket
                # Davy Jones - Give damage
                pyautogui.keyDown('ctrl')  # hold down the shift key
                pyautogui.press('num1')
                pyautogui.keyUp('ctrl')
                time.sleep(0.2)
                self.use_ability()
                battle_done = self.execute_boss_fight(enemy_location)
        else:
            self.GameController.is_fighting = False
            self.GameController.shooting_boss = False

        if self.GameController.shooting_boss or time.time() - self.last_time_boss_spotted <= 5:
            return True

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True

        # Fight aggr enemies
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
        batteled = False

        # Fight boss
        enemy_location = self.find_boss()
        if enemy_location:
            batteled = True
            self.GameController.is_fighting = True
            self.GameController.shooting_boss = True
            if self.is_valid_click_location(enemy_location.x, enemy_location.y):
                gui.doubleClick(enemy_location)
                gui.leftClick(gui.Point(enemy_location.x, enemy_location.y - 60))
                gui.press('num3')  # Shoot Thunder rocket
                # Davy Jones - Give damage
                pyautogui.keyDown('ctrl')  # hold down the shift key
                pyautogui.press('num1')
                pyautogui.keyUp('ctrl')
                time.sleep(0.2)
                self.use_ability()
                battle_done = self.execute_boss_fight(enemy_location)
        else:
            self.GameController.is_fighting = False
            self.GameController.shooting_boss = False

        if self.GameController.shooting_boss or time.time() - self.last_time_boss_spotted <= 5:
            return True

        if batteled:
            gui.press('num2')  # Repair
            self.GameController.last_fought = time.time()
            self.GameController.is_fighting = False

        if batteled or self.GameController.is_looting or self.GameController.is_refilling:
            return True

        # Fight aggr enemies
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

    def keep_distance_from_enemy(self, enemy_location):
        if enemy_location:
            enemy_location = self.get_enemy_center_location(enemy_location)
            # enemy is left, we go right
            if game_screen_center_location.x - enemy_location.x >= 0:
                x_loc = game_screen_center_location.x + ( perfect_x_dist - (game_screen_center_location.x - enemy_location.x) )
            # enemy is right, we go left
            else:
                x_loc = game_screen_center_location.x - ( perfect_x_dist + (game_screen_center_location.x - enemy_location.x))
            # Enemy is up, we go down
            if game_screen_center_location.y - enemy_location.y >= 0:
                y_loc = game_screen_center_location.y + ( perfect_y_dist - (game_screen_center_location.y - enemy_location.y))
            # Enemy is down, we go up
            else:
                y_loc = game_screen_center_location.y - ( perfect_y_dist + (game_screen_center_location.y - enemy_location.y))

            travel_location = gui.Point(x_loc, y_loc)
            if self.is_valid_click_location(travel_location.x, travel_location.y):
                gui.leftClick(travel_location)

    def execute_aggr_fight(self, enemy_location):
        self.shoot(enemy_location)
        self.use_ability()
        self.keep_distance_from_enemy(self.get_enemy_center_location(enemy_location))

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
                    self.keep_distance_from_enemy(self.get_enemy_center_location(gui.Point(posX, posY)))
                    break
            if enemy_lives:
                time.sleep(1)
                enemy_loc_list = gui.locateAllOnScreen(img_dir + "Aggr_enemy_start_icon.png", confidence=0.9)
                continue
            else:
                break

    def execute_boss_fight(self, enemy_location):
        # Check if we still have enemy near last position and continue fighting
        boss_location = self.find_boss()
        boss_lives = False
        if boss_location:
            boss_lives = True
            self.GameController.shooting_boss = True
            posX = boss_location.x
            posY = boss_location.y
        else:
            self.GameController.shooting_boss = False
        iter_shoot_check = 0
        while boss_lives:
            iter_shoot_check += 1
            if iter_shoot_check == 5:
                self.shoot(gui.Point(posX, posY))
                iter_shoot_check = 0
            if self.is_valid_click_location(posX - 80, posY):
                gui.leftClick(gui.Point(posX - 80, posY)) # keep with boss at all times
            boss_location = self.find_boss()
            if boss_location:
                posX = boss_location.x
                posY = boss_location.y
            else:
                boss_lives = False

    def shoot(self, enemy_location):
        center_location = self.get_enemy_center_location(enemy_location)

        if self.is_valid_click_location(center_location.x, center_location.y):
            gui.doubleClick(center_location.x, center_location.y)

    def get_enemy_center_location(self, label_location):
        if label_location:
            return gui.Point(label_location.x + 60, label_location.y + 37)


    def is_valid_click_location(self, x, y):
        # Bottom Battle utils menu
        if x > 476 and x < 887 and y > 658 and y < 769:
            return False

        return True

    def find_boss(self):
        boss_location = gui.locateCenterOnScreen(img_dir + "BossLabel.png", confidence=0.7)
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