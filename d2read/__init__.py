'''proc - handles reading memory from the d2r process.'''

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

from bitstring import BitArray
import requests
import numpy as np

import yaml
import orjson

from scipy.spatial.distance import cdist
from scipy.spatial.distance import cityblock
from scipy.spatial import distance
from scipy.cluster.vq import kmeans
from scipy.spatial import KDTree

import pymem
from . import game_state
from .event import events
from .mem import *
from .enums import *
from .utils import *

running = False
api_thread = None
monsters = None

class FPS:
    def __init__(self,avarageof=50):
        self.frametimestamps = collections.deque(maxlen=avarageof)
    def __call__(self):
        self.frametimestamps.append(time.time())
        if(len(self.frametimestamps) > 1):
            return len(self.frametimestamps)/(self.frametimestamps[-1]-self.frametimestamps[0])
        else:
            return 0.0

def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]
def closest_node_index(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index


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

    screen_coords = (x,y)

    return screen_coords

def shutdown():
    """Summary - end API thread
    """
    global running

    running = False

    log = ("API THREAD SHUTDOWN")
    log_color(log)

def cluster_map_data(nodes):
    """Summary - clusters map data
    Args:
        nodes (TYPE): Description
    """

    game_state.clusters=None
    game_state.features=None
    features_mod = np.array([[0,0]])

    features = np.array([[0,0]])
    tmp_clusters = np.array([[0,0]])

    tile_size = 32
    x=0
    y=0
    for node in nodes:
        for key in node:
            if key:
                if x % tile_size == 0 and y % tile_size ==0:
                    features_mod = np.concatenate((features_mod, [np.array([x,y])]))
                features = np.concatenate((features, [np.array([x,y])]))
            x+=1
        x=0
        y+=1
    features[0,0:-1,...] = features[0,1:,...]
    game_state.features = features
    features_mod[0,0:-1,...] = features_mod[0,1:,...]

    tmp_clusters=np.delete(features_mod,0,0)
    game_state.clusters=tmp_clusters


def game_tick():
    """Summary - main execution loop in sync with game ticks
    """
    global running

    current_level = -1
    local_tick = -1
    #fetch global offsets on startup
    populate_offsets()
    fps = FPS()

    while running:

        get_in_game_flag()
        get_tick()

        #this should sync us to the current game clock, to prevent acessing things during loading times
        if game_state.tick >0 and game_state.tick != local_tick:

            game_state.fps = fps()

            if game_state.new_session==1 and game_state.in_game ==1:
                #in game offsets
                log = ("In Game!")
                log_color(log,fg_color=important_color)
                populate_punit()
                get_current_level()
                get_map_json(game_state.map_seed,game_state.level,game_state.difficulty )
                cluster_map_data(game_state.map)
                #read_loot_cfg()
                game_state.new_session=0
                current_level = game_state.level
                game_state.loaded = 1

            if game_state.in_game == 1 and game_state.loaded==1:

                try:
                    get_current_level()
                except Exception as err:
                    #some times we get a memory read error, its mostly ok...
                    print(err)
                    pass

                if current_level != game_state.level:
                    log = ("New Map!")
                    log_color(log,fg_color=important_color)
                    game_state.clusters =  None
                    game_state.features =  None
                    game_state.loaded=0
                    get_map_json(str(game_state.map_seed), game_state.level, game_state.difficulty)
                    game_state.features = None
                    cluster_map_data(game_state.map)
                    game_state.loaded=1
                    current_level = game_state.level

                try:
                    get_ppos()
                    find_mobs()
                    get_game_ip()
                    get_game_name()
                    get_game_pass()
                    get_ui()

                except Exception as err:
                    #some times we get a memory read error, its mostly ok...
                    print(err)
                    pass
            if game_state.in_game == 1:
                events.emit("game_state_update")

            if game_state.in_game == 0:
                game_state.new_session = 1
                game_state.loaded = 0

        local_tick = game_state.tick


def start():
    """Summary - start API thread
    """
    global running
    global api_thread

    if running == False:
        running = True
        api_thread = threading.Thread(target=game_tick, daemon=True, args=())
        log = ("API THREAD STARTED")
        log_color(log,fg_color=note_color)
        api_thread.start()

def populate_offsets():
    """ Summary - populate memory offsets on initalization

    """
    get_exp_offset()
    get_unit_offset()
    get_game_info_offset()
    get_ui_settings_offset()
    get_menu_vis_offset()
    get_menu_data_offset()
    get_hover_object_offset()

def populate_punit():
    """Summary - get the player uinit offsets
    """
    get_player_offset(128)
    find_info()
    get_ppos()

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


def get_map_json(seed:int, mapid:int,difficulty:int):
    """Summary
    Args:
        seed (int): current map seed read from memory - 123456
        mapid (int): current in game map number - ie 79 for durance of hate
        difficulty (int): normal, nm, hell (0,1,2)
    Returns:
        TYPE: generates map json
    """
    json_data = get_map_d2api(game_state.map_seed,game_state.level,game_state.difficulty )

    try:
        #try and get local map api data
        map_api_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)),"d2mapapi_piped.exe")

        json_data = get_map_d2api(game_state.map_seed,game_state.level,game_state.difficulty )
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

    map_offset =np.array([map_offset_x,map_offset_y])
    game_state.map_offset = map_offset

    row = []
    for point in json_data['mapData']:
        if point != -1:
            row.append (point)
        else:
            game_state.grid.append (row)
            row = []

    if json_data is not None:
        map_crop = json_data['crop']
        obj_str = "|"
        poi_str = "|"

        game_state.points_of_interest = []
        game_state.map_objects = []

        #these are mostly garbage and not useful, its map decorator stuff
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
                    game_state.map_objects.append(new_obj)
                    break

        #filter ut way points from the objects list
        if json_data['objects'] is not None:
            for key in json_data['objects']:
                value = json_data['objects'][key]
                name = objects[int(key)]
                if 'waypoint' in name or 'Waypoint' in name:
                    poi_str+=name+"|"
                    for instance in value:
                        offset_x =instance['x']
                        offset_y=instance['y']
                        pos =np.array([offset_x,offset_y])
                        pos_area = pos-map_offset
                        flag = 0
                        new_obj = {"position":pos,"flag":1,"label":name,"pos_area":pos_area}
                        game_state.points_of_interest.append(new_obj)
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
                game_state.points_of_interest.append(new_poi)

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
                    game_state.points_of_interest.append(new_poi)

        map_id = json_data['id']
        map_data = json_data['mapData']
        map_size = json_data['size']
        map_decode = list(split(map_data,sep=[-1]))

        game_state.area_origin = map_offset
        nodes = []
        col_grid = []

        collision_grid = np.empty([int(map_size['height']),int(map_size['width'])], dtype=np.uint8)

        if map_data is not None:
            game_state.mini_map_w=int(map_size['width'])
            game_state.mini_map_h=int(map_size['height'])
            walkable = True
            y = 0
            for ele in map_decode:
                x = 0
                row = []
                for i in range(len(ele)):
                    if walkable:
                        for j in range(ele[i]):
                            nodes.append([x,y,walkable])
                            row.append(0)
                            collision_grid[y][x] = 0
                            x+=1
                    if not walkable:
                        for j in range(ele[i]):
                            nodes.append([x,y,walkable])
                            row.append(-1)
                            collision_grid[y][x] = -1
                            x+=1

                    walkable = not walkable
                y+=1
                if len(row)>0:
                    col_grid.append(row)
                x=0
                walkable = True

        game_state.map = collision_grid

        new_map = {"crop": map_crop,
                   "id": map_id,
                   'poi': game_state.points_of_interest,
                   "objects": game_state.map_objects,
                   "size": map_size,
                   "nodes":nodes,
                   "data":col_grid}

        log = ("Loaded map              -> {}".format(area_list[new_map['id']]))
        game_state.current_area=area_list[new_map['id']]

        log_color(log,fg_color=mem_color)
        log = ("Number of POI           -> {}".format(len(game_state.points_of_interest)))
        log_color(log,fg_color=mem_color)
        log = ("{}".format(poi_str))
        log_color(log,fg_color=mem_color)
        log = ("Number of OBJ           -> {}".format(len(game_state.map_objects)))
        log_color(log,fg_color=mem_color)
        log = ("{}".format(obj_str))
        log_color(log,fg_color=mem_color)
        game_state.maps.append(new_map)
        game_state.poi = game_state.points_of_interest


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
        TYPE: Description
    """
    ui = base + ui_settings_offset
    igo =0x08
    in_game_ptr = process.read_bytes(ui+igo,1)
    game_state.in_game = int.from_bytes(in_game_ptr ,"little")

def get_game_info_offset():
    """Summary

    Returns:
        TYPE: Description
    """
    #get game info offset
    global game_info_offset
    pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+8)
    game_info_offset = ((pat_addr - base)  + 7 -256 + 5 + offset_buffer)
    log = ("Found game info offset  ->")
    log_color(log,target=hex(game_info_offset),fg_color=mem_color,fg2_color=offset_color)


def get_hover_object_offset():
    """Summary

    Returns:
        TYPE: Description
    """
    global hover_offset
    pat = b'\xc6\x84\xc2.....\x48\x8b\x74.'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat, return_multiple=False)
    offset_buffer = process.read_bytes(pat_addr+3,4)
    offset_buffer_int = int.from_bytes(offset_buffer,'little')
    hover_offset = (offset_buffer_int)-1
    log = ("Found hover offset      ->")
    log_color(log,target=hex(hover_offset),fg_color=mem_color,fg2_color=offset_color)

'''
#TO DO
        public IntPtr GetInteractedNpcOffset()
        {
            var pattern = "\x42\x0F\xB6\x84\x20\x00\x00\x00\x00\x38\x02";
            var mask = "xxxxx????xx";
            var patternAddress = FindPattern(pattern, mask);

            var offsetBuffer = new byte[4];
            var resultRelativeAddress = IntPtr.Add(patternAddress, 5);
            if (!WindowsExternal.ReadProcessMemory(_handle, resultRelativeAddress, offsetBuffer, sizeof(int), out _))
            {
                _log.Info($"Failed to find pattern {PatternToString(pattern)}");
                return IntPtr.Zero;
            }
            var offsetAddressToInt = BitConverter.ToInt32(offsetBuffer, 0);
            return IntPtr.Add(_baseAddr, (int)(offsetAddressToInt - 0xC4));
        }

'''
def get_interacted_npc_offset():
    """NPC interaction offset - NO CORRECT OR IMPLEMENTED

    """
    #expansion offset scan pattern
    pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....\x83\x78\x5C.\x0F\x84....\x33\xD2\x41'
    #this works fine, shorter pattern?
    global exp_offset
    pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr-4)
    exp_offset = ((pat_addr - base) + offset_buffer)
    log = ("Found exp offset        ->")
    log_color(log,target=hex(exp_offset),fg_color=mem_color,fg2_color=offset_color)

def get_exp_offset():
    """Summary - get expansion offsets

    """
    #expansion offset scan pattern
    pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....\x83\x78\x5C.\x0F\x84....\x33\xD2\x41'
    #this works fine, shorter pattern?
    global exp_offset
    pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr-4)
    exp_offset = ((pat_addr - base) + offset_buffer)
    log = ("Found exp offset        ->")
    log_color(log,target=hex(exp_offset),fg_color=mem_color,fg2_color=offset_color)

def get_unit_offset():
    '''Summary - gets some unit table offsets from memory

    '''
    #unit table offset scan pattern
    global starting_offset
    global player_offset
    pat = b"\x48\x8d.....\x8b\xd1"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+3)
    player_offset = ((pat_addr - base) + 7 + offset_buffer)
    log = ("Found player offset     ->")
    log_color(log,target=hex(player_offset),fg_color=mem_color,fg2_color=offset_color)
    starting_offset = player_offset

def get_menu_data_offset():
    """Summary - get menu data offsets
    """
    #unit table offset
    global ui_offset
    #scan pattern
    pat = b"\x41\x0f\xb6\xac\x3f...."
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr-5)
    ui_offset = ((pat_addr - base) + offset_buffer)
    log = ("Found menu data offset  ->")
    log_color(log,target=hex(ui_offset),fg_color=mem_color,fg2_color=offset_color)

def get_ui_settings_offset():
    """Summary - ui settings offsets
    """
    #unit table offset
    global ui_settings_offset
    pat = b"\x40\x84\xed\x0f\x94\x05"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+6)
    ui_settings_offset = ((pat_addr - base) + 10 + offset_buffer)
    log = ("Found ui offset         ->")
    log_color(log,target=hex(ui_settings_offset),fg_color=mem_color,fg2_color=offset_color)

def get_menu_vis_offset():
    """Summary - menu vis offsets

    """
    #menu vis offset
    #pat = b'\x8B\x05....\x89\x44\x24\x20\x74\x07'
    #?? search less direct matches?
    global menu_offset
    pat = b'\x8B\x05....\x89\x44.\x20\x74\x07'
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+2)
    #maybe dont need +6 here?
    menu_offset = ((pat_addr - base) + 6 + offset_buffer)
    log = ("Found menu offset       ->")
    log_color(log,target=hex(menu_offset),fg_color=mem_color,fg2_color=offset_color)

def get_last_hovered():
    """Summary - get last hovered object and check unit tables for a match
    """
    global hover_offset

    offset = hover_offset
    is_hovered = process.read_int(offset+base+0x00)
    is_tooltip = process.read_int(offset+base+0x01)
    hovered_unit_type = process.read_int(offset+base+0x03)
    hid =process.read_uint(offset+base+0x08)

    if is_hovered:

        game_state.hover_obj = hid

        if hovered_unit_type == 1024:
            for item in game_state.items:
                try:
                    game_state.hovered_item = game_state.items[hid-1]
                    break
                except:
                    pass
                break


        if hovered_unit_type == 256:
            if game_state.monsters is not None:
                for m in game_state.monsters:
                    if hid == m['id'] and is_hovered:
                        game_state.hovered_entity = m['id']
                        break


def get_player_offset(loops=128):
    """Summary - scan for player unit as a starting point for all relevant memory offsets

    Args:
        loops (TYPE): iterations

    Returns:
        TYPE: sets the global player unit offset
    """
    found = False

    attempts=0
    name = ""
    new_offset=0

    global player_unit
    global path_addr

    for i in range(loops):
        attempts=i+0

        new_offset = (starting_offset)+(attempts-1)*8

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
                act_addr = process.read_ulonglong(p_act)
                map_seed_addr = act_addr +0x14
                map_seed = process.read_uint(map_seed_addr)
                game_state.map_seed = map_seed

                #print(map_seed)
                p_path = player_unit+0x38
                path_addr = process.read_longlong(p_path)

                x_pos = process.read_ushort(path_addr+0x02)
                y_pos = process.read_ushort(path_addr+0x06)

                p_unit_data = player_unit +0x10
                try:
                    player_name_addr = process.read_longlong(p_unit_data)
                except:
                    pass
                #
                for q in range(16):
                    name = name + str(chr(process.read_uchar(player_name_addr+q-1)))

                if(x_pos> 0 and y_pos >0 and len(str(map_seed))>6):
                    if loops > 1:
                        log = ("Found player name       ->")
                        log_color(log,target=name,fg_color=mem_color,fg2_color=important_color)

                        log = ("Found map seed          ->")
                        log_color(log,target=str(map_seed),fg_color=mem_color,fg2_color=important_color)
                    new_offset = new_offset+0
                    found = True
                    player_unit = new_offset
                    path_addr = path_addr
                    return True

            new_offset = (player_unit+0x150)-base
            try:
                player_unit = process.read_longlong(player_unit +0x150)
            except:
                pass


def get_current_level():
    """Summary
    """
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
    game_state.level = levelNo

def find_info():
    """Summary

    Returns:
        TYPE: Description
    """
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
            hp = hp >> 8
        if (statEnum == 7):
            maxhp = process.read_uint(statPtr + 0x4 + statOffset)
            max_hp = maxhp >> 8
    log = "LVL:" +str(player_level)+", HP:"+str(max_hp)+", EXP:"+str(experience)
    log_color(log,fg_color=mem_color)

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
    log = ("current level      -> "+str(area_list[levelNo]))
    log_color(log,fg_color=mem_color)

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
    game_state.difficulty = difficulty

    if difficulty==0:
        log = ("current difficulty      -> Normal")
        log_color(log,fg_color=mem_color)
    if difficulty==1:
        log = ("current difficulty      -> Nightmare")
        log_color(log,fg_color=mem_color)
    if difficulty==2:
        log = ("current difficulty      -> Hell")
        log_color(log,fg_color=mem_color)


def get_ppos():
    """Summary - update the player positon game state globals, sets the new game state
    """
    global path_addr
    #global player_world_pos
    bytes_read = process.read_bytes(path_addr,8)
    xf,x,yf,y = unpack('HHHH', bytes_read)
    dx = float(xf) / 65535.0
    dy = float(yf) / 65535.0
    game_state.player_world_pos = np.array([x,y], dtype=np.int)
    game_state.player_area_pos = np.array([x,y], dtype=np.int) - game_state.area_origin
    game_state.player_float_offset = np.array([dx,dy],dtype=np.float32)

def find_objects(file_number:int):
    """Summary - look up file object by text file no
    
    Args:
        file_number (int): Description
    
    Returns:
        TYPE: string of name
    """
    super_chests =[]
    object_offset = starting_offset + (2 * 1024)
    attempts=0


    for i in range(256):
        attempts=i+0
        new_offset = object_offset + (8 * (i-1))
        item_addr = base + new_offset
        object_unit = process.read_longlong(item_addr)

        #print(i)
        while (object_unit>0):
            item_type = process.read_int(object_unit+0x00)
            pRoomnext = process.read_ulonglong(object_unit+0x158)
            #pRoomEx = process.read_ulonglong (pRoomnext+0x18)
            if(item_type==2):
                file_no = process.read_int(object_unit+0x04)
                if file_no == file_number:
                    print ("Object found")
                    p_unit_data = process.read_ulonglong(object_unit + 0x10)
                    mode = process.read_uint (object_unit + 0x0C)
                    #pObjectTxt = process.read_ulonglong(p_unit_data)
                    #print(str(pObjectTxt))
                    #sObjectTxt = process.read_string(p_unit_data, 16)
                    #shrineTxt = process.read_string(p_unit_data + 0x0c, 16)
                    pPath = process.read_ulonglong(object_unit + 0x38)
                    objectx = process.read_ushort(pPath + 0x10)
                    objecty = process.read_ushort(pPath + 0x14)
                    x_pos = process.read_ushort(path_addr+0x02)
                    y_pos = process.read_ushort(path_addr+0x06)
                    odist = math.dist([objectx,objecty],[x_pos,y_pos])
                    #print(y_pos)
                    #print(x_pos)
                    print(txt_obj_name[file_no-1] + ""+ str(str(file_no)))
                    print('dist -> '+ str(odist))
                    obj = Object (objectx, objecty, mode)
                    return obj

            object_unit = process.read_longlong(object_unit + 0x150)




def get_ui():
    """Summary - update the global UI state
    """
    offset = ui_settings_offset
    ui = base + offset
    bytes_read = process.read_bytes(ui-10,31)
    ret = unpack('??????xx???????xxxx?x?xx????x??', bytes_read)
    game_state.ui_state = game_state.UI(*ret)

def scan_around_16():
    """Summary - for debug
    """
    global game_info_state

    offset = game_info_offset
    game_info_addr = base + offset

    i=0
    while i < (72*4):
        bytes_read = process.read_bytes(game_info_addr+i,16)
        ret = unpack('cccccccccccccccc', bytes_read)
        #name = process.read_string(game_info_addr,10)
        #print(ret, i)
        out = b''
        for b in ret:
            out+=b
        print(out, i)
        i+=16



def get_tick():
    """Summary - for debug, gets the 3D graphics ticks based on frame rate cap
    """
    global game_info_state

    offset = game_info_offset
    game_info_addr = base + offset

    off = 0xb4+68
    result = process.read_ulonglong(game_info_addr+off)
    result_2 = process.read_bytes(result+16,1)

    tick = result_2
    game_state.tick = int.from_bytes(tick,'little')


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
                    stat_ptr = process.read_longlong(p_stat_list_ex + 0x30)
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



def get_addr_test():
    """Summary - for debug
    """
    global game_info_state

    offset = game_info_offset
    game_info_addr = base + offset

    result = process.read_bytes(game_info_addr+0x2a+24+6,14)
    off = 0x2a
    off = 0x6d
    off = 0xb4
    #result = process.read_bytes(game_info_addr+off+24+6,4)
    '''
    for i in range(-128,128):
        result = process.read_ulonglong(game_info_addr+off+24+6+i)
        try:
            result_2 = process.read_bytes(result,32)
            #result_3 = process.read_uint(result)
            #r = int.from_bytes(result,"little")
            print(result_2,i)
        except:
            pass
    '''
    result = process.read_ulonglong(game_info_addr+off+24+6+38)
    result_2 = process.read_bytes(result+4+2+2-2,11)

    result_2 = process.read_bytes(result+4+2+2-2+10,1)

    #print(hex(result-base))

    #ret = unpack('<Q', result_2)
    #result_3 = int.from_bytes(result_2,'little')
    #result_4 = process.read_ulong(result+8)
    #print(result_2)
    return result_2


def get_game_pass():
    """Summary - update the game data globals with the current game password
    """
    global game_info_state

    offset = game_info_offset
    game_info_addr = base + offset

    read_game_pass = process.read_string(game_info_addr+120,16)
    game_state.game_pass = read_game_pass

def get_game_name():
    """Summary - update the game data globals with the current game name
    """
    offset = game_info_offset
    game_info_addr = base + offset
    read_game_name = process.read_string(game_info_addr+72,16)
    game_state.game_name = read_game_name

def get_game_ip():
    """Summary - update the game data globals with IP
    """
    offset = game_info_offset
    game_info_addr = base + offset
    #bytes_read = process.read_bytes(game_info_addr+0x1D0,31)
    #ret = unpack('??????xx???????xxxx?x?xx????x??', bytes_read)
    game_state.ip = process.read_string(game_info_addr+0X1D0,16)

def get_items():
    """Summary - dump item list to global game state
    """
    items=[]
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
                if item_loc == 0 or 1:
                    #print("item on ground")
                    p_unit_data = process.read_longlong(item_unit + 0x10)
                    #itemQuality - 5 is set, 7 is unique (6 rare, 4, magic)
                    item_quality = process.read_uint(p_unit_data)
                    p_path = process.read_longlong(item_unit+0x38)
                    item_x = process.read_ushort(p_path+0x10)
                    item_y = process.read_ushort(p_path+0x14)

                    p_stat_list_ex = process.read_longlong(item_unit + 0x88)
                    stat_ptr = process.read_longlong(p_stat_list_ex + 0x30)
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


                    body_loc = process.read_uchar(p_unit_data+0x54)
                    inventory_page = process.read_uchar(p_unit_data+0x0c)
                    inventory_ptr = process.read_ulonglong(p_unit_data+0x70)

                    node = process.read_uchar(p_unit_data+0x88)
                    nodeOther = process.read_uchar(p_unit_data+0x89)

                    item = (txt_file_no,quality,item_name[txt_file_no],item_quality,item_loc,item_x,item_y,num_sockets,inventory_page,inventory_ptr,body_loc)

                    items.append(item)

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

    game_state.items=items


def find_mobs():
    """Summary - locate monster units in memory
    """

    monstersOffset = starting_offset + 1024
    mobs = []
    loc_monsters = []
    loc_mob_obj = []
    skel_count =0
    mage_count =0
    golem_count = 'none'

    for i in range(128):
        newOffset = monstersOffset + (8 * (i - 1))
        mobAddress = base + newOffset
        mobUnit = process.read_longlong(mobAddress)

        while (mobUnit> 0):

            txtFileNo = process.read_uint(mobUnit + 0x04)
            hide_check = 0
            try:
                hide_npc[txtFileNo]
            except:
                #no key
                pass

            if not hide_check:

                mobTypeString = ""
                #
                unit_data = process.read_ulonglong(mobUnit + 0x10)
                mob_type = process.read_bytes(unit_data+0x1a,1)
                mob_type_int = int.from_bytes(mob_type,"little")

                if mob_type_int == 0:
                    mobTypeString = 'None'
                if mob_type_int == 1:
                    mobTypeString = 'Other'
                if mob_type_int  == 10:
                    mobTypeString = 'SuperUnique'
                if mob_type_int == 8:
                    mobTypeString = 'Unique'
                if mob_type_int == 12:
                    mobTypeString = 'Champion'
                if mob_type_int == 16:
                    mobTypeString = 'Minion'
                if mob_type_int == 32:
                    mobTypeString = 'Possessed?'
                if mob_type_int == 76:
                    mobTypeString = 'Ghostly'
                if mob_type_int == 64:
                    mobTypeString = 'Multishot?'



                unitId = process.read_uint(mobUnit + 0x08)
                mode = process.read_uint(mobUnit + 0x0c)
                iscorpse = process.read_uchar (mobUnit + 0x1A6)
                interactable = process.read_uchar (mobUnit + 0x1A6+4)
                pUnitData = process.read_longlong(mobUnit + 0x10)
                pPath = process.read_longlong(mobUnit + 0x38)

                isUnique = process.read_ushort(pUnitData + 0x18)
                #????
                uniqueNo = process.read_ushort(pUnitData + 42)

                monx = process.read_ushort(pPath + 0x02)
                mony = process.read_ushort(pPath + 0x06)
                xPosOffset = process.read_ushort(pPath + 0x00)
                yPosOffset = process.read_ushort(pPath + 0x04)
                xPosOffset = xPosOffset / 65536
                yPosOffset = yPosOffset / 65536
                monx = monx + xPosOffset
                mony = mony + yPosOffset

                #+026?
                #+017 - eLastMode
                #+018 - dwDuriel - set only for duriel
                #+01C - MonUModList[9] - nine bytes holding the Ids for each MonUMod assigned to the unit
                #+026 - bossNo - hcIdx from superuniques.txt for superuniques (word)
                #+028 - pAiGeneral
                BossLineID = process.read_ushort(unit_data + 0x2A)

                isBoss = 0
                textTitle = None

                textTitle = get_mob_name[txtFileNo]

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
                ownerType = process.read_uint(pStatsListEx + 0x08)
                ownerId = process.read_uint(pStatsListEx + 0x0C)

                statPtr = process.read_longlong(pStatsListEx + 0x30)
                statCount = process.read_longlong(pStatsListEx + 0x38)

                #if(isUnique):
                    #print(textTitle,mobTypeString, mob_type_int)

                '''
                #these need to be added

                loadEncText(auraStrings[33], cfg->MightAura);
                loadEncText(auraStrings[35], cfg->HolyFireAura);
                loadEncText(auraStrings[40], cfg->BlessedAimAura);
                loadEncText(auraStrings[43], cfg->HolyFreezeAura);
                loadEncText(auraStrings[46], cfg->HolyShockAura);
                loadEncText(auraStrings[28], cfg->ConvictionAura);
                loadEncText(auraStrings[49], cfg->FanaticismAura);

                loadEncText(enchantStrings[5], cfg->encTxtExtraStrong);
                loadEncText(enchantStrings[6], cfg->encTxtExtraFast);
                loadEncText(enchantStrings[7], cfg->encTxtCursed);
                loadEncText(enchantStrings[8], cfg->encTxtMagicResistant);
                loadEncText(enchantStrings[9], cfg->encTxtFireEnchanted);
                loadEncText(enchantStrings[17], cfg->encTxtLigntningEnchanted);
                loadEncText(enchantStrings[18], cfg->encTxtColdEnchanted);
                loadEncText(enchantStrings[25], cfg->encTxtManaBurn);
                loadEncText(enchantStrings[26], cfg->encTxtTeleportation);
                loadEncText(enchantStrings[27], cfg->encTxtSpectralHit);
                loadEncText(enchantStrings[28], cfg->encTxtStoneSkin);
                loadEncText(enchantStrings[29], cfg->encTxtMultipleShots);
                loadEncText(enchantStrings[37], cfg->encTxtFanatic);
                loadEncText(enchantStrings[39], cfg->encTxtBerserker);

                '''
                #
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
                get_ppos()
                dist = math.dist(game_state.player_world_pos,np.array([int(monx),int(mony)]))

                abs_screen_position = world_to_abs(np.array([monx,mony]), game_state.player_world_pos)
                mob = {'position': np.array([int(monx),int(mony)]),'dist': dist, 'abs_screen_position': abs_screen_position, 'immunities': immunities, 'unit_type': 'Monster', 'type': mobTypeString, 'id': unitId, 'name': textTitle, 'mode': mode, 'number': txtFileNo, 'super_unique':isUnique,'boss':isBoss,'is_corpse':iscorpse, 'interactable':interactable }
                mob_obj = game_state.Monster(immunities = immunities,
                                         pos=np.array([int(monx),int(mony)]),
                                         area_pos = np.array([int(monx),int(mony)]) - game_state.area_origin,
                                         abs_scren_pos=abs_screen_position,
                                         dist = dist,
                                         type = 0,
                                         flag = 0,
                                         mob_type_str = mobTypeString,
                                         unit_id=unitId,
                                         name=textTitle, 
                                         mode=mode,
                                         text_file_no = txtFileNo
                                             )
                # filter out some stuff and calculate summon count
                if textTitle is not None:
                    if 'ClayGolem' in mob['name']:
                        if mob['mode'] != 12:
                            golem_count = "ClayGolem"

                    elif 'FireGolem' in mob['name']:
                        if mob['mode'] != 12:
                            golem_count = "FireGolem"

                    elif 'BloodGolem' in mob['name']:
                        if mob['mode'] != 12:
                            golem_count = "BloodGolem"

                    elif 'IronGolem' in mob['name']:
                        if mob['mode'] != 12:
                            golem_count = "IronGolem"

                    elif 'NecroMage' == mob['name']:
                        if mob['mode'] != 12:
                            mage_count +=1

                    elif 'NecroSkeleton' == mob['name']:
                        if mob['mode'] != 12:
                            skel_count +=1
                    elif 'Rouge' in mob['name']:
                        pass
                    elif 'Gaurd' in mob['name']:
                        pass
                    elif 'Alkor' in mob['name']:
                        pass
                    elif 'a trap' in mob['name']:
                        pass
                    elif 'IronWolf' in mob['name']:
                        pass
                    elif 'Malachai' in mob['name']:
                        pass
                    elif mob['name'] == '':
                        pass
                    elif '?' in mob['name']:
                        pass
                    elif 'Barricade' in mob['name']:
                        pass
                    else:
                        loc_monsters.append(mob)
                        loc_mob_obj.append(mob_obj)

                        #if dist<5:
                        #    print(mob['name'])

                        #    print(mob['id'])
                        #    print(mob['number'])

            #get next mob
            mobUnit = process.read_longlong(mobUnit + 0x150)
    game_state.monsters = loc_monsters
    game_state.monsters_obj = loc_mob_obj
    game_state.necro_skel = skel_count
    game_state.necro_mage = mage_count
    game_state.necro_gol = golem_count