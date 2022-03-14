import time
import d2read

#d2read.populate()

#constant update
#print(dir(d2read))
r = None
ro = None
start = time.time()
ticks=0

d2read.start()

@d2read.events.on("game_state_update")
def game_state_changed():
    #print(">got new state")
    pass
    #d2read.populate()
    #d2read.find_info()
    #d2read.find_mobs()
    #d2read.get_ui()
    #d2read.get_game_ip()
    #d2read.get_game_name()
    #d2read.get_game_pass()
    #d2read.get_tick()
    #d2read.get_cursor_item()
    #d2read.get_items()
    #d2read.get_last_hovered()


input("Press enter to close program \n")

#key=input("press close to exit") 

#while True:
    #idle
    #time.sleep(.00001)

#events.add_listener("game_state_update")


#events.remove_listener("data", self._update_state)

'''
while i<10:
    #d2read.get_ppos()
 
    #print(d2read.get_tick())
    #print(d2read.game_state.game_name)
    #print(d2read.game_state.game_pass)
    #print(d2read.game_state.ui_state)

    time.sleep(.05)
    i+=1
'''
#d2read.shutdown()