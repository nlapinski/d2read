import sys
import time
import pymem
from ctypes import *
import ctypes
from time import sleep
import json
import re
import os

process = pymem.Pymem("D2R.exe")
handle = process.process_handle
module = pymem.process.module_from_name(handle,"D2R.exe")
base = process.base_address


def print_fields(struct):
    """dump a struct to stdout
    
    Args:
        struct (TYPE): struct to print
    """
    out = ""
    for field_name, field_type in struct._fields_:
        out +=str(field_name)+": "+str(getattr(struct, field_name))+", "
    print(out+'\n')


def read_into(addr,struct):
    """copy struct from a adress, to a ctype struct
    
    Args:
        addr (TYPE): memory adrress
        struct (TYPE): ctype struct 
    
    Returns:
        BOOL: sucess
    """
    try:
        read_buff = process.read_bytes(addr,sizeof(struct))
        memmove(addressof(struct), read_buff[:], sizeof(struct))
        return True 
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()

        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        log = ("WARNING MEMORY ERROR")
        #log_color(log,fg_color=warning_color)
        #traceback.print_tb(exc_tb, limit=8, file=sys.stdout)
        #print(exc_tb)
        #print(inspect.stack()[1].function)
        os._exit(0)
        return False

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



def prep_pat(pat):

    byte_array = b''
    pat = pat.replace("?",".")
    split = pat.split(" ")

    for e in split:
        if '.' in e:
            byte_array += b'.'
        else:
            byte_array += bytes.fromhex(e)

    return byte_array


def get_tick(info):
    """in game D2r main 3D frame ticks, used to synchronize reads, and prevent loading stuff from memory during loading screens
    
    Args:
        game_info_clist (TYPE): Description
    
    Returns:
        TYPE: uint8 tick 0 or 8 on frame update, not sure why, or what I'm really reading here
    """
    t = 0
    while 1:
        #sleep(.1)
        game_info = GameInfo()
        game_info_addr = info
        #print(game_info_addr)
        read_into_result = read_into(game_info_addr ,game_info)
        
        #5 18 19 23 25 27 31
        v = game_info.unk1[17]
        out = c_uint8()
                
        b = process.read_bytes(v+16,16)
        
        if t != b:
            print(b)
            print("tick")
        t = b
        #read_into(v+16 , out)   

        #if out.value > 0:
        #    print(1)
        #else:
        #    print(0)


pat = b"\x44\x88\x25....\x66\x44\x89\x25...."
pat_addr = pymem.pattern.pattern_scan_module(handle, module, pat)

offset = process.read_long(pat_addr+3)

game_info = GameInfo()
delta = pat_addr-base
new = base + (delta-0x121+offset)-8
read_into_result = read_into(new,game_info)

get_tick(new)