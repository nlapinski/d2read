'''globals for game state'''
from dataclasses import dataclass
import dataclasses
import numpy as np

new_session = 1
loaded = 0
in_game = 0
game_info_state = 0
game_name = "blank"
game_pass = "blank"
tick_count=0
hevent = 0
get_tick_count = 0
counter =0 
frame_counter = 0
tick = 0x00
difficulty = -1

fps = 999

#loot/items
loot_data = []
items = []
hover_obj = 0

#player info
player_world_pos = np.array([0,0])
player_area_pos = np.array([0,0])
player_float_offset = np.array([0.0,0.0],dtype=np.float32)

necro_skel = 0
necro_mage = 0
necro_gol = "none"
necro_rev = 0

used_skill = 0
right_skill = 0
left_skill = 0
belt_health_pots = 0
belt_mana_pots = 0

#path info
astar_current_path = None
current_path = None

ip = '127.0.0.1'

#map info
mini_map_w = 0
mini_map_h = 0
map = []
grid=[] #used
level = 100
area_origin = np.array([0,0])
current_area = 0
collision_grid = None
points_of_interest = []
map_objects = []
maps = []
features = []
clusters = None


#gs info
monsters = []
poi = []


@dataclass
class GameInfo:
    """ store game info
    """
    in_game : int = 0,
    new_session : int = 1,
    loaded : int = 0,
    ip_addr : str = "127.0.0.1",
    game_name : str="blank",
    game_pass : str="blank",

@dataclass
class NPC:
    """ store the data for a NPC
    """
    pos:np.ndarray = np.array([0,0]),
    type:int=0
    flag:int=0
    name:str =""
    pos_area:np.ndarray = np.array([0,0]),

@dataclass
class Monster:
    """ store the data for a monster
    """
    pos:np.ndarray = np.array([0,0]),
    type:int=0
    flag:int=0
    name:str =""
    pos_area:np.ndarray = np.array([0,0]),

@dataclass
class GameObject:
    """ store some static game object info
    """
    pos:np.ndarray = np.array([0,0]),
    type:int=0
    flag:int=0
    name:str =""
    pos_area:np.ndarray = np.array([0,0]),

@dataclass
class POI:
    """ store a point of interest, usually a waypooint or zone exit
    """
    pos:np.ndarray = np.array([0,0]),
    type:int =0
    label:str =""
    pos_area:np.ndarray = np.array([0,0]),
    is_npc:int = 0,
    is_portal:int =0,



@dataclass
class Map:

    """map storage
    """
    
    loaded:int = 0,
    map_offset :int = 0,
    grid:list =[],
    level:int = 100,
    mini_map_w:int = 0,
    mini_map_h:int = 0,
    poi:list = [],
    map:list = [],
    current_area:int = 0,
    area_origin:np.ndarray = np.array([0,0]),
    points_of_interest:list = [],
    map_objects:list = [],
    collision_grid: np.ndarray = None,
    features: np.ndarray = None,
    clusters: np.ndarray = None,
#global map store
_tmp_map = Map()


@dataclass
class Player:

    """ player info
    """
    
    name: str = "",
    exp: int  = 0,
    lvl: int = 0,
    world_pos : np.ndarray = np.array([0,0]),
    area_pos : np.ndarray = np.array([0,0]),
    pos_float_offset : np.ndarray = np.array([0.0,0.0],dtype=np.float32),
    inventory :list = [],
    used_skill:int  = 0,
    right_skill: int = 0,
    left_skill: int = 0,
    belt_health_pots :int  = 0,
    belt_mana_pots: int = 0,
#global player store
player = Player()

@dataclass
class UI:

    """ ui state data
    """

    InGame : bool = False
    Inventory :  bool = False
    Character :  bool = False
    SkillSelect : bool = False
    SkillTree : bool = False
    Chat : bool = False
    NpcInteract :  bool = False
    EscMenu : bool = False
    Map : bool = False
    NpcShop : bool = False
    GroundItems : bool = False
    Anvil : bool = False
    QuestLog : bool = False
    Waypoint : bool = False
    Party : bool = False
    Stash : bool = False
    Cube : bool = False
    PotionBelt : bool = False
    Help : bool = False
    Portraits : bool = False
    MercenaryInventory : bool = False
    Help : bool = False
#make a global
ui_state = UI()
