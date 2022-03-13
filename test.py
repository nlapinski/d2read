import time
#from d2read import proc as d2read
import d2read
from d2read import game_state

d2read.populate()
d2read.find_info()
#constant update
#print(dir(d2read))
r = None
ro = None
start = time.time()
ticks=0
while 1:
    #d2read.get_ppos()
    d2read.find_mobs()
    d2read.get_ui()
    d2read.get_game_ip()
    d2read.get_game_name()
    d2read.get_game_pass()
    d2read.get_tick()
    #d2read.get_cursor_item()
    d2read.get_items()
    d2read.get_last_hovered()

    '''
    if r!= ro:
        
        ro = r
        if r[0]!=0:
            ticks+=1
            diff = time.time()-start
            s = ""
            for p in r:
                s+= str(p).zfill(3)+" "
            print('updated',s,diff,ticks)
            start = time.time()
    '''

    #print(game_state.game_name)
    #print(game_state.game_pass)
    #print(game_state.ui_state)

    time.sleep(.1)