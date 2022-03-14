'''utils - some misc helper functions'''
import os
import struct
from colored import fg, bg, attr
os.system('color')

status=242
''' loot log colors '''
warn=202
''' loot log colors '''
good=123
''' loot log colors '''
purp=99
''' loot log colors '''
combat_color = 160
''' combat log colors '''
loot_color = 208
''' loot log colors '''
traverse_color = 53
''' loot log colors '''
manager_color = 240
''' loot log colors '''
traverse_color = 125
''' loot log colors '''
sensing_color = 117
''' loot log colors '''
note_color = 109
''' loot log colors '''
mem_color = 57
''' loot log colors '''
offset_color = 128
''' loot log colors '''
important_color = 87
''' loot log colors '''

def log_color(text, fg_color=242,bg_color=0,target="",fg2_color=242,bg2_color=0):
    out_text =  fg(fg_color)+bg(bg_color)+text+attr('reset')
    if target != "":
        target_text =  fg(fg2_color)+bg(bg2_color)+target+attr('reset')
        print(fg(235)+':: '+out_text+" "+target_text)
    else:
        print(fg(235)+':: '+out_text)
