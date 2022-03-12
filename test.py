import d2read
from d2read import UI
import time



d2read.populate()

#for thing in dir(d2read):
#	print(thing)


d2read.find_info()
#constant update
while 1:
    #d2read.get_ppos()
    d2read.get_ui()
    #print(d2read.ui_state)
    #print(d2read.ui_state)
    time.sleep(.005)