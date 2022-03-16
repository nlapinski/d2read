'''globals for game state'''
from dataclasses import dataclass
import dataclasses
import numpy as np

tick = 0x00
fps = 999

#loot/items
loot_data = []
items = []

#current player pathing
astar_current_path = None
current_path = None

#list of all monsters in game, nearby
monsters=[]

@dataclass
class Summons:
    """ store game info for summons
    """
    skele:int = 0,
    mage:int = 0,
    golem:str = "none",
    revive:int = 0,

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
    immunities:dict
    pos: np.ndarray = np.array([0,0])
    area_pos: np.ndarray = np.array([0,0]),
    abs_scren_pos: np.ndarray = np.array([0,0])
    dist:float = 9999.0
    type:int=0
    flag:int=0
    mob_type_str : str = "none"
    unit_id: int = 0
    name:str =""
    mode: int =0
    text_file_no:int = 0
    

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
class Area:
    """map storage
    """
    loaded:int = 0,
    offset:np.ndarray = np.array([0,0]),
    level:int = -2,
    mini_map_w: int = 100,
    mini_map_h: int = 100,
    poi:list = [],
    map:list = [],
    current_area:str = "not loaded",
    origin:np.ndarray = np.array([0,0]),
    points_of_interest:list = [],
    objects:list = [],
    collision_grid: np.ndarray = None,
    features: np.ndarray = np.array([0,0]),
    clusters: np.ndarray= np.array([0,0]),



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

@dataclass
class UI:
    """ui state data
    
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

@dataclass
class Item:
    """ ui state data
    """
    world_pos : np.ndarray = np.array([0,0]),
    id: int =0,
    good:int =0

@dataclass
class GameInfo:
    """ store game info, implemented
    """
    in_game:int = 0,
    new_session:int = 1,
    loaded:int=0,
    ip_addr:str = "127.0.0.1",
    game_name : str="blank",
    game_pass : str="blank",
    seed:int  = 0,
    difficulty:int = -1,
    hovered_item:Item = None,
    hovered_monster:Monster = None
    hovered_id:int = 0,

#global ui info
ui_state = UI()
#global map store
area = Area(mini_map_w = 0,mini_map_h = 0,level=-2)
#global player info
player = Player()
#game info store
game_info = GameInfo(
                in_game=0,
                new_session = 1,
                loaded=0,
                ip_addr= "127.0.0.1",
                game_name ="blank",
                game_pass ="blank",
                seed = 0,
                difficulty= -1
            )
#player summoned things
summons = Summons(0,0,"none",0)
