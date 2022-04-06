'''globals for game state'''
import numpy as np
from multiprocessing import shared_memory
from multiprocessing import Process
import multiprocessing
import pymem
from ctypes import *
import ctypes
from multiprocessing.sharedctypes import RawArray, RawValue

from .utils import FPS

manager_list  = None
ofl  = None

tick = 0x00
fps = 999

#current player pathing
astar_current_path = None
current_path = None

#global player

process = pymem.Pymem("D2R.exe")
handle = process.process_handle
module = pymem.process.module_from_name(handle,"D2R.exe")
base = process.base_address


class Point(Structure):
    _fields_ = [("x", c_double), ("y", c_double)]

class Point_i(Structure):
    _fields_ = [("x", c_short), ("y", c_short)]



class GamePointers(Structure):
    """ store memory offsets
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("act", c_uint64),
                ("player", c_uint64),
                ("player_path", c_uint64),
                ("level", c_uint64),
                ]


class MemoryOffsets(Structure):
    """ store memory offsets
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("base", c_uint64),
                ("game_info", c_uint64),
                ("hover_object", c_uint64),
                ("expansion", c_uint64),
                ("unit_table", c_uint64),
                ("menu_data", c_uint64),
                ("ui_settings", c_uint64),
                ("menu_vis", c_uint64),
                ("player_unit", c_uint64),
                ("player_path", c_uint64),
                ("player_hp", c_uint64),
                ("player_mp", c_uint64),

                ("unit", c_uint64),
                ("roster", c_uint64),
                ]


class Running(Structure):
    """ store a main shutdown var
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("main", c_short),
                ("fps1", c_float),
                ("fps2", c_float),
                ("fps3", c_float),
                ("fps4", c_float),
                ("fps5", c_float),
                ("tick_lock", c_short),
                ]


class Summons(Structure):
    """ store the data for a player summons (necro / druid )
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("skel", c_short),
                ("mage", c_short),
                ("rev", c_short),
                ("gol", ctypes.c_char*32),                
                ]

class Monster(Structure):
    """ store the data for a monster
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("immunities", ctypes.c_char*8),
                ("pos", Point),
                ("area_pos", Point),
                ("abs_screen_pos", Point),
                ("dist", c_float),
                ("type", c_short),
                ("flag", c_short),
                ("mob_type_str", ctypes.c_char*16),
                ("unit_id", c_uint32),
                ("name", ctypes.c_char*32),
                ("mode", c_short),
                ("text_file_no", c_short),
                ("updated", c_short),
                ("is_npc", c_short),
                ]


class GameObject(Structure):
    """ store the data for a monster
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("name", ctypes.c_char*64),
                ("pos", Point),
                ("area_pos", Point),
                ("abs_screen_pos", Point),
                ("dist", c_float),
                ("type", c_short),
                ("mode", c_short),
                ("text_file_no", c_short),
                ]

class POI(Structure):
    """ store the data for a monster
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("name", ctypes.c_char*64),
                ("pos", Point),
                ("area_pos", Point),
                ("abs_screen_pos", Point),
                ("dist", c_float),
                ("type", c_short),
                ("mode", c_short),
                ("is_npc", c_short),
                ("is_portal", c_short),
                ("text_file_no", c_short),
                ("is_exit", c_short),
                ]

class Area(Structure):
    """ store the data for a area loaded (map data)
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("current_area", ctypes.c_char*42),
                ("origin", Point),
                ("level", c_long),
                ("mini_map_size", Point),
                ("poi", POI*128),
                ("objects", GameObject*128),
                ("map", (ctypes.c_short * 2048) * 2048),
                ("pos_float_offset", Point),
                ("clusters", Point_i*512),
                ("cluster_count", c_long),
                ("feature_count", c_long),
                ("clusters_ready",c_short),
                ("loaded", c_short),
                ("seed", c_long),
                ("difficulty", c_uint8),
                ]    

class Player(Structure):
    """ store the data for a player
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [('name',((c_uint16 ) * 16)),
                ("lvl", c_short),
                ("exp", c_long),
                ("pos", Point),
                ("pos_i", Point_i),
                ("area_pos", Point),
                ("pos_float_offset", Point),
                ("hp", c_long),
                ("mp", c_long),
                ("base_hp", c_long),
                ("base_mp", c_long),
                ("updated", c_short),
                ("summons", Summons)
                ]

class UI(Structure):
    """ui state data - not currently used
    
    Args:
        InGame (bool): are we in game
        Inventory (bool): inventory screen ui
        Character (bool): char stat screen
        SkillSelect (bool): mini skill ui
        SkillTree (bool): skill tree / add points
        Chat (bool): chats
        NpcInteract (bool): are we talking to a npc/ overhead menu
        EscMenu (bool): exit
        Map (bool): map overlay
        NpcShop (bool): shoppping inventory
        GroundItems (bool): alt key ground items
        Anvil (bool): imbue
        QuestLog (bool): quest menu
        Waypoint (bool): travel wp menu
        Party (bool): party
        Stash (bool): stashing
        Cube (bool): cube
        PotionBelt (bool): pots
        Help (bool): help ui
        Portraits (bool): merc/summon portraits
        MercenaryInventory (bool): merc inv O
        Help (bool): help
    
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("InGame", c_short),
                ("Inventory", c_short),
                ("Character", c_short),
                ("SkillSelect", c_short),
                ("SkillTree", c_short),
                ("Chat", c_short),
                ("NpcInteract", c_short),
                ("Map", c_short),
                ("NpcShop", c_short),
                ("GroundItems", c_short),
                ("Anvil", c_short),
                ("QuestLog", c_short),
                ("Waypoint", c_short),
                ("Party", c_short),
                ("Stash", c_short),
                ("Cube", c_short),
                ("PotionBelt", c_short),
                ("Help", c_short),
                ("Portraits", c_short),
                ("MercenaryInventory", c_short),
                ("Help", c_short),
                ]

class Item(Structure):
    """ store the data for a item
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("name", ctypes.c_char*32),
                ("pos", Point),
                ("area_pos", Point),
                ("abs_screen_pos", Point),
                ("dist", c_float),
                ("quality", c_short),
                ("quality_str", ctypes.c_char*16),
                ("slot", c_short),
                ("location", c_short),
                ("sockets", c_short),
                ("inventory_page", c_short),
                ("txt_id", c_short),
                ("good", c_short),
                ("unit_id", c_short),
                ]


#global ui info
ui_state = UI()


class GameInfo(Structure):
    """ store the data for a game
    """
    def __repr__(self):
        '''Print the fields'''
        res = []
        for field in self._fields_:
            res.append('%s=%s' % (field[0], repr(getattr(self, field[0]))))            
        return self.__class__.__name__ + '(' + ','.join(res) + ')'

    _fields_ = [("name", ctypes.c_char*32),
                ("ip", ctypes.c_char*24),
                ("game_name", ctypes.c_char*42),
                ("game_pass", ctypes.c_char*42),
                ("offset", Point),
                ("id", c_uint32),
                ("seed", c_long),
                ("difficulty", c_uint8),
                ("loaded", c_short),
                ("unit_id", c_short),
                ("in_game", c_short),
                ("new_session", c_short),
                ("hovered_id", c_long),
                ("hovered_item", Item),
                ("hovered_monster", Monster),
                ("tick_lock", c_short),
                ("mem", MemoryOffsets),
                ("ptr", GamePointers),
                ("player", Player),
                ]