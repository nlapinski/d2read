import pymem 
import numpy as np

d2_process = 0
exp_offset = 0
starting_offset = 0
game_info_offset = 0
ui_settings_offset = 0
menu_vis_offset = 0
menu_data_offset = 0
hover_offset = 0
path_addr = 0
process = pymem.Pymem("D2R.exe")
handle = process.process_handle
module = pymem.process.module_from_name(handle,"D2R.exe")
base = process.base_address