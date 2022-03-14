'''utils - some misc helper functions'''

import struct


from colored import fg, bg, attr
import os
os.system('color')

#COLORS
status=242
warn=202
good=123
purp=99

#color globals
combat_color = 160
loot_color = 208
traverse_color = 53
manager_color = 240
traverse_color = 125
sensing_color = 117
note_color = 109
mem_color = 57
offset_color = 128
important_color = 87


'''
def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]

def closest_node_index(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index
'''
def log_color(text, fg_color=242,bg_color=0,target="",fg2_color=242,bg2_color=0):
    out_text =  fg(fg_color)+bg(bg_color)+text+attr('reset')
    if target != "":
        target_text =  fg(fg2_color)+bg(bg2_color)+target+attr('reset')
        print(fg(235)+':: '+out_text+" "+target_text)
    else:
        print(fg(235)+':: '+out_text)
'''
def close_down_d2():
    subprocess.call(["taskkill","/F","/IM","D2R.exe"], stderr=subprocess.DEVNULL)

def find_d2r_window() -> tuple[int, int]:
    if os.name == 'nt':
        window_list = []
        EnumWindows(lambda w, l: l.append((w, *GetWindowThreadProcessId(w))), window_list)
        for (hwnd, _, process_id) in window_list:
            if psutil.Process(process_id).name() =="D2R.exe":
                left, top, right, bottom = GetClientRect(hwnd)
                (left, top), (right, bottom) = ClientToScreen(hwnd, (left, top)), ClientToScreen(hwnd, (right, bottom))
                return (left, top)
    return None
'''
