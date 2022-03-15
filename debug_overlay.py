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


def closest_node(node, nodes):
    return nodes[cdist([node], nodes).argmin()]
def closest_node_index(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return closest_index

class Overlay:

    def __init__(self, game_state):
        self._api = None
        self._game_state = game_state
        self._current_area = "0"
        self._mini_map_h =game_state.mini_map_h
        self._mini_map_w =game_state.mini_map_h
        
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
        time_start = time.time()
    
        while game_state.clusters is None:
            time.sleep(.15)
            print("waiting for clusters")


        nodes = game_state.map
        self._clusters = game_state.clusters


        colors = []
        for centroid in self._clusters:
            seed = centroid[0]+centroid[1]
            random.seed(seed+234234)
            r = float(random.randint(0,255))/255.0
            random.seed(seed+32345)
            g = float(random.randint(0,255))/255.0
            random.seed(seed+234230)
            b = float(random.randint(0,255))/255.0
            colors.append([r*.26,g*.26,b*.26])
        time_start=time.time()
        for node in nodes:
            for key in node:
                if key:
                    closest = closest_node_index([x,y],self._clusters)
                    r = colors[closest][0]
                    g = colors[closest][1]
                    b = colors[closest][2]
                    self._texture_data.append(r)
                    self._texture_data.append(g)
                    self._texture_data.append(b)
                    self._texture_data.append(1.0)

                else:
                    self._texture_data.append(0.0)
                    self._texture_data.append(0.0)
                    self._texture_data.append(0.0)
                    self._texture_data.append(0.0)
                    pass
                x+=1
            x=0
            y+=1

        dpg.delete_item("texture_tag")
        dpg.remove_alias("texture_tag")
        dpg.delete_item("map_node", children_only=True)
        dpg.add_static_texture(self._mini_map_w,self._mini_map_h, self._texture_data,parent="_txt", tag="texture_tag")
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


        with dpg.window(label="static entities",width=220,height=220,pos=(1060,220), tag="entities_main",no_resize=True,no_scrollbar=False,no_title_bar=False,no_move=True,no_collapse=True):
            with dpg.table(header_row=False,tag="entity_table"):
                dpg.add_table_column()
                for i in range(0, 2):
                    with dpg.table_row():
                        for j in range(0, 1):
                            dpg.add_text(f"Row{i} Column{j}")


        with dpg.window(label="summons",width=220,height=140,pos=(1060,440), tag="entities_summons",no_resize=True,no_scrollbar=False,no_title_bar=False,no_move=True,no_collapse=True):
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
    
        fps = 25
        time_delta = 1./fps
        
        while dpg.is_dearpygui_running():

            if game_state.tick<7:
                pass

            t0 = time.time()
            time.sleep(time_delta)
            t1 = time.time()

            if len(game_state.map)<2 :
                #exit early no data loaded yet
                print("here")
                continue 

            else:

                if str(self._current_area) not in str(game_state.current_area):
                    print("update map")
                    self._current_area = str(game_state.current_area)
                    self._mini_map_h = game_state.map.shape[0]
                    self._mini_map_w = game_state.map.shape[1]
                    self.update_map(game_state)


                    dpg.delete_item("entities_main", children_only=True)

                    with dpg.table(header_row=False,tag="entity_table",parent="entities_main"):
                        dpg.add_table_column()
                        dpg.add_table_column()
                        for poi in game_state.poi:
                            with dpg.table_row():
                                dpg.add_text(poi['label'])
                                dpg.add_text(poi['position']-game_state.area_origin)

            if self._current_area is not None:
                #draw txt?

                offset_w = self._mini_map_w
                offset_h = self._mini_map_h
                center = 110
                px = game_state.player_area_pos[0] + game_state.player_offset[1]
                py = game_state.player_area_pos[1] + game_state.player_offset[1]

                dpg.apply_transform("map_node", dpg.create_translation_matrix([0,0]))
                dpg.apply_transform("player", dpg.create_translation_matrix([px,py]))
                dpg.apply_transform("root_node", dpg.create_translation_matrix([-px+center,-py+center]))
                
                dpg.delete_item("monsters", children_only=True)
                dpg.delete_item("no_scale", children_only=True)

                dpg.draw_text((0, 0), game_state.player_area_pos, color=(255, 82, 255, 255),size=12,parent="no_scale")
                dpg.draw_text((150, 0), int(1. / (t1 - t0)), color=(0, 255, 255, 255),size=12,parent="no_scale")

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

                #for npc in data['static_npcs']:
                #    local = npc['position']-data["area_origin"]
                    #print(local)
                #    x = local[0]
                #    y = local[1]
                #    name = str(npc['name'])
                #    dpg.draw_circle((1+x, 1+y), 2, color=(0, 255, 255, 255),parent="monsters")
                #    dpg.draw_text((1+x, 1+y), name, color=(111, 222, 255, 255),size=12,parent="monsters")

                for poi in game_state.poi:
                    local = poi['position']-game_state.area_origin
                    #print(local)
                    x = local[0]
                    y = local[1]
                    name = str(poi['label'])
                    dpg.draw_circle((1+x, 1+y), 2, color=(0, 255, 255, 255),parent="monsters")
                    dpg.draw_text((1+x, 1+y), name, color=(255, 255, 0, 255),size=12,parent="monsters")

                for mob in game_state.monsters:
                    #print(mob)
                    local = mob['position']-game_state.area_origin

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
                        dpg.add_text(game_state.necro_skel)
                    with dpg.table_row():
                        dpg.add_text('mage')
                        dpg.add_text(game_state.necro_mage)
                    with dpg.table_row():
                        dpg.add_text('golem')
                        dpg.add_text(game_state.necro_gol)
                    with dpg.table_row():
                        dpg.add_text('revives')
                        dpg.add_text(game_state.necro_rev)

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
            
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

        
    def stop_overlay(self):
        dpg.stop_dearpygui()
        dpg.destroy_context()
        #os.exit(1)


def stop():
    dpg.stop_dearpygui()
    dpg.destroy_context()
    sys.exit(1)
