'''read_mem.py - Simple docs generator for Python code documented to Google docstring standard.'''
import sys
import os
from bitstring import BitArray
import requests
import math
import pymem
import pymem.pattern
import os
os.system('color')
#from utils.misc import log_color
#from read_mem.lists import *
import numpy as np
import time
from subprocess import PIPE, Popen
import json
import yaml

#import re
import pymem.memory
import pymem.ressources.kernel32
import pymem.ressources.structure
#from mas.world_to_abs import world_to_abs

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



class d2r_proc:

    def __init__(self):

        '''Some doc string
        Args:
            c (str): some a.
            b (str): some b.
            a (str): some c.
        Returns:
            something I hope
        '''

        self.pm = None
        self.pm = pymem.Pymem("D2R.exe")
        self.process = self.pm
        self.player_unit = 0
        self.handle = self.pm.process_handle
        self.module = pymem.process.module_from_name(self.handle,"D2R.exe")
        self.base = self.pm.base_address
        self.exp_offset = self.get_exp_offset()
        self.starting_offset = self.get_unit_offset()
        self.game_info_offset = self.get_game_info_offset()
        self.ui_settings_offset = self.get_ui_settings_offset()
        self.menu_vis_offset = self.get_menu_vis_offset()
        self.menu_data_offset = self.get_menu_data_offset()
        self.hoverd_offset = self.get_hover_object_offset()
        self.responseList = []
        self.map_offset = None
        self.grid=[]
        self.level = 1
        self.player_world_pos = np.array([0,0])
        self.area_origin = np.array([0,0])

        self.in_game = 0
        self.loaded = 0

        #data to include
        self.monsters = []
        self.poi = []
        self.items = []
        self.map = []
        self.current_area = None
        self.used_skill = None
        self.right_skill = None
        self.left_skill = None

        self.belt_health_pots = None
        self.belt_mana_pots = None

        self.menus =    {'InGame': False,
                        'Inventory': False,
                        'Character': False,
                        'SkillSelect': False,
                        'SkillTree': False,
                        'Chat': False,
                        'NpcInteract': False,
                        'EscMenu': False,
                        'Map': False,
                        'NpcShop': False,
                        'QuestLog': False,
                        'Waypoint': False,
                        'Party': False,
                        'Stash': False,
                        'Cube': False,
                        'AltPick':False,
                        'Potions':False
                        }

        self.maps = []
        self._loot_data = []

        self.botty_data = {"monsters": [],"poi": [],
            "objects": [],"items": [],
            "map": None,
            "player_pos_world": None,
            "player_pos_area": None,
            "area_origin": None,
            "current_area": None,
            "used_skill": None,
            "right_skill": None,
            "left_skill": None,
            "menus":None,
            "belt_health_pots":None,
            "belt_mana_pots":None,
            "player_pos":None,       
            "player_offset":np.array([0,0]),
            "necroSkel": 0,
            "necroMage": 0,
            "necroGol": 'none',
            "features": [],}


        
        log_color(":: Base address            -> {}".format(hex(self.base)),fg_color=0,bg_color=traverse_color)

    def read_loot_cfg(self):
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
                self._loot_data = loot_filter
            except yaml.YAMLError as exc:
                print(exc)


    def get_map_d2api(self,seed):
        """Get map values for input seed, using the piped api
        
        Args:
            seed (uint): current map seed
        """

        p = Popen(["d2mapapi_piped.exe", "C:/Program Files/Diablo II"], stdin=PIPE, stdout=PIPE)
        #seed
        s = (seed).to_bytes(4,'little')
        #difficulty
        d = (2).to_bytes(4,'little')
        #map id
        m = (79).to_bytes(4,'little')
        
        p.stdin.write(s)
        p.stdin.write(d)
        p.stdin.write(m)
        data,err = p.communicate()
        sd = data.decode('ascii','ignore')
        #nasty 
        sd = sd[sd.find('{'):]
        j = json.loads(sd,strict=False) 
        obj = j['objects']
        #get chests....
        chests = obj['580']
        #print(sd)
        map_offset_x = j['offset']['x']
        map_offset_y = j['offset']['y']
        self.chests = chests
        self.map_ox = map_offset_x
        self.map_oy = map_offset_y


    def get_map_json(self,seed, mapid:int, objectIDs:list=None):
        """Summary
        
        Args:
            seed (TYPE): current map seed read from memory
            mapid (int): current in game map number
            objectIDs (list, optional): Description
        
        Returns:
            TYPE: Description
        """

        #url for map api
        base_url='http://34.69.54.92:8000'    
        url=base_url+'/'+str(seed)+f'/2/{str(mapid)}/1'

        log = (":: Got data from           -> {}".format(url))
        log_color(log,fg_color=0,bg_color=traverse_color)
        resp = requests.get(url=url)
        j = resp.json()

        obj = j['objects']
        if objectIDs is not None:
            for objectID in objectIDs:
                self.responseList.append (obj[objectID])
        map_offset_x = j['offset']['x']
        map_offset_y = j['offset']['y']

        map_offset =np.array([map_offset_x,map_offset_y])


        self.map_offset = map_offset
        row = []
        for point in j['mapData']:
            if point != -1:
                row.append (point)
            else:
                self.grid.append (row)
                row = []              
        
        

        def split(a, sep):
            """Summary
            
            Args:
                a (TYPE): Description
                sep (TYPE): Description
            
            Yields:
                TYPE: Description
            """
            pos = i = 0
            while i <len(a):
                if a[i:i+len(sep)] == sep:
                    yield a[pos:i]
                    pos = i = i+len(sep)
                else:
                    i += 1
            yield a[pos:i]

        points_of_interest = []
        map_objects = []

        if j != None:
            map_crop = j['crop']
            obj_str = "|"
            poi_str = "|"
            #these are mostly garbage and not useful, its map decorator stuff
            for key in j['objects']:
                value = j['objects'][key]
                name = objects[int(key)]
                obj_str+=name+"|"
                #print(int(key),name)
                for instance in value:
                    offset_x =instance['x']
                    offset_y=instance['y']
                    pos =np.array([offset_x,offset_y])
                    pos_area = pos-map_offset
                    flag = 0
                    new_obj = {"position":pos,"flag":1,"name":name,"pos_area":pos_area}
                    map_objects.append(new_obj)
                    break

            #filter ut way points from the objects list
            for key in j['objects']:
                value = j['objects'][key]
                name = objects[int(key)]
                if 'waypoint' in name or 'Waypoint' in name:
                    poi_str+=name+"|"
                    #print(int(key),name)
                    for instance in value:
                        offset_x =instance['x']
                        offset_y=instance['y']
                        pos =np.array([offset_x,offset_y])
                        pos_area = pos-map_offset
                        flag = 0
                        new_obj = {"position":pos,"flag":1,"label":name,"pos_area":pos_area}
                        points_of_interest.append(new_obj)
                        break

            #convert exits to a uniform format in poi
            for key in j['exits']:
                value = j['exits'][key]
                name = areas[int(key)]
                poi_str+=name+"|"
                is_portal = value['isPortal']
                offset_x = value['offsets'][0]['x']
                offset_y = value['offsets'][0]['y']
                pos =np.array([offset_x,offset_y])
                pos_area = pos-map_offset
                new_poi = {"position":pos,"type":1,"label":name,"pos_area":pos_area}
                points_of_interest.append(new_poi)
            #convert npcs to a uniform format
            if j['npcs'] is not None:
                for key in j['npcs']:
                    if int(key)<738:
                        value = j['npcs'][key]
                        name = get_mob_name[int(key)]
                        poi_str+=name+"|"
                        is_portal=False
                        is_npc=True
                        offset_x = value[0]['x']
                        offset_y = value[0]['y']
                        pos = np.array([offset_x,offset_y])
                        pos_area = pos-map_offset
                        new_poi = {"position":pos,"type":1,"label":name,"pos_area":pos_area}
                        points_of_interest.append(new_poi)

            map_id = j['id']
            map_data = j['mapData']
            #map_offset = j['offset']
            map_size = j['size']
            map_decode = list(split(map_data,sep=[-1]))

            self.area_origin = map_offset
            self.botty_data['area_origin'] = map_offset

            nodes = []
            col_grid = []

            #map_decode.pop(-1)

            collision_grid = np.empty([int(map_size['height']),int(map_size['width'])], dtype=np.uint8)
            
            if map_data != None:
                mini_map_w=int(map_size['width'])
                mini_map_h=int(map_size['height'])
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
                    col_grid.append(row)
                    x=0
                    walkable = True
            

            new_map = {"crop": map_crop,"id": map_id,'poi': points_of_interest,"objects": map_objects,"size": map_size,"nodes":nodes,"data":col_grid}

            log = (":: Loaded map              -> {}".format(area_list[new_map['id']]))
            self.current_area=area_list[new_map['id']]
            self.botty_data['current_area']=area_list[new_map['id']]


            log_color(log,fg_color=0,bg_color=traverse_color)
            log = (":: Number of POI           -> {}".format(len(points_of_interest)))
            log_color(log,fg_color=0,bg_color=traverse_color)
            log = (":: {}".format(poi_str))
            log_color(log,fg_color=0,bg_color=traverse_color)
            log = (":: Number of OBJ           -> {}".format(len(map_objects)))
            log_color(log,fg_color=0,bg_color=traverse_color)
            log = (":: {}".format(obj_str))
            log_color(log,fg_color=0,bg_color=traverse_color)

            self.maps.append(new_map)
            self.botty_data['poi'] = points_of_interest
            self.botty_data['objects'] = map_objects
            self.botty_data['map']= collision_grid #np.array(collision_grid, dtype=np.uint8)
            return self.responseList

    def get_map_json_exit(self,seed, mapid:int, objectIDs:list=None):
        """Summary
        
        Args:
            seed (TYPE): Description
            mapid (int): Description
            objectIDs (list, optional): Description
        
        Returns:
            TYPE: Description
        """
        #map hosting
        base_url='http://34.69.54.92:8000'
        url=base_url+'/'+str(seed)+f'/2/{str(mapid)}/1'
        #
        print(url)
        resp = requests.get(url=url)
        j = resp.json()
        #data = json.loads(data,strict=False)   
        with open('data.json', 'w') as f:
            json.dump(j, f)
        obj = j['exits']
        obj = obj [str(objectIDs)]
        
        #print(sd)
        map_offset_x = j['offset']['x']
        map_offset_y = j['offset']['y']
        #self.chests = chests
        self.map_ox = map_offset_x
        self.map_oy = map_offset_y
        return obj['offsets']

    def get_game_info_offset(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        #get game info offset
        pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat)
        offset_buffer = self.process.read_int(pat_addr+8)
        game_info_offset = ((pat_addr - self.base)  + 7 -256 + 5 + offset_buffer)
        log = (":: Found game info offset  -> {}".format(hex(game_info_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        return game_info_offset

    def get_hover_object_offset(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        pat = b'\xc6\x84\xc2.....\x48\x8b\x74.'
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat, return_multiple=False)
        offset_buffer = self.process.read_bytes(pat_addr+3,4)
        offset_buffer_int = int.from_bytes(offset_buffer,'little')
        hover_offset = (offset_buffer_int)-1
        log = (":: Found hover offset        -> {}".format(hex(hover_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        return hover_offset

    def get_exp_offset(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        #expansion offset
        pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....\x83\x78\x5C.\x0F\x84....\x33\xD2\x41'
        #this works fine, shorter pattern
        pat = b'\xC7\x05........\x48\x85\xC0\x0F\x84....'
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat)
        offset_buffer = self.process.read_int(pat_addr-4)
        exp_offset = ((pat_addr - self.base) + offset_buffer)
        log = (":: Found exp offset        -> {}".format(hex(exp_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        return exp_offset

    def get_unit_offset(self):
        '''doc string
        
        Returns:
            TYPE: Description
        '''
        #unit table offset
        pat = b"\x48\x8d.....\x8b\xd1"
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat)
        offset_buffer = self.process.read_int(pat_addr+3)
        player_offset = ((pat_addr - self.base) + 7 + offset_buffer)
        log = (":: Found player offset     -> {}".format(hex(player_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        return player_offset


    def get_menu_data_offset(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        #unit table offset
        pat = b"\x41\x0f\xb6\xac\x3f...."
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat)
        offset_buffer = self.process.read_int(pat_addr-5)
        ui_offset = ((pat_addr - self.base) + offset_buffer)
        log = (":: Found menu data offset  -> {}".format(hex(ui_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        #ui_offset =  0x21F89AA
        return ui_offset

    def get_ui_settings_offset(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        #unit table offset
        pat = b"\x40\x84\xed\x0f\x94\x05"
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat)
        offset_buffer = self.process.read_int(pat_addr+6)
        ui_offset = ((pat_addr - self.base) + 10 + offset_buffer)
        log = (":: Found ui offset         -> {}".format(hex(ui_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        #ui_offset =  0x21F89AA
        return ui_offset

    def get_menu_vis_offset(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        #menu vis offset
        #pat = b'\x8B\x05....\x89\x44\x24\x20\x74\x07'
        #?? search less direct matches?
        pat = b'\x8B\x05....\x89\x44.\x20\x74\x07'
        pat_addr = pymem.pattern.pattern_scan_module(self.handle, self.module, pat)
        offset_buffer = self.process.read_int(pat_addr+2)
        #maybe dont need +6 here?
        menu_offset = ((pat_addr - self.base) + 6 + offset_buffer)
        log = (":: Found menu offset       -> {}".format(hex(menu_offset)))
        log_color(log,fg_color=0,bg_color=traverse_color)
        return menu_offset

    def get_last_hovered(self):
        """Summary
        """
        offset = self.hoverd_offset
        is_hovered = self.process.read_int(offset+self.base+0x00)
        is_tooltip = self.process.read_int(offset+self.base+0x01)
        hovered_unit_type = self.process.read_int(offset+self.base+0x03)
        hoverd_id = self.process.read_uint(offset+self.base+0x08)

        for m in self.monsters:
            if hoverd_id == m['id'] and is_hovered:
                print(m['name'])
                break


    def get_player_offset(self,loops):
        """Summary
        
        Args:
            loops (TYPE): Description
        
        Returns:
            TYPE: Description
        """
        found = False
        #ui_offset = 0x21F89AA
        attempts=0
        name = ""
        new_offset=0

        for i in range(loops):
            attempts=i+0
            new_offset = (self.starting_offset)+(attempts-1)*8

            start_addr = self.base + new_offset

            player_unit = self.process.read_longlong(start_addr)
            #print (player_unit)
            while player_unit>0:
                p_inventory = player_unit+0x90
                inventory = self.process.read_longlong(p_inventory)
                if(inventory):
                    log = (":: Found inventory offset  -> {}".format(hex(self.base-inventory)))
                    log_color(log,fg_color=0,bg_color=traverse_color)
                    exp_char = self.process.read_ushort(self.base+self.exp_offset)
                    base_check = self.process.read_ushort(inventory+0x30) !=1
                    if(exp_char):
                        log = (":: Expansion char          -> True")
                        log_color(log,fg_color=0,bg_color=traverse_color)
                        base_check = self.process.read_ushort(inventory+0x70) !=0

                if(base_check):
                    #print("base checks")
                    p_act = player_unit+0x20
                    act_addr = self.process.read_ulonglong(p_act)
                    map_seed_addr = act_addr +0x14
                    map_seed = self.process.read_uint(map_seed_addr)
                    self.map_seed = map_seed
                    #print(map_seed)
                    p_path = player_unit+0x38
                    path_addr = self.process.read_longlong(p_path)

                    x_pos = self.process.read_ushort(path_addr+0x02)
                    #print (x_pos)
                    y_pos = self.process.read_ushort(path_addr+0x06)
                    #print (y_pos)
                    p_unit_data = player_unit +0x10
                    try:
                        player_name_addr = self.process.read_longlong(p_unit_data)
                    except:
                        pass
                    p_name = ""
                    #
                    for i in range(16):
                        name = name + str(chr(self.process.read_uchar(player_name_addr+i-1)))

                    if(x_pos> 0 and y_pos >0 and len(str(map_seed))>6):
                        if loops > 1:
                            log = (":: Found player name       -> {}".format(name))
                            log_color(log,fg_color=0,bg_color=traverse_color)
                            log = (":: Found map seed          -> {}".format(map_seed))
                            log_color(log,fg_color=0,bg_color=traverse_color)
                        new_offset = new_offset+0
                        found = True
                        self.player_unit = new_offset
                        self.path_addr = path_addr
                        return True

                new_offset = (player_unit+0x150)-self.base
                try:
                    player_unit = self.process.read_longlong(player_unit +0x150)
                except:
                    pass


    def get_current_level(self):
        """Summary
        """
        startingAddress = self.base + self.player_unit
        playerUnit = self.process.read_ulonglong(startingAddress)
        pUnitData = playerUnit + 0x10
        #get the level number
        pPathAddress = playerUnit + 0x38
        pPath = self.process.read_ulonglong(pPathAddress)
        pRoom1 = pPath + 0x20
        pRoom1Address = self.process.read_ulonglong(pRoom1)
        pRoom2 = pRoom1Address + 0x18
        pRoom2Address = self.process.read_ulonglong(pRoom2)
        pLevel = pRoom2Address + 0x90
        pLevelAddress = self.process.read_ulonglong(pLevel)
        dwLevelNo = pLevelAddress + 0x1F8
        levelNo = self.process.read_uint(dwLevelNo)
        self._level_addr = dwLevelNo
        self.level = levelNo

    def find_info(self):
        """Summary
        
        Returns:
            TYPE: Description
        """
        startingAddress = self.base + self.player_unit
        playerUnit = self.process.read_ulonglong(startingAddress)

        pUnitData = playerUnit + 0x10
        try:
            playerNameAddress = self.process.read_ulonglong(pUnitData)
        except:
            print("FAILED")
            print("FAILED")
            print("FAILED")
            print("FAILED")
            print("FAILED")
            print("FAILED")
            return False
            pass
        if(playerNameAddress):
            playerName = self.process.read_string(playerNameAddress)
        
        pStatsListEx = self.process.read_ulonglong(playerUnit+0x88)
        statPtr = self.process.read_ulonglong(pStatsListEx+0x30)
        statCount = self.process.read_ulonglong(pStatsListEx+0x38)

        for i in range(statCount):

            statOffset = (i-1) * 8
            statEnum = self.process.read_ushort(statPtr + 0x2 + statOffset)
            if (statEnum == 12):
                self.player_level = self.process.read_uint(statPtr + 0x4 + statOffset)
            if (statEnum == 13):
                self.experience = self.process.read_uint(statPtr + 0x4 + statOffset)
            if (statEnum == 6):
                hp = self.process.read_uint(statPtr + 0x4 + statOffset)
                self.hp = hp >> 8
            if (statEnum == 7):
                maxhp = self.process.read_uint(statPtr + 0x4 + statOffset)
                self.max_hp = maxhp >> 8
        log = ":: LVL:" +str(self.player_level)+", HP:"+str(self.max_hp)+", EXP:"+str(self.experience)
        log_color(log,fg_color=0,bg_color=traverse_color)

        #get the level number
        pPathAddress = playerUnit + 0x38
        pPath = self.process.read_ulonglong(pPathAddress)
        pRoom1 = pPath + 0x20
        pRoom1Address = self.process.read_ulonglong(pRoom1)
        pRoom2 = pRoom1Address + 0x18
        pRoom2Address = self.process.read_ulonglong(pRoom2)
        pLevel = pRoom2Address + 0x90
        pLevelAddress = self.process.read_ulonglong(pLevel)
        dwLevelNo = pLevelAddress + 0x1F8
        levelNo = self.process.read_uint(dwLevelNo)
        self._level_addr = dwLevelNo
        
        
        self.level = levelNo
        log = (":: current level      -> "+str(area_list[levelNo]))
        log_color(log,fg_color=0,bg_color=traverse_color)

        if not levelNo:
            log = "!! Did not find level num using player offset" +str(playerOffset)
            log_color(log,fg_color=0,bg_color=traverse_color)


        #get the map seed
        pAct = playerUnit + 0x20
        actAddress = self.process.read_ulonglong(pAct)


        if actAddress:
            mapSeedAddress = actAddress + 0x14
            if mapSeedAddress:
                mapSeed = self.process.read_uint(mapSeedAddress)
                self.map_seed = mapSeed
                #print("Found seed"+str(mapSeed)+ "at address" +str(mapSeedAddress))
            else:
                log = ("!! Did not find map seed at address"+(mapSeedAddress))
                log_color(log,fg_color=0,bg_color=traverse_color)

        #get the level number
        actAddress = self.process.read_ulonglong(pAct)

        pActUnk1 = actAddress + 0x70
        aActUnk2 = self.process.read_ulonglong(pActUnk1)
        aDifficulty = aActUnk2 + 0x830
        difficulty = self.process.read_ushort(aDifficulty)
        self.difficulty=difficulty

        if difficulty==0:
            log = (":: current difficulty      -> Normal")
            log_color(log,fg_color=0,bg_color=traverse_color)
        if difficulty==1:
            log = (":: current difficulty      -> Nightmare")
            log_color(log,fg_color=0,bg_color=traverse_color)
        if difficulty==2:
            log = (":: current difficulty      -> Hell")
            log_color(log,fg_color=0,bg_color=traverse_color)

    def normalized_p(self):
        """Summary
        """
        self.np_x = float(self.map_ox)/float(self.process.read_ushort(self.path_addr+0x02))
        self.np_y = float(self.map_oy)/float(self.process.read_ushort(self.path_addr+0x06))

    def get_ppos(self):
        """Summary
        """
        x = self.process.read_ushort(self.path_addr+0x02)
        y = self.process.read_ushort(self.path_addr+0x06)
        self.player_world_pos = np.array([x,y])
        self.botty_data['player_pos_area'] =self.player_world_pos -self.area_origin
        self.botty_data['player_pos_world'] = self.player_world_pos

    def chest_dist(self):
        '''doc string'''
        self.x_pos = self.process.read_ushort(self.path_addr+0x02)-self.map_ox
        self.y_pos = self.process.read_ushort(self.path_addr+0x06)-self.map_oy

        for chest in self.chests:
            chest_loc_x = chest['x']
            chest_loc_y = chest['y']
            odist = math.dist([chest_loc_x,chest_loc_y],[self.x_pos,self.y_pos])
            #print('dist -> '+ str(odist))
            #print('current pos ->  '+str(self.x_pos)+','+str(self.y_pos))

    def find_objects(self, file_number:int):
        """Summary
        
        Args:
            file_number (int): Description
        
        Returns:
            TYPE: Description
        """
        self.super_chests =[]
        object_offset = self.starting_offset + (2 * 1024)
        attempts=0


        for i in range(256):
            attempts=i+0
            new_offset = object_offset + (8 * (i-1))
            item_addr = self.base + new_offset
            object_unit = self.process.read_longlong(item_addr)

            #print(i)
            while (object_unit>0):
                item_type = self.process.read_int(object_unit+0x00)
                pRoomnext = self.process.read_ulonglong(object_unit+0x158)
                #pRoomEx = self.process.read_ulonglong (pRoomnext+0x18)
                if(item_type==2):
                    file_no = self.process.read_int(object_unit+0x04)
                    if file_no == file_number:
                        print ("Object found")
                        p_unit_data = self.process.read_ulonglong(object_unit + 0x10)
                        mode = self.process.read_uint (object_unit + 0x0C)
                        #pObjectTxt = self.process.read_ulonglong(p_unit_data)
                        #print(str(pObjectTxt))
                        #sObjectTxt = self.process.read_string(p_unit_data, 16)
                        #shrineTxt = self.process.read_string(p_unit_data + 0x0c, 16)
                        pPath = self.process.read_ulonglong(object_unit + 0x38)  
                        objectx = self.process.read_ushort(pPath + 0x10)
                        objecty = self.process.read_ushort(pPath + 0x14)
                        self.x_pos = self.process.read_ushort(self.path_addr+0x02)
                        self.y_pos = self.process.read_ushort(self.path_addr+0x06)
                        odist = math.dist([objectx,objecty],[self.x_pos,self.y_pos])
                        #print(self.y_pos)
                        #print(self.x_pos)
                        print(txt_obj_name[file_no-1] + ""+ str(str(file_no)))    
                        print('dist -> '+ str(odist))
                        obj = Object (objectx, objecty, mode)
                        return obj



                object_unit = self.process.read_longlong(object_unit + 0x150)
    




    def ui_status(self):
        """Summary
        """
        InGame = False
        Inventory =  False
        Character =  False
        SkillSelect = False
        SkillTree = False
        Chat = False
        NpcInteract =  False
        EscMenu = False
        Map = False
        NpcShop = False
        QuestLog = False
        Waypoint = False
        Party = False
        Stash = False
        Cube = False
        AltPick = False
        Potions=False

        offset = self.ui_settings_offset
        ui = self.base + offset
        item_pick = self.process.read_ushort(ui+2)
        quit_menu = self.process.read_bytes(ui-0x01,1)
        quit_menu_int = int.from_bytes(quit_menu,"little")
        quest_menu = self.process.read_bytes(ui+0x04,1)
        quest_menu_int = int.from_bytes(quest_menu,"little")
        skill_menu = self.process.read_bytes(ui-0x06,1)
        skill_menu_int = int.from_bytes(skill_menu,"little")
        char_menu = self.process.read_bytes(ui-0x08,1)
        char_menu_int = int.from_bytes(char_menu,"little")
        stash_menu = self.process.read_bytes(ui-0x19+0x28-1,1)
        stash_menu_int = int.from_bytes(stash_menu,"little")
        npc_menu = self.process.read_bytes(ui+1,1)
        npc_menu_int = int.from_bytes(npc_menu,"little")
        inv_menu = self.process.read_bytes(ui-0x09,1)
        inv_menu_int = int.from_bytes(inv_menu,"little")
        merc_menu = self.process.read_ushort(ui+0x14)
        party_menu = self.process.read_bytes(ui+0x0b,1)
        party_menu_int = int.from_bytes(party_menu,"little")
        waypoint_menu = self.process.read_bytes(ui+0x09,1)
        #ugh why
        waypoint_menu_int = int.from_bytes(waypoint_menu,"little")
        in_game = self.process.read_bytes(ui+0x08,1)
        in_game_int = int.from_bytes(in_game,"little")

        cube_menu = self.process.read_bytes(ui-0x19+0x28,1)
        cube_menu_int = int.from_bytes(cube_menu,"little")
        
        map_menu = self.process.read_bytes(ui-0x19+0x28-15,1)
        map_menu_int = int.from_bytes(map_menu,"little")

        potion_menu = self.process.read_bytes(ui-0x19+0x28+1,1)
        potion_menu_int = int.from_bytes(potion_menu,"little")

        npc_interact = self.process.read_bytes(ui-0x19+0x28-0x11,1)
        npc_interact_int = int.from_bytes(npc_interact,"little")
        

        chat = self.process.read_bytes(ui-0x19+0x28-0x11-3,1)
        chat_int = int.from_bytes(chat,"little")

        if chat_int:
            Chat=True
            #print("chattings")
        if npc_interact_int:
            NpcInteract=True
            #print('talkign to npc')
        if potion_menu_int:
            Potions=True
            #print('pOtioOn is active')
        if map_menu_int:
            Map=True
            #print('Map is active')
        if cube_menu_int:
            Cube=True
            #print('Cube is active')
        if in_game_int:
            #print('in game') #works
            InGame=True
        if stash_menu_int:
            #print('stash menu is  active')
            Stash=True
        if npc_menu_int:
            #print('npc menu is  active')
            NpcShop=True
        if party_menu_int:
            #print('party menu is  active')
            Party=True
        if inv_menu_int:
            #print('inv menu is  active')
            Inventory=True
        if waypoint_menu_int:
            #print('waypoint menu is  active')
            Waypoint=True
        if quit_menu_int:
            EscMenu=True
            #print('!!!quit menu is  active')
        if item_pick:
            AltPick=True
            #print('item pick is active')
        if quest_menu_int:
            QuestLog=True
            #print('Quest log is active')
        if char_menu_int:
            Character=True
            #print('Char menu is active')
        if skill_menu_int:
            SkillTree=True
            #print('Skill tree is active')

        self.menus =    {'InGame': InGame,
                        'Inventory': Inventory,
                        'Character': Character,
                        'SkillSelect': SkillSelect,
                        'SkillTree': SkillTree,
                        'Chat': Chat,
                        'NpcInteract': NpcInteract,
                        'EscMenu': EscMenu,
                        'Map': Map,
                        'NpcShop': NpcShop,
                        'QuestLog': QuestLog,
                        'Waypoint': Waypoint,
                        'Party': Party,
                        'Stash': Stash,
                        'Cube': Cube,
                        'AltPick':AltPick,
                        'Potions':Potions
                        }


    def find_items(self):
        """Summary
        """
        items = []
        item_offset = self.starting_offset + (4*1024)

        for i in range(256):


            new_offset = item_offset +(8 *(i))
            item_addr = self.base + new_offset
            item_unit = self.process.read_longlong(item_addr)

            while (item_unit>0):
                item_type = self.process.read_uint(item_unit+0x00)
                if item_type == 4:
                    txt_file_no = self.process.read_uint(item_unit+0x04)
                    item_loc = self.process.read_uint(item_unit+0x0C)

                    # item loc 0 = inventory, 1 = equipped, 2 in belt, 3 on ground, 4 cursor, 5 dropping ,6 socketed
                    if item_loc == 3 or item_loc == 5:
                        #print("item on ground")
                        p_unit_data = self.process.read_longlong(item_unit + 0x10)
                        #itemQuality - 5 is set, 7 is unique (6 rare, 4, magic)
                        item_quality = self.process.read_uint(p_unit_data)
                        p_path = self.process.read_longlong(item_unit+0x38)
                        item_x = self.process.read_ushort(p_path+0x10)
                        item_y = self.process.read_ushort(p_path+0x14)

                        p_stat_list_ex = self.process.read_longlong(item_unit + 0x88)
                        stat_ptr = self.process.read_longlong(p_stat_list_ex + 0x30)
                        stat_count = self.process.read_longlong(p_stat_list_ex + 0x38)
                        num_sockets = 0

                        for j in range(stat_count):
                            #print("checking for sockets")
                            stat_offset = (j)*8
                            stat_enum = self.process.read_ushort(stat_ptr+0x2+stat_offset)
                            if stat_enum == 194:
                                num_sockets = self.process.read_uint(stat_ptr+0x4+stat_offset)
                                #print('number of sockets ->'+str(num_sockets))
                                break

                        flags = self.process.read_uint(p_unit_data+0x18)


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


                        for category in self._loot_data:
                            q_match = 0
                            i_match = 0
                            loot_check = 0

                            data = self._loot_data.get(category)
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
                                #self._move_to_mem(item_x,item_y)
                                print(item_name[txt_file_no])


                        #hard coded test for thul and ist
                        #if txt_file_no == 619 or txt_file_no == 620 or txt_file_no == 633:
                        #   self._move_to_mem(item_x,item_y)
                        #   print(items_list.item_name[txt_file_no])

                    if item_loc == 4:
                        #print("item on cursor")
                        p_unit_data = self.process.read_longlong(item_unit + 0x10)
                        item_quality = self.process.read_longlong(p_unit_data)
                        p_path = self.process.read_longlong(item_unit+0x38)
                        item_x = self.process.read_ushort(p_path+0x10)
                        item_y = self.process.read_ushort(p_path+0x14)
                        #print(item_loc,item_type,txt_file_no)
                        #print(item_x,item_y)
                        

                item_unit = self.process.read_longlong(item_unit + 0x150)


    def find_mobs(self):
        """Summary
        """
        monstersOffset = self.starting_offset + 1024
        mobs = []
        loc_monsters = []
        skel_count =0
        mage_count =0
        golem_count = 'none'

        for i in range(128):
            newOffset = monstersOffset + (8 * (i - 1))
            mobAddress = self.base + newOffset
            mobUnit = self.process.read_longlong(mobAddress)
            
            while (mobUnit> 0):

                txtFileNo = self.process.read_uint(mobUnit + 0x04)
                hide_check = 0
                try:
                    hide_npc[txtFileNo]
                except:
                    #no key 
                    pass

                if not hide_check:

                    mobTypeString = ""
                    #
                    unit_data = self.process.read_ulonglong(mobUnit + 0x10)
                    mob_type = self.process.read_bytes(unit_data+0x1a,1)
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
                        
                    

                    unitId = self.process.read_uint(mobUnit + 0x08)
                    mode = self.process.read_uint(mobUnit + 0x0c)
                    iscorpse = self.process.read_uchar (mobUnit + 0x1A6)
                    interactable = self.process.read_uchar (mobUnit + 0x1A6+4)
                    pUnitData = self.process.read_longlong(mobUnit + 0x10)
                    pPath = self.process.read_longlong(mobUnit + 0x38)
                
                    isUnique = self.process.read_ushort(pUnitData + 0x18)
                    #????
                    uniqueNo = self.process.read_ushort(pUnitData + 42)

                    monx = self.process.read_ushort(pPath + 0x02)
                    mony = self.process.read_ushort(pPath + 0x06)
                    xPosOffset = self.process.read_ushort(pPath + 0x00) 
                    yPosOffset = self.process.read_ushort(pPath + 0x04)
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
                    BossLineID = self.process.read_ushort(unit_data + 0x2A) 

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
                    pStatsListEx = self.process.read_longlong(mobUnit + 0x88)
                    ownerType = self.process.read_uint(pStatsListEx + 0x08)
                    ownerId = self.process.read_uint(pStatsListEx + 0x0C)

                    statPtr = self.process.read_longlong(pStatsListEx + 0x30)
                    statCount = self.process.read_longlong(pStatsListEx + 0x38)

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
                    immunities = {'physical': 0,'magic': 0,'fire': 0,'light': 0,'cold': 0,'poison': 0}
                    auras = {'MightAura': 0,'HolyFireAura': 0, 'BlessedAimAura': 0, 'HolyFreezeAura': 0, 'HolyShockAura': 0,'ConvictionAura': 0,'FanaticismAura':0}
                    enchants = {'ExtraStrong': 0,'ExtraFast': 0, 'Cursed': 0, 'MagicResistant': 0, 'FireEnchanted': 0,'LigntningEnchanted': 0,'ColdEnchanted':0,'ManaBurn':0,'Teleportation':0,'SpectralHit':0,'StoneSkin':0,'MultipleShots':0,'Berserker':0}

                    for s in range(statCount):
                        offset = (s -1) * 8
                        statParam = self.process.read_ushort(statPtr + offset)
                        statEnum = self.process.read_ushort(statPtr + 0x2 + offset)
                        statValue = self.process.read_uint(statPtr + 0x4 + offset)
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
                    self.get_ppos()
                    dist = math.dist(self.player_world_pos,np.array([int(monx),int(mony)]))

                    abs_screen_position = world_to_abs(np.array([monx,mony]), self.player_world_pos)
                    mob = {'position': np.array([int(monx),int(mony)]),'dist': dist, 'abs_screen_position': abs_screen_position, 'immunities': immunities, 'unit_type': 'Monster', 'type': mobTypeString, 'id': unitId, 'name': textTitle, 'mode': mode, 'number': txtFileNo, 'super_unique':isUnique,'boss':isBoss,'is_corpse':iscorpse, 'interactable':interactable }
                    
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

                            #if dist<5:
                            #    print(mob['name'])

                            #    print(mob['id'])
                            #    print(mob['number'])

                #get next mob
                mobUnit = self.process.read_longlong(mobUnit + 0x150)
        self.monsters = loc_monsters
        self.botty_data['monsters'] = loc_monsters
        if self.botty_data['necroSkel'] != skel_count:
            self.botty_data['necroSkel']=skel_count
        if self.botty_data['necroMage'] != mage_count:
            self.botty_data['necroMage']=mage_count
        if self.botty_data['necroGol']!=golem_count:
            self.botty_data['necroGol'] = golem_count



if __name__ == "__main__":
    
    #get new starting offsets
    d2 = d2r_proc()

    #check if we are in game
    ui = d2.base + d2.ui_settings_offset
    igo =0x08
    in_game = d2.process.read_bytes(ui+igo,1)
    in_game = int.from_bytes(in_game,"little")
    current_level = -1

    new_session = 1
    #constant update
    while 1:
        if new_session==1 and in_game==1:

            d2.get_player_offset(128)
            d2.find_info()
            d2.get_ppos()

            d2.get_map_json(str(d2.map_seed), d2.level)
            d2.read_loot_cfg()
            new_session=0
            current_level = d2.level

        if in_game==1:
            try:
                d2.get_current_level()
            except:
                pass
            if current_level != d2.level:
                d2.get_map_json(str(d2.map_seed), d2.level)
                current_level = d2.level
            d2.get_ppos()
            d2.find_mobs()
            d2.ui_status()
            d2.find_items()
            d2.botty_data['menus'] = d2.menus

            d2.get_last_hovered()
        if in_game == 0:
            new_session=1
        in_game = d2.process.read_bytes(ui+igo,1)
        in_game = int.from_bytes(in_game,"little")
        time.sleep(.02)

