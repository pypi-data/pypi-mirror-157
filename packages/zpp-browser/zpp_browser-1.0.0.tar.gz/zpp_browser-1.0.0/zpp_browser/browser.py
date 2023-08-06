####################################################################
#/ Nom du projet: py-zpp_browser                                  /#
#/ Nom du fichier: browser.py                                     /#
#/ Type de fichier: fichier principal                             /#
#/ Fichier annexe:                                                /#
#/                                                                /#
#/ Auteur: ZephyrOff  (Alexandre Pajak)                           /#
#/ Version: 1.0                                                   /#
#/ Description: Browser (Explorateur) de fichier en cli           /#
#/ Date: 27/06/2022                                               /#
####################################################################

import os
from glob import glob

if os.name=="nt":
    from msvcrt import getch,kbhit
else:
    import sys,tty,os,termios

########################### Getch ###########################
def getkey():
    if os.name=="nt":
        c1 = getch()
        if kbhit():
            c2 = getch()
            if c1 in (b"\x00", b"\xe0"):
                key_mapping = {72: "up", 80: "down", 77: "right", 75: "left"}
                return key_mapping.get(ord(c2), c1 + c2)
        key_mapping = {13: "enter"}
        return key_mapping.get(ord(c1), c1.decode())

    else:
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            while True:
                b = os.read(sys.stdin.fileno(), 3).decode()
                if len(b) == 3:
                    k = ord(b[2])
                    key_mapping = {10: 'enter', 65: 'up', 66: 'down', 67: 'right', 68: 'left'}
                else:
                    k = ord(b)
                    key_mapping = {10: 'enter'}
                return key_mapping.get(k, None)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

########################### Color ###########################
class ColorClass(object):
    def __init__(self, idc):
        self.ESC = "\x1b["
        self.END = "m"
        self.idc = idc

        if os.name=="nt":
            self.terminal_mode()

        self.color = {"black": "0","red": "1","green": "2","yellow": "3","blue": "4","magenta": "5","cyan": "6","light_gray": "7","dark_gray": "8","light_red": "9","light_green": "10","light_yellow": "11","light_blue": "12","light_magenta": "13","light_cyan": "14","white": "15","grey_0": "16","navy_blue": "17","dark_blue": "18","blue_3a": "19","blue_3b": "20","blue_1": "21","dark_green": "22","deep_sky_blue_4a": "23","deep_sky_blue_4b": "24","deep_sky_blue_4c": "25","dodger_blue_3": "26","dodger_blue_2": "27","green_4": "28","spring_green_4": "29","turquoise_4": "30","deep_sky_blue_3a": "31","deep_sky_blue_3b": "32","dodger_blue_1": "33","green_3a": "34","spring_green_3a": "35","dark_cyan": "36","light_sea_green": "37","deep_sky_blue_2": "38","deep_sky_blue_1": "39","green_3b": "40","spring_green_3b": "41","spring_green_2a": "42","cyan_3": "43","dark_turquoise": "44","turquoise_2": "45","green_1": "46","spring_green_2b": "47","spring_green_1": "48","medium_spring_green": "49","cyan_2": "50","cyan_1": "51","dark_red_1": "52","deep_pink_4a": "53","purple_4a": "54","purple_4b": "55","purple_3": "56","blue_violet": "57","orange_4a": "58","grey_37": "59","medium_purple_4": "60","slate_blue_3a": "61","slate_blue_3b": "62","royal_blue_1": "63","chartreuse_4": "64","dark_sea_green_4a": "65","pale_turquoise_4": "66","steel_blue": "67","steel_blue_3": "68","cornflower_blue": "69","chartreuse_3a": "70","dark_sea_green_4b": "71","cadet_blue_2": "72","cadet_blue_1": "73","sky_blue_3": "74","steel_blue_1a": "75","chartreuse_3b": "76","pale_green_3a": "77","sea_green_3": "78","aquamarine_3": "79","medium_turquoise": "80","steel_blue_1b": "81","chartreuse_2a": "82","sea_green_2": "83","sea_green_1a": "84","sea_green_1b": "85","aquamarine_1a": "86","dark_slate_gray_2": "87","dark_red_2": "88","deep_pink_4b": "89","dark_magenta_1": "90","dark_magenta_2": "91","dark_violet_1a": "92","purple_1a": "93","orange_4b": "94","light_pink_4": "95","plum_4": "96","medium_purple_3a": "97","medium_purple_3b": "98","slate_blue_1": "99","yellow_4a": "100","wheat_4": "101","grey_53": "102","light_slate_grey": "103","medium_purple": "104","light_slate_blue": "105","yellow_4b": "106","dark_olive_green_3a": "107","dark_green_sea": "108","light_sky_blue_3a": "109","light_sky_blue_3b": "110","sky_blue_2": "111","chartreuse_2b": "112","dark_olive_green_3b": "113","pale_green_3b": "114","dark_sea_green_3a": "115","dark_slate_gray_3": "116","sky_blue_1": "117","chartreuse_1": "118","light_green_2": "119","light_green_3": "120","pale_green_1a": "121","aquamarine_1b": "122","dark_slate_gray_1": "123","red_3a": "124","deep_pink_4c": "125","medium_violet_red": "126","magenta_3a": "127","dark_violet_1b": "128","purple_1b": "129","dark_orange_3a": "130","indian_red_1a": "131","hot_pink_3a": "132","medium_orchid_3": "133","medium_orchid": "134","medium_purple_2a": "135","dark_goldenrod": "136","light_salmon_3a": "137","rosy_brown": "138","grey_63": "139","medium_purple_2b": "140","medium_purple_1": "141","gold_3a": "142","dark_khaki": "143","navajo_white_3": "144","grey_69": "145","light_steel_blue_3": "146","light_steel_blue": "147","yellow_3a": "148","dark_olive_green_3": "149","dark_sea_green_3b": "150","dark_sea_green_2": "151","light_cyan_3": "152","light_sky_blue_1": "153","green_yellow": "154","dark_olive_green_2": "155","pale_green_1b": "156","dark_sea_green_5b": "157","dark_sea_green_5a": "158","pale_turquoise_1": "159","red_3b": "160","deep_pink_3a": "161","deep_pink_3b": "162","magenta_3b": "163","magenta_3c": "164","magenta_2a": "165","dark_orange_3b": "166","indian_red_1b": "167","hot_pink_3b": "168","hot_pink_2": "169","orchid": "170","medium_orchid_1a": "171","orange_3": "172","light_salmon_3b": "173","light_pink_3": "174","pink_3": "175","plum_3": "176","violet": "177","gold_3b": "178","light_goldenrod_3": "179","tan": "180","misty_rose_3": "181","thistle_3": "182","plum_2": "183","yellow_3b": "184","khaki_3": "185","light_goldenrod_2a": "186","light_yellow_3": "187","grey_84": "188","light_steel_blue_1": "189","yellow_2": "190","dark_olive_green_1a": "191","dark_olive_green_1b": "192","dark_sea_green_1": "193","honeydew_2": "194","light_cyan_1": "195","red_1": "196","deep_pink_2": "197","deep_pink_1a": "198","deep_pink_1b": "199","magenta_2b": "200","magenta_1": "201","orange_red_1": "202","indian_red_1c": "203","indian_red_1d": "204","hot_pink_1a": "205","hot_pink_1b": "206","medium_orchid_1b": "207","dark_orange": "208","salmon_1": "209","light_coral": "210","pale_violet_red_1": "211","orchid_2": "212","orchid_1": "213","orange_1": "214","sandy_brown": "215","light_salmon_1": "216","light_pink_1": "217","pink_1": "218","plum_1": "219","gold_1": "220","light_goldenrod_2b": "221","light_goldenrod_2c": "222","navajo_white_1": "223","misty_rose1": "224","thistle_1": "225","yellow_1": "226","light_goldenrod_1": "227","khaki_1": "228","wheat_1": "229","cornsilk_1": "230","grey_100": "231","grey_3": "232","grey_7": "233","grey_11": "234","grey_15": "235","grey_19": "236","grey_23": "237","grey_27": "238","grey_30": "239","grey_35": "240","grey_39": "241","grey_42": "242","grey_46": "243","grey_50": "244","grey_54": "245","grey_58": "246","grey_62": "247","grey_66": "248","grey_70": "249","grey_74": "250","grey_78": "251","grey_82": "252","grey_85": "253","grey_89": "254","grey_93": "255"}
        self.mode = {"bold": "1",1: "1","dim": "2",2: "2","italic": "3",3: "3","underlined": "4",4: "4","blink": "5",5: "5","reverse": "7",7: "7","hidden": "8",8: "8","strikethrough": "9",9: "9","reset": "0",0: "0","res_bold": "21",21: "21","res_dim": "22",22: "22","res_underlined": "24",24: "24","res_blink": "25",25: "25","res_reverse": "27",27: "27","res_hidden": "28",28: "28"}

    def terminal_mode(self):
        from ctypes import windll, c_int, byref
        stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))
        mode = c_int(0)
        windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(mode))
        mode = c_int(mode.value | 4)
        windll.kernel32.SetConsoleMode(c_int(stdout_handle), mode)

    def attribute(self):
        if self.idc=='None' or self.idc==None:
            return ""
        else:
            if self.idc in self.mode:
                return self.ESC + self.mode[self.idc] + self.END
            else:
                return ""

    def foreground(self):
        if self.idc=='None' or self.idc==None:
            return ""
        else:
            if str(self.idc).isdigit():
                return self.ESC + "38;5;" + str(self.idc) + self.END
            else:
                if self.idc in self.color:
                    return self.ESC + "38;5;" + self.color[self.idc] + self.END
                else:
                    return ""

    def background(self):
        if self.idc=='None' or self.idc==None:
            return ""
        else:
            if str(self.idc).isdigit():
                return self.ESC + "48;5;" + str(self.idc) + self.END
            else:
                if self.idc in self.color:
                    return self.ESC + "48;5;" + self.color[self.idc] + self.END
                else:
                    return ""

def attr(color):
    return ColorClass(color).attribute()

def fg(color):
    return ColorClass(color).foreground()

def bg(color):
    return ColorClass(color).background()

########################### Cursor ##########################
def com(val):
    print("\033"+val,end="")

def cursorTo(x=0):
    com("["+str(x)+";0H")

def cursorSave():
    com("7")

def cursorRestore():
    com("8")

def cursorHide():
    com("[?25l")

def cursorShow():
    com("[?25h")

def EraseLine():
    com("[2K")

def clear():
    print("\033[2J",end="")

############################ browser ###########################
class BrowserClass():
    def __init__(self,Path, Filter, ShowHidden, ShowDir, ShowFirst, Color, Pointer, Padding):
        self.Selected = 0
        self.filter = Filter
        self.ShowHidden = ShowHidden
        self.ShowDir = ShowDir
        self.ShowFirst = ShowFirst

        self.mapping_color(Color)

        self.path = os.path.abspath(Path).replace("\\","/")

        cursorHide()

        self.edgeY = Padding
        self.pointer = Pointer

    def __del__(self):
        cursorShow()
        clear()

    def print_path(self):
        max = os.get_terminal_size().columns
        size = len(" "*(self.edgeY+len(self.pointer))+"-- "+self.path+" --\n")

        if size<max:
            print(" "*(self.edgeY+len(self.pointer))+"-- "+self.path+" --\n")
        else:
            path = self.path.split("/")
            while len(" "*(self.edgeY+len(self.pointer))+"-- ../"+"/".join(path)+" --\n")>max:
                del path[0]
            print(" "*(self.edgeY+len(self.pointer))+"-- ../"+"/".join(path)+" --\n")            


    def glob_dir(self):
        if self.ShowFirst!=None:
            data_dir = []
            data_file = []

        data = []

        if self.ShowDir:
            glob_data = [".."]
        else:
            glob_data = []

        if self.ShowHidden:
            glob_data += sorted(glob(self.path+"/*") + glob(self.path+"/.*"))
        else:
            glob_data += sorted(glob(self.path+"/*"))
        for element in glob_data:
            fileName, fileExtension = os.path.splitext(element)
            if (self.filter!=["*"] and (fileExtension in self.filter or (os.path.isdir(element) and self.ShowDir==True))) or (self.filter==["*"] and ((os.path.isdir(element) and self.ShowDir==True) or (os.path.isdir(element)==False))):
                if self.ShowFirst!=None:
                    if os.path.isdir(element):
                        data_dir.append(element)
                    else:
                        data_file.append(element)
                else:
                    data.append(element)

        if self.ShowFirst=="dir":
            data = data_dir+data_file
        elif self.ShowFirst=="file":
            data = data_file+data_dir

        return data


    def load(self):
        self.Options = self.glob_dir()
        self.MenuMax = len(self.Options)-1

        file_choice = None
        choice = None
        while file_choice==None:
            clear()
            self.Selected = self.show()
            file = self.Options[self.Selected]
            if os.path.isfile(file):
                file_choice=file
            elif file=="..":
                pathtemp = self.path.split("/")
                self.path = "/".join(pathtemp[0:len(pathtemp)-1])
                self.Options = self.glob_dir()
                self.MenuMax = len(self.Options)-1
            elif os.path.isdir(file):
                self.path = file.replace("\\","/")
                self.Options = self.glob_dir()
                self.MenuMax = len(self.Options)-1


    def show(self):
            tmax = (os.get_terminal_size().lines)-2
            self.print_path()
            for i,element in enumerate(self.Options):
                element = element.replace("\\","/").replace(self.path+"/","")
                fore,back = self.get_color_content(self.Options[i])
                if i<tmax-1:
                    if i==0:
                        print(" "*self.edgeY + self.pointer + fg(self.map_color['__selected__']['fore'])+bg(self.map_color['__selected__']['back'])+element+attr(0))
                    else:
                        if os.path.isdir(element):
                            print(" "*(self.edgeY+len(self.pointer)) + fg(fore)+bg(back)+element+attr(0))
                        else:
                            print(" "*(self.edgeY+len(self.pointer)) + fg(fore)+bg(back)+element+attr(0))
            
            if tmax<self.MenuMax:
                self.size = tmax-2
            else:
                self.size = self.MenuMax

            self.Selected = 0
            self.cursor = 2
            while True:
                k = getkey()
                if k=="up" and len(self.Options)>1:
                    self.Rewrite_line()
                    if self.Selected-1<0:
                        self.Selected=self.MenuMax
                        self.cursor = self.size+2
                        self.Rewrite_screen("bottom")
                    else:
                        self.Selected-=1
                        if self.cursor==2 and self.Selected>=0:
                            self.Rewrite_screen("up")
                        else:
                            self.cursor-=1
                    self.Rewrite_Selected()
                elif k=="down" and len(self.Options)>1:
                    self.Rewrite_line()
                    if self.Selected+1>self.MenuMax:
                        self.Selected=0
                        self.cursor=2
                        self.Rewrite_screen("top")
                    else:
                        self.Selected+=1
                        if self.cursor==self.size+2 and self.cursor<self.MenuMax and self.Selected<self.MenuMax+1:
                            self.Rewrite_screen("down")
                        else:
                            self.cursor+=1
                        cursorTo(self.cursor)
                    self.Rewrite_Selected()
                elif k=="enter":
                    return self.Selected
    
    def Rewrite_screen(self,direction):
        clear()
        self.print_path()

        if direction=="down":
            list_f = self.Options[self.Selected-self.size:self.Selected+1]
        elif direction=="up":
            list_f = self.Options[self.Selected:self.Selected+self.size+1]
        elif direction=="top":
            list_f = self.Options[0:self.size+1]
        elif direction=="bottom":
            list_f = self.Options[self.Selected-self.size:self.Selected]

        for i in list_f:
            element = element = i.replace("\\","/").replace(self.path+"/","")
            fore,back = self.get_color_content(i)
            if os.path.isdir(i):
                print(" "*(self.edgeY+len(self.pointer)) + fg(fore)+bg(back)+element+attr(0))
            else:
                print(" "*(self.edgeY+len(self.pointer)) + fg(fore)+bg(back)+element+attr(0))

    def Rewrite_line(self):
        cursorSave()
        cursorTo(self.cursor+1)
        EraseLine()
        fore,back = self.get_color_content(self.Options[self.Selected])
        print(" "*(self.edgeY+len(self.pointer)) + fg(fore)+bg(back) + self.Options[self.Selected].replace("\\","/").replace(self.path+"/","")+attr(0),end="")

    def Rewrite_Selected(self):
        cursorTo(self.cursor+1)
        EraseLine()
        print(" "*self.edgeY + self.pointer + fg(self.map_color['__selected__']['fore'])+bg(self.map_color['__selected__']['back'])+self.Options[self.Selected].replace("\\","/").replace(self.path+"/","")+attr(0))
        cursorRestore()

    def get_color_content(self, element):
        if os.path.isdir(element):
            return self.map_color['__dir__']['fore'], self.map_color['__dir__']['back'] 
        else:
            fileName, fileExtension = os.path.splitext(element)
            element = element.replace("\\","/").replace(self.path+"/","")
            if fileExtension in self.map_color.keys():
                return self.map_color[fileExtension]['fore'], self.map_color[fileExtension]['back']
            elif element.startswith('.'):
                return self.map_color['__hidden__']['fore'], self.map_color['__hidden__']['back']
            else:
                return self.map_color['__default__']['fore'], self.map_color['__default__']['back']

    def mapping_color(self,list_color):
        if isinstance(list_color, list):
            self.map_color = {}
            for line in list_color:
                if len(line)==3:
                    if "," in line[0]:
                        for ext in line[0].split(","):
                            self.map_color[ext] = {}
                            self.map_color[ext]['fore'] = line[1] 
                            self.map_color[ext]['back'] = line[2]
                    else:
                        self.map_color[line[0]] = {}
                        self.map_color[line[0]]['fore'] = line[1] 
                        self.map_color[line[0]]['back'] = line[2]

            default_data = ['__default__','white','black'],['__hidden__','yellow','black'],['__selected__','red','black'],['__dir__','green','black']
            for elem in default_data:
                if elem[0] not in self.map_color.keys():
                    self.map_color[elem[0]] = {}
                    self.map_color[elem[0]]['fore'] = elem[1] 
                    self.map_color[elem[0]]['back'] = elem[2]
            print(self.map_color['__selected__']['fore'])
        else:
            self.map_color = {'__default__': {'fore': 'white', 'back': 'black'}, '__hidden__': {'fore': 'grey', 'back': 'black'}, '__selected__': {'fore': 'red', 'back': 'black'}, '__dir__': {'fore': 'green', 'back': 'black'}}

def Browser(Path, Filter=["*"], ShowHidden=True, ShowDir=True, ShowFirst="dir", Color=None, Pointer="> ", Padding=2):
    return BrowserClass(Path, Filter, ShowHidden, ShowDir, ShowFirst, Color, Pointer, Padding).load()
