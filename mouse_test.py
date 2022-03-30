import time
import win32api
import win32gui
import win32con
from dataclasses import dataclass

input_queue = []
running = True

vk_codes= {
    'a':0x41,
    'b':0x42,
    'c':0x43,
    'd':0x44,
    'e':0x45,
    'f':0x46,
    'g':0x47,
    'h':0x48,
    'i':0x49,
    'j':0x4A,
    'k':0x4B,
    'l':0x4C,
    'm':0x4D,
    'n':0x4E,
    'o':0x5F,
    'p':0x50,
    'q':0x51,
    'r':0x52,
    's':0x53,
    't':0x54,
    'u':0x55,
    'v':0x56,
    'w':0x57,
    'x':0x58,
    'y':0x59,
    'z':0x5A,
    '0':0x30,
    '1':0x31,
    '2':0x32,
    '3':0x33,
    '4':0x34,
    '5':0x35,
    '6':0x36,
    '7':0x37,
    '8':0x38,
    '9':0x39,
    "up": win32con.VK_UP
    , "kp_up": win32con.VK_UP
    , "down": win32con.VK_DOWN
    , "kp_down": win32con.VK_DOWN
    , "left": win32con.VK_LEFT
    , "kp_left": win32con.VK_LEFT
    , "right": win32con.VK_RIGHT
    , "kp_right": win32con.VK_RIGHT
    , "prior": win32con.VK_PRIOR
    , "kp_prior": win32con.VK_PRIOR
    , "next": win32con.VK_NEXT
    , "kp_next": win32con.VK_NEXT
    , "home": win32con.VK_HOME
    , "kp_home": win32con.VK_HOME
    , "end": win32con.VK_END
    , "kp_end": win32con.VK_END
    , "insert": win32con.VK_INSERT
    , "return": win32con.VK_RETURN
    , "tab": win32con.VK_TAB
    , "space": win32con.VK_SPACE
    , "backspace": win32con.VK_BACK
    , "delete": win32con.VK_DELETE
    , "escape": win32con.VK_ESCAPE , "pause": win32con.VK_PAUSE
    , "kp_multiply": win32con.VK_MULTIPLY
    , "kp_add": win32con.VK_ADD
    , "kp_separator": win32con.VK_SEPARATOR
    , "kp_subtract": win32con.VK_SUBTRACT
    , "kp_decimal": win32con.VK_DECIMAL
    , "kp_divide": win32con.VK_DIVIDE
    , "kp_0": win32con.VK_NUMPAD0
    , "kp_1": win32con.VK_NUMPAD1
    , "kp_2": win32con.VK_NUMPAD2
    , "kp_3": win32con.VK_NUMPAD3
    , "kp_4": win32con.VK_NUMPAD4
    , "kp_5": win32con.VK_NUMPAD5
    , "kp_6": win32con.VK_NUMPAD6
    , "kp_7": win32con.VK_NUMPAD7
    , "kp_8": win32con.VK_NUMPAD8
    , "kp_9": win32con.VK_NUMPAD9
    , "f1": win32con.VK_F1
    , "f2": win32con.VK_F2
    , "f3": win32con.VK_F3
    , "f4": win32con.VK_F4
    , "f5": win32con.VK_F5
    , "f6": win32con.VK_F6
    , "f7": win32con.VK_F7
    , "f8": win32con.VK_F8
    , "f9": win32con.VK_F9
    , "f10": win32con.VK_F10
    , "f11": win32con.VK_F11
    , "f12": win32con.VK_F12
    , "f13": win32con.VK_F13
    , "f14": win32con.VK_F14
    , "f15": win32con.VK_F15
    , "f16": win32con.VK_F16
    , "f17": win32con.VK_F17
    , "f18": win32con.VK_F18
    , "f19": win32con.VK_F19
    , "f20": win32con.VK_F20
    , "f21": win32con.VK_F21
    , "f22": win32con.VK_F22
    , "f23": win32con.VK_F23
    , "f24": win32con.VK_F24
    }
win_modders = {
    "shift": win32con.MOD_SHIFT
    ,"control": win32con.MOD_CONTROL
    ,"alt": win32con.MOD_ALT
    ,"super": win32con.MOD_WIN
    }

@dataclass
class Mouse:
    """input object
    """    
    btn: 0
    x:0
    y:0


@dataclass
class Key:
    """input object
    """    
    key: str

def queue_click(btn,x,y):
    global input_queue
    qm = Mouse(btn,x,y)
    input_queue.append(qm)

def queue_key(key):
    global input_queue
    qk = Key(key)
    input_queue.append(qk)

def halt():
    global running
    running = False

def process_queue():
    global input_queue
    global running

    while running:
        time.sleep(.1)
        if len(input_queue)>0:
            task = input_queue[0]
            if type(task) == Mouse:
                send_click(task.btn,task.x,task.y)
            if type(task) == Key:
                print("processing",task.key)
                press_key(task.key)
            input_queue.pop(0)
        else:
            continue
        
    print('halted')

def hold_key(key):
    hWnd = win32gui.FindWindow(None, "Diablo II: Resurrected")
    key_code = vk_codes[key]
    win32api.PostMessage(hWnd, win32con.WM_KEYDOWN, key_code, None)

def release_key(key):
    hWnd = win32gui.FindWindow(None, "Diablo II: Resurrected")
    key_code = vk_codes[key]
    win32api.PostMessage(hWnd, win32con.WM_KEYUP, key_code, None)

def press_key(key):
    hWnd = win32gui.FindWindow(None, "Diablo II: Resurrected")
    key_code = vk_codes[key]
    win32api.PostMessage(hWnd, win32con.WM_KEYDOWN, key_code, None)
    win32api.PostMessage(hWnd, win32con.WM_KEYUP, key_code, None)


def send_click(btn,x, y):
    hWnd = win32gui.FindWindow(None, "Diablo II: Resurrected")
    abs_coords = win32gui.ClientToScreen(hWnd,(int(x),int(y)))
    print(abs_coords)
    win32api.SetCursorPos((abs_coords[0],abs_coords[1]))
    print(abs_coords)
    mouse_position = win32api.MAKELONG(abs_coords[0],abs_coords[1])
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONDOWN , win32con.MK_LBUTTON, mouse_position)
    win32api.SendMessage(hWnd, win32con.WM_LBUTTONUP , win32con.MK_LBUTTON, mouse_position)

def exit_game():
    press_key('escape')
    time.sleep(0.08)
    send_click(0,640,320)

def enter_game_normal():
    time.sleep(0.08)
    send_click(0,580,640)
    press_key('r')

def enter_game_nightmare():
    time.sleep(0.08)
    send_click(0,580,640)
    press_key('n')

def enter_game_hell():
    time.sleep(0.08)
    send_click(0,580,640)
    press_key('h')

