from multiprocessing.sharedctypes import RawArray, RawValue
from multiprocessing import Process

import d2read
from d2read import game_state

def main():

    running_manager = RawValue(game_state.Running)
    running_manager.main=1

    manager_proc = Process(target=d2read.start, args=(running_manager,))
    manager_proc.start()

    input("Press enter to close program \n")
    running_manager.main=0

    manager_proc.join()

if __name__ == '__main__':


    main()