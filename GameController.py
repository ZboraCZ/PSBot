import pyautogui
import time
import datetime
import threading
import pyperclip

from Ship_Shooter import ShipShooter
from Looter import Looter
from Mover import Mover
from ExitWaiter import ExitWaiter


gui = pyautogui
img_dir = 'img/'
top_gamescreen_first_pixel = 63
game_screen_center_location = gui.Point(x=683, y=410)


class GameController():

    def __init__(self):
        self.performing_action = False
        self.is_fighting = False
        self.is_looting = False
        self.is_refilling = False
        self.game_exited = False
        self.last_fought = time.time()
        self.need_healing = False
        self.time_respawned = time.time()
        self.player_nickname = ""
        self.player_password = ""

        self.load_username_and_password()

        self.Ship_Shooter_Thread = ShipShooter("Ship_Shooter_Thread", 1, self)
        self.Looter_Thread = Looter("Looter_Thread", 2, self)
        self.Mover_Thread = Mover("Mover_Thread", 3, self)
        self.Exit_Waiter = ExitWaiter("Exit_Waiter_Thread", 4, self)


    def run(self):
        self.check_health()
        self.check_ammo()
        self.check_respawn()
        self.check_miscellaneous()

        self.Ship_Shooter_Thread.start()
        self.Looter_Thread.start()
        self.Mover_Thread.start()
        self.Exit_Waiter.start()

        while not self.game_exited:
            self.check_health()
            self.check_ammo()
            self.check_respawn()
            self.check_miscellaneous()

        self.Exit_Waiter.join()
        self.Mover_Thread.join()
        self.Looter_Thread.join()
        self.Ship_Shooter_Thread.join()

    def load_username_and_password(self):
        f = open("My_Nickname_and_Password.txt", "r")
        for i in range(0,2):
            line = f.readline().strip()
            if i == 0: # First line username
                if not line == "":
                    self.player_nickname = line
            if i == 1: # Second line password
                if not line == "":
                    self.player_password = line
        f.close()


    def check_health(self):
        if not self.need_healing:
            low_health_loc = gui.locateCenterOnScreen(img_dir + "low_health_indicator.png", confidence=0.9)
            if low_health_loc:
                self.is_refilling = True
                self.need_healing = True
                gui.keyDown('ctrl')  # hold down the shift key
                gui.press('num2')
                gui.keyUp('ctrl')  # hold down the shift key
                self.is_refilling = False
        else:
            high_health_loc = gui.locateCenterOnScreen(img_dir + "high_health_indicator.png")
            if high_health_loc:
                self.need_healing = False

    def check_ammo(self):
        # 2K cannonballs left
        cannon_balls_location1 = gui.locateCenterOnScreen(img_dir + "cannonballs_icon_2K.png")
        if cannon_balls_location1:
            self.is_refilling = True
            self.refill_cannonballs(cannon_balls_location1)
            self.is_refilling = False

        # 1K cannonballs left
        cannon_balls_location2 = gui.locateCenterOnScreen(img_dir + "cannonballs_icon_1K.png")
        if cannon_balls_location2:
            self.is_refilling = True
            self.refill_cannonballs(cannon_balls_location2)
            self.is_refilling = False

        # 2K harpoons left
        harpoons_location1 = gui.locateCenterOnScreen(img_dir + "harpoons_icon_2K.png")
        if harpoons_location1:
            self.is_refilling = True
            self.refill_harpoons(harpoons_location1)
            self.is_refilling = False

        # 1K harpoons left
        harpoons_location2 = gui.locateCenterOnScreen(img_dir + "harpoons_icon_1K.png")
        if harpoons_location2:
            self.is_refilling = True
            self.refill_harpoons(harpoons_location2)
            self.is_refilling = False


    def refill_cannonballs(self, cannonballs_location):
        time.sleep(0.5)
        # Open menu
        gui.leftClick(cannonballs_location.x, cannonballs_location.y)
        time.sleep(0.5)
        gui.moveTo(cannonballs_location.x, cannonballs_location.y - 44)
        time.sleep(0.5)
        # Click buy button
        gui.leftClick(786, 725)
        time.sleep(0.5)
        # Close menu
        gui.leftClick(cannonballs_location.x, cannonballs_location.y)
        time.sleep(0.5)

    def refill_harpoons(self, harpoons_location):
        time.sleep(0.5)
        # Open menu
        gui.leftClick(harpoons_location.x, harpoons_location.y)
        time.sleep(0.5)
        gui.moveTo(harpoons_location.x, harpoons_location.y - 44)
        time.sleep(0.5)
        # Click buy button
        gui.leftClick(826, 725)
        time.sleep(0.5)
        # Close menu
        gui.leftClick(harpoons_location.x, harpoons_location.y)
        time.sleep(0.5)

    def check_respawn(self):
        restore_icon = gui.locateCenterOnScreen(img_dir + "restore_ship_icon.png", confidence=0.8)
        if restore_icon:
            self.is_refilling = True
            self.time_respawned = time.time()
            self.create_death_image()
            gui.moveTo(restore_icon.x, restore_icon.y + 82)
            gui.leftClick()
            time.sleep(5)
            self.check_correct_ammo_selected()
            gui.leftClick(545,745)  # Start Repair
            time.sleep(80)
            gui.leftClick(683,510) # SET SAIL button
            self.is_refilling = False
            return True

        # Accidentally got into Harbour?
        set_sail_icon = gui.locateCenterOnScreen(img_dir + "set_sail_icon.png")
        if set_sail_icon:
            self.is_refilling = True
            if time.time() - self.time_respawned <= 80 and self.need_healing:
                time.sleep(30)
            gui.leftClick(set_sail_icon)
            self.is_refilling = False

    def check_miscellaneous(self):

        no_cannonballs_selected_icon = gui.locateCenterOnScreen(img_dir + "no_cannonballs_selected_icon.png")
        if no_cannonballs_selected_icon:
            self.is_refilling = True
            gui.leftClick(no_cannonballs_selected_icon)
            time.sleep(0.5)
            gui.leftClick(no_cannonballs_selected_icon.x, no_cannonballs_selected_icon.y - 50) # Click stone cannonballs
            time.sleep(0.5)
            self.is_refilling = False

        okay_button = gui.locateCenterOnScreen(img_dir + "okay_icon.png")
        if okay_button:
            self.create_feed_image("New_achievement_probably")
            self.is_refilling = True
            gui.leftClick(okay_button)
            self.is_refilling = False

        # For example opened map premium popup displays - 2 closes must be performed, thats why there is while
        close_button = gui.locateCenterOnScreen(img_dir + "close_button.png")
        if close_button:
            self.is_refilling = True
            while close_button:
                gui.leftClick(close_button)
                time.sleep(0.5)
                close_button = gui.locateCenterOnScreen(img_dir + "close_button.png")
            self.is_refilling = False

        feed_icons = gui.locateCenterOnScreen(img_dir + "Feed_window_icon.png", confidence=0.9)
        if feed_icons:
            self.is_refilling = True
            gui.moveTo(feed_icons)
            time.sleep(2)
            gui.leftClick(26, 631)
            self.is_refilling = False

        minimap_icons = gui.locateCenterOnScreen(img_dir + "minimap_icons.png", confidence=0.9)
        if minimap_icons:
            self.is_refilling = True
            gui.moveTo(minimap_icons)
            time.sleep(2)
            gui.leftClick(1218, 594)
            self.is_refilling = False

        reconnect_button = gui.locateCenterOnScreen(img_dir + "reconnect_button.png", confidence=0.9)
        if reconnect_button:
            self.is_refilling = True
            self.create_feed_image("connection_lost")
            gui.leftClick(reconnect_button)
            time.sleep(30)
            self.is_refilling = False

        play_button = gui.locateCenterOnScreen(img_dir + "Play_button_main.png", confidence=0.9)
        if play_button:
            self.is_refilling = True
            self.create_feed_image("hard_disconnect")
            gui.leftClick(play_button)
            time.sleep(20)
            self.is_refilling = False

        play_button = gui.locateCenterOnScreen(img_dir + "Play_button_main_highlighted.png", confidence=0.9)
        if play_button:
            self.is_refilling = True
            self.create_feed_image("hard_disconnect")
            gui.leftClick(play_button)
            time.sleep(20)
            self.is_refilling = False

        # We got black screen after login -> refresh usually works
        black_screen_after_login = gui.locateCenterOnScreen(img_dir + "black_loading_screen.png")
        if black_screen_after_login:
            self.is_refilling = True
            self.create_feed_image("black_screen_after_login")
            gui.leftClick(30,9) # File button
            time.sleep(1)
            gui.leftClick(30, 52)  # Refresh page button
            time.sleep(20)
            self.is_refilling = False

        close_icon_main_menu = gui.locateCenterOnScreen(img_dir + "Close_icon_main.png", confidence=0.9)
        if close_icon_main_menu:
            self.is_refilling = True
            self.is_refilling = True
            self.create_feed_image("hard_disconnect_menu_window_opened")
            gui.leftClick(close_icon_main_menu)
            self.is_refilling = False

        auto_logoff_cancel_button = gui.locateCenterOnScreen(img_dir + "cancel_auto_logoff_button.png", confidence=0.9)
        if auto_logoff_cancel_button:
            self.is_refilling = True
            gui.leftClick(auto_logoff_cancel_button)
            self.is_refilling = False

        session_expired_okay_button = gui.locateCenterOnScreen(img_dir + "session_expired_okay_button.png")
        if session_expired_okay_button:
            # No is_refilling = False comes, because the Play button must be clicked to start game after login
            self.is_refilling = True
            #gui.leftClick(session_expired_okay_button)
            gui.leftClick(21,11) # File menu
            gui.leftClick(21,35) # Home button
            gui.leftClick(230,60) # Username Field
            pyperclip.copy(self.player_nickname)
            gui.hotkey("ctrl", "v")
            gui.leftClick(340, 60)  # Password Field
            pyperclip.copy(self.player_password)
            gui.hotkey("ctrl", "v")
            gui.leftClick(460, 60)  # LOGIN button

        # Game logouted and GUI is switched to Czech for some reason, so switch to english
        czech_lang_input_logouted = gui.locateCenterOnScreen(img_dir + "czech_lang_input.png")
        if czech_lang_input_logouted:
            # No is_refilling = False comes, because the Play button must be clicked to start game after login
            self.is_refilling = True
            # gui.leftClick(session_expired_okay_button)
            gui.leftClick(czech_lang_input_logouted)  # Czech lang select
            time.sleep(1)
            gui.leftClick(czech_lang_input_logouted.x, czech_lang_input_logouted.y + 120)  # English (United Kingdom select option)
            time.sleep(5)

        # If we got somehow logouted out of any logic, try to log back in
        username_input = gui.locateCenterOnScreen(img_dir + "username_input.png", confidence=0.9)
        if username_input:
            # No is_refilling = False comes, because the Play button must be clicked to start game after login
            self.is_refilling = True
            gui.leftClick(username_input)
            pyperclip.copy(self.player_nickname)
            time.sleep(0.5)
            gui.hotkey("ctrl", "v")
            gui.leftClick(340, 60)  # Password Field
            pyperclip.copy(self.player_password)
            time.sleep(0.5)
            gui.hotkey("ctrl", "v")
            time.sleep(0.5)
            gui.leftClick(460, 60)  # LOGIN button

        # If we log back in in the morning, Accept daily button must be clicked
        daily_bonus_btn = gui.locateCenterOnScreen(img_dir + "accept_daily_bonus_btn.png")
        if daily_bonus_btn:
            # Avoid arena battle invitation accept button in top right corner
            if not (daily_bonus_btn.x > 1137 and daily_bonus_btn.y < 240):
                # No is_refilling = False comes, because the Play button must be clicked to start game after login
                self.is_refilling = True
                gui.leftClick(daily_bonus_btn)
                self.is_refilling = False

        # Internet connection lost -> refresh should work
        no_internet_icon = gui.locateCenterOnScreen(img_dir + "no_internet_icon.png")
        if no_internet_icon:
            self.is_refilling = True
            self.create_feed_image("internet_connection_lost")
            gui.leftClick(30, 9)  # File button
            time.sleep(1)
            gui.leftClick(30, 52)  # Refresh page button
            time.sleep(20)
            self.is_refilling = False


    def create_death_image(self):
        now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        gui.screenshot("Log\\Deaths\\" + "death-"+ str( now ).replace(":", "-") + ".png" )

    def create_feed_image(self, event_keyword):
        now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        gui.screenshot("Log\\Feed\\" + str(event_keyword) +"-" + str( now ).replace(":", "-") + ".png" )

    def check_correct_ammo_selected(self):
        stone_cannonballs_icon = gui.locateCenterOnScreen(img_dir + "stone_cannonballs_icon.png")
        if not stone_cannonballs_icon:
            self.is_refilling = True
            gui.leftClick(603,705) # cannonballs icon
            time.sleep(0.5)
            gui.leftClick(603, 655)  # Stone cannonballs icon
            time.sleep(0.5)
            self.is_refilling = False

        harpoon_icon = gui.locateCenterOnScreen(img_dir + "harpoon_icon.png")
        if not harpoon_icon:
            self.is_refilling = True
            gui.leftClick(644, 705)  # harpoons icon
            time.sleep(0.5)
            gui.leftClick(644, 655)  # harpoons icon
            time.sleep(0.5)
            self.is_refilling = False
