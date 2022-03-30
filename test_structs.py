from multiprocessing.sharedctypes import RawArray, RawValue
from multiprocessing import Process

import d2read
from d2read import game_state

def main():
    game_state.init()

    running_manager = RawValue(game_state.Running)
    running_manager.main=1



    d2read.process_data.read_hash_table()

    input("Press enter to close program \n")


if __name__ == '__main__':


    main()