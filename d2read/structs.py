from ctypes import *
import ctypes

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


'''

//ptGame : 04E4007C
struct Game
{                                                 //Offset from Code.
     BYTE uk1[0x18];                         //+00
     DWORD     _ptLock;                      //+18 Unknown
     DWORD     memoryPool;                        //+1C Memory Pool (??)
     BYTE uk2[0x4D];                         //+20
     BYTE difficultyLevel;              //+6D (Difficulty 0,1 or 2)
     WORD unknown1;                     //+6E Cube puts 4 here
     DWORD     isLODGame;                         //+70 (D2=0 LOD =1) (DWORD ?)
     BYTE uk3[0x04];                         //+71
     WORD unknown2;                     //+78
     BYTE uk4[0x0E];                         //+7A
     NetClient*     ptClient;                //+88
     BYTE __8C[0x1C];                        //+8C
     DWORD     gameFrame;                         //+A8
     BYTE __AC[0x10];                        //+AC
     ActMap*   mapAct[5];                         //+BC
     BYTE ukD0[0x1024];                 //+D0
     DWORD*    game10F4;                     //+10F4
     BYTE uk6[0x28];                         //+10F8
     Unit*     units[0xA00];                 //+1120
     Unit*     roomtitles[0x200];            //+1B20
};
//WORD ptGame+28 game ID ?


'''

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
     _fields_ = [ ('unk0',((c_uint64 ) * 3)),
                  ('unk1',c_uint32),

                  #0x1c 
                  ('seed',c_uint32),
                  ('room1_ptr',c_uint64),
                  ('unk4',c_uint32),
                  #0x28
                  ('act_id',c_uint32),
                  ('unk2',c_uint32),
                  ('unk3',((c_uint64 ) * 8)),
                  #0x78
                  ('misc_ptr',c_uint64),
                   ]


'''
#old struct
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
'''

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
                  ('action_stamp',c_uint64),
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
                  ('unk0',c_uint64), #act?
                  ('act_ptr',c_uint64),
                  ('seed',c_uint64),
                  ('init_seed',c_uint64),
                  ('path_ptr',c_uint64),
                  ('unk2',(c_uint32 * 8)),
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
                  ('unk5',(c_uint64 * 13)),
                  ('skill_ptr',c_uint64),
                  ('unk6',(c_uint64 * 9)),
                  ('next_ptr',c_uint64),
                  ('room_next_ptr',c_uint64),
                   ]