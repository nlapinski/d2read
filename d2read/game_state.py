'''globals for game state'''

import numpy as np
from dataclasses import dataclass
import dataclasses


new_session = 1
loaded = 0
in_game = 0



responseList = []
map_offset = 0
grid=[]
level = 100
player_world_pos = np.array([0,0])

area_origin = np.array([0,0])


mini_map_w = 0
mini_map_h = 0

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

hover_obj = 0

#00a4    # of tiles spawned counter
#00a8    frame counter, nope!!! 1501-7499 (1-5 min) delete game, empty
#00ac    +b0*1000/(Tick-b4)
#00b0    counter
#00b4    GetTickCount
#00b8    hEvent
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
