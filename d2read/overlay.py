import win32gui
import win32api
import win32con
import win32ui
from win32gui import FindWindow, GetWindowRect, ClientToScreen
import os
import numpy as np
import dearpygui.dearpygui as dpg
from multiprocessing import shared_memory
import traceback

import multiprocessing
from time import sleep
import time

from . import game_state

from collections import namedtuple
from multiprocessing import Process

from ctypes import *
import ctypes

from shapely.ops import unary_union
from shapely import geometry as gs

import math
import ctypes
import keyboard  # using module keyboard

dwm = ctypes.windll.dwmapi

from .utils import *

class MARGINS(ctypes.Structure):
  _fields_ = [("cxLeftWidth", c_int),
              ("cxRightWidth", c_int),
              ("cyTopHeight", c_int),
              ("cyBottomHeight", c_int)
             ]

def delta_helper(delta, diag, scale, delta_z=0.0):
    """Summary - screen space conversion helper
    Args:
        delta (TYPE): Description
        diag (TYPE): Description
        scale (TYPE): Description
        deltaZ (float, optional): Description
    Returns:
        TYPE: Description
    """
    camera_angle = -26.0 * 3.14159274 / 180.0
    cos = (diag * math.cos(camera_angle) / scale)
    sin = (diag * math.sin(camera_angle) / scale)
    d = ((delta[0] - delta[1]) * cos, delta_z - (delta[0] + delta[1]) * sin)
    return d

def world_to_abs(dest, player):
    """Summary - convert d2 space to absolute screen space centerd in the 1280x720 screen window
    Args:
        dest (TYPE): target point
        player (TYPE): player pos ref
    Returns:
        TYPE: screen coords in ABS space
    """
    w = 1280
    h = 720
    delta = delta_helper(dest-player, math.sqrt(w*w+h*h), 68.5,30)
    x = np.clip(delta[0]-9.5, -638, 638)
    y = np.clip(delta[1]-39.5, -350, 235)
    screen_coords = np.array([x,y])
    return screen_coords


def xform(sender,data):

    global _player
    global current_level


def main_update(sender,data):
    """update gui data on frame callback
    
    Args:
        sender (TYPE): Description
        data (TYPE): Description
    """
    
    i=0
    global _player
    global current_level
    global game_info_list
    
    if game_info_list.in_game == 0:
        current_level = None
        dpg.hide_item('map_node')
        dpg.hide_item('player_marker')
    else:
        if current_level != game_info_list.id or current_level is None: 
            dpg.hide_item('map_node')
            if area_list.loaded == 1:
                area_list.loaded=0
                #print("UPDATEED", current_level,game_info_list.id)
                current_level = game_info_list.id
                #print("NEW_LVL>", current_level,game_info_list.id)
                poly = []
                dpg.delete_item("map_node", children_only=True)
                w = int(area_list.mini_map_size.x)
                h = int(area_list.mini_map_size.y)
                draw_color = [255, 0, 0]
                log = 'constructing -> '
                log_color(log,target=str(np.array([w,h])),fg_color=important_color,fg2_color=offset_color)
                values = [None]*(w*h)
                idx=0
                
                first = 0
                second = 1
                p1 = [0,0]
                p2 = [0,0]
                p3 = [0,0]
                p4 = [0,0]

                for i in range(w):
                    for j in range(h):
                        #first = 0

                        if area_list.map[j][i] == -1:
                            if first ==0:

                                first = 1
                                second = 0
                                p1 = np.array([j,i-.5])
                                p2 = np.array([j,i+.5])

                        if second == 0 and area_list.map[j][i]== 0:
                            first =0 
                            second = 1
                            p3 = np.array([j,i-.5])
                            p4 = np.array([j,i+.5])
                            poly.append(gs.Polygon([p3,p4,p2,p1]))
                            #dpg.draw_polygon([p3,p4,p2,p1], parent='map_node', thickness=.15, color =[150,150,150,66])
                    first = 0 

                weld = unary_union(poly)
                pgons = []
                try:
                    for p in list(weld.geoms):
                        simple = p.simplify(0.1, preserve_topology=False)
                        pgons_outside = list(simple.exterior.coords)
                        dpg.draw_polygon(pgons_outside, parent='map_node',thickness=.5, fill = [ 0,0,0,0], color =[190,190,190,255])


                        pgons_inside = list(p.interiors)
                        for inside in pgons_inside:
                            simple = inside.simplify(0.1, preserve_topology=False)
                            l = list(simple.coords)        
                            dpg.draw_polygon(l, parent='map_node', thickness=.5, color =[190,190,190,255])

                except Exception as e:
                    #print(e)
                    #pass
                    p = weld
                    simple = p.simplify(0.1, preserve_topology=False)
                    pgons_outside = list(simple.exterior.coords)
                    dpg.draw_polygon(pgons_outside,  parent='map_node',thickness=.5, fill = [ 0,0,0,0], color =[190,190,190,255])
                    pgons_inside = list(p.interiors)
                    for inside in pgons_inside:
                        simple = inside.simplify(0.1, preserve_topology=False)
                        l = list(simple.coords)
                        dpg.draw_polygon(l,thickness=.5, fill = [ 0,0,0,0],  color =[190,190,190,255],  parent='map_node')



                
                map_tag = 'map__info_1'
                dpg.set_value(map_tag,str(area_list.current_area))
                map_tag = 'map__info_2'
                dpg.set_value(map_tag, str(area_list.level))
                map_tag = 'map__info_3'
                dpg.set_value(map_tag, str(area_list.seed))
                map_tag = 'map__info_4'
                dpg.set_value(map_tag, str(area_list.difficulty))
                map_tag = 'map__info_5'
                dpg.set_value(map_tag, str(area_list.loaded))
                
                map_tag = 'map__info_6'
                dpg.set_value(map_tag, str(game_info_list.ip))                
                map_tag = 'map__info_7'
                dpg.set_value(map_tag, str(game_info_list.game_name))                
                map_tag = 'map__info_8'
                dpg.set_value(map_tag, str(game_info_list.game_pass))                

                map_tag = 'map__info_9'
                dpg.set_value(map_tag, str(area_list.origin.x))
                map_tag = 'map__info_10'
                dpg.set_value(map_tag, str(area_list.origin.y))



                for i in range(area_list.cluster_count):
                    dpg.draw_circle((area_list.clusters[i].y,area_list.clusters[i].x),4,color=(0,0,255,45),fill=[0,0,255,22],parent='map_node')
                dpg.show_item('map_node')
                dpg.show_item('player_marker')


                j = 0 
                #iterate poi list
                for poi in area_list.poi:
                    tag1 = 'poi_info_1_'+str(j+1)
                    tag2 = 'poi_info_2_'+str(j+1)
                    tag3 = 'poi_info_3_'+str(j+1)


                    dpg.set_value(tag1,poi.name.decode('utf-8'))
                    pos = np.array([poi.area_pos.x,poi.area_pos.y])
                    dpg.set_value(tag2, str(pos))
                    dpg.set_value(tag3, str(poi.is_portal))
                    if "Waypoint" in poi.name.decode('utf-8') and poi.name.decode('utf-8') != "":
                        dpg.draw_circle((poi.area_pos.y,poi.area_pos.x),8,color=(68,144,160,255),fill=[68,144,160,75],parent='map_node')
                        dpg.draw_text((poi.area_pos.y,poi.area_pos.x), "WP", color=(250, 250, 250, 255), size=15,parent='map_node')
                    if poi.is_exit and poi.name.decode('utf-8') != "":
                        dpg.draw_circle((poi.area_pos.y,poi.area_pos.x),12,color=(255,120,80,255),fill=[255,120,80,75],parent='map_node')                    
                        dpg.draw_text((poi.area_pos.y,poi.area_pos.x), str(poi.name.decode('utf-8')), color=(250, 250, 250, 255), size=15,parent='map_node')
                    dpg.show_item(tag1)
                    dpg.show_item(tag2)
                    dpg.show_item(tag3)
                    if poi.name == b'':
                        dpg.hide_item(tag1)
                        dpg.hide_item(tag2)
                        dpg.hide_item(tag3)
                    j+=1
                i=0
                    



    tag = 'player_info_1'
    dpg.set_value(tag,_player.name)
    tag = 'player_info_2'
    dpg.set_value(tag,_player.lvl)
    tag = 'player_info_3'
    dpg.set_value(tag,_player.exp)
    tag = 'player_info_4'
    dpg.set_value(tag,_player.pos.x)
    tag = 'player_info_5'
    dpg.set_value(tag,_player.pos.y)
    tag = 'player_info_6'
    dpg.set_value(tag,_player.area_pos.x)
    tag = 'player_info_7'
    dpg.set_value(tag,_player.area_pos.y)
    tag = 'player_info_8'
    dpg.set_value(tag,_player.pos_float_offset.x)
    tag = 'player_info_9'
    dpg.set_value(tag,_player.pos_float_offset.y)
    tag = 'player_info_10'
    dpg.set_value(tag,_player.hp)
    tag = 'player_info_11'
    dpg.set_value(tag,_player.mp)
    tag = 'player_info_12'
    dpg.set_value(tag,_player.base_hp)
    tag = 'player_info_13'
    dpg.set_value(tag,_player.base_mp)
    tag = 'player_info_14'
    dpg.set_value(tag,_player.summons.skel)
    tag = 'player_info_15'
    dpg.set_value(tag,_player.summons.mage)
    tag = 'player_info_16'
    dpg.set_value(tag,_player.summons.gol)
    tag = 'player_info_17'
    dpg.set_value(tag,_player.summons.rev)


    dpg.set_value('FPS_MAIN',int(run.fps1))
    dpg.set_value('FPS_MONSTERS',int(run.fps2))
    dpg.set_value('FPS_ITEMS',int(run.fps3))
    dpg.set_value('FPS_OBJ',int(run.fps4))
    #start_time = time.time()
    for m in monster_list:
        tag1 = 'monster_info_1_'+str(i+1)    
        tag2 = 'monster_info_2_'+str(i+1)
        tag3 = 'monster_info_3_'+str(i+1)
        tag_m = 'monster_info_4_'+str(i+1)
        tag_mm = 'monster_info_5_'+str(i+1)
        tag_mmm = 'monster_info_6_'+str(i+1)



        exists = dpg.does_item_exist(tag_m)
        exists2 = dpg.does_item_exist(tag_mm)
        exists3 = dpg.does_item_exist(tag_mmm)

        if m.name == b'':
            dpg.hide_item(tag1)
            dpg.hide_item(tag2)
            dpg.hide_item(tag3)
            if exists2:
                dpg.delete_item(tag_mm)
            if exists3:
                dpg.delete_item(tag_mmm)
        else:
            
            if m.is_npc:
                dpg.set_value(tag1,'[' + m.name.decode('utf-8') + ']')
            else:
                dpg.set_value(tag1,m.name.decode('utf-8'))
            pos = np.array([m.area_pos.x,m.area_pos.y])
            dpg.set_value(tag2, str(pos))    
            dpg.set_value(tag3, str(m.dist))

            if m.mode == 12 and exists2:
                dpg.delete_item(tag_mm)
            if m.mode != 12 and exists3:
                dpg.delete_item(tag_mmm)

            if exists:
                if exists2 or exists3:
                    dpg.apply_transform(tag_m, dpg.create_translation_matrix([m.area_pos.y,m.area_pos.x]))
                else:
                    if m.mode == 12:
                        dpg.draw_circle((0,0),4,color=(99,99,99,99),fill=[99,99,99,99],parent=tag_m,tag=tag_mmm)
                    else:
                        dpg.draw_circle((0,0),4,color=(255,0,0,255),fill=[255,0,255,99],parent=tag_m,tag=tag_mm)
                        
                    dpg.apply_transform(tag_m, dpg.create_translation_matrix([m.area_pos.y,m.area_pos.x]))
            else:
                with dpg.draw_node(tag=tag_m,parent='map_node'):
                    if m.mode == 12:
                        dpg.draw_circle((0,0),4,color=(99,99,99,99),fill=[99,99,99,99],parent=tag_m,tag=tag_mmm)
                    else:
                        dpg.draw_circle((0,0),4,color=(255,0,0,255),fill=[255,0,255,99],parent=tag_m,tag=tag_mm)

                dpg.apply_transform(tag_m, dpg.create_translation_matrix([m.area_pos.y,m.area_pos.x]))

            dpg.show_item(tag1)
            dpg.show_item(tag2)
            dpg.show_item(tag3)


        item = item_list[i]
        #iterate item list
        tag1 = 'item_info_1_'+str(i+1)    
        tag2 = 'item_info_2_'+str(i+1)
        tag3 = 'item_info_3_'+str(i+1)
        if item.name == b'':
            dpg.hide_item(tag1)
            dpg.hide_item(tag2)
            dpg.hide_item(tag3)
        else:
            dpg.set_value(tag1,item.name.decode('utf-8'))
            pos = np.array([item.area_pos.x,item.area_pos.y])
            dpg.set_value(tag2, str(pos))
            dpg.set_value(tag3, str(item.dist))
            dpg.show_item(tag1)
            dpg.show_item(tag2)
            dpg.show_item(tag3)

        obj = object_list[i]
        #iterate obj list
        tag1 = 'obj_info_1_'+str(i+1)    
        tag2 = 'obj_info_2_'+str(i+1)
        tag3 = 'obj_info_3_'+str(i+1)
        tag4 = 'obj_info_4_'+str(i+1)

        if obj.name == b'':
            dpg.hide_item(tag1)
            dpg.hide_item(tag2)
            dpg.hide_item(tag3)
            dpg.hide_item(tag4)
        else:
            dpg.set_value(tag1, obj.name.decode('utf-8'))
            pos = np.array([obj.area_pos.x,item.area_pos.y])
            dpg.set_value(tag2,str(pos))
            dpg.set_value(tag3,str(obj.dist))
            dpg.set_value(tag4,str(obj.mode))

            dpg.show_item(tag1)
            dpg.show_item(tag2)
            dpg.show_item(tag3)
            dpg.show_item(tag4)

        i+=1

    #print("--- %s seconds ---" % (time.time() - start_time))

monster_list = None
item_list = None
object_list = None
run = None
_player = None
game_info_list = None
area_list = None
current_level = None
lock = 0

def start_bot(sender, data):
    global lock
    log = ("starting bot.....")
    log_color(log,fg_color=manager_color)
    lock = 1

def overlay(monster_clist,item_clist,object_clist,poi_clist, game_info_clist, player, area_clist, running_manager):
    """gui setup, takes lists from the manager, makes some globals for the updater function
    
    Args:
        monster_clist (TYPE): Description
        item_clist (TYPE): Description
        object_clist (TYPE): Description
        poi_clist (TYPE): Description
        game_info_clist (TYPE): Description
        player (TYPE): Description
        area_clist (TYPE): Description
    """

    global running
    global map_list

    global monster_list
    global item_list
    global object_list
    global area_list

    global run
    global _player
    global current_level
    global game_info_list
    global area_list
    global lock
    _player = game_info_clist.player

    item_list = item_clist
    monster_list = monster_clist
    object_list = object_clist
    area_list = area_clist
    game_info_list = game_info_clist
    current_level = None
    

    run = running_manager

    fuchsia = (255,0,255)  # Transparency color

    dpg.create_context()
    
    mem_labels = ["base","game info","hover","exp","unit","menu","ui settings","menu vis","player unit", "playerpath", "hp", "mp","?","?","?","?","?","?","?"]
    player_labels = ['name','lvl', 'exp', 'world_x', 'worly_y', 'area_x', 'area_y', 'offset_x', 'offset_y', 'real_hp', 'real_mp', 'base_hp', 'base_mp', 'nerco_skel', 'necro_mage','necro_gol','necro_revive']
    map_labels = ["name",'id','seed','difficulty','loaded','ip','game_name','game_pass','offset_x','offset_y']

    dpg.create_viewport(title='overlay',vsync=False,always_on_top=True,decorated=False,clear_color=[0.0,0.0,0.0,0.0])
    
    dpg.set_viewport_always_top(True)
    dpg.setup_dearpygui()
  

    poly = []

    with dpg.window(label="map", pos=(0,0),width=1280,height=720, tag="map_gui", no_scrollbar=True, no_background=True, no_title_bar=True):

        with dpg.draw_node(tag="player_marker", parent='map_node'):
            dpg.draw_circle((0,0),4,color=(255,0,0,255),fill=[0,0,0,0],parent='player_marker', tag='l_player_marker')                
                    
                        
        with dpg.draw_node(tag="map_root_transform", parent='map_gui'):
            with dpg.draw_node(tag="map_root", parent='map_root_transform'):
                with dpg.draw_node(tag="map_node", parent='map_root'):
                    pass
    
    


    with dpg.window(label="debug",width=340,height=800, tag="debug_gui", no_scrollbar=True):
     
        with dpg.table(header_row=False, tag="fpstable",parent='debug_gui'):
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()
            dpg.add_table_column()

            with dpg.table_row():
                dpg.add_text("main:",color=[255, 55, 55])
                dpg.add_text(str(-99999), tag="FPS_MAIN",color=[255, 55, 55])
                dpg.add_text("mobs:",color=[255, 55, 55])
                dpg.add_text(str(-99999), tag="FPS_MONSTERS",color=[255, 55, 55])
            with dpg.table_row():
                dpg.add_text("items:",color=[255, 55, 55])
                dpg.add_text(str(-99999), tag="FPS_ITEMS",color=[255, 55, 55])
                dpg.add_text("draw:",color=[255, 55, 55])
                dpg.add_text(str(-99999), tag="FPS_DRAW",color=[255, 55, 55])
            with dpg.table_row():
                dpg.add_text("obj:",color=[255, 55, 55])
                dpg.add_text(str(-99999), tag="FPS_OBJ",color=[255, 55, 55])
                dpg.add_text("?:",color=[255, 55, 55])
                dpg.add_text(str(-99999), tag="FPS_?",color=[255, 55, 55])
                
        with dpg.tab_bar(parent="debug_gui"):
            with dpg.tab(label="monsters"):
                with dpg.table(header_row=False, tag="monstertable", resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True, clipper=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    i=0
                    for m in monster_clist:
                        with dpg.table_row():
                            tag1 = 'monster_info_1_'+str(i+1)    
                            tag2 = 'monster_info_2_'+str(i+1)
                            tag3 = 'monster_info_3_'+str(i+1)
                            dpg.add_text(m.name.decode('utf-8'),tag=tag1, color=[0, 255, 255])
                            pos = np.array([m.area_pos.x,m.area_pos.y])
                            dpg.add_text(str(pos),tag=tag2,color=[255, 55, 55])
                            dpg.add_text(str(m.dist),tag=tag3,color=[255, 55, 55])
                        i+=1

            with dpg.tab(label="npcs"):
                with dpg.table(header_row=False, tag="npctable", resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True, clipper=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    i=0
                    for m in monster_clist:
                        with dpg.table_row():
                            tag1 = 'npc_info_1_'+str(i+1)    
                            tag2 = 'npc_info_2_'+str(i+1)
                            tag3 = 'npc_info_3_'+str(i+1)
                            dpg.add_text(m.name.decode('utf-8'),tag=tag1, color=[0, 255, 255])
                            pos = np.array([m.area_pos.x,m.area_pos.y])
                            dpg.add_text(str(pos),tag=tag2,color=[255, 55, 55])
                            dpg.add_text(str(m.dist),tag=tag3,color=[255, 55, 55])
                        i+=1

            with dpg.tab(label="proc"):
                with dpg.table(header_row=False, tag="memtable",  resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    for i in range(len(mem_labels)):
                        with dpg.table_row():
                            tag = 'memory_offsets_'+str(i+1)
                            dpg.add_text(str(mem_labels[i]), color=[0, 255, 255])
                            dpg.add_text(str(mem_labels[i]),tag=tag, color=[0, 255, 255])

            with dpg.tab(label="player"):
                with dpg.table(header_row=False, tag="playertable",  resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    for i in range(len(player_labels)):
                        with dpg.table_row():
                            tag = 'player_info_title_'+str(i+1)
                            dpg.add_text(str(player_labels[i]),tag=tag, color=[0, 255, 255])
                            tag1 = 'player_info_'+str(i+1)
                            dpg.add_text(str("blank"),tag=tag1,color=[255, 55, 55])



            with dpg.tab(label="map"):
                with dpg.table(header_row=False, tag="maptable", resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True, clipper=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    i=0
                    
                    while i<len(map_labels):
                        with dpg.table_row():
                            map_tag = 'map__info_'+str(i+1)
                            dpg.add_text(str(map_labels[i]), color=[0, 255, 255])
                            dpg.add_text(str(map_labels[i]),tag=map_tag,color=[255, 55, 55])
                            i+=1

            with dpg.tab(label="items"):
                with dpg.table(header_row=False, tag="itemtable", resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True, clipper=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    i=0
                    for item in item_clist:
                        #print(item.name)
                        with dpg.table_row():
                            tag1 = 'item_info_1_'+str(i+1)    
                            tag2 = 'item_info_2_'+str(i+1)
                            tag3 = 'item_info_3_'+str(i+1)
                            dpg.add_text(item.name.decode('utf-8'),tag=tag1, color=[0, 255, 255])
                            pos = np.array([item.area_pos.x,item.area_pos.y])
                            dpg.add_text(str(pos),tag=tag2,color=[255, 55, 55])
                            dpg.add_text(str(item.dist),tag=tag3,color=[255, 55, 55])
                        i+=1

            with dpg.tab(label="poi"):
                with dpg.table(header_row=False, tag="poitable", resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True, clipper=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    i=0

                    for poi in poi_clist:
                        with dpg.table_row():
                            tag1 = 'poi_info_1_'+str(i+1)
                            tag2 = 'poi_info_2_'+str(i+1)
                            tag3 = 'poi_info_3_'+str(i+1)

                            dpg.add_text(poi.name.decode('utf-8'),tag=tag1, color=[0, 255, 255])
                            pos = np.array([poi.area_pos.x,poi.area_pos.y])
                            dpg.add_text(str(pos),tag=tag2,color=[255, 55, 55])                            
                            dpg.add_text(str(poi.is_portal),tag=tag3,color=[255, 55, 55])

                        i+=1
            

            with dpg.tab(label="obj"):
                with dpg.table(header_row=False, tag="objtable", resizable=True, policy=dpg.mvTable_SizingStretchProp, borders_outerH=True, borders_innerV=True, borders_outerV=True, clipper=True):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    i=0
                    for obj in object_clist:
                        #print(item.name)
                        with dpg.table_row():
                            tag1 = 'obj_info_1_'+str(i+1)    
                            tag2 = 'obj_info_2_'+str(i+1)
                            tag3 = 'obj_info_3_'+str(i+1)
                            tag4 = 'obj_info_4_'+str(i+1)

                            dpg.add_text(obj.name.decode('utf-8'),tag=tag1, color=[0, 255, 255])
                            pos = np.array([obj.area_pos.x,item.area_pos.y])
                            dpg.add_text(str(pos),tag=tag2,color=[255, 55, 55])
                            dpg.add_text(str(obj.dist),tag=tag3,color=[255, 55, 55])
                            dpg.add_text(str(obj.mode),tag=tag4,color=[255, 55, 55])
                        i+=1
            
            with dpg.tab(label="ctrl"):
                
                dpg.add_button(label="start bot",callback=start_bot)
            
                dpg.add_slider_float(label="rx", default_value=60, max_value=90, min_value=-90, tag='rx')
                dpg.add_slider_float(label="ry", default_value=-3, max_value=90, min_value=-90, tag='ry')
                dpg.add_slider_float(label="rz", default_value=44.2, max_value=90, min_value=-90, tag='rz')
    
                dpg.add_slider_float(label="sx", default_value=.991, max_value=1.8, min_value=.1, tag='sx')
                dpg.add_slider_float(label="ty", default_value=-13.592, max_value=200, min_value=-200, tag='ty')
                dpg.add_slider_float(label="tz", default_value=-118.447, max_value=200, min_value=-200, tag='tz')
    


    dpg.show_viewport()
    hwnd = FindWindow(None,"overlay")
    original_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT )

    dpg.set_viewport_pos([0,0])
    dpg.toggle_viewport_fullscreen()

    
    d2 = FindWindow(None,"Diablo II: Resurrected")
    PyCWnd = win32ui.CreateWindowFromHandle(d2)
    mat = dpg.create_translation_matrix([0,0])

    xx0,yy0,xx1,yy1   = GetWindowRect(d2)
    x0,y0,x1,y1 = win32gui.GetClientRect(d2)
    w = (x1-x0)
    h = (y1-y0)
    tl = ClientToScreen(d2,(x0,y0))
    rb = ClientToScreen(d2,(x1,y1))

    left_border = tl[0]-xx0
    right_border = xx1-rb[0]
    bottom_border = yy1-rb[1]
    top_border = tl[1]-yy0



    np.set_printoptions(formatter={'float': '{: 0.2f}'.format})

    margins = MARGINS(-1, -1,-1, -1)
    dwm.DwmExtendFrameIntoClientArea(hwnd, margins)
    xx0,yy0,xx1,yy1   = GetWindowRect(d2)
    dpg.set_item_pos('map_gui',[xx0+left_border-5,yy0+33])
    trans_tgl = 0 
    debounce = 0

    xx = (_player.area_pos.x)
    yy = (_player.area_pos.y)

    txx = (_player.area_pos.x)
    tyy = (_player.area_pos.y)

    tick = 0x99
    p_tick = 0
    tick = running_manager.tick_lock

 
    while dpg.is_dearpygui_running():

        #if running_manager.main is False:
        #    break

        tick = running_manager.tick_lock
        frame = dpg.get_frame_count()

        if tick != p_tick and tick == 0x08:
            #!!!this locks all execution outside of safe areas in d2r, prevents trying to get memory during loading !!!
            #not sure if its actually needed in the UI, but it seems to fix a freezing issue 
            p_tick=tick
            if frame>1:        
                    dpg.set_frame_callback(frame+1,main_update)
        else:
            p_tick=tick
            continue

        #handle keypresses to unlock the gui
        if lock == 1:
            log = ("LOCKED THE UI!")
            log_color(log,fg_color=manager_color)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT )
            trans_tgl = not trans_tgl
            lock = 0
        if keyboard.is_pressed('end'):
            
            if trans_tgl==0:
                if debounce == 1:
                    log = ("UNLOCKED THE UI!")
                    log_color(log,fg_color=important_color)
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, original_style )
                    trans_tgl = not trans_tgl
            else:
                if debounce == 1: 
                    log = ("LOCKED THE UI!")
                    log_color(log,fg_color=manager_color)
                    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT )
                    trans_tgl = not trans_tgl
            debounce+=1
        else:
            debounce = 0



        fps = dpg.get_frame_rate()
        dpg.set_value('FPS_DRAW',int(fps))  


        w =  dpg.get_item_width('map_gui')/2.0
        h =  dpg.get_item_height('map_gui')/2.0

        x_rot = dpg.get_value("rx")
        y_rot = dpg.get_value("ry")
        z_rot = dpg.get_value("rz")

        sx = dpg.get_value("sx")
        ty = dpg.get_value("ty")
        tz = dpg.get_value("tz")

        camera_angle = -26.0 * 3.14159274 / 180.0
        proj = dpg.create_perspective_matrix(camera_angle, 1.0, 0.1, 100)
        view = dpg.create_orthographic_matrix(.28*sx,-.28*sx, -.28*sx, .28*sx, .1, 100)
        model_z = dpg.create_rotation_matrix(math.pi*z_rot/180.0 , [0, 0, 1])
        model_x = dpg.create_rotation_matrix(math.pi*x_rot/180.0 , [1, 0, 0])
        model_y = dpg.create_rotation_matrix(math.pi*y_rot/180.0 , [0 ,1, 0])

        a_y = float(area_clist.mini_map_size.y)
        a_x = float(area_clist.mini_map_size.x)
        zero = dpg.create_translation_matrix([a_y/2.0,a_x/2.0])
        izero = dpg.create_translation_matrix([-a_y/2.0,-a_x/2.0])
        mx = dpg.create_translation_matrix([w,h,1])

        

        txx = (_player.area_pos.x+txx)/2.0
        tyy = (_player.area_pos.y+tyy)/2.0
        if frame % 2 == 1:
            xx = txx
            yy = tyy
        pp = dpg.create_translation_matrix([-yy,-xx,1])
        
        dpg.apply_transform("map_root", mx*view*model_y*model_x*model_z*izero*pp*zero)
        dpg.apply_transform("player_marker", mx*view*model_y*model_x*model_z)

        dpg.render_dearpygui_frame()

    print("WE CRASHED SHULdNT GET HERE")
    #dpg.destroy_context()