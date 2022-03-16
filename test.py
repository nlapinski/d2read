import os
import sys
import time
import d2read
from debug_overlay import Overlay
import threading

r = None
ro = None
start = time.time()
ticks=0

d2read.start()
overlay_started = False

@d2read.events.on("game_state_update")
def game_state_changed():
    global overlay_started

    #for m in d2read.game_state.monsters_obj:
        #print(m.name)
    if overlay_started is False:
        overlay = Overlay(d2read.game_state)
        overlay_thread = threading.Thread(target=overlay.init)
        overlay_thread.daemon = False
        overlay_thread.start()
        overlay_started = True
    pass

input("Press enter to close program \n")