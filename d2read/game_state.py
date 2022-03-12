import pymem 
import numpy as np
from dataclasses import dataclass
import dataclasses

d2_process = 0
exp_offset = 0
starting_offset = 0
game_info_offset = 0
ui_settings_offset = 0
menu_vis_offset = 0
menu_data_offset = 0
hovered_offset = 0
process = pymem.Pymem("D2R.exe")
player_unit = 0
player_offset = 0
handle = process.process_handle
module = pymem.process.module_from_name(handle,"D2R.exe")
base = process.base_address
responseList = []
map_offset = 0
grid=[]
level = 1
player_world_pos = np.array([0,0])
area_origin = np.array([0,0])
in_game = 0
loaded = 0
monsters = []
poi = []
items = []
map = []
current_area = 0
used_skill = 0
right_skill = 0
left_skill = 0
belt_health_pots = 0
belt_mana_pots = 0
area_origin = np.array([0,0])
points_of_interest = []
map_objects = []
collision_grid = None
path_addr = 0

menus =    {'InGame': False,
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

maps = []
loot_data = []

features = []
clusters = []
necro_skel = 0
necro_mage = 0
necro_gol = "none"

#initalize our UI storage object
@dataclass
class UI:
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
