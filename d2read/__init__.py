'''proc - handles reading memory from the d2r process.'''

import multiprocessing
from multiprocessing import shared_memory
from multiprocessing import Process

from multiprocessing.sharedctypes import RawArray, RawValue

#import marshal
import random

from os import getpid
import gc

import sys
import os
import time
import string
import collections

from dataclasses import dataclass
import dataclasses
import math

from subprocess import PIPE, Popen
import subprocess
import threading

from struct import unpack
from struct import pack
import copy

import requests
import numpy as np

import yaml
import orjson

import fpstimer

from .utils import FPS

from scipy.spatial.distance import cdist
from scipy.spatial.distance import cityblock
from scipy.spatial import distance
from scipy.cluster.vq import kmeans
from scipy.spatial import KDTree

import pymem
from . import game_state
from .event import events

from .enums import *
from .utils import *

from . import process_data

from .overlay import overlay

import traceback

global running

from .game_state import process
from .game_state import base
from .game_state import handle
from .game_state import module

from collections import namedtuple

from ctypes import *
import ctypes

from . import interact
import time
from threading import Thread


def get_any_offset(keys):
    result = []
    ofl = shared_memory.ShareableList(name='offset_list')
    offset = {
            'base':0,
            'game_info':1,
            'hover':2,
            'exp':3,
            'unit':4,
            'menu_data':5,
            'ui_settings':6,
            'menu_vis':7,
            }
    for i in keys: 
        result.append(game_state.ofl[offset[i]])

    return tuple(result)


def update_base_offset():
    ofl = shared_memory.ShareableList(name='offset_list')
    game_state.ofl[0]=base

# ------------------------------ memory offset code ------------------------------ #

def get_base_offset():
    #ofl = shared_memory.ShareableList(name='offset_list')
    return game_state.ofl[0]


def update_game_info_offset():
    """Summary
    credit to :https://github.com/joffreybesos/d2r-mapview/
    Returns:
        TYPE: Description
    """
    #get game info offset
    pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+8)
    game_info_offset = ((pat_addr - base)  + 7 -256 + 5 + offset_buffer)
    log = ("Found game info offset  ->")
    #log_color(log,target=hex(game_info_offset),fg_color=mem_color,fg2_color=offset_color)
    ofl = shared_memory.ShareableList(name='offset_list')
    game_state.ofl[1]=game_info_offset

def get_game_info_offset():
    ofl = shared_memory.ShareableList(name='offset_list')
    return game_state.ofl[1]

def update_hover_object_offset():
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
    log = ("Found hover offset      ->")
    log_color(log,target=hex(hover_offset),fg_color=mem_color,fg2_color=offset_color)
    game_state.ofl[2]=hover_offset
    
def get_hover_object_offset():
    
    return game_state.ofl[2]

def update_exp_offset():
    """Summary - get expansion offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/

    """
    #expansion offset scan pattern
    pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....\x83\x78\x5C.\x0F\x84....\x33\xD2\x41'
    #this works fine, shorter pattern?
    pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr-4)
    exp_offset = ((pat_addr - base) + offset_buffer)
    log = ("Found exp offset        ->")
    log_color(log,target=hex(exp_offset),fg_color=mem_color,fg2_color=offset_color)
    game_state.ofl[3]=exp_offset

def get_exp_offset():
    ofl = shared_memory.ShareableList(name='offset_list')
    return game_state.ofl[3]    

def update_unit_offset():
    '''Summary - gets some unit table offsets from memory
    credit to :https://github.com/joffreybesos/d2r-mapview/

    '''
    #unit table offset scan pattern
    #global player_offset
    pat = b"\x48\x8d.....\x8b\xd1"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+3)
    player_offset = ((pat_addr - base) + 7 + offset_buffer)
    log = ("Found player offset     ->")
    log_color(log,target=hex(player_offset),fg_color=mem_color,fg2_color=offset_color)
    #starting_offset = player_offset
    game_state.ofl[4]=player_offset

def get_unit_offset():
    return game_state.ofl[4]

def update_menu_data_offset():
    """Summary - get menu data offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    """
    #unit table offset
    #scan pattern
    pat = b"\x41\x0f\xb6\xac\x3f...."
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr-5)
    ui_offset = ((pat_addr - base) + offset_buffer)
    log = ("Found menu data offset  ->")
    log_color(log,target=hex(ui_offset),fg_color=mem_color,fg2_color=offset_color)
    ofl = shared_memory.ShareableList(name='offset_list')
    game_state.ofl[5]=ui_offset

def get_menu_data_offset():
    ofl = shared_memory.ShareableList(name='offset_list')
    return game_state.ofl[5]

def update_ui_settings_offset():
    """Summary - ui settings offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    """
    #unit table offset
    pat = b"\x40\x84\xed\x0f\x94\x05"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+6)
    ui_settings_offset = ((pat_addr - base) + 10 + offset_buffer)
    log = ("Found ui offset         ->")
    log_color(log,target=hex(ui_settings_offset),fg_color=mem_color,fg2_color=offset_color)
    game_state.ofl[6]=ui_settings_offset

def get_ui_settings_offset():

    ofl = shared_memory.ShareableList(name='offset_list')
    return game_state.ofl[6]

def update_menu_vis_offset():
    """Summary - menu vis offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    """
    #menu vis offset
    #pat = b'\x8B\x05....\x89\x44\x24\x20\x74\x07'
    #?? search less direct matches?
    pat = b'\x8B\x05....\x89\x44.\x20\x74\x07'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+2)
    #maybe dont need +6 here?
    menu_offset = ((pat_addr - base) + 6 + offset_buffer)
    log = ("Found menu offset       ->")
    #log_color(log,target=hex(menu_offset),fg_color=mem_color,fg2_color=offset_color)
    game_state.ofl[7]=menu_offset

def get_menu_vis_offset():
    return game_state.ofl[7]

def get_player_unit_offset():
    return game_state.ofl[8]

def get_player_path_offset():
    return game_state.ofl[9]

def populate_offsets(offset_clist):
    """ Summary - populate memory offsets on initalization

    """
    update_base_offset()
    update_exp_offset()
    update_unit_offset()
    update_game_info_offset()
    update_ui_settings_offset()
    update_menu_vis_offset()
    update_menu_data_offset()
    update_hover_object_offset()

# ------------------------------ end of memory offset code ------------------------------ #

def update_player_info(game_info_clist, player):
    """update player volatile
    [player_list, name, lvl, exp, world_x, worly_y, area_x, area_y, offset_x, offset_y, hp, mp, skil, skil]

    Args:
        key (TYPE): text name for data
    """
    
    global base
    global process


    path_addr = game_state.ofl[9]
    bytes_read = process.read_bytes(path_addr,8)
    xf,x,yf,y = unpack('HHHH', bytes_read)
    dx = float(xf) / 65535.0
    dy = float(yf) / 65535.0
    #world pos
    player.pos.x = x + dx
    player.pos.y = y + dy

    #area pos
    player.area_pos.x = x + dx - game_info_clist.offset.x
    player.area_pos.y = y + dy - game_info_clist.offset.y

    player.pos_float_offset.x = dx
    player.pos_float_offset.y = dy
    #health + mp
    player.hp = process.read_uint(game_state.ofl[10]) >> 8
    player.mp = process.read_uint(game_state.ofl[11]) >> 8



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

def shutdown():
    """Summary - end API thread
    """
    global running
    running = False
    log = ("API THREAD SHUTDOWN")
    log_color(log)

def cluster_map_data(area_clist):
    """Summary - clusters map data
    Args:
        nodes (TYPE): Description
    """
    pass

def monster_wrapper(raw_list, player, game_info_clist,running_manager):
    """ wrapper for the monster scanning process, kills thread on main thread exit
    """
    game_state.update()
    running = game_state.manager_list
    fps = FPS()

    tick = 0
    p_tick = 0
    tick = get_tick()

 

    
    while running_manager.main:
        tick = get_tick()        

        if tick != p_tick and tick == 0x08:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            p_tick=tick
        else:
            p_tick=tick
            continue
        running_manager.fps2 = fps()
        update_monster_list(raw_list, player)
    
def item_wrapper(item_clist, player, game_info_clist,running_manager):
    """ wrapper for the item scanning process, kills thread on main thread exit
    """
    game_state.update()
    running = game_state.manager_list
    fps = FPS()

    tick = 0
    p_tick = 0
    tick = get_tick()

    while running_manager.main:
        tick = get_tick()        

        if tick != p_tick and tick == 0x08:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            p_tick=tick
        else:
            p_tick=tick
            continue        
        
        running_manager.fps3 = fps()
        update_item_list(item_clist, player)


def object_wrapper(object_clist, player, game_info_clist,running_manager):
    """ wrapper for the item scanning process, kills thread on main thread exit
    """
    game_state.update()
    running = game_state.manager_list
    fps = FPS()

    tick = 0
    p_tick = 0
    tick = get_tick()

 

    while running_manager.main:
        tick = get_tick()        

        if tick != p_tick and tick == 0x08:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            p_tick=tick
        else:
            p_tick=tick
            continue        

        running_manager.fps4 = fps()
        update_object_list(object_clist, player)

def start(running_manager):
    """Summary - start API thread, dispatch reader threads and core loop
    """

    input_thread = Thread(target = interact.process_queue)
    input_thread.start()
    
    
    #############
    monster_clist = RawArray(game_state.Monster,128)
    item_clist = RawArray(game_state.Item,128)
    object_clist = RawArray(game_state.GameObject,128)
    poi_clist = RawArray(game_state.POI,128)
    game_info_clist = RawValue(game_state.GameInfo)
    area_clist = RawValue(game_state.Area)
    #
    player = RawValue(game_state.Player)
    #player_clist = RawValue(game_state.POI,1)
    offset_clist = RawArray(game_state.POI,1)
    #############

    game_state.update()

    #map_list  = game_state.map_list
    #player_list = game_state.player_list
    ofl = game_state.ofl
    running = game_state.manager_list

    timer = fpstimer.FPSTimer(60)    

    populate_offsets(offset_clist)
    log = ("API THREAD STARTED")
    log_color(log,fg_color=note_color)
    needs_punit = True

    #start scanning for monsters in a new process
    monster_proc = Process(target=monster_wrapper, args=(monster_clist,player,game_info_clist,running_manager,))
    monster_proc.start()

    #start scanning for items in a new process
    item_proc = Process(target=item_wrapper, args=(item_clist,player,game_info_clist,running_manager,))
    item_proc.start()

    #start scanning for objects in a new process
    object_proc = Process(target=object_wrapper, args=(object_clist,player,game_info_clist,running_manager,))
    object_proc.start()

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
    timer = fpstimer.FPSTimer(60)
    current_level = None
    
    #interact.enter_game_hell()

    
    tick = get_tick()
    p_tick = 0
    game_info_clist.tick_lock = 0
    area_clist.clusters_ready=0         
    game_info_clist.loaded=0
    area_clist.loaded=0
    while running_manager.main:

        tick = get_tick()

        if tick != p_tick and tick == 0x08:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            game_info_clist.tick_lock = 1
            p_tick=tick
        else:
            game_info_clist.tick_lock = 0
            p_tick=tick
            continue            

        in_game = get_any_ui('InGame')
        game_info_clist.in_game = in_game
        running_manager.fps1=fps()

        if in_game:
            
            if needs_punit == False:
                update_current_level(game_info_clist)

            if needs_punit:
                #get new offsets
                try:
                    populate_offsets(offset_clist)
                    update_player_offset(game_info_clist, player)
                    update_game_info(game_info_clist, player)    
                    update_player_info(game_info_clist, player)
                    update_current_level(game_info_clist)
                    update_game_ip(game_info_clist)
                    update_game_name(game_info_clist)
                    update_game_pass(game_info_clist)
                    update_current_level(game_info_clist)
                    needs_punit = False

                except:
                    needs_punit = True
                    pass
                


            else:

                if current_level != game_info_clist.id or current_level is None:
                    if needs_punit == False:
                        log = ("New Map!")
                        log_color(log,fg_color=important_color)       
                        game_info_clist.loaded=0
                        area_clist.loaded=0
                        update_map(int(game_info_clist.seed),int(game_info_clist.id),int(game_info_clist.difficulty),poi_clist, game_info_clist, area_clist)
                        current_level = game_info_clist.id
                        area_clist.loaded=1


                else:
                    update_player_info(game_info_clist, player)
                
        else:
            needs_punit = True
            current_level = None
            game_info_clist.id = -999
            game_info_clist.loaded=0
            area_clist.loaded=0
    
    interact.halt()
    input_thread.join()
    monster_proc.join()
    item_proc.join()
    object_proc.join()
    gui_proc.join()
    #monster_proc.terminate()
    #item_proc.terminate()
    #object_proc.terminate()
    #gui_proc.terminate()


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

    except:
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

    game_info_clist.offset = game_state.Point()
    game_info_clist.offset.x = map_offset_x
    game_info_clist.offset.y = map_offset_y

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
        #print(map_decode)
        


        idx =0
        for poi in area_clist.poi:
            poi_clist[idx] = area_clist.poi[idx]
            idx+=1

        nodes = []
        col_grid = []

        #collision_grid = np.empty([int(map_size['height']),int(map_size['width'])], dtype=np.int)
        

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
        '''
        for i in range(w):
            l = ""
            for j in range(h):
                l += str(area_clist.map[i][j]) +' '
            print(l)
            print("\n")
        '''

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
        aspect_h = h/w
        aspect_w = w/h

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


def read_loot_cfg():
    """Summary - read yaml loot cfg
    """
    with open("Z:/botty-r-latest/src/read_mem/item_filter.yaml", "r") as stream:
        try:
            loot_filter = yaml.safe_load(stream)
            #print(loot_filter)
            '''
            for category in loot_filter:
                print(str(category))
                #for item in loot_filter.get(category):
                print(loot_filter.get(category))
            '''
                #for value in key:
                #   print(str(value))
            loot_data = loot_filter
        except yaml.YAMLError as exc:
            print(exc)


def get_in_game_flag():
    """Summary - check if we are ingame, fast check outside of all the other data reading for the UI
    
    Returns:
        TYPE: int 
    """
    base, offset = get_any_offset(['base','ui_settings'])
    ui = base + offset
    bytes_read = process.read_bytes(ui-10,1)

    return int.from_bytes(bytes_read,'little')


def get_last_hovered(game_info_clist):
    """Summary - get last hovered object and check unit tables for a match
    """
        
    base, offset = get_any_offset(['base','hover'])
    
    is_hovered = process.read_int(offset+base+0x00)
    is_tooltip = process.read_int(offset+base+0x01)

    hovered_unit_type = process.read_int(offset+base+0x03)
    hid =process.read_uint(offset+base+0x08)
    
    game_info_clist.hovered_item = game_state.Item()
    game_info_clist.hovered_monster = game_state.Monster({})
    

    if is_hovered == 1 or is_hovered == 257:
        game_info_clist.hovered_id = hid

        if hovered_unit_type == 1024:
            for di in game_state.items:
                item = game_state.items[di]
                if item.unit_id == hid:
                    game_info_clist.hovered_item = item
                    
                    break
        
        elif hovered_unit_type == 256:
            if game_state.monsters is not None:
                for key in game_state.monsters:
                    m = game_state.monsters[key]
                    if m.unit_id == hid:
                        game_info_clist.hovered_monster = m

                        break

    
                    

def update_player_offset(game_info_clist, player):
    """Summary - scan for player unit as a starting point for all relevant memory offsets
    credit to :https://github.com/joffreybesos/d2r-mapview/
    Args:
        loops (TYPE): iterations

    Returns:
        TYPE: sets the global player unit offset
    """
    loops = 128
    ofl = shared_memory.ShareableList(name='offset_list')
    base, starting_offset, exp_offset = get_any_offset(['base','unit','exp'])
    
    found = False

    attempts=0
    name = ""
    new_offset=0

    #player_unit = 0


    for i in range(loops):
        
        new_offset = (starting_offset)+(i*8)
        start_addr = base + new_offset
        player_unit = process.read_longlong(start_addr)

        while player_unit>0:

            p_inventory = player_unit+0x90
            inventory = process.read_longlong(p_inventory)
            if(inventory):

                exp_char = process.read_ushort(base+exp_offset)
                base_check = process.read_ushort(inventory+0x30) !=1
                if(exp_char):
                    base_check = process.read_ushort(inventory+0x70) !=0

            if(base_check):

                log = ("Found inventory offset  ->")
                log_color(log,target=hex(base-inventory),fg_color=mem_color,fg2_color=offset_color)

                if(exp_char):
                    log = ("Char Type               ->")
                    log_color(log,target="Expansion",fg_color=mem_color,fg2_color=offset_color)
                else:
                    log = ("Char Type               ->")
                    log_color(log,target="Classic",fg_color=mem_color,fg2_color=offset_color)


                p_act = player_unit+0x20
                act_addr = process.read_longlong(p_act)
                map_seed_addr = act_addr +0x14
                map_seed = -1

                map_seed = process.read_uint(map_seed_addr)

                    
            
                p_path = player_unit+0x38
                path_addr = process.read_longlong(p_path)

                x_pos = process.read_ushort(path_addr+0x02)
                y_pos = process.read_ushort(path_addr+0x06)

                p_unit_data = player_unit +0x10
                player_name_addr = process.read_longlong(p_unit_data)
                
                #
                for q in range(1,16):
                    name = name + str(chr(process.read_uchar(player_name_addr+q-1)))

                if(x_pos> 0 and y_pos >0 and len(str(map_seed))>6):
                    
                    log = ("Found player name       ->")
                    log_color(log,target=name,fg_color=mem_color,fg2_color=important_color)

                    log = ("Found map seed          ->")
                    log_color(log,target=str(map_seed),fg_color=mem_color,fg2_color=important_color)

                    found = True
                    path_addr = path_addr
                    game_state.ofl[8] = new_offset
                    game_state.ofl[9] = path_addr
                    return True

            new_offset = (player_unit+0x150)-base
            player_unit = process.read_longlong(player_unit +0x150)

def update_current_level(game_info_clist):
    """Summary
    """

    player_unit = game_state.ofl[8]
    #base = get_base_offset()
    base = game_state.ofl[0]

    startingAddress = base + player_unit
    playerUnit = process.read_ulonglong(startingAddress)
    pUnitData = playerUnit + 0x10
    #get the level number
    pPathAddress = playerUnit + 0x38
    pPath = process.read_ulonglong(pPathAddress)
    pRoom1 = pPath + 0x20
    pRoom1Address = process.read_ulonglong(pRoom1)
    pRoom2 = pRoom1Address + 0x18
    pRoom2Address = process.read_ulonglong(pRoom2)
    pLevel = pRoom2Address + 0x90
    pLevelAddress = process.read_ulonglong(pLevel)
    dwLevelNo = pLevelAddress + 0x1F8
    levelNo = process.read_uint(dwLevelNo)
    level_addr = dwLevelNo
    
    #game_state.map_list[0] = str(area_list[levelNo])
    #game_state.map_list[1] = int(levelNo)
    name = str(area_list[levelNo])
    game_info_clist.name = name.encode('utf-8')
    game_info_clist.id = levelNo


def update_game_info(game_info_clist, player):
    """Summary

    Returns:
        TYPE: Description
    """


    base = get_base_offset()
    player_unit = get_player_unit_offset()
    path_addr = get_player_path_offset()

    startingAddress = base + player_unit
    playerUnit = process.read_ulonglong(startingAddress)
    pUnitData = playerUnit + 0x10
    try:
        playerNameAddress = process.read_ulonglong(pUnitData)
    except:
        #just so we really know
        print("FAILED")
        print("FAILED")
        print("FAILED")
        print("FAILED")
        print("FAILED")
        print("FAILED")
        return False
        pass
    if(playerNameAddress):
        playerName = process.read_string(playerNameAddress)

        player.name = playerName.encode('utf-8')


    pStatsListEx = process.read_ulonglong(playerUnit+0x88)
    statPtr = process.read_ulonglong(pStatsListEx+0x30)
    statCount = process.read_ulonglong(pStatsListEx+0x38)

    experience=0

    for i in range(statCount):

        statOffset = (i-1) * 8
        statEnum = process.read_ushort(statPtr + 0x2 + statOffset)

        if (statEnum == 12):
            player_level = process.read_uint(statPtr + 0x4 + statOffset)
        if (statEnum == 13):
            experience = process.read_uint(statPtr + 0x4 + statOffset)
        if (statEnum == 6):
            hp = process.read_uint(statPtr + 0x4 + statOffset)
            game_state.ofl[10] = statPtr + 0x4 + statOffset
            hp = hp >> 8
            #game_state.player_list[9] = hp
            player.hp = hp
        if (statEnum == 7):
            maxhp = process.read_uint(statPtr + 0x4 + statOffset)
            max_hp = maxhp >> 8
            #game_state.player_list[11] = max_hp
            player.base_hp = max_hp
        if (statEnum == 8):
            mp = process.read_uint(statPtr + 0x4 + statOffset)
            game_state.ofl[11] = statPtr + 0x4 + statOffset
            mp = mp >> 8
            #game_state.player_list[10] = mp
            player.mp = mp

        if (statEnum == 9):
            maxmp = process.read_uint(statPtr + 0x4 + statOffset)
            max_mp = maxmp >> 8
            #game_state.player_list[12] = max_mp
            player.base_mp = max_mp
            
    log = "LVL:" +str(player_level)+", HP:"+str(max_hp)+", EXP:"+str(experience)
    log_color(log,fg_color=mem_color)

    #game_state.player_list[1] = player_level
    #game_state.player_list[2] = experience
    #game_state.player.exp = experience
    player.lvl = player_level


    #get the level number
    pPathAddress = playerUnit + 0x38
    pPath = process.read_ulonglong(pPathAddress)
    pRoom1 = pPath + 0x20
    pRoom1Address = process.read_ulonglong(pRoom1)
    pRoom2 = pRoom1Address + 0x18
    pRoom2Address = process.read_ulonglong(pRoom2)
    pLevel = pRoom2Address + 0x90
    pLevelAddress = process.read_ulonglong(pLevel)
    dwLevelNo = pLevelAddress + 0x1F8
    levelNo = process.read_uint(dwLevelNo)
    level_addr = dwLevelNo


    level = levelNo
    log = ("current level           -> "+str(area_list[levelNo]))
    log_color(log,fg_color=mem_color)

    #game_state.map_list[0] = str(area_list[levelNo])
    #game_state.map_list[1] = levelNo
    game_info_clist.id = levelNo
    name = str(area_list[levelNo])

    game_info_clist.name = name.encode('utf-8')

    if not levelNo:
        log = "!! Did not find level num using player offset" +str(playerOffset)
        log_color(log,fg_color=mem_color)


    #get the map seed
    pAct = playerUnit + 0x20
    actAddress = process.read_ulonglong(pAct)


    if actAddress:
        mapSeedAddress = actAddress + 0x14
        if mapSeedAddress:
            mapSeed = process.read_uint(mapSeedAddress)
            map_seed = mapSeed
            #game_state.map_list[2] = int(map_seed)
            game_info_clist.seed = int(map_seed)
        else:
            log = ("!! Did not find map seed at address"+(mapSeedAddress))
            log_color(log,fg_color=mem_color)

    #get the level number
    actAddress = process.read_ulonglong(pAct)

    pActUnk1 = actAddress + 0x70
    aActUnk2 = process.read_ulonglong(pActUnk1)
    aDifficulty = aActUnk2 + 0x830
    difficulty = process.read_ushort(aDifficulty)
    difficulty=difficulty
    #game_info_clist.difficulty = difficulty

    if difficulty==0:
        log = ("current difficulty      -> Normal")
        log_color(log,fg_color=mem_color)
    if difficulty==1:
        log = ("current difficulty      -> Nightmare")
        log_color(log,fg_color=mem_color)
    if difficulty==2:
        log = ("current difficulty      -> Hell")
        log_color(log,fg_color=mem_color)

    #game_state.map_list[3] = int(difficulty)
    game_info_clist.difficulty = int(difficulty)


def get_ppos(player):
    """Summary - update the player positon game state globals, sets the new game state
    """
    global path_addr
    #global player_world_pos
    bytes_read = process.read_bytes(path_addr,8)
    xf,x,yf,y = unpack('HHHH', bytes_read)
    dx = float(xf) / 65535.0
    dy = float(yf) / 65535.0

    player.pos_float_offset.x = dx
    player.pos_float_offset.x = dy

    player.pos = game_state.Point(float(x)+dx, float(y) + dy)
    player.area_pos = game_state.Point( x- area_clist.origin.x ,y - area_clist.origin.y)

def ui_in_game():
    ofl = shared_memory.ShareableList(name='offset_list')
    offset = get_ui_settings_offset()
    base = get_base_offset()
    ui = base + offset
    bytes_read = process.read_bytes(ui-10,1)
    ret = unpack('?', bytes_read)[0]
    
    return ret

def get_any_ui(key):

    #ofl = shared_memory.ShareableList(name='offset_list')
    offset = get_ui_settings_offset()
    base = get_base_offset()
    ui = base + offset
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

def get_tick():
    """Summary - for debug, gets the 3D graphics ticks based on frame rate cap
     THIS MAY NOT WORK OFFLINE FOR SOME REASON!
    """
    
    offset = game_state.ofl[1]
    game_info_addr = base + offset

    off = 0xb4+68
    result = process.read_ulonglong(game_info_addr+off)
    result_2 = process.read_bytes(result+16,1)
    tick = result_2

    return int.from_bytes(tick,'little')

def get_cursor_item():
    """Summary - get the current item on the cursor
    """
    #pUnit->inventory_0x60->unitdata_0x20->itemdata0x14->itemLvl_0x2C
    items = []
    item_offset = starting_offset + (4*1024)

    for i in range(256):


        new_offset = item_offset +(8 *(i))
        item_addr = base + new_offset
        item_unit = process.read_longlong(item_addr)

        while (item_unit>0):
            item_type = process.read_uint(item_unit+0x00)
            if item_type == 4:
                txt_file_no = process.read_uint(item_unit+0x04)
                item_loc = process.read_uint(item_unit+0x0C)

                # item loc 0 = inventory, 1 = equipped, 2 in belt, 3 on ground, 4 cursor, 5 dropping ,6 socketed
                if item_loc == 4:
                    #print("item on ground")
                    print("item on cursor")
                    p_unit_data = process.read_longlong(item_unit + 0x10)
                    #itemQuality - 5 is set, 7 is unique (6 rare, 4, magic)
                    item_quality = process.read_uint(p_unit_data)
                    p_path = process.read_longlong(item_unit+0x38)
                    item_x = process.read_ushort(p_path+0x10)
                    item_y = process.read_ushort(p_path+0x14)


                    p_stat_list_ex = process.read_longlong(item_unit + 0x88)
                    try:
                        stat_ptr = process.read_longlong(p_stat_list_ex + 0x30)
                    except:
                        continue
                    stat_count = process.read_longlong(p_stat_list_ex + 0x38)
                    num_sockets = 0

                    for j in range(stat_count):
                        #print("checking for sockets")
                        stat_offset = (j)*8
                        stat_enum = process.read_ushort(stat_ptr+0x2+stat_offset)
                        #print(stat_enum)

                        if stat_enum == 73:
                            s_73 = process.read_uint(stat_ptr+0x4+stat_offset)
                            #print('number of sockets ->'+str(num_sockets))
                            #print(s_73)

                        if stat_enum == 72:
                            s_72 = process.read_uint(stat_ptr+0x4+stat_offset)
                            #print('number of sockets ->'+str(num_sockets))
                            #print(s_72)

                        if stat_enum == 22:
                            s_22 = process.read_uint(stat_ptr+0x4+stat_offset)
                            #print(s_22)
                            #print('number of sockets ->'+str(num_sockets))

                        if stat_enum == 21:
                            s_21 = process.read_uint(stat_ptr+0x4+stat_offset)
                            #print(s_21)
                            #print('number of sockets ->'+str(num_sockets))

                        if stat_enum == 194:
                            num_sockets = process.read_uint(stat_ptr+0x4+stat_offset)
                            #print('number of sockets ->'+str(num_sockets))


                    flags = process.read_uint(p_unit_data+0x18)

                    identified = False
                    if(0x00000010 & flags):
                        identified = True
                        #print("id'd")
                    ethereal = False
                    if(0x00400000 & flags):
                        ethereal = True

                    quality='Any'
                    if item_quality == 1:
                        quality = 'Inferior'
                    if item_quality == 2:
                        quality = 'Normal'
                    if item_quality == 3:
                        quality = 'Superior'
                    if item_quality == 4:
                        quality = 'Magic'
                    if item_quality == 5:
                        quality = 'Set'
                    if item_quality == 6:
                        quality = 'Rare'
                    if item_quality == 7:
                        quality = 'Unique'
                    if item_quality == 8:
                        quality = 'Crafted'
                    if item_quality == 9:
                        quality = 'Tempered'

                    #print(txt_file_no)
                    if txt_file_no >= 557 and txt_file_no <= 586 or txt_file_no>= 597 and txt_file_no<= 601:
                        quality = 'Gem'
                    if txt_file_no >= 610 and txt_file_no <= 642:
                        quality = 'Rune'

                    item = (txt_file_no,quality,item_name[txt_file_no],item_quality,item_loc,item_x,item_y,num_sockets)

                    print(item_name[txt_file_no],item)

            item_unit = process.read_longlong(item_unit + 0x150)


def update_game_pass(game_info_clist):
    """Summary - update the game data globals with the current game password
    """
    #map_list  = shared_memory.ShareableList(name="map_list")
    ofl = shared_memory.ShareableList(name='offset_list')
    offset = game_state.ofl[1]
    game_info_addr = base + offset
    read_game_pass = process.read_string(game_info_addr+120,16)
    
    #game_state.map_list[7] = str(read_game_pass)
    game_info_clist.game_pass = read_game_pass.encode('utf-8')

def get_game_pass():
    #map_list  = shared_memory.ShareableList(name="map_list")
    return 'blank' #game_state.map_list[7]

def update_game_name(game_info_clist):
    """Summary - update the game data globals with the current game name
    """
    #map_list  = shared_memory.ShareableList(name="map_list")
    ofl = shared_memory.ShareableList(name='offset_list')
    offset = game_state.ofl[1]
    game_info_addr = base + offset
    read_game_name = process.read_string(game_info_addr+72,16)
    #game_state.map_list[6] = str(read_game_name)
    game_info_clist.game_name = read_game_name.encode('utf-8')

def get_game_name():
    #map_list  = shared_memory.ShareableList(name="map_list")
    #return game_state.map_list[6]
    return 'blank'

def update_game_ip(game_info_clist):
    """Summary - update the game data globals with IP
    """
    #map_list  = shared_memory.ShareableList(name="map_list")
    ofl = shared_memory.ShareableList(name='offset_list')
    offset = game_state.ofl[1]
    game_info_addr = base + offset
    #game_state.map_list[5] = str(process.read_string(game_info_addr+0X1D0,16))
    game_ip = str(process.read_string(game_info_addr+0X1D0,16))
    game_info_clist.ip = game_ip.encode('utf-8')

def get_game_ip():
    #map_list  = shared_memory.ShareableList(name="map_list")
    #return game_state.map_list[5]
    return 'blank for now'

def update_item_list(item_clist, player):
    """Summary - dump item list to global game state struct
    """

    base = game_state.ofl[0]
    starting_offset = game_state.ofl[4]
    
    idx = 0

    updated = []
    item_offset = starting_offset + (4*1024)

    raw_idx = 0

    for i in range(256):

        new_offset = item_offset +(8 *(i))
        item_addr = base + new_offset
        item_unit = process.read_longlong(item_addr)

        while (item_unit>0):
            item_type = process.read_uint(item_unit+0x00)

            if item_type == 4:
                txt_file_no = process.read_uint(item_unit+0x04)
                item_loc = process.read_uint(item_unit+0x0C)

                # item loc 0 = inventory, 1 = equipped, 2 in belt, 3 on ground, 4 cursor, 5 dropping ,6 socketed
                if item_loc == 3 or item_loc == 5:
                    #print("item on ground")
                    p_unit_data = process.read_longlong(item_unit + 0x10)
                    #itemQuality - 5 is set, 7 is unique (6 rare, 4, magic)
                    item_quality = process.read_uint(p_unit_data)
                    p_path = process.read_longlong(item_unit+0x38)
                    item_x = process.read_ushort(p_path+0x10)
                    item_y = process.read_ushort(p_path+0x14)

                    unitId = process.read_uint(item_unit + 0x08)

                    p_stat_list_ex = process.read_longlong(item_unit + 0x88)
                    try:
                        stat_ptr = process.read_longlong(p_stat_list_ex + 0x30)
                    except:
                        continue
                    stat_count = process.read_longlong(p_stat_list_ex + 0x38)
                    num_sockets = 0

                    for j in range(stat_count):
                        #print("checking for sockets")
                        stat_offset = (j)*8
                        stat_enum = process.read_ushort(stat_ptr+0x2+stat_offset)
                        if stat_enum == 194:
                            num_sockets = process.read_uint(stat_ptr+0x4+stat_offset)
                            #print('number of sockets ->'+str(num_sockets))
                            break

                    flags = process.read_uint(p_unit_data+0x18)


                    identified = False
                    if(0x00000010 & flags):
                        identified = True
                        #print("id'd")
                    ethereal = False
                    if(0x00400000 & flags):
                        ethereal = True

                    quality='Any'
                    quality = item_quality_list[item_quality]


                    if txt_file_no >= 557 and txt_file_no <= 586 or txt_file_no>= 597 and txt_file_no<= 601:
                        quality = 'Gem'
                    if txt_file_no >= 610 and txt_file_no <= 642:
                        quality = 'Rune'


                    body_loc = process.read_uchar(p_unit_data+0x54)
                    inventory_page = process.read_uchar(p_unit_data+0x0c)
                    inventory_ptr = process.read_ulonglong(p_unit_data+0x70)

                    node = process.read_uchar(p_unit_data+0x88)
                    nodeOther = process.read_uchar(p_unit_data+0x89)

                    pos = np.array([item_x,item_y])
                    name = item_name[txt_file_no]

                    #items
                    area_x =  float(pos[0]) #game_state.map_list[8]
                    area_y = float(pos[1]) #game_state.map_list[9]
                    #dist = float(dist)
                    item = game_state.Item()
                    item.name = name.encode('utf_8')
                    item.pos = game_state.Point(pos[0],pos[1])
                    item.area_pos = game_state.Point(area_x,area_y)
                    item.good = 0
                    item.unit_id = unitId
                    item.txt_id = txt_file_no
                    item.sockets = num_sockets
                    item.location = item_loc
                    item.slot = body_loc
                    item.quality = item_quality
                    item.quality_str = quality.encode('utf-8')
                    #add dist item.dist to player
                    item_clist[raw_idx] = item
                    updated.append(raw_idx)
                    raw_idx+=1
                    

                    '''
                    for category in _loot_data:
                        q_match = 0
                        i_match = 0
                        loot_check = 0

                        data = _loot_data.get(category)
                        quality_match = ['Any']
                        item_match = ['Any']
                        try:
                            quality_match = data['quality']
                        except:
                            quality_match = ['Inferior','Normal','Superior','Magic','Set','Rare','Unique','Crafted','Tempered','Gem','Rune']
                            pass
                        try:
                            item_match = data['items']
                        except:
                            item_match = ['Any']
                            pass

                        for q in quality_match:
                            if quality in q:
                                q_match=1

                        for i in item_match:
                            item_to_check = str(item_name[txt_file_no])
                            if num_sockets>0:
                                item_to_check = str(item_name[txt_file_no])+','+str(num_sockets)
                            if item_to_check in i or item_match[0] is 'Any':
                                i_match=1

                        if q_match and i_match:
                            loot_check =1

                        try:
                            if data['ignoreidentified'] is True and identified:
                                loot_check=0
                        except:
                            pass

                        if loot_check:
                            print("good to loot")
                            #_move_to_mem(item_x,item_y)
                            print(item_name[txt_file_no])
                    '''

            item_unit = process.read_longlong(item_unit + 0x150)

    for i in range(128):
        if i not in updated:
            item_clist[i].name = b''


def update_object_list(object_clist,player):

    super_chests =[]
    base = game_state.ofl[0]
    starting_offset = game_state.ofl[4]
    object_offset = starting_offset + (2 * 1024)
    attempts=0

    #map_offset_x = game_state.map_list[8]
    #map_offset_y = game_state.map_list[9]
    map_offset_x = 0
    map_offset_y = 0

    raw_idx = 0

    player_world_x = player.pos.x
    player_world_y = player.pos.y
    player_world_pos = np.array([player_world_x,player_world_y])
    updated = []

    #this needs to be 256
    for i in range(1,128):
        new_offset = object_offset + (8 * (i-1))
        obj_addr = base + new_offset
        object_unit = process.read_longlong(obj_addr)

        while (object_unit>0):
            obj_type = process.read_int(object_unit+0x00)

            if obj_type==2:
                file_no = process.read_int(object_unit+0x04)
                p_unit_data = process.read_ulonglong(object_unit + 0x10)
                mode = process.read_uint (object_unit + 0x0C)
                pObjectTxt = process.read_ulonglong(p_unit_data)
                name = ""
                for q in range(1,32):
                    try:
                        name = name + str(chr(process.read_uchar(pObjectTxt+q+1)))
                    except:
                        pass
                name = name.strip()
                name = name.rstrip()
                #sObjectTxt = self.process.read_string(p_unit_data, 16)
                #shrineTxt = self.process.read_string(p_unit_data + 0x0c, 16)
                pPath = process.read_ulonglong(object_unit + 0x38)  
                objectx = process.read_ushort(pPath + 0x10)
                objecty = process.read_ushort(pPath + 0x14)
                
                odist = math.dist(np.array([objectx,objecty]),player_world_pos)

                if len(name)>0:            
                    obj = game_state.GameObject()
                    obj.name = name.encode('utf-8')

                    obj.pos = game_state.Point(objectx,objecty)
                    obj.area_pos = game_state.Point(objectx-map_offset_x, objecty-map_offset_y)
                    obj.dist = odist
                    obj.abs_scren_pos = game_state.Point(0,0)
                    obj.mode = mode
                    object_clist[raw_idx] = obj
                    updated.append(raw_idx)
                    raw_idx +=1

            object_unit = process.read_longlong(object_unit + 0x150)
    for i in range(128):
        if i not in updated:
            object_clist[i].name = b''


def update_monster_list(monster_clist,player):
    """Summary - locate monster units in memory
    """

    base = game_state.ofl[0]
    starting_offset = game_state.ofl[4]
    monstersOffset = starting_offset + 1024
    
    idx = 0

    skel_count =0
    revive_count =0
    mage_count =0
    golem_count = 'none'
    j=0

                
    updated = []

    player_world_x = player.pos.x
    player_world_y = player.pos.y
    player_world_pos = np.array([player_world_x,player_world_y])


    raw_idx = 0

    for i in range(1,128):
        newOffset = monstersOffset + (8 * (i-1))
        mobAddress = base + newOffset
        mobUnit = process.read_longlong(mobAddress)

        while (mobUnit> 0):

            txtFileNo = process.read_uint(mobUnit + 0x04)
            hide_check = 0
            try:
                hide_npc[txtFileNo]
            except:
                pass

            if hide_check:
                continue

            if not hide_check:

                mobTypeString = ""
                #
                mob_type = 0
                mob_type_int = 0
                unit_data = process.read_ulonglong(mobUnit + 0x10)
                try:
                    mob_type = process.read_bytes(unit_data+0x1a,1)
                    mob_type_int = int.from_bytes(mob_type,"little")
                except:
                    mob_type = 0
                    mob_type_int = 0
                
                mob_types = {
                        0:'None',
                        1:'Other',
                        10: 'SuperUnique',
                        8: 'Unique',
                        12: 'Champion',
                        16: 'Minion',
                        32: 'Possessed?',
                        76: 'Ghostly',
                        64: 'Multishot?',
                        99: 'Unk',
                        98: 'Unk',
                        }
                try:                        
                    mobTypeString = mob_types[mob_type_int]
                except:
                    mobTypeString = 'Unk'
                
                unitId = process.read_uint(mobUnit + 0x08)
                mode = process.read_uint(mobUnit + 0x0c)
                iscorpse = process.read_uchar (mobUnit + 0x1A6)
                interactable = process.read_uchar (mobUnit + 0x1A6+4)
                pUnitData = process.read_longlong(mobUnit + 0x10)
                pPath = process.read_longlong(mobUnit + 0x38)
                
                isUnique = 0
                uniqueNo = 0
                try:
                    isUnique = process.read_ushort(pUnitData + 0x18)
                    uniqueNo = process.read_ushort(pUnitData + 42)
                except:
                    pass
                #????
                

                #monx = process.read_ushort(pPath + 0x02)
                #mony = process.read_ushort(pPath + 0x06)
                #xPosOffset = process.read_ushort(pPath + 0x00)
                #yPosOffset = process.read_ushort(pPath + 0x04)
                #xPosOffset = xPosOffset / 65536
                #yPosOffset = yPosOffset / 65536
                #monx = monx + xPosOffset
                #mony = mony + yPosOffset

                
                #+026?
                #+017 - eLastMode
                #+018 - dwDuriel - set only for duriel
                #+01C - MonUModList[9] - nine bytes holding the Ids for each MonUMod assigned to the unit
                #+026 - bossNo - hcIdx from superuniques.txt for superuniques (word)
                #+028 - pAiGeneral

                BossLineID = process.read_ushort(unit_data + 0x2A)

                isBoss = 0
                textTitle = None

                try:
                    textTitle = get_mob_name[txtFileNo]
                except:
                    textTile = "blank"

                if mob_type_int == 10:
                    try:
                        textTitle = super_unique_names[uniqueNo]
                    except:
                        pass
                if mob_type_int == 8:
                    try:
                        textTitle = get_mob_name[txtFileNo]
                    except:
                        pass
                    isBoss= 1


                #get immunities
                pStatsListEx = process.read_longlong(mobUnit + 0x88)
                #??????????? this maybe needed but throws a error
                #ownerType = process.read_uint(pStatsListEx + 0x08)
                #?????????????????
                #ownerId = process.read_uint(pStatsListEx + 0x0C)
                statCount = 0
                try:
                    statPtr = process.read_longlong(pStatsListEx + 0x30)
                    statCount = process.read_longlong(pStatsListEx + 0x38)
                except:
                    pass
                

                #if(isUnique):
                    #print(textTitle,mobTypeString, mob_type_int)


                immunities = {'physical': 0,
                              'magic': 0,
                              'fire': 0,
                              'light': 0,
                              'cold': 0,
                              'poison': 0}

                auras = {'MightAura': 0,
                         'HolyFireAura': 0,
                         'BlessedAimAura': 0,
                         'HolyFreezeAura': 0,
                         'HolyShockAura': 0,
                         'ConvictionAura': 0,
                         'FanaticismAura':0}

                enchants = {'ExtraStrong': 0,
                            'ExtraFast': 0,
                            'Cursed': 0,
                            'MagicResistant': 0,
                            'FireEnchanted': 0,
                            'LigntningEnchanted': 0,
                            'ColdEnchanted':0,
                            'ManaBurn':0,
                            'Teleportation':0,
                            'SpectralHit':0,
                            'StoneSkin':0,
                            'MultipleShots':0,
                            'Berserker':0}


                for s in range(statCount):
                    offset = (s -1) * 8
                    statParam = process.read_ushort(statPtr + offset)
                    statEnum = process.read_ushort(statPtr + 0x2 + offset)
                    statValue = process.read_uint(statPtr + 0x4 + offset)
                    if (statValue>= 100):
                        if statEnum == 36:
                            immunities["physical"] = 1 #physical immune
                        if statEnum == 37:
                            immunities["magic"] = 1
                        if statEnum == 39:
                            immunities["fire"] = 1
                        if statEnum == 41:
                            immunities["light"] = 1
                        if statEnum == 43:
                            immunities["cold"] = 1
                        if statEnum == 45:
                            immunities["poison"] = 1
                
                
                try:
                    bytes_read = process.read_bytes(pPath,8)
                except:
                    continue
                
                xf,x,yf,y = unpack('HHHH', bytes_read)
                dx = float(xf) / 65535.0
                dy = float(yf) / 65535.0

                monx = dx+float(x)
                mony = dy+float(y)

                mon_arr = np.array([monx,mony],dtype=np.float32)

                dist = math.dist(player_world_pos,mon_arr)
                
                #abs_screen_position = world_to_abs(mon_arr, player_world_pos)

                #area_origin = np.array([game_state.map_list[8],game_state.map_list[9]])

                '''
                mob_obj = game_state.Monster(immunities = immunities,
                                         pos=mon_arr,
                                         area_pos = mon_arr - area_clist.origin,
                                         abs_scren_pos=abs_screen_position,
                                         dist = dist,
                                         type = 0,
                                         flag = 0,
                                         mob_type_str = mobTypeString,
                                         unit_id=unitId,
                                         name=textTitle, 
                                         mode=mode,
                                         text_file_no = txtFileNo,
                                             )
                # filter out some stuff and calculate summon count
                '''
                if textTitle is not None:
 
                    if 'ClayGolem' in textTitle:
                        if mode != 12:
                            golem_count = "ClayGolem"

                    elif 'FireGolem' in textTitle:
                        if mode != 12:
                            golem_count = "FireGolem"

                    elif 'BloodGolem' in textTitle:
                        if mode != 12:
                            golem_count = "BloodGolem"

                    elif 'IronGolem' in textTitle:
                        if mode != 12:
                            golem_count = "IronGolem"

                    elif 'NecroMage' == textTitle:
                        if mode != 12:
                            mage_count +=1

                    elif 'NecroSkeleton' == textTitle:
                        if mode != 12:
                            skel_count +=1
                    elif 'Rouge' in textTitle:
                        pass
                    elif 'Gaurd' in textTitle:
                        pass
                    elif 'Alkor' in textTitle:
                        pass
                    elif 'a trap' in textTitle:
                        pass
                    elif 'IronWolf' in textTitle:
                        pass
                    elif 'Malachai' in textTitle:
                        pass
                    elif textTitle == '':
                        pass
                    elif '?' in textTitle:
                        pass
                    elif 'Barricade' in textTitle:
                        pass
                    else:
                        #mob_d[unitId] = (mob_obj)
                        area_x =  float(mon_arr[0]) #game_state.map_list[8]
                        area_y = float(mon_arr[1]) #game_state.map_list[9]
                        dist = float(dist)
                        m = game_state.Monster()
                        m.name = textTitle.encode('utf_8')
                        m.area_pos = game_state.Point(area_x,area_y)
                        m.dist = dist
                        m.updated = 1
                        monster_clist[raw_idx] = m
                        updated.append(raw_idx)
                        raw_idx+=1
            #get next mob
            mobUnit = process.read_longlong(mobUnit + 0x150)


    for i in range(128):
        if i not in updated:
            monster_clist[i].name = b''

    player.summons.skel = skel_count
    player.summons.mage = mage_count
    player.summons.gol = golem_count.encode('utf-8')
    player.summons.rev = revive_count
