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

map_players = dict()

class MapPlayer(Structure):
     _fields_ = [ ('act',c_uint32),
                  ('seed',c_uint32),
                  ('level_id',c_uint32),
                  ('pos_x',c_uint32),
                  ('pos_y',c_uint32),
                  ('name',((c_uint16 ) * 16)),
                  ('class_id',c_uint32),
                  ('level',c_uint16),
                  ('party',c_uint16),
                  ('difficulty',c_uint8),
                  ('level_changed',c_bool),
                  ('stats',((c_uint32 ) * 16)),
                  ('skill_ptr',c_uint64),
                   ]

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
                  ('unk0',((c_uint32 ) * 2)),
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
                  ('unk0',((c_char ) * 24)),
                  ('game_name',VectorData),
                  ('game_name_buffer',((c_char ) * 24)),
                  ('game_pass',VectorData),
                  ('game_pass_buffer',((c_char ) * 24)),
                  ('region',VectorData),
                  ('region_buffer',((c_char ) * 24)),
                  ('unk1',((c_uint64 ) * 31)),
                  ('game_ip',VectorData),
                  ('game_ip_buffer',((c_char ) * 24)),
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
                  ('unk4',((c_uint64 ) * 6)),
                  ('unk5',c_uint16),
                  ('name2',((c_char ) * 16)),
                  ('unk6',c_uint32),
                  ('wide_name',((c_wchar * 1) * 16)),
                  ('unk7',((c_uint16 ) * 3)),
                  ('unk8',((c_uint64 ) * 8)),
                  ('order',c_uint32),
                  ('unk9',((c_uint32 ) * 3)),
                  ('next_ptr',c_uint64),
                  ]

class DrlgAct(Structure):
     _fields_ = [ ('unk0',((c_uint64 ) * 2)),
                  ('unk1',c_uint32),
                  ('seed',c_uint32),
                  ('room1_ptr',c_uint64),
                  ('act_id',c_uint32),
                  ('unk2',c_uint32),
                  ('unk3',((c_uint64 ) * 9)),
                  ('misc_ptr',c_uint64),
                   ]


class DrlgRoom1(Structure):
     _fields_ = [ ('rooms_near_list_ptr',c_uint32),
                  ('unk0',((c_uint64 ) * 2)),
                  ('room2_ptr',c_uint64),
                  ('unk1',((c_uint64 ) * 4)),
                  ('rooms_near',c_uint32),
                  ('unk2',c_uint32),
                  ('act_addr',c_uint64),
                  ('unk3',((c_uint64 ) * 11)),
                  ('unit_first_addr',c_uint64),
                  ('next_ptr',c_uint64),
                   ]

class DrlgRoom2(Structure):
     _fields_ = [ ('unk0',((c_uint64 ) * 2)),
                  ('rooms_near_list_ptr',c_uint64),
                  ('unk1',((c_uint64 ) * 5)),
                  ('level_preset_ptr',c_uint64),
                  ('next_ptr',c_uint64),
                  ('rooms_near',c_uint16),
                  ('unk2',c_uint16),
                  ('room_tiles',c_uint32),
                  ('room1_ptr',c_uint64),
                  ('pos_x',c_uint32),
                  ('pos_y',c_uint32),
                  ('size_x',c_uint32),
                  ('size_y',c_uint32),
                  ('unk3',c_uint32),
                  ('preset_type',c_uint32),
                  ('room_tiles_ptr',c_uint64),
                  ('unk4',((c_uint64 ) * 2)),
                  ('level_ptr',c_uint64),
                  ('preset_units_ptr',c_uint64),
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
                  ('unk0',((c_uint32 ) * 2)),
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
                  ('components',((c_uint8 ) * 16)),
                  ('name_seed',c_uint16),
                  ('flag',c_uint8),
                  ('last_mode',c_uint8),
                  ('duriel',c_uint32),
                  ('enchants',((c_uint8 ) * 9)),
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
                  ('unk0',((c_uint64 ) * 2)),
                  ('action_stamp',c_uint32),
                  ('file_index',c_uint32),
                  ('item_level',c_uint32),
                  ('format',c_uint16),
                  ('rare_prefix',c_uint16),
                  ('rare_suffix',c_uint16),
                  ('auto_prefix',c_uint16),
                  ('magic_prefix',((c_uint16 ) * 3)),
                  ('magic_suffix',((c_uint16 ) * 3)),
                  ('body_location',c_uint8),
                  ('item_location',c_uint8),
                  ('unk1',c_uint16),
                  ('unk2',c_uint32),
                  ('ear_level',c_uint16),
                  ('inv_gfx_idx',c_uint8),
                  ('player_name',((c_uint16 ) * 16)),
                  ('unk3',((c_uint8 ) * 5)),
                  ('owner_inv_ptr',c_uint64),
                  ('prev_item_ptr',c_uint64),
                  ('next_item_ptr',c_uint64),
                  ('unk4',c_uint8),
                  ('location',c_uint8),
                  ('unk5',((c_uint8 ) * 6)),
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
                  ('unk2',((c_uint32 ) * 8)),
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
                  ('unk5',((c_uint64 ) * 13)),
                  ('skill_ptr',c_uint64),
                  ('unk6',((c_uint64 ) * 9)),
                  ('next_ptr',c_uint64),
                  ('room_next_ptr',c_uint64),
                   ]


def update_unit_offset():
    '''Summary - gets some unit table offsets from memory, return the adress of the table

    '''
    global process
    global handle
    global module
    global base

    pat = b"\x48\x8d.....\x8b\xd1"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_long(pat_addr+3)
    unit_hashtable = ((pat_addr - base) + 7 + offset_buffer)
    return (unit_hashtable+base)

def update_roster_offset():
    '''Summary - gets some player roste offsets from memory, returns the address in memory

    '''
    global process
    global handle
    global module
    global base

    pat = b"\x02\x45\x33\xd2\x4d\x8b"
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_long(pat_addr-3)
    roster_addr = ((pat_addr - base) + 1 + offset_buffer)
    return (roster_addr+base)

def update_game_info_offset():
    '''Summary - gets some game info offsets in memory
    Returns:
        TYPE: Description
    '''
    global process
    global handle
    global module
    global base

    #pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'
    #pat = b'\xE8....\x48\x8D\x0D....\x44\x88\x2D....'
    #pat = b'\xE8....\x48\x8B\x15....\x48\xB9........\x44\x88\x25....'
    pat = b'\x48\x8D\x0D....\xE8....\x48\x8B\x15....\x48\xB9........'
    #E8 ? ? ? ? 48 8B 15 ? ? ? ? 48 B9 ? ? ? ? ? ? ? ? 44 88 25 ? ? ? ? 
    pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)
    offset_buffer = process.read_int(pat_addr+8)
    game_info_offset = ((pat_addr - base)  - 244 + offset_buffer)
    
    return (game_info_offset+base)


def read_hash_table():    
    addr_list = [0x80]
    units = []

    addr = update_unit_offset()

    read_rosters()

    while 1:
        unit_type = 1#npcs/monsters
        monster_addr = addr +(128*8*unit_type)

        for i in range(128):
            paddr = process.read_longlong(monster_addr+(i*8))
            while paddr:
                unit = UnitAny()
                read = process.read_bytes(paddr,sizeof(unit))
                memmove(addressof(unit), read[:], sizeof(unit))
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

def read_player_unit(unit:UnitAny):
    #if (unit.unitId == focusedPlayer) { return; }
    act = DrlgAct()
    read_into_result = read_into(unit.act_ptr,act)
    if not read_into_result:
        return False

    map_players[unit.unit_id] = MapPlayer()
    player = map_players[unit.unit_id]
    read_into(unit.union_ptr,player.name)
    

    player.level_changed = False
    player.act = act.act_id
    player.seed = act.seed
    player.difficulty=10
    
    
    
    difficulty = c_uint8()
    read_into((act.misc_ptr+0x830),difficulty)
    player.difficulty = difficulty

    # this needs to be reimplemented
    #for stat_id in range(16):
    #    player.stats[stat_id] = c_uint32(1)
    
    path = DynamicPath()
    
    read_into_result = read_into(unit.path_ptr,path)
    if not read_into_result:
        return False
    
    player.pos_x = path.pos_x;
    player.pos_y = path.pos_y;
    xf = path.offset_x / 65535.0
    yf = path.offset_y / 65535.0
    #print(path.map_pos_x,path.map_pos_y)

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
    player.level_id = level_id

def read_monster_unit(unit:UnitAny):
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
    y = path.pos_x
    if name in get_is_npc:
        is_npc=1

    is_unique = (monster.flag & 0x0E) != 0

    if is_unique:
        try:
            name = get_super_unique_name[unit.txt_file_no]
            print(name)
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

def read_game_info():

    game_info_addr = update_game_info_offset()
    game_info = GameInfo()

    read_into_result = read_into(game_info_addr ,game_info)
    if not read_into_result:
        print("FAILED")
        return False
    game_name = game_info.game_name_buffer
    game_pass = game_info.game_pass_buffer
    region = game_info.region_buffer
    game_ip = game_info.game_ip_buffer
    print(game_name,game_pass,region,game_ip)

def read_tick():

    game_info_addr = update_game_info_offset()
    game_info = GameInfo()
    tick = 0
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
        
        s += str(out)+" "
        print(s)


if __name__ == '__main__':
    read_game_info()
    read_hash_table()
