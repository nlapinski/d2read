from multiprocessing.sharedctypes import RawArray, RawValue
from multiprocessing import Process

import d2read
from d2read import game_state

import configparser
import time

def main():
    #game_state.init()

    running_manager = RawValue(game_state.Running)
    running_manager.main=1

    d2_data =configparser.ConfigParser()
    d2_data.optionxform = str

    d2_data.read("game_data.ini", encoding='utf-8')
    '''
    for each_section in d2_data.sections():
        if each_section == "superuniques":
            for (each_key, each_val) in d2_data.items(each_section):
                #print(each_key)
                pass
                #print(each_val)
    #test loading data
    #print(d2_data['superuniques'][1])
    #print all items
    for i in range(len(d2_data['items'])):
        item = (d2_data['items'][i][:3])
        print(d2_data['strings'][item+'[0]'])
    '''
    #while 1:
    d2read.process_data.read_game_info()
    #d2read.process_data.read_hash_table()
    #d2read.process_data.read_tick()

    input("Press enter to close program \n")


if __name__ == '__main__':


    main()