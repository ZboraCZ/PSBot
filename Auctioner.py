import pyautogui
import threading
import keyboard

gui = pyautogui
img_dir = 'img/'
top_gamescreen_first_pixel = 63
game_screen_center_location = gui.Point(x=683, y=410)
nearby_coordinates = (395,175, 515, 415)

end_game = False

def thread_wait():
    keyboard.wait('esc')
    global end_game
    end_game = True
    return

def thread_check_finished_auction():
    global end_game
    pounder_finished_b = False
    harpoon_finished_b = False
    while end_game == False:
        pounder_finished = gui.locateCenterOnScreen(img_dir + "pounder_finished.png")
        if pounder_finished:
            pounder_finished_b = True

        harpoon_finished = gui.locateCenterOnScreen(img_dir + "harpoon_finished.png")
        if harpoon_finished:
            harpoon_finished_b = True


        if pounder_finished_b and harpoon_finished_b:
            end_game = True
            gui.press("esc")
            return

# Create a Thread with a function without any arguments
th = threading.Thread(target=thread_wait)
th.start()

# Create a Thread checking auction items ended
th2 = threading.Thread(target=thread_check_finished_auction)
th2.start()

print("Auctioner started. Press esc to end")

while end_game == False:
    found = False
    pounder = gui.locateCenterOnScreen(img_dir + "pounder_auction_time.png")
    if pounder:
        found = True
        gui.leftClick(pounder.x + 267, pounder.y + 14)

    harpoon = gui.locateCenterOnScreen(img_dir + "harpoon_auction_time.png")
    if harpoon:
        found = True
        gui.leftClick(harpoon.x + 267, harpoon.y + 14)

    # Click to place where Reconnect button displays on idle
    if not found:
        gui.leftClick(663,442)

print("Auctioner ended.")