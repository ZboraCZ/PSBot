import pyautogui
import threading
import keyboard

gui = pyautogui
img_dir = 'img/Smugglers_auction/'
top_gamescreen_first_pixel = 63
game_screen_center_location = gui.Point(x=683, y=410)
nearby_coordinates = (395,175, 515, 415)

end_game = False

def thread_wait():
    global end_game
    print("waiting thread")
    while True:
        if keyboard.read_key() == "esc" or end_game == True:
            print("Game ended.")
            break

    end_game = True
    print("waiting thread ended")
    return

# Create a Thread with a function without any arguments
th = threading.Thread(target=thread_wait)
th.start()

print("Auctioner started. Press esc to end")

while end_game == False:
    found = False
    # Total Eclipse
    total_eclipse = gui.locateCenterOnScreen(img_dir + "total_eclipse_auction_time.png")
    if total_eclipse:
        found = True
        gui.leftClick(total_eclipse.x + 267, total_eclipse.y + 14)

    # Corona deck
    corona_deck = gui.locateCenterOnScreen(img_dir + "corona_deck_auction_time.png")
    if corona_deck:
        found = True
        gui.leftClick(corona_deck.x + 267, corona_deck.y + 14)

    # Moonlight figurehead
    #moonlight_figurehead = gui.locateCenterOnScreen(img_dir + "moonlight_figurehead_auction_time.png")
    #if moonlight_figurehead:
        #    found = True
    #    gui.leftClick(moonlight_figurehead.x + 267, moonlight_figurehead.y + 14)

    # Moonforged Anchor Weights
    moonforged_anchor = gui.locateCenterOnScreen(img_dir + "moonforged_anchor_weights_auction_time.png")
    if moonforged_anchor:
        found = True
        gui.leftClick(moonforged_anchor.x + 267, moonforged_anchor.y + 14)

    # Blood moon bulkhead
    #bloodmoon_bulkhead = gui.locateCenterOnScreen(img_dir + "blood_moon_bulkhead_auction_time.png")
    #if bloodmoon_bulkhead:
    #    found = True
    #    gui.leftClick(bloodmoon_bulkhead.x + 267, bloodmoon_bulkhead.y + 14)


    # Blood moon deck - last because not so necessary
    #bloodmoon_deck = gui.locateCenterOnScreen(img_dir + "blood_moon_deck_auction_time.png")
    #if bloodmoon_deck:
    #    found = True
    #    gui.leftClick(bloodmoon_deck.x + 267, bloodmoon_deck.y + 14)

    # Click to place where Reconnect button displays on idle
    if not found:
        gui.leftClick(663,442)

print("Auctioner ended.")