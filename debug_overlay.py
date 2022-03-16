import win32gui
import win32api
import win32con
import win32ui
from win32gui import FindWindow, GetWindowRect, ClientToScreen
import os

import numpy as np
import dearpygui.dearpygui as dpg
import math
import random
from scipy.spatial.distance import cdist
from scipy.spatial import distance
import time
import collections
from copy import deepcopy


def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]
def closest_node_index(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

class Overlay:

    def __init__(self, game_state):
        self._api = None
        self._game_state = game_state
        self._current_area = "0"
        self._mini_map_h =game_state.area.mini_map_h
        self._mini_map_w =game_state.area.mini_map_w
        self._draw_path=None
        self._astar_path = None
        self._texture_data = None
        self._clusters= game_state.clusters
        self._features= game_state.features

    def update_map(self,game_state):
        
        x = 0
        y = 0 
        self._texture_data=None
        self._texture_data=[]
        self._clusters = game_state.clusters
        time_start = time.time()
        nodes = game_state.area.map
        colors = []

        blank = []
        flat = nodes.flatten()

        for n in flat:
            if n:
                self._texture_data.append(0)
                self._texture_data.append(0)
                self._texture_data.append(0)
                self._texture_data.append(0.0)

            else:
                self._texture_data.append(0.138)
                self._texture_data.append(0.138)
                self._texture_data.append(0.138)
                self._texture_data.append(1.0)
                pass

        dpg.delete_item("texture_tag")
        dpg.remove_alias("texture_tag")
        dpg.delete_item("map_node", children_only=True)
        dpg.add_static_texture(self._mini_map_w,self._mini_map_h, self._texture_data,parent="_txt", tag="texture_tag")


        with dpg.draw_node(tag="clusters",parent="map_node"):
            jj = 0
            for c in self._clusters:
                jj +=1
                seed = c[0]+c[1]+jj
                random.seed(seed+234234)
                r = float(random.randint(0,255))*.2
                random.seed(seed+32345)
                g = float(random.randint(0,255))*.2
                random.seed(seed+234230)
                b = float(random.randint(0,255))*.2
                draw_size = 100
                p_min = [0,0] + c - (draw_size/2)
                p_max = [draw_size,draw_size] + c + (draw_size/2)
                dpg.draw_rectangle(p_min,p_max, thickness=0, color=[0,0,0,0], fill=[r,g,b,255])
                #dpg.draw_circle([c[0], c[1]], 40, color=[r,g, b], fill=[r, g, b]) # sun

        dpg.draw_image("texture_tag",parent="map_node",pmin=[0,0],pmax=[self._mini_map_w,self._mini_map_h])


    def init(self):

        game_state = self._game_state
        fuchsia = (255,0,255)  # Transparency color

        dpg.create_context()

        self._texture_data = []
        for i in range(0, self._mini_map_w * self._mini_map_h):
            self._texture_data.append(0)
            self._texture_data.append(1.0)
            self._texture_data.append(0)
            self._texture_data.append(255 / 255)

        dpg.add_texture_registry(label="txt_con", tag="_txt",show=False)
        dpg.add_static_texture(self._mini_map_w,self._mini_map_h, self._texture_data,parent="_txt", tag="texture_tag")

        with dpg.window(label="stats",width=220,height=220,pos=(1060,0), tag="main",no_resize=True,no_scrollbar=True,no_title_bar=True,no_move=True,no_collapse=True):
            #dpg.draw_circle((250,250),500,color=(55,55,55,255),fill=[55,55,55],parent="main")

            with dpg.draw_node(tag="root_scale"):
                with dpg.draw_node(tag="root_node"):
                    with dpg.draw_node(tag="map_node"):
                        dpg.draw_image("texture_tag",parent="map_node",pmin=(0,0),pmax=(self._mini_map_w,self._mini_map_h))
                    with dpg.draw_node(tag="player"):
                        dpg.draw_circle((2, 2), 4, color=(255, 255, 0, 255),parent="player",tag="ppos")
                    with dpg.draw_node(tag="monsters"):
                        dpg.draw_circle((0, 0), 0, color=(255, 0, 255, 255),parent="monsters",tag="mon_root")
            with dpg.draw_node(tag="no_scale"):
                dpg.draw_text((0, 0), '0', color=(255, 55, 75, 255),size=14,parent="no_scale")


        with dpg.window(label="monsters",width=220,height=520,pos=(0,100), tag="entities_monsters",no_resize=True,  no_background=True,no_scrollbar=False,no_title_bar=True,no_move=True,no_collapse=True):
            with dpg.table(header_row=False,tag="monster_table"):
                dpg.add_table_column()
                for i in range(0, 2):
                    with dpg.table_row():
                        for j in range(0, 1):
                            dpg.add_text(f"Row{i} Column{j}")


        with dpg.window(label="static entities",width=220,height=620,pos=(1060,220), tag="entities_main",no_resize=True,no_background=True,no_scrollbar=True,no_title_bar=True,no_move=True,no_collapse=True):
            with dpg.table(header_row=False,tag="entity_table"):
                dpg.add_table_column()
                for i in range(0, 2):
                    with dpg.table_row():
                        for j in range(0, 1):
                            dpg.add_text(f"Row{i} Column{j}")


        with dpg.window(label="summons",width=220,height=140,pos=(800,0), tag="entities_summons",no_resize=True, no_background=True,no_scrollbar=True,no_title_bar=True,no_move=True,no_collapse=True):
            with dpg.table(header_row=False,tag="summon_table"):
                dpg.add_table_column()
                for i in range(0, 2):
                    with dpg.table_row():
                        for j in range(0, 1):
                            dpg.add_text(f"Row{i} Column{j}")

        dpg.create_viewport(title='overlay', width=1280, height=720,decorated=False,clear_color=[255,0,255])
        dpg.setup_dearpygui()
        dpg.show_viewport()


        hwnd = FindWindow(None,"overlay")
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED  | win32con.WS_EX_TRANSPARENT)



        #this stuff is left incase I need to go back to non transparent, for reference
        # WS_EX_LAYERED | WS_EX_TRANSPARENT
        #styles = GetWindowLong(hwnd, GWL_EXSTYLE)
        #styles = WS_EX_LAYERED | WS_EX_TRANSPARENT
        #SetWindowLong(hwnd, GWL_EXSTYLE, styles)
        #SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
        #win32gui.SetLayeredWindowAttributes(hwnd, win32con.WS_EX_TRANSPARENT)


        d2 = FindWindow(None,"Diablo II: Resurrected")
        PyCWnd = win32ui.CreateWindowFromHandle(d2)

        mat = dpg.create_translation_matrix([0,0])

        
        tick = False
        ptick = True

        while dpg.is_dearpygui_running():

            hide = False

            #uhhh...
            hide = game_state.ui_state.Inventory | game_state.ui_state.SkillTree | game_state.ui_state.Character | game_state.ui_state.NpcInteract | game_state.ui_state.QuestLog | game_state.ui_state.Party | game_state.ui_state.MercenaryInventory | game_state.ui_state.SkillTree | game_state.ui_state.EscMenu | game_state.ui_state.Waypoint | game_state.ui_state.GroundItems

            if hide:
                dpg.hide_item("entities_monsters")
                dpg.hide_item("entities_main")
                dpg.hide_item("entities_summons")
                dpg.hide_item("map_node")
                dpg.hide_item("main")
                dpg.hide_item("no_scale")
            else:
                dpg.show_item("entities_monsters")
                dpg.show_item("entities_main")
                dpg.show_item("entities_summons")
                dpg.show_item("map_node")
                dpg.show_item("main")
                dpg.show_item("no_scale")

            if game_state.tick<7 and tick != ptick:    
                ptick = tick
                tick = not tick
                start_time = time.time()
                pass



            start_time = time.time() # start time of the loop

            if len(game_state.area.map)<2 :
                #exit early no data loaded yet
                #print("here")
                continue 

            else:

                if str(self._current_area) not in str(game_state.area.current_area):
                    #print("update map")
                    
                    self._mini_map_h = game_state.area.map.shape[0]
                    self._mini_map_w = game_state.area.map.shape[1]
                    if game_state.clusters is not None:
                        self.update_map(game_state)
                        self._current_area = str(game_state.area.current_area)

                    dpg.delete_item("entities_main", children_only=True)




                    with dpg.table(header_row=False,tag="entity_table",parent="entities_main"):
                        dpg.add_table_column()
                        dpg.add_table_column()
                        for poi in game_state.poi:
                            with dpg.table_row():
                                dpg.add_text(poi['label'])
                                dpg.add_text(poi['position']-game_state.area.origin)

            if self._current_area is not None:
                #draw txt?

                offset_w = self._mini_map_w
                offset_h = self._mini_map_h
                center = 110
                px = float(game_state.player.area_pos[0]) + game_state.player.float_offset[0]
                py = float(game_state.player.area_pos[1]) + game_state.player.float_offset[1]

                spx = f'{px:.2f}'
                spy = f'{py:.2f}'
                
                dpg.delete_item("entities_monsters", children_only=True)
                with dpg.table(header_row=False,tag="monster_table",parent="entities_monsters"):
                    dpg.add_table_column()
                    dpg.add_table_column()
                    dpg.add_table_column()
                    for m in game_state.monsters:
                        with dpg.table_row():
                            dpg.add_text(m['name'])
                            dpg.add_text(m['position']-game_state.area.origin)
                            dpg.add_text(m['dist'])

                dpg.apply_transform("map_node", dpg.create_translation_matrix([0,0]))
                dpg.apply_transform("player", dpg.create_translation_matrix([px-2,py-2]))
                dpg.apply_transform("root_node", dpg.create_translation_matrix([-px+center,-py+center]))
                
                dpg.delete_item("monsters", children_only=True)
                dpg.delete_item("no_scale", children_only=True)

                dpg.draw_text((0, 0), '['+spx+' '+spy+']', color=(255, 82, 255, 255),size=12,parent="no_scale")
                

                self._astar_path = game_state.astar_current_path
                self._draw_path = game_state.current_path

                if self._clusters is not None:
                    for node in self._clusters:
                        x = node[0]
                        y = node[1]
                        dpg.draw_circle((1+x, 1+y), 6, color=(0, 255, 0, 255),parent="monsters")

                if self._draw_path is not None:
                    for node in self._draw_path:
                        #these are flipped, unfortunate ha
                        x = node[0]
                        y = node[1]
                        #pygame.draw.rect(map_surface, (0,0,255), pygame.Rect(x,y, 2,2))
                        dpg.draw_circle((1+x, 1+y), 2, color=(0, 0, 255, 255),parent="monsters")

                px = 0 
                py = 0
                if self._astar_path is not None:
                    for node in self._astar_path:
                        #these are flipped, unfortunate ha

                        x = node[1]+1.5
                        y = node[0]+1.5
                        dpg.draw_circle((x, y), 3, color=(255, 0, 0, 255),parent="monsters")
                        #pygame.draw.rect(map_surface, (0,255,0), pygame.Rect(x,y, 9,9))
                        if px>0 and py>0:
                            dpg.draw_line((px, py), (x, y), color=(255, 255, 0, 255), thickness=0.05,parent="monsters")
                        px=x
                        py=y

                for poi in game_state.poi:
                    local = poi['position']-game_state.area.origin
                    x = local[0]
                    y = local[1]
                    name = str(poi['label'])
                    dpg.draw_circle((1+x, 1+y), 2, color=(0, 255, 255, 255),parent="monsters")
                    dpg.draw_text((1+x, 1+y), name, color=(255, 255, 0, 255),size=12,parent="monsters")

                for mob in game_state.monsters:
                    local = mob['position']-game_state.area.origin

                    x = local[0]
                    y = local[1]
                    #if mob['mode'] == 13:
                        #REVIVE?
                        #dpg.draw_circle((1+x, 1+y), 2, color=(255, 0, 190, 255),parent="monsters")
                    if mob['mode'] == 1:
                        #aware of you/activly pathing?
                        dpg.draw_circle((1+x, 1+y), 2, color=(120, 90, 10, 255),parent="monsters")
                    if mob['mode'] == 0:
                        #attacking??
                        dpg.draw_circle((1+x, 1+y), 2, color=(90, 10, 190, 255),parent="monsters")
                    if mob['mode'] == 2:
                        #?
                        dpg.draw_circle((1+x, 1+y), 2, color=(25, 70, 255, 255),parent="monsters")
                    if mob['mode'] == 12:
                        #dead
                        dpg.draw_circle((1+x, 1+y), 2, color=(255, 255, 255, 255),parent="monsters")
                dpg.apply_transform("root_scale", dpg.create_scale_matrix([2,2])*dpg.create_translation_matrix([-center/2,-center/2]))

                dpg.delete_item("entities_summons", children_only=True)
                with dpg.table(header_row=False,tag="summon_table",parent="entities_summons"):
                    dpg.add_table_column()
                    dpg.add_table_column()

                    with dpg.table_row():
                        dpg.add_text('skel')
                        dpg.add_text(game_state.summons.skele)
                    with dpg.table_row():
                        dpg.add_text('mage')
                        dpg.add_text(game_state.summons.mage)
                    with dpg.table_row():
                        dpg.add_text('golem')
                        dpg.add_text(game_state.summons.golem)
                    with dpg.table_row():
                        dpg.add_text('revives')
                        dpg.add_text(game_state.summons.revive)

                pass

            xx0,yy0,xx1,yy1   = GetWindowRect(d2)
            x0,y0,x1,y1 = win32gui.GetClientRect(d2)
            w = x1-x0
            h = y1-y0
            tl = ClientToScreen(d2,(x0,y0))
            rb = ClientToScreen(d2,(x1,y1))

            left_border = tl[0]-xx0
            right_border = xx1-rb[0]
            bottom_border = yy1-rb[1]
            top_border = tl[1]-yy0
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, xx0+left_border,yy0+top_border, int(w), int(h), win32con.SWP_NOSIZE)
            
            delta_time = (1000 * dpg.get_delta_time()) 
            if delta_time ==0:
                delta_time = 999
            
            dpg.draw_text((150, 0), int(1000 / int(delta_time)), color=(0, 255, 255, 255),size=12,parent="no_scale")
            dpg.draw_text((180, 0), int(game_state.fps), color=(255, 0, 255, 255),size=12,parent="no_scale")
            dpg.draw_text((20, 200), str(game_state.game_info.ip_addr), color=(80, 47, 255, 255),size=12,parent="no_scale")
            dpg.render_dearpygui_frame()
            t0 = time.time()

        dpg.destroy_context()

        
    def stop_overlay(self):
        dpg.stop_dearpygui()
        dpg.destroy_context()
        #os.exit(1)


def stop():
    dpg.stop_dearpygui()
    dpg.destroy_context()
    sys.exit(1)
