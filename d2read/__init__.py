'''proc - handles reading memory from the d2r process.'''
from multiprocessing import Process
from multiprocessing.sharedctypes import RawArray, RawValue
from threading import Thread
import subprocess

import inspect

import sys, os, time, string, collections, math, random, traceback
from struct import unpack, pack
from ctypes import *
import ctypes

import requests
import numpy as np
import orjson

from scipy.spatial.distance import cdist
from scipy.spatial.distance import cityblock
from scipy.spatial import distance

import pymem

from . import game_state
from .event import events
from .enums import *
from .utils import *
from . import process_data
from .overlay import overlay
from . import interact
from . import core
from .game_state import process
from .game_state import base
from .game_state import handle
from .game_state import module
from .structs import *

from timeit import default_timer as timer

map_players = dict()


# ------------------------------ memory offset code ------------------------------ #

def update_base_offset(game_info_clist):
    """Summary - base memory location of d2r
    Args:
        game_info_clist (TYPE): Description
    """
    game_info_clist.mem.base=game_state.base
    print(game_state.base)
    print(game_state.base)
    print(game_state.base)

def read_unit_offset():
    '''Summary - gets some unit table offsets from memory, return the adress of the table

    '''
    # var pattern = "\x48\x8D\x0D\x00\x00\x00\x00\x48\xC1\xE0\x0A\x48\x03\xC1\xC3\xCC";
    #pat = b"\x48\x8d.....\x8b\xd1"
    #######

    #pat = b"\x48\x8D\x0D....\x48\xC1\xE0\x0A\x48\x03\xC1\xC3\xCC"
    #pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    #offset_buffer = process.read_long(pat_addr)
    #unit_hashtable = ((pat_addr - base) + 7 + offset_buffer)

    #return (unit_hashtable+base)


    pat = b"\x48\x8D\x0D....\x48\xC1\xE0\x0A\x48\x03\xC1\xC3\xCC"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset = process.read_int(pat_addr+3)
    delta = pat_addr-base
    new = base + (delta+7+offset)
    return new


def read_roster_offset():
    '''Summary - gets some player roste offsets from memory, returns the address in memory

    '''

    pat = b"\x02\x45\x33\xd2\x4d\x8b"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_long(pat_addr-3)
    roster_addr = ((pat_addr - base) + 1 + offset_buffer)
    return (roster_addr+base)


def read_game_info_offset():
    '''Summary - gets some game info offsets in memory
    Returns:
        TYPE: Description
    '''
    #E8 ? ? ? ? 48 8B 15 ? ? ? ? 48 B9 ? ? ? ? ? ? ? ? 44 88 25 ? ? ? ? 
    #pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'
    #pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    #offset_buffer = process.read_int(pat_addr+8)
    #game_info_offset = ((pat_addr - base)  - 244 + offset_buffer)
    #return (0x29B7A70)
    #pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'

    #base game info ptr ref func
    #pat = b'\xE8....\x48\x8B\x15....\x48\xB9........\x44\x88\x25....'
    #pat = b'\x48\x8D\x0D....\xE8....\x48\x8B\x15....\x48\xB9........'

    #E8 ? ? ? ? 48 8B 15 ? ? ? ? 48 B9 ? ? ? ? ? ? ? ? 44 88 25 ? ? ? ? 
    #pat = b'E8....\x48\x8B\x15....\x48\xB9........\x44\x88\x25....'
    

    #pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    #offset_buffer = process.read_int(pat_addr+8+2)
    #game_info_offset = ((pat_addr - base)  -244 + offset_buffer)
    #pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    #offset_buffer = process.read_int(pat_addr+8)

    #game_info_offset = ((pat_addr - base)  - 244 + offset_buffer)
    #game_info_offset = 0x29B7A70
    #log = (":: Found game info offset  -> {}".format(hex(game_info_offset)))
    #log_color(log,fg_color=0,bg_color=traverse_color)
    #print("NEW GAME INFO",game_info_offset+base)

    #return (game_info_offset+base)
    pat = b"\x44\x88\x25....\x66\x44\x89\x25...."
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)

    offset = process.read_long(pat_addr+3)

    game_info = GameInfo()
    delta = pat_addr-base
    new = base + (delta-0x121+offset)-8
    return new

def read_hover_object_offset():
    """Summary
    credit to :https://github.com/joffreybesos/d2r-mapview/
    Returns:
        TYPE: Description
    """

    pat = b'\xc6\x84\xc2.....\x48\x8b\x74.'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat, return_multiple=False)
    offset_buffer = process.read_bytes(pat_addr+3,4)
    offset_buffer_int = int.from_bytes(offset_buffer,'little')
    hover_offset = (offset_buffer_int)-1
    return (hover_offset+base)
    

def read_exp_offset():
    """Summary - get expansion offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/

    """
    #var pattern = "\x48\x8B\x05\x00\x00\x00\x00\x48\x8B\xD9\xF3\x0F\x10\x50\x00";
    #var mask = "xxx????xxxxxxx?";
    #expansion offset scan pattern
    #pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....\x83\x78\x5C.\x0F\x84....\x33\xD2\x41'
    #this works fine, shorter pattern?
    #pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....'
    
    ####
    #pat = b'\x48\x8B\x05....\x48\x8B\xD9\xF3\x0F\x10\x50.'
    
    #pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    #offset_buffer = process.read_int(pat_addr+3)
    #exp_offset = ((pat_addr - base)+7 + offset_buffer)
    #return (exp_offset+base)
    ####

    pat = b"\x48\x8B\x05....\x48\x8B\xD9\xF3\x0F\x10\x50."
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset = process.read_int(pat_addr+3)
    delta = pat_addr-base
    new = base + (delta+7+offset)
    #print('ex',process.read_bytes(new,32))
    return new

def read_menu_data_offset():
    """Summary - get menu data offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    """
    #unit table offset
    #scan pattern
    pat = b"\x41\x0f\xb6\xac\x3f...."
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr-5)
    ui_offset = ((pat_addr - base) + offset_buffer)

    return(ui_offset+base)

def read_ui_settings_offset():
    """Summary - ui settings offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    """


    pat = b"\x40\x84\xed\x0f\x94\x05"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+6)
    ui_settings_offset = ((pat_addr - base) + 10 + offset_buffer)
    return (ui_settings_offset+base)

def read_menu_vis_offset():
    """Summary - menu vis offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    """

    #menu vis offset
    #pat = b'\x8B\x05....\x89\x44\x24\x20\x74\x07'
    #?? search less direct matches?
    pat = b'\x8B\x05....\x89\x44.\x20\x74\x07'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+2)
    menu_offset = ((pat_addr - base) + 6 + offset_buffer)
    return (menu_offset+base)

def populate_offsets(game_info_clist):
    """ Summary - populate memory offsets on initalization
    """
    update_base_offset(game_info_clist)
    game_info_clist.mem.expansion = read_exp_offset()
    game_info_clist.mem.unit = read_unit_offset()
    game_info_clist.mem.game_info = read_game_info_offset()
    game_info_clist.mem.ui_settings = read_ui_settings_offset()
    game_info_clist.mem.menu_vis = read_menu_vis_offset()
    game_info_clist.mem.menu_data = read_menu_data_offset()
    game_info_clist.mem.hover = read_hover_object_offset()
    game_info_clist.mem.roster = read_roster_offset()


# ------------------------------ end of memory offset code ------------------------------ #


def delta_helper(delta, diag, scale, delta_z=0.0):
    """Summary - screen space conversion helper
    Args:
        delta (TYPE): Description
        diag (TYPE): Description
        scale (TYPE): Description
        deltaZ (float, optional): Description
    Returns:
        TYPE: Description
    """
    camera_angle = -26.0 * 3.14159274 / 180.0
    cos = (diag * math.cos(camera_angle) / scale)
    sin = (diag * math.sin(camera_angle) / scale)
    d = ((delta[0] - delta[1]) * cos, delta_z - (delta[0] + delta[1]) * sin)
    return d

def world_to_abs(dest, player):
    """Summary - convert d2 space to absolute screen space centerd in the 1280x720 screen window
    Args:
        dest (TYPE): target point
        player (TYPE): player pos ref
    Returns:
        TYPE: screen coords in ABS space
    """
    w = 1280
    h = 720
    delta = delta_helper(dest-player, math.sqrt(w*w+h*h), 68.5,30)
    x = np.clip(delta[0]-9.5, -638, 638)
    y = np.clip(delta[1]-39.5, -350, 235)
    screen_coords = np.array([x,y])
    return screen_coords

def item_wrapper(item_clist, player, game_info_clist,running_manager):
    """ wrapper for the item scanning process, kills thread on main thread exit
    """
    
    fps = FPS()

    tick = 0
    p_tick = 0
    tick = get_tick(game_info_clist)

    import fpstimer
    timer = fpstimer.FPSTimer(25)

    while running_manager.main:
        tick = get_tick(game_info_clist)        

        if tick != p_tick:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            p_tick=tick
        else:
            p_tick=tick
            continue        
        running_manager.fps3 = fps()
        scan_item_units(item_clist, player, game_info_clist)
        #read_hash_table(game_info_clist)   
        #timer.sleep()
        

def monster_wrapper(monster_clist, player, game_info_clist,running_manager):
    """ wrapper for the monster scanning process, kills thread on main thread exit
    """
    running = game_state.manager_list
    fps = FPS()

    tick = 0
    p_tick = 0
    tick = get_tick(game_info_clist)

    import fpstimer
    timer = fpstimer.FPSTimer(25)

    while running_manager.main:
        
        tick = get_tick(game_info_clist)        

        if tick != p_tick:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            p_tick=tick

        else:
            p_tick=tick
            continue
        running_manager.fps2 = fps()
        scan_monster_units(monster_clist, player, game_info_clist)
        #timer.sleep()

        

def start(running_manager):
    """Summary - start API thread, dispatch reader threads and core loop
    """
    #input manager
    input_thread = Thread(target = interact.process_queue)
    input_thread.start()
    
    #############
    monster_clist = RawArray(game_state.Monster,128)
    item_clist = RawArray(game_state.Item,128)
    object_clist = RawArray(game_state.GameObject,128)
    poi_clist = RawArray(game_state.POI,128)
    game_info_clist = RawValue(game_state.GameInfo)
    area_clist = RawValue(game_state.Area)
    player = RawValue(game_state.Player)
    #############

    game_info_clist.mem.base = game_state.base
    running = game_state.manager_list

    #populate memory data
    populate_offsets(game_info_clist)
    print("MEM GAME INFO",game_info_clist.mem.game_info)
    log = ("API THREAD STARTED")
    log_color(log,fg_color=note_color)
    needs_punit = True
    
    #start scanning for monsters in a new process
    monster_proc = Process(target=monster_wrapper, args=(monster_clist,player,game_info_clist,running_manager,))
    #monster_proc.start()
    
    #start scanning for items in a new process
    item_proc = Process(target=item_wrapper, args=(item_clist,player,game_info_clist,running_manager,))
    #item_proc.start()
    
    #start scanning for objects in a new process
    #object_proc = Process(target=object_wrapper, args=(object_clist,player,game_info_clist,running_manager,))
    #object_proc.start()
    

    #core plugin loop
    core_proc = Process(target=core.main, args=(item_clist,monster_clist,object_clist,player,game_info_clist,running_manager,))
    #core_proc.start()

    #start the gui
    gui_proc = Process(target=overlay, args=(                                        
                                             monster_clist,
                                             item_clist,
                                             object_clist,
                                             poi_clist,
                                             game_info_clist,
                                             player,
                                             area_clist,
                                             running_manager
                                             ))
    gui_proc.start()
    
    fps = FPS()
    current_level = None
    #interact.enter_game_hell()

    tick = get_tick(game_info_clist)
    p_tick = 0
    game_info_clist.tick_lock = 0
    area_clist.clusters_ready=0         
    game_info_clist.loaded=0
    area_clist.loaded=0

    proc_started = 0
    

    while running_manager.main:
        
        tick = get_tick(game_info_clist)
        running_manager.tick_lock = tick

        if tick != p_tick:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            game_info_clist.tick_lock = 1
            p_tick=tick
        else:
            game_info_clist.tick_lock = 0
            p_tick=tick
            continue            

        in_game = get_any_ui('InGame',game_info_clist)
        game_info_clist.in_game = in_game
        running_manager.fps1=fps()

        if in_game:
            if needs_punit:
                try:
                    #get new offsets
                    populate_offsets(game_info_clist)
                    game_info_struct = read_game_info()
                    game_info_clist.game_name = game_info_struct.game_name_buffer
                    game_info_clist.game_pass = game_info_struct.game_pass_buffer
                    game_info_clist.ip = game_info_struct.game_ip_buffer
                    read_hash_table(game_info_clist)
                    needs_punit = False
                    if proc_started == 0:
                        item_proc.start()
                        monster_proc.start()
                        core_proc.start()
                        proc_started = 1

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    needs_punit = True
                    log = ("Error getting punit")
                    log_color(log,fg_color=warning_color)
            else:
                if current_level != game_info_clist.id or current_level is None:   
                    if needs_punit == False: 
                        log = ("New Map!")
                        log_color(log,fg_color=important_color)                   
                        area_clist.loaded=0
                        update_player_unit(game_info_clist)
                        print(int(game_info_clist.seed),int(game_info_clist.id),int(game_info_clist.difficulty))
                        update_map(int(game_info_clist.seed),int(game_info_clist.id),int(game_info_clist.difficulty),poi_clist, game_info_clist, area_clist)
                        current_level = game_info_clist.id
                        area_clist.loaded=1
                else:
                    #print(game_info_clist.offset.y)
                    update_player_unit(game_info_clist) 
        else:
            #we have left game, reset
            needs_punit = True
            current_level = None
            game_info_clist.id = -999
            game_info_clist.loaded=0
            area_clist.loaded=0

    #shut down session
    log = ("API THREAD SHUTDOWN")
    log_color(log,fg_color=note_color)
    interact.halt()
    input_thread.join()

    #monster_proc.join()
    #item_proc.join()
    #object_proc.join()
    #gui_proc.join()
    #core_proc.join()
    monster_proc.terminate()
    item_proc.terminate()
    #object_proc.terminate()
    gui_proc.terminate()
    core_proc.terminate()



def get_map_d2api(seed:int, mapid:int, difficulty:int):
    """Summary - alternative to using a server, gets map data from a local d2 install
        uses d1mapapi_piped.exe from: https://github.com/soarqin/D2RMH
    Args:
        seed (int): map seed
        mapid (int): location id
        difficulty (int): 1 2 3 ( norm nm hell )
    Returns:
        TYPE: get raw map data
    """
    #this requires the d2mapapi_piped.exe to be used with a local install of diablo2
    #prob just use the server instead, falls back on error

    map_api_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)),"d2mapapi_piped.exe")
    request = pack('<III', seed, difficulty, mapid)
    d2location = "C:/Program Files/Diablo II"
    p = subprocess.run([map_api_exe,d2location], input=request, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
    json = None
    json = p.stdout.replace(b'\x00', b'').decode('ascii','ignore').replace("N#","")
    printable = set(string.printable)
    s = "".join(filter(lambda c: c in printable, json))
    #bit of a hack to clean some extra bytes on the json header?
    filtered = s[s.find('{'):]
    if json is not None:
        return orjson.loads(filtered)
    else:
        return None


def split(data, sep):
    """Summary segment up map data for the correct formatting for collisions/path finding
    Args:
        a (TYPE): data
        sep (TYPE): delimiter
    Yields:
        TYPE: Chop up our map xx
    """
    pos = i = 0
    while i <len(data):
        if data[i:i+len(sep)] == sep:
            yield data[pos:i]
            pos = i = i+len(sep)
        else:
            i += 1
    yield data[pos:i]


def update_map(seed:int, mapid:int,difficulty:int,poi_clist, game_info_clist, area_clist):
    """Summary
    Args:
        seed (int): current map seed read from memory - 123456
        mapid (int): current in game map number - ie 79 for durance of hate
        difficulty (int): normal, nm, hell (0,1,2)
    Returns:
        TYPE: generates map json
    """
    #handle for shared memory
    #map_list  = shared_memory.ShareableList(name="map_list")
    
    _area_clist=game_state.Area()
    area_clist.map = _area_clist.map

    try:
        #try and get local map api data
        map_api_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)),"d2mapapi_piped.exe")

        json_data = get_map_d2api(seed,mapid,difficulty)
        if json_data is None:
            raise ValueError
        log = ("Got data from           -> {}".format(map_api_exe))
        log_color(log,fg_color=mem_color)

    except Exception as e:
        print(e)
        #fall back to server data
        log = ("Unable to use d2mapapi_piped.exe, falling back to the server...")
        log_color(log,fg_color=important_color)
        base_url='http://34.69.54.92:8000'
        url=base_url+'/'+str(seed)+'/'+str(difficulty)+'/'+f'{str(mapid)}/1'

        log = ("Got data from           -> {}".format(url))
        log_color(log,fg_color=mem_color)
        resp = requests.get(url=url)
        json_data = resp.json()

    map_offset_x = json_data['offset']['x']
    map_offset_y = json_data['offset']['y']

    map_offset = np.array([map_offset_x,map_offset_y])

    game_info_clist.offset = game_state.Point(float(map_offset_x),float(map_offset_y))
    area_clist.origin = game_state.Point(map_offset_x,map_offset_y)

    row = []
    idx = 0
    for poi in area_clist.poi:
        poi.name = b''
        poi_clist[idx].name=b''
        idx+=1

    

    if json_data is not None:
        map_crop = json_data['crop']
        obj_str = "|"
        poi_str = "|"

        #initalize/clear area lists
        for poi in area_clist.poi:
            poi = game_state.POI()
        for obj in area_clist.objects:
            poi = game_state.GameObject()

        #these are mostly garbage and not useful, its map decorator stuff
        idx = 0
        if json_data['objects'] is not None:
            for key in json_data['objects']:
                value = json_data['objects'][key]
                name = objects[int(key)]
                obj_str+=name+"|"
                for instance in value:
                    offset_x =instance['x']
                    offset_y=instance['y']
                    pos =np.array([offset_x,offset_y])
                    pos_area = pos-map_offset
                    #need to make this do somethings
                    flag = 1
                    new_obj = {"position":pos,"flag":flag,"name":name,"pos_area":pos_area}
                    area_clist.objects[idx] = game_state.GameObject()
                    area_clist.objects[idx].name = name.encode('utf-8')
                    area_clist.objects[idx].pos = game_state.Point(offset_x,offset_y)
                    area_clist.objects[idx].area_pos = game_state.Point(pos_area[0],pos_area[1])
                    idx+=1
                    break

        #static map objects
        idx = 0
        if json_data['objects'] is not None:
            for key in json_data['objects']:
                value = json_data['objects'][key]
                name = objects[int(key)]
                poi_str+=name+"|"
                for instance in value:
                    offset_x =instance['x']
                    offset_y=instance['y']
                    pos =np.array([offset_x,offset_y])
                    pos_area = pos-map_offset
                    #need to make this do somethings
                    flag = 1
                    new_poi = {"position":pos,
                               "type":1,
                               "label":name,
                               "pos_area":pos_area,
                               "is_npc":False,
                               "is_portal":False}
                    area_clist.poi[idx] = game_state.POI()
                    area_clist.poi[idx].name = name.encode('utf-8')
                    area_clist.poi[idx].pos = game_state.Point(offset_x,offset_y)
                    area_clist.poi[idx].area_pos = game_state.Point(pos_area[0],pos_area[1])
                    idx+=1

                    break

        #convert exits to a uniform format in poi
        if json_data['exits'] is not None:
            for key in json_data['exits']:
                value = json_data['exits'][key]
                name = areas[int(key)]
                poi_str+=name+"|"
                is_portal = value['isPortal']
                offset_x = value['offsets'][0]['x']
                offset_y = value['offsets'][0]['y']
                pos =np.array([offset_x,offset_y])
                pos_area = pos-map_offset
                new_poi = {"position":pos,
                           "type":1,
                           "label":name,
                           "pos_area":pos_area,
                           "is_npc":False,
                           "is_portal":is_portal}
                area_clist.poi[idx] = game_state.POI()
                area_clist.poi[idx].name = name.encode('utf-8')
                area_clist.poi[idx].pos = game_state.Point(offset_x,offset_y)
                area_clist.poi[idx].area_pos = game_state.Point(pos_area[0],pos_area[1])
                area_clist.poi[idx].is_exit = 1
                idx+=1

        #convert npcs to a uniform format
        if json_data['npcs'] is not None:
            for key in json_data['npcs']:
                if int(key)<738:
                    value = json_data['npcs'][key]
                    name = get_mob_name[int(key)]
                    poi_str+=name+"|"
                    is_portal=False
                    is_npc=True
                    offset_x = value[0]['x']
                    offset_y = value[0]['y']
                    pos = np.array([offset_x,offset_y])
                    pos_area = pos-map_offset
                    new_poi = {"position":pos,
                               "type":1,
                               "label":name,
                               "pos_area":pos_area,
                               "is_npc":is_npc,
                               "is_portal":False}
                    area_clist.poi[idx] = game_state.POI()
                    area_clist.poi[idx].name = name.encode('utf-8')
                    area_clist.poi[idx].pos = game_state.Point(offset_x,offset_y)
                    area_clist.poi[idx].area_pos = game_state.Point(pos_area[0],pos_area[1])
                    idx+=1

        map_id = json_data['id']
        map_data = json_data['mapData']
        map_size = json_data['size']
        map_decode = list(split(map_data,sep=[-1]))

        map_decode = map_decode[:-1]

        idx =0
        for poi in area_clist.poi:
            poi_clist[idx] = area_clist.poi[idx]
            idx+=1

        nodes = []
        col_grid = []

        if map_data is not None:
            area_clist.mini_map_size = game_state.Point(int(map_size['width']), int(map_size['height']))
            walkable = True
            y = 0
            for ele in map_decode:
                x = 0
                row = []
                for i in range(len(ele)):
                    if walkable:
                        for j in range(ele[i]):
                            nodes.append([x,y-1,walkable])
                            row.append(0)
                            #collision_grid[y][x] = 0
                            area_clist.map[y-1][x] = 0 
                            x+=1
                    if not walkable:
                        for j in range(ele[i]):
                            nodes.append([x,y-1,walkable])
                            row.append(-1)
                            #collision_grid[y][x] = -1
                            area_clist.map[y-1][x] = -1 
                            x+=1

                    walkable = not walkable
                y+=1

                x=0
                walkable = True
        
        w = int(area_clist.mini_map_size.x)
        h = int(area_clist.mini_map_size.y)

        log = ("Loaded map              -> {}".format(area_list[map_id]))
        log_color(log,fg_color=mem_color)
        log = ("Number of POI           -> {}".format(len(area_clist.poi)))
        log_color(log,fg_color=mem_color)
        log = ("{}".format(poi_str))
        log_color(log,fg_color=mem_color)
        log = ("Number of OBJ           -> {}".format(len(area_clist.objects)))
        log_color(log,fg_color=mem_color)
        log = ("{}".format(obj_str))
        log_color(log,fg_color=mem_color)


        w = int(area_clist.mini_map_size.x)
        h = int(area_clist.mini_map_size.y)

        features_mod = np.array([[0,0]])
        tmp_clusters = np.array([[0,0]])
        tile_size = 32

        t_start_1 = time.time()

        j=0
        i=0

        while i < w:
            j=0
            while j < h:
                if area_clist.map[j][i] == -1:
                    features_mod = np.concatenate((features_mod, [np.array([int(i),int(j)])]))
                j+=int(tile_size)
            i+=int(tile_size)



        t_start = time.time()
        features_mod[0,0:-1,...] = features_mod[0,1:,...]
        tmp_clusters=np.delete(features_mod,0,0)

        idx=0
        for c in tmp_clusters:
            area_clist.clusters[idx]= game_state.Point_i(c[0],c[1])
            if(idx+1>512):
                break
            idx+=1
        area_clist.cluster_count = len(tmp_clusters)
        area_clist.clusters_ready=1

        area_clist.current_area = (area_list[map_id]).encode('utf-8')
        area_clist.level = int(map_id)



def get_any_ui(key,game_info_clist):

    ui = game_info_clist.mem.ui_settings
    bytes_read = process.read_bytes(ui-10,31)
    ret = unpack('??????xx???????xxxx?x?xx????x??', bytes_read)
    names = {
            'InGame':0,
            'Inventory':1,
            'Character':2,
            'SkillSelect':3,
            'SkillTree':4,
            'Chat':5,
            'NpcInteract':6,
            'EscMenu':7,
            'Map' : 8,
            'NpcShop' :9,
            'GroundItems' :10,
            'Anvil' : 11,
            'QuestLog' :12,
            'Waypoint' : 13,
            'Party' : 14,
            'Stash' : 15,
            'Cube' : 16,
            'PotionBelt' :17,
            'Help' : 18,
            'Portraits' :19,
            'MercenaryInventory' : 20,
            'Help' : 21,
            }

    return ret[names[key]]


# ------------------------------ converting to struct reads ------------------------------ #


def read_into(addr,struct):
    """copy struct from a adress, to a ctype struct
    
    Args:
        addr (TYPE): memory adrress
        struct (TYPE): ctype struct 
    
    Returns:
        BOOL: sucess
    """
    try:
        read_buff = process.read_bytes(addr,sizeof(struct))
        memmove(addressof(struct), read_buff[:], sizeof(struct))
        return True 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()

        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        log = ("WARNING MEMORY ERROR")
        log_color(log,fg_color=warning_color)
        traceback.print_tb(exc_tb, limit=8, file=sys.stdout)
        print(exc_tb)
        print(inspect.stack()[1].function)
        os._exit(0)
        return False

def print_fields(struct):
    """dump a struct to stdout
    
    Args:
        struct (TYPE): struct to print
    """
    out = ""
    for field_name, field_type in struct._fields_:
        out +=str(field_name)+": "+str(getattr(struct, field_name))+", "
    print(out+'\n')


def _get_tick(game_info_clist):
    """OLD - to be removed
    
    """
    try:
        game_info_addr = game_info_clist.mem.game_info
        game_info = GameInfo()
        read_into_result = read_into(game_info_addr ,game_info)
        if not read_into_result:
            return 0
        v = game_info.unk1[7]
        print("7",v)
        out = c_uint8()
        read_into(v+16 , out)
        return int.from_bytes(bytes(out),'little')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        log = ("GETTING GAME CLOCK FAILED")
        log_color(log,fg_color=warning_color)

        return 0

tt = 0

def __get_tick(game_info_clist):
    """in game D2r main 3D frame ticks, used to synchronize reads, and prevent loading stuff from memory during loading screens
    
    Args:
        game_info_clist (TYPE): Description
    
    Returns:
        TYPE: uint8 tick 0 or 8 on frame update, not sure why, or what I'm really reading here
    """
    global tt
    game_info_addr = game_info_clist.mem.game_info
    game_info = GameInfo()
    if tt == 0x08:
        tt = 0x0
    else:
        tt = 0x08

    return tt
    '''
    while 1:
        read_into_result = read_into(game_info_addr ,game_info)
        if not read_into_result:
            print("FAILED")
            return False
        game_name = game_info.game_name_buffer
        game_pass = game_info.game_pass_buffer
        region = game_info.region_buffer
        game_ip = game_info.game_ip_buffer
        #print(game_name,game_pass,region,game_ip)
        s = ""
        
        v = game_info.unk1[7]
        out = c_uint8()
        read_into(v+16 , out)
        if out.value > 0:
            return 0x08
        #s += str(out)+" "
        #print(s)
        return 0
    '''

def get_tick(game_info_clist):
    """in game D2r main 3D frame ticks, used to synchronize reads, and prevent loading stuff from memory during loading screens
    
    Args:
        game_info_clist (TYPE): Description
    
    Returns:
        TYPE: uint8 tick 0 or 8 on frame update, not sure why, or what I'm really reading here
    """
    global tt
    game_info_addr = game_info_clist.mem.game_info
    game_info = GameInfo()
    
    while 1:
        read_into_result = read_into(game_info_addr ,game_info)
        if not read_into_result:
            print("FAILED")
            return False
        v = game_info.unk1[17]
        #print(process.read_bytes(v,64))
        out = c_uint8()
        #read_into(v+16+16 , out)   
        #read_into(v+16 , out)   
        read_into(v+16 , out)   

        if out.value > 0:
            return 0x08
        #s += str(out)+" "
        #print(s)
        return 0



def read_hash_table(game_info_clist):    
    """inital memory scan of unit table
    
    Args:
        game_info_clist (TYPE): Description
    """
    addr_list = [0x80] #128
    units = []

    addr = game_info_clist.mem.unit
    read_rosters(game_info_clist)
    
    unit_type = 1#npcs/monsters
    monster_addr = addr +(128*8*unit_type)

    for i in range(128):
        paddr = process.read_longlong(monster_addr+(i*8))
        while paddr:
            unit = UnitAny()
            read = process.read_bytes(paddr,sizeof(unit))
            memmove(addressof(unit), read[:], sizeof(unit))
            read_unit(unit,game_info_clist)
            paddr = unit.next_ptr

    unit_type = 2#objects
    object_addr = addr +(128*8*unit_type)

    for i in range(256):
        paddr = process.read_longlong(object_addr+(i*8))
        while paddr:
            unit = UnitAny()
            read = process.read_bytes(paddr,sizeof(unit))
            memmove(addressof(unit), read[:], sizeof(unit))
            read_unit(unit,game_info_clist)
            paddr = unit.next_ptr

    unit_type = 4#items
    item_addr = addr +(128*8*unit_type)


    for i in range(128):
        paddr = process.read_longlong(item_addr+(i*8))
        while paddr:
            unit = UnitAny()
            read = process.read_bytes(paddr,sizeof(unit))
            memmove(addressof(unit), read[:], sizeof(unit))
            read_unit(unit,game_info_clist)
            paddr = unit.next_ptr
    
def scan_object_units(game_info_clist):
    """update object units
    
    Args:
        game_info_clist (TYPE): Description
    """
    addr = game_info_clist.mem.unit

    unit_type = 2#objects
    object_addr = addr +(128*8*unit_type)

    for i in range(256):
        paddr = process.read_longlong(object_addr+(i*8))
        while paddr:
            unit = UnitAny()
            read = process.read_bytes(paddr,sizeof(unit))
            memmove(addressof(unit), read[:], sizeof(unit))
            read_unit(unit,game_info_clist)
            paddr = unit.next_ptr


def scan_item_units(item_clist,player,game_info_clist):    
    """inital memory scan of unit table
    
    Args:
        game_info_clist (TYPE): Description
    """
    #addr_list = [0x80] #128
    #units = []
    addr = game_info_clist.mem.unit
    item_addr = addr +(4*1024)

    items = dict()

    for i in range(128):
        
        paddr = process.read_longlong(item_addr+(i*8))

        while paddr:
            
            unit = UnitAny()
            read = process.read_bytes(paddr,sizeof(unit))
            memmove(addressof(unit), read[:], sizeof(unit))
            
            if unit.unit_type == 4:
                item = False
                item = read_item_unit(unit,game_info_clist)
                
                if item is not False:
                    #print_fields(item)
                    items[unit.unit_id] = item
                    

                #next item pointer apparently
                paddr = unit.unk6[8]
                '''                
                #old look up offset...
                paddr = process.read_longlong(paddr+0x150)
                for i in range(13):
                    #trying to find something that matched the correct pointer location
                    print(i ,unit.unk5[i], paddr)
                for i in range(9):
                    print(i, unit.unk6[i], paddr)
                '''                
    idx = 0
    for ite in items:
        item_clist[idx] = items[ite]
        idx +=1
    for i in range(len(items),128):
        item_clist[i].name = b''


    
    

def scan_monster_units(monster_clist, player, game_info_clist):
    """update all units
    
    Args:
        game_info_clist (TYPE): Description
    """
    #start = timer()

    addr = game_info_clist.mem.unit

    unit_type = 1 #npcs/monsters
    monster_addr = addr +(1024*unit_type)

    raw_idx = 0
    updated = []
    mobs = dict()
    skele_count = 0

    for i in range(128):
        paddr = process.read_longlong(monster_addr+(i*8))
        while paddr:
            unit = UnitAny()
            read = process.read_bytes(paddr,sizeof(unit))
            memmove(addressof(unit), read[:], sizeof(unit))
            if unit.unit_type==1:
                m = False
                m = read_monster_unit(unit,game_info_clist)
                if m is not False:
                    mobs[m.unit_id] = m
                    paddr = unit.next_ptr
            else:
                break
    
    sort = (sorted(mobs.items(), key=lambda item: (item[1].dist)))

    for i in range(0,len(sort)):
        monster_clist[i] = sort[i][1]        
    for i in range(len(sort),128):
        monster_clist[i].name = b''

    '''
    end = timer()
    t = end - start
    if t < .006:
        log = ('monster execution time - > '+str(t))
        log_color(log,fg_color=important_color)
    else:
        log = ('monster execution time - > '+str(t))
        log_color(log,fg_color=warning_color)
    '''

def read_unit(unit:UnitAny, game_info_clist):
    """read a unit
    
    Args:
        unit (UnitAny): Description
        game_info_clist (TYPE): Description
    """
    if unit.unit_type == 0:
        read_player_unit(unit,game_info_clist)
    if unit.unit_type == 1:
        return read_monster_unit(unit,game_info_clist)
    if unit.unit_type == 2:
        read_object_unit(unit)
    if unit.unit_type == 4:
        return read_item_unit(unit,game_info_clist)

'''
void ProcessData::readStatList(uint64_t addr, uint32_t unitId, const std::function<void(const StatList &)> &callback) {
    StatList stats;
    if (!READ(addr, stats)) { return; }
    do {
        /* check if this is owner stat or aura */
        if (!unitId || stats.ownerId == unitId) {
            callback(stats);
        }
        if (!(stats.flag & 0x80000000u)) { break; }
        if (!stats.nextListEx || !READ(stats.nextListEx, stats)) { break; }
    } while (true);
}
'''
'''
def read_stat_list(addr, unit_id):
    stats = StatList()
    read_into_result = read_into(addr, stats)

    if not read_into_result:
        return False

    while True:
        if not unit_id or stats.owner_id == unit_id:
            #pass
            #callback stats?
            pass
        if not stats.flag & 0x80000000:
            break
'''

'''
void ProcessData::readPlayerStats(const UnitAny &unit, const std::function<void(uint16_t, int32_t)> &callback) {
    readStatList(unit.statListPtr, 0, [this, &callback](const StatList &stats) {
        if (!(stats.flag & 0x80000000u)) { return; }
        static StatEx statEx[256];
        auto cnt = std::min(255u, uint32_t(stats.fullStat.statCount));
        if (!READN(stats.fullStat.statPtr, statEx, sizeof(StatEx) * cnt)) { return; }
        StatEx *st = statEx;
        st[cnt].statId = 0xFFFF;
        uint16_t statId;
        for (; (statId = st->statId) != 0xFFFF; ++st) {
            if (statId >= 16) { break; }
            callback(statId, statId >= 6 && statId <= 11 ? (st->value >> 8) : st->value);
        }
    });
'''

'''
def read_player_stats(unit:UnitAny):
    pass
'''

def get_skill(id):
    """not implemenented yet
    
    Args:
        id (TYPE): Description
    """
    #not implemeneted
    pass

'''

Skill *ProcessData::getSkill(uint16_t id) {
    if (!currPlayer) { return nullptr; }
    SkillInfo si;
    if (READ(currPlayer->skillPtr, si)) {
        static Skill sk;
        uint64_t ptr = si.firstSkillPtr;
        while (ptr && READ(ptr, sk)) {
            uint16_t skillId;
            READ(sk.skillTxtPtr, skillId);
            if (skillId == id) { return &sk; }
            ptr = sk.nextSkillPtr;
        }
    }
    return nullptr;
}


'''

def update_player_unit(game_info_clist):
    """update the player pos and stats using existing ptrs
    
    Args:
        game_info_clist (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    act = DrlgAct()
    read_into_result = read_into(game_info_clist.ptr.act,act)
    if not read_into_result:
        return False

    path = DynamicPath()
    
    read_into_result = read_into(game_info_clist.ptr.player_path,path)
    if not read_into_result:
        return False

    xf = (path.offset_x / 65535.0)-.5
    yf = (path.offset_y / 65535.0)-.5
    game_info_clist.player.pos_i.x = path.pos_x
    game_info_clist.player.pos_i.y = path.pos_y
    game_info_clist.player.pos.x = float(path.pos_x) + xf
    game_info_clist.player.pos.y = float(path.pos_y) + yf

    
    game_info_clist.player.area_pos.x = (float(path.pos_x) + xf) - float(game_info_clist.offset.x)
    game_info_clist.player.area_pos.y = (float(path.pos_y) + yf) - float(game_info_clist.offset.y)
    game_info_clist.player.pos_float_offset.x = xf
    game_info_clist.player.pos_float_offset.y = yf
    
    #need to add this back in
    #player.hp = process.read_uint(game_info_clist.mem.player_hp) >> 8
    #player.mp = process.read_uint(game_info_clist.mem.player_mp) >> 8

    room1 = DrlgRoom1()
    read_into_result = read_into(path.room1_ptr,room1)
    if not read_into_result:
        return False
    
    room2 = DrlgRoom2()
    read_into_result = read_into(room1.room2_ptr,room2)
    if not read_into_result:
        return False

    level_id = c_uint32()
    read_into_result = read_into(room2.level_ptr + 0x1f8 ,level_id)
    if not read_into_result:
        return False
    #this is our map ID
    game_info_clist.id= level_id

def read_player_unit(unit:UnitAny,game_info_clist):
    """inital player unit lookup
    
    Args:
        unit (UnitAny): Description
        game_info_clist (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    #if (unit.unitId == focusedPlayer) { return; }
    game_info_clist.ptr.act = unit.act_ptr

    act = DrlgAct()

    read_into_result = read_into(unit.act_ptr,act)

    if not read_into_result:
        return False
    map_players[unit.unit_id] = MapPlayer()
    player = map_players[unit.unit_id]

    read_into_result = read_into(unit.union_ptr,game_info_clist.player.name)

    #out = ctypes.cast(game_info_clist.player.name, ctypes.c_char_p )


    if not read_into_result:
        return False


    player.level_changed = False
    player.act = act.act_id
    player.seed = act.seed
    player.difficulty=10
    #print("SEED",player.seed)
    #print(player.seed)
    game_info_clist.seed= act.seed    
    
    difficulty = c_uint8()
    read_into_result = read_into((act.misc_ptr+0x830),difficulty)
    #print(difficulty)
    #print(difficulty)
    #print(difficulty)
    #print(difficulty,"this broke")
    if not read_into_result:
        return False
    game_info_clist.difficulty = difficulty


    # this needs to be reimplemented
    #for stat_id in range(16):
    #    player.stats[stat_id] = c_uint32(1)
    
    path = DynamicPath()
    
    read_into_result = read_into(unit.path_ptr,path)
    if not read_into_result:
        return False

    game_info_clist.ptr.player_path = unit.path_ptr
    

    xf = path.offset_x / 65535.0
    yf = path.offset_y / 65535.0
    game_info_clist.player.pos_i.x = path.pos_x
    game_info_clist.player.pos_i.y = path.pos_y
    game_info_clist.player.pos.x = float(path.pos_x) + xf
    game_info_clist.player.pos.y = float(path.pos_y) + yf
    #print(game_info_clist.player.pos.x, game_info_clist.player.pos.y)



    room1 = DrlgRoom1()
    read_into_result = read_into(path.room1_ptr,room1)
    if not read_into_result:
        return False
    
    room2 = DrlgRoom2()
    read_into_result = read_into(room1.room2_ptr,room2)
    if not read_into_result:
        return False

    level_id = c_uint32()
    read_into_result = read_into(room2.level_ptr + 0x1f8 ,level_id)
    if not read_into_result:
        return False
    #this is our map ID
    game_info_clist.id= level_id

def read_monster_unit(unit:UnitAny, game_info_clist):
    """read monster unit data
    
    Args:
        unit (UnitAny): Description
    
    Returns:
        TYPE: Description
    """
    monster = MonsterData()

    read_into_result = read_into(unit.union_ptr,monster)
    if not read_into_result:
        return False

    is_unique = 0
    is_npc = 0
    name = get_mob_name[unit.txt_file_no]
    path = DynamicPath()

    read_into_result = read_into(unit.path_ptr,path)
    if not read_into_result:
        return False

    x = path.pos_x
    y = path.pos_y
    xf = (path.offset_x / 65535.0)-.5
    yf = (path.offset_y / 65535.0)-.5

    if name in get_is_npc:
        is_npc=1
        #print(name)

    is_unique = (monster.flag & 0x0E) != 0

    if is_unique:
        try:
            name = get_super_unique_name[unit.txt_file_no]
            #print(name)
        except:
            pass

    

    flag = monster.flag
    super_unique_check = (monster.flag & 2)
    if super_unique_check:
        pass

    has_aura = 0

    for i in range(9):
        eid = monster.enchants[i]
        if eid == 30:
            has_aura=True
        #todo!! decode these
        #enchant_string = monster.enchants
    immunities = 0
    immunitiy_string = ""
    
    m = game_state.Monster()
    m.name = name.encode('utf_8')

    area_x = x - game_info_clist.offset.x + xf
    area_y = y - game_info_clist.offset.y + yf

    m.dist = math.dist(np.array([area_x,area_y]),
                       np.array([game_info_clist.player.area_pos.x,game_info_clist.player.area_pos.y]))
    m.mode = monster.last_mode
    m.pos = game_state.Point(x,y)
    m.updated = 1
    m.area_pos = game_state.Point(area_x,area_y)
    m.unit_id = unit.unit_id
    m.text_file_no = unit.txt_file_no
    m.mob_type_str = b'None'
    m.is_npc = is_npc


    return m
    '''
    _fields_ = [("immunities", ctypes.c_char*8),
                ("abs_screen_pos", Point),
                ("type", c_short),
                ("flag", c_short),
                ("text_file_no", c_short),
                ("updated", c_short),
                ]
    '''


    ##TODO - stat read/immunities
'''
    readStatList(unit.statListPtr, unit.unitId, [this, &off, &mon, hasAura, showMI](const StatList &stats) {
        if (stats.stateNo) {
            if (!hasAura) { return; }
            const wchar_t *str = auraStrings[stats.stateNo];
            while (*str) {
                mon.enchants[off++] = *str++;
            }
            return;
        }
        if (!showMI) { return; }
        static StatEx statEx[64];
        auto cnt = std::min(64u, uint32_t(stats.baseStat.statCount));
        if (!READN(stats.baseStat.statPtr, statEx, sizeof(StatEx) * cnt)) { return; }
        StatEx *st = statEx;
        for (; cnt; --cnt, ++st) {
            auto statId = st->statId;
            if (statId >= uint16_t(StatId::TotalCount)) { continue; }
            auto mapping = statsMapping[statId];
            if (!mapping || st->value < 100) { continue; }
            const wchar_t *str = immunityStrings[mapping];
            while (*str) {
                mon.enchants[off++] = *str++;
            }
        }
    });
    mon.enchants[off] = 0;
}
'''
def read_object_unit(unit:UnitAny):
    """read object unit data
    
    Args:
        unit (UnitAny): Description
    
    Returns:
        TYPE: Description
    """
    name = object_list[unit.txt_file_no-1]
    flag = c_uint8()
    read_into_result = read_into(unit.union_ptr+8 ,flag)
    if not read_into_result:
        return False
    path = StaticPath()
    read_into_result = read_into(unit.path_ptr ,path)
    if not read_into_result:
        return False
    obj_type = ""
    if "Shrine" in name:
        obj_type="Shrine"
        #print(name)
    if "Waypoint" in name:
        obj_type="Waypoint"
    if "Portal" in name:
        obj_type="Portal"
    if "Well" in name:
        obj_type="Well"
    if "Chest" in name:
        obj_type="Chest"
    x = path.pos_x
    y = path.pos_y
    mode = unit.mode


def read_rosters(game_info_clist):
    """read roster data
    
    Args:
        game_info_clist (TYPE): Description
    """
    global process
    #roster_offset = read_roster_offset()
    roster_offset = game_info_clist.mem.roster
    roster_data_ptr = process.read_longlong(roster_offset)

    while roster_data_ptr:
        mem = RosterUnit()
        #print(process.read_bytes(roster_data_ptr-3,64))
        read_into(roster_data_ptr,mem)
        name = string_at(byref(mem.name), 16)
        

        class_id = mem.class_id
        level = mem.level
        party = mem.party_id;
        #print(level,class_id)
        #print(class_id)
        #   print(name)
        

        focused_player = mem.unit_id
        #current_player = player
        #print(focused_player)

        roster_data_ptr = mem.next_ptr

'''
void ProcessData::readRosters() {
    uint64_t addr;
    READ(rosterDataAddr, addr);
    while (addr) {
        RosterUnit mem;
        if (!READ(addr, mem)) { break; }
        auto &p = mapPlayers[mem.unitId];
        p.classId = mem.classId;
        p.level = mem.level;
        p.party = mem.partyId;
        memcpy(p.name, mem.name, 16);
        if (/* Battle.Net */ mem.wideName[0] || /* Single-player */ (!mem.posX && mem.unk9[2] == uint32_t(-1))) {
            focusedPlayer = mem.unitId;
            currPlayer = &p;
        } else {
            p.posX = mem.posX;
            p.posY = mem.posY;
            p.act = mem.actId;
        }
        addr = mem.nextPtr;
    }
}
'''

def read_item_unit(unit:UnitAny, game_info_clist):
    """read item unit data
    
    Args:
        unit (UnitAny): Description
    
    Returns:
        TYPE: Description
    """
    #global process
    #copy item memory into struct
    item = ItemData()

    if unit.union_ptr == 0:
        return False

    read_into_result = read_into(unit.union_ptr,item)

    if not read_into_result:
        print("FAILED")
        return False

    txt_name = item_name[int(unit.txt_file_no)]
    item_location = item.item_location
    item_body_location = item.body_location
    world_location = unit.mode
    
    #mode stores the current world location, falling/ground/inv/dropping
    #print(item.location)
    
    if world_location == 3 or world_location == 5 :
        
        #if item.location == 137:

        #print('onground->',unit.mode,txt_name)
        #print_fields(unit)
        #items
        #area_x =  float(pos[0]) #game_state.map_list[8]
        #area_y = float(pos[1]) #game_state.map_list[9]
        #dist = float(dist)

        _item = game_state.Item()
        _item.name = txt_name.encode('utf_8')
        #print_fields(_item)
        return _item
        #_item.pos = game_state.Point(pos[0],pos[1])
        #_item.area_pos = game_state.Point(area_x,area_y)
        #_item.good = 0
        #_item.unit_id = unit.unit_id
        #_item.txt_id = txt_file_no
        #_item.sockets = num_sockets
        #_item.location = item_loc
        #_item.slot = body_loc
        #_item.quality = item_quality
        #_item.quality_str = quality.encode('utf-8')
        #_item_clist[raw_idx] = item
    return False

def read_game_info():
    """base session info, ip, game, pass
    
    Returns:
        TYPE: game info struct
    """
    game_info_addr = read_game_info_offset()
    game_info = GameInfo()
    read_into_result = read_into(game_info_addr ,game_info)
    if not read_into_result:
        log = ("FAILED TO READ GAME INFO")
        log_color(log,fg_color=warning_color)
        return False

    return game_info