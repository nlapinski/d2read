from multiprocessing.sharedctypes import RawArray, RawValue
from multiprocessing import Process
import collections
import time
import pymem
from ctypes import *
import ctypes

from . import game_state
from .event import events

from .enums import *
from .utils import *


process = pymem.Pymem("D2R.exe")
handle = process.process_handle
module = pymem.process.module_from_name(handle,"D2R.exe")
base = process.base_address

class FPS:
    def __init__(self,avarageof=50):
        self.frametimestamps = collections.deque(maxlen=avarageof)
    def __call__(self):
        self.frametimestamps.append(time.time())
        if(len(self.frametimestamps) > 1):
            return len(self.frametimestamps)/((self.frametimestamps[-1]-self.frametimestamps[0])+.0001)
        else:
            return 0.0

class StatEx(Structure):
     _fields_ = [ ('param',c_uint16),
                  ('stat_id',c_uint16),
                  ('value',c_uint32),
                   ]

class Stats(Structure):
     _fields_ = [ ('stat_ptr',c_uint64),
                  ('stat_count',c_uint64),
                  ('stat_capacity',c_uint64),
                   ]

class StatList(Structure):
     _fields_ = [ ('unit_ptr',c_uint64),
                  ('owner_type',c_uint32),
                  ('owner_id',c_uint32),
                  ('unk0',c_uint32),
                  ('flag',c_uint32),
                  ('state_no',c_uint32),
                  ('expire_frame',c_uint32),
                  ('skill_no',c_uint32),
                  ('skill_level',c_uint32),
                  ('base_stat',c_uint32),
                  ('unk1',c_uint64),
                  ('prev_list',c_uint64),
                  ('next_list',c_uint64),
                  ('prev',c_uint64),
                  ('next_list_ex',c_uint64),
                  ('next',c_uint64),
                  ('unk2',c_uint64),
                  ('full_stat',Stats),
                  ('mod_stat',Stats),
                   ]

class Skill(Structure):
     _fields_ = [ ('skill_txt_ptr',c_uint64),
                  ('next_skill_ptr',c_uint64),
                  ('mode',c_uint32),
                  ('flag0',c_uint32),
                  ('unk0',((c_uint32 * 1) * 2)),
                  ('targets',c_uint32),
                  ('target_type',c_uint32),
                  ('target_id',c_uint32),
                  ('unk1',c_uint64),
                  ('skill_level',c_uint32),
                  ('level_bonus',c_uint32),
                  ('quantity',c_uint32),
                  ('flags',c_uint32),
                   ]

class SkillInfo(Structure):
     _fields_ = [ ('first_skill_ptr',c_uint64),
                  ('left_skill_ptr',c_uint64),
                  ('right_skill_ptr',c_uint64),
                  ('current_skill_ptr',c_uint64),
                   ]

class UnitInventory(Structure):
     _fields_ = [ ('magic',c_uint32),
                  ('unk0',c_uint32),
                  ('owner_ptr',c_uint64),
                  ('first_item_ptr',c_uint64),
                  ('last_item_ptr',c_uint64),
                  ('inv_info_ptr',c_uint64),
                  ('inv_info_size',c_uint64),
                  ('inv_info_capacity',c_uint64),
                  ('weapon_id',c_uint32),
                  ('unk1',c_uint32),
                  ('cursor_item_ptr',c_uint64),
                  ('owner_id',c_uint32),
                  ('filled_sockets',c_uint32),
                   ]

class PvPInfo(Structure):
     _fields_ = [ ('unit_id',c_uint32),
                  ('flags',c_uint32),
                  ('next_ptr',c_uint64),
                   ]

class VectorData(Structure):
     _fields_ = [ ('ptr',c_uint64),
                  ('size',c_uint32),
                  ('unk0',c_uint32),
                  ('capacity',c_uint32),
                  ('unk1',c_uint32),
                  ]

class GameInfo(Structure):
     _fields_ = [ ('session',VectorData),
                  ('unk0',((c_char * 1) * 24)),
                  ('game_name',VectorData),
                  ('game_name_buffer',((c_char * 1) * 24)),
                  ('game_pass',VectorData),
                  ('game_pass_buffer',((c_char * 1) * 24)),
                  ('region',VectorData),
                  ('region_buffer',((c_char * 1) * 24)),
                  ('unk1',((c_uint64 * 1) * 31)),
                  ('game_ip',VectorData),
                  ('game_ip_buffer',((c_char * 1) * 24)),
                  ]

class RosterUnit(Structure):
     _fields_ = [ ('name',((c_char * 1) * 16)),
                  ('unk0',c_uint64),
                  ('unit_id',c_uint32),
                  ('life_percent',c_uint32),
                  ('kills',c_uint32),
                  ('class_id',c_uint32),
                  ('level',c_uint16),
                  ('party_id',c_uint16),
                  ('act_id',c_uint32),
                  ('pos_x',c_uint32),
                  ('pos_y',c_uint32),
                  ('flags',c_uint32),
                  ('unk3',c_uint32),
                  ('pvp_info_ptr',c_uint64),
                  ('unk4',((c_uint64 * 1) * 6)),
                  ('unk5',c_uint16),
                  ('name2',((c_char * 1) * 16)),
                  ('unk6',c_uint32),
                  ('wide_name',((c_wchar * 1) * 16)),
                  ('unk7',((c_uint16 * 1) * 3)),
                  ('unk8',((c_uint64 * 1) * 8)),
                  ('order',c_uint32),
                  ('unk9',((c_uint32 * 1) * 3)),
                  ('next_ptr',c_uint64),
                  ]

class DrlgAct(Structure):
     _fields_ = [ ('unk0',((c_uint64 * 1) * 2)),
                  ('unk1',c_uint32),
                  ('seed',c_uint32),
                  ('room1_ptr',c_uint64),
                  ('act_id',c_uint32),
                  ('unk2',c_uint32),
                  ('unk3',((c_uint64 * 1) * 9)),
                  ('misc_ptr',c_uint64),
                   ]


class DrlgRoom1(Structure):
     _fields_ = [ ('rooms_near_list_ptr',c_uint32),
                  ('unk0',((c_uint64 * 1) * 2)),
                  ('room_2_ptr',c_uint64),
                  ('unk1',((c_uint64 * 1) * 4)),
                  ('rooms_near',c_uint32),
                  ('unk2',c_uint32),
                  ('act_addr',c_uint64),
                  ('unk3',((c_uint64 * 1) * 11)),
                  ('unit_first_addr',c_uint64),
                  ('next_ptr',c_uint64),
                   ]

class DynamicPath(Structure):
     _fields_ = [ ('offset_x',c_uint16),
                  ('pos_x',c_uint16),
                  ('offset_y',c_uint16),
                  ('pos_y',c_uint16),
                  ('map_pos_x',c_uint32),
                  ('map_pos_y',c_uint32),
                  ('target_x',c_uint32),
                  ('target_y',c_uint32),
                  ('unk0',((c_uint32 * 1) * 2)),
                  ('room1_ptr',c_uint64),
                   ]

class StaticPath(Structure):
     _fields_ = [ ('room1_ptr',c_uint64),
                  ('map_pos_x',c_uint32),
                  ('map_pos_y',c_uint32),
                  ('pos_x',c_uint32),
                  ('pos_y',c_uint32),
                   ]


class MonsterData(Structure):
     _fields_ = [ ('monster_txt_ptr',c_uint64),
                  ('components',((c_uint8 * 1) * 16)),
                  ('name_seed',c_uint16),
                  ('flag',c_uint8),
                  ('last_mode',c_uint8),
                  ('duriel',c_uint32),
                  ('enchants',((c_uint8 * 1) * 9)),
                  ('unk0',c_uint8),
                  ('unique_no',c_uint16),
                  ('unk1',c_uint32),
                  ('unk2',c_uint16),
                  ('merc_name_id',c_uint16),
                  ('unk3',c_uint32),
                   ]


class ItemData(Structure):
     _fields_ = [ ('quality',c_uint32),
                  ('seed_low',c_uint32),
                  ('seed_high',c_uint32),
                  ('owner_id',c_uint32),
                  ('fingerprint',c_uint32),
                  ('command_flags',c_uint32),
                  ('item_flags',c_uint32),
                  ('unk0',((c_uint64 * 1) * 2)),
                  ('action_stamp',c_uint32),
                  ('file_index',c_uint32),
                  ('item_level',c_uint32),
                  ('format',c_uint16),
                  ('rare_prefix',c_uint16),
                  ('rare_suffix',c_uint16),
                  ('auto_prefix',c_uint16),
                  ('magic_prefix',((c_uint16 * 1) * 3)),
                  ('magic_suffix',((c_uint16 * 1) * 3)),
                  ('body_location',c_uint8),
                  ('item_location',c_uint8),
                  ('unk1',c_uint16),
                  ('unk2',c_uint32),
                  ('ear_level',c_uint16),
                  ('inv_gfx_idx',c_uint8),
                  ('player_name',((c_uint16 * 1) * 16)),
                  ('unk3',((c_uint8 * 1) * 5)),
                  ('owner_inv_ptr',c_uint64),
                  ('prev_item_ptr',c_uint64),
                  ('next_item_ptr',c_uint64),
                  ('unk4',c_uint8),
                  ('location',c_uint8),
                  ('unk5',((c_uint8 * 1) * 6)),
                   ]


class UnitAny(Structure):
     _fields_ = [ ('unit_type',c_uint32),
                  ('txt_file_no',c_uint32),
                  ('unit_id',c_uint32),
                  ('mode',c_uint32),
                  ('union_ptr',c_uint64),
                  ('unk0',c_uint64),
                  ('act_ptr',c_uint64),
                  ('seed',c_uint64),
                  ('init_seed',c_uint64),
                  ('path_ptr',c_uint64),
                  ('unk2',((c_uint32 * 1) * 8)),
                  ('gfx_frame',c_uint32),
                  ('frame_remain',c_uint32),
                  ('frame_rate',c_uint32),
                  ('unk3',c_uint32),
                  ('p_gfx_unk',c_uint8),
                  ('p_gfx_info',c_uint32),
                  ('p_gfx_unk_ptr',c_uint64),
                  ('p_gfx_info_ptr',c_uint64),
                  ('unk4',c_uint64),
                  ('stat_list_ptr',c_uint64),
                  ('inventory_ptr',c_uint64),
                  ('unk5',((c_uint64 * 1) * 13)),
                  ('skill_ptr',c_uint64),
                  ('unk6',((c_uint64 * 1) * 9)),
                  ('next_ptr',c_uint64),
                  ('room_next_ptr',c_uint64),
                   ]


def update_unit_offset():
    '''Summary - gets some unit table offsets from memory
    credit to :https://github.com/joffreybesos/d2r-mapview/

    '''
    #unit table offset scan pattern
    global process
    global handle
    global module
    global base

    pat = b"\x48\x8d.....\x8b\xd1"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_long(pat_addr+3)
    unit_hashtable = ((pat_addr - base) + 7 + offset_buffer)
    
    return (unit_hashtable+base)


'''
        const uint8_t search3[] = {0x02, 0x45, 0x33, 0xD2, 0x4D, 0x8B};
        const uint8_t mask3[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
        off = searchMem(mem, size_t(baseSize), search3, mask3, sizeof(search3));
        if (off != size_t(-1)) {
            int32_t rel;
            if (READ(baseAddr + off - 3, rel)) {
                rosterDataAddr = baseAddr + off + 1 + rel;
            }
        }

'''
def update_roster_offset():
    '''Summary - gets some unit table offsets from memory
    credit to :https://github.com/joffreybesos/d2r-mapview/

    '''
    #unit table offset scan pattern
    global process
    global handle
    global module
    global base

    pat = b"\x02\x45\x33\xd2\x4d\x8b"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_long(pat_addr-3)
    roster_addr = ((pat_addr - base) + 1 + offset_buffer)
    
    return (roster_addr+base)

def read_hash_table():    
    addr_list = [0x80]
    units = []

    addr = update_unit_offset()
    fps = FPS()

    read_rosters()

    while 1:
        #print(fps())
        unit_type = 1#npcs/monsters
        monster_addr = addr +(128*8*unit_type)

        for i in range(128):
            paddr = process.read_longlong(monster_addr+(i*8))
            while paddr:
                unit = UnitAny()
                read = process.read_bytes(paddr,sizeof(unit))
                memmove(addressof(unit), read[:], sizeof(unit))
                #units.append(unit)
                read_unit(unit)
                paddr = unit.next_ptr

        unit_type = 2#objects
        object_addr = addr +(128*8*unit_type)

        for i in range(256):
            paddr = process.read_longlong(object_addr+(i*8))
            while paddr:
                unit = UnitAny()
                read = process.read_bytes(paddr,sizeof(unit))
                memmove(addressof(unit), read[:], sizeof(unit))
                #units.append(unit)
                read_unit(unit)
                paddr = unit.next_ptr

        unit_type = 4#items
        item_addr = addr +(128*8*unit_type)

        for i in range(128):
            paddr = process.read_longlong(item_addr+(i*8))
            while paddr:
                unit = UnitAny()
                read = process.read_bytes(paddr,sizeof(unit))
                memmove(addressof(unit), read[:], sizeof(unit))
                #units.append(unit)
                read_unit(unit)
                paddr = unit.next_ptr


def read_into(addr,struct):
    global process
    try:
        read_buff = process.read_bytes(addr,sizeof(struct))
        memmove(addressof(struct), read_buff[:], sizeof(struct))
        return True 
    except:
        return False

def print_fields(struct):
    out = ""
    for field_name, field_type in struct._fields_:
        out +=str(field_name)+": "+str(getattr(struct, field_name))+", "
    print(out+'\n')

def read_unit(unit:UnitAny):
    if unit.unit_type == 0:
        read_player_unit(unit)
    if unit.unit_type == 1:
        read_monster_unit(unit)
    if unit.unit_type == 2:
        read_object_unit(unit)
    if unit.unit_type == 4:
        read_item_unit(unit)

def read_player_unit(unit:UnitAny):
    pass

def read_monster_unit(unit:UnitAny):
    pass

def read_object_unit(unit:UnitAny):
    pass

'''

struct MapPlayer {
    uint32_t act;
    uint32_t seed;
    uint32_t levelId;
    int posX, posY;
    char name[16];
    uint32_t classId;
    uint16_t level;
    uint16_t party;
    uint8_t difficulty;
    bool levelChanged;
    std::array<int32_t, 16> stats;
    uint64_t skillPtr;
};
struct MapMonster {
    int x, y;
    const std::array<std::wstring, 13> *name;
    wchar_t enchants[32];
    uint8_t flag;
    bool isNpc;
    bool isUnique;
};
struct MapObject {
    int x, y;
    const std::array<std::wstring, 13> *name;
    uint8_t type;
    uint8_t flag;
    float w, h;
};
struct MapItem {
    int x, y;
    const std::array<std::wstring, 13> *name;
    uint8_t flag;
    uint8_t color;
};

}
'''

map_players = []

def read_rosters():
    global process
    roster_offset = update_roster_offset()
    roster_data_ptr = process.read_longlong(roster_offset)

    while roster_data_ptr:
        mem = RosterUnit()

        read_into(roster_data_ptr,mem)
        #auto &p = mapPlayers[mem.unitId];
        #memcpy(p.name, mem.name, 16);
        #player = map_players[mem.unit_id]
        name = string_at(byref(mem.name), 16)
        #name = string_at(byref(mem.wide_name), 16)

        class_id = mem.class_id
        level = mem.level
        party = mem.party_id;
        print(name,class_id,level)

        focused_player = mem.unit_id
        #current_player = player
        print(focused_player)

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

'''
void ProcessData::readUnitPlayer(const UnitAny &unit) {
    if (unit.unitId == focusedPlayer) { return; }
    DrlgAct act;
    if (!READ(unit.actPtr, act)) { return; }
    auto &player = mapPlayers[unit.unitId];
    player.name[0] = 0;
    READ(unit.unionPtr, player.name);
    player.levelChanged = false;
    player.act = act.actId;
    player.seed = act.seed;
    READ(act.miscPtr + 0x830, player.difficulty);
    player.stats.fill(0);
    readPlayerStats(unit, [&player](uint16_t statId, int32_t value) {
        if (statId > 15) {
            return;
        }
        player.stats[statId] = value;
    });
    DynamicPath path;
    if (!READ(unit.pathPtr, path)) { return; }
    player.posX = path.posX;
    player.posY = path.posY;
    DrlgRoom1 room1;
    if (!READ(path.room1Ptr, room1)) { return; }
    DrlgRoom2 room2;
    if (!READ(room1.room2Ptr, room2)) { return; }
    if (!READ(room2.levelPtr + 0x1F8, player.levelId)) { return; }
}
'''


def read_item_unit(unit:UnitAny):
    global process
    #copy item memory into struct
    item = ItemData()
    read_into_result = read_into(unit.union_ptr,item)

    if not read_into_result:
        return False

    txt_name = item_name[int(unit.txt_file_no)]
    item_location = item.item_location
    item_body_location = item.body_location
    world_location = unit.mode
    #mode stores the current world location, falling/ground/inv/dropping

    if world_location == 3 or world_location == 5:
        #print('onground->',unit.mode,txt_name)
        #print_fields(unit)
        #items
        #area_x =  float(pos[0]) #game_state.map_list[8]
        #area_y = float(pos[1]) #game_state.map_list[9]
        #dist = float(dist)
        _item = game_state.Item()
        _item.name = txt_name.encode('utf_8')
        print_fields(_item)
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

if __name__ == '__main__':
    
    read_hash_table()
