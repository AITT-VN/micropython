import _thread
from time import sleep_ms
from pixel import *
from image import *
from utility import *
from setting import DEV_VERSION

Black = [0, 0, 0]
White = [255, 255, 255]
Red = [255, 0, 0]
Orange = [255, 165, 0]
Yellow = [255, 255, 0]
Green = [0, 128, 0]
Blue = [0, 0, 255]
Indigo = [75, 0, 130]
Purple = [128, 0, 128]

Zero = [Black] * 5
# 0-Black, 1-Red, 2-Orange, 3-Yellow, 4-Green, 5-Blue, 6-Indigo, 7-Purple, 8-White
Colors = [Black, Red, Orange, Yellow, Green, Blue, Indigo, Purple, White]

class Display:
    def __init__(self):
        self.queue = {}
        self.last_id = -1
        self.current_show = None
        self.Led = Pixel()
        self.tem = [[0, 0, 0]] * 25  # Display buffer
        if DEV_VERSION >=4: # v4 and up using small led 2020
            self.brightness = 20
        else: # v3 and previous versions using big led 5050
            self.brightness = 50

    def __convert_color(self, color):
        if color is None:
            color = Red

        if isinstance(color, str):
            try:
                color = hex_to_rgb(color)
            except Exception as e:
                color = Red

        # apply brightness
        rate = self.brightness/float(100)
        return (int(color[0]*rate/4), int(color[1]*rate/4), int(color[2]*rate/4))

    # generate new id assigned for each new thread
    def __get_id(self):
        if len(self.queue) > 1:
            return -1

        for i in self.queue:
            self.queue[i] = True
        
        id = self.last_id + 1

        if id > 100:
            id = 0
        
        self.last_id = id

        self.queue[id] = False
        return id
    
    def __show(self, it, color=None, id=0):
        it = iter(it)
        for r in range(25):
            if self.queue[id]:
                return
            col = next(it)
            if color != None:
                self.Led.LoadPos(r, color if col else Black)
            else:
                self.Led.LoadPos(r, self.__convert_color(Colors[col]))
        self.Led.Show()

    def __scroll(self, val, color=Red, delay=200, id=0):        
        # if string to show is only 1 char, show instead of scrolling
        val = str(val) + ' '
        if len(val) == 2:
            if isinstance(color[0], list):
                color = color[0]
            color = self.__convert_color(color)
            self.__show(CharData[val[0]], color, id)
            if self.queue.get(id) != None:
                del self.queue[id]
            self.current_show = None
            return

        color_num = 1
        if color != Red:
            if isinstance(color, list) and isinstance(color[0], list):
                color_num = len(color)
        col_cnt = 0
        it = iter(color)

        try:
            for i in range(len(val)-1):
                if self.queue[id]:
                    break

                char1 = CharData[val[i]]
                char2 = CharData[val[i+1]]

                combined_matrix = [0]*55
                for r in range(5):
                    for c in range(5):
                        combined_matrix[r*11 + c] = char1[r*5 + c]
                    for c in range(6, 11):
                        combined_matrix[r*11 + c] = char2[r*5 + c-6]

                if color_num == 1:
                    now_col = color
                else:
                    if col_cnt < color_num:
                        now_col = next(it)  # get next color
                    else:
                        col_cnt = 0
                        it = iter(color)
                        now_col = next(it)
                    col_cnt += 1

                now_col = self.__convert_color(now_col)

                ##########################
                self.tem = [0]*25
                for step in range(6):
                    if self.queue[id]:
                        break
                    for c in range(5):
                        if self.queue[id]:
                            break
                        for r in range(5):
                            if self.queue[id]:
                                break
                            self.tem[r*5 + c] = combined_matrix[r*11 + step + c]
                    self.__show(self.tem, now_col, id)
                    sleep_ms(delay)
                #######################
        finally:
            if self.queue.get(id) != None:
                del self.queue[id]
            self.current_show = None

    def scroll(self, val, color=Red, delay=200, wait=True):
        if self.current_show == val:
            return
        
        id = self.__get_id()
        if id == -1:
            return

        self.current_show = val

        if wait:
            self.__scroll(val, color, delay, id)
        else:
            if len(str(val)) < 2:
                self.__scroll(val, color, delay, id)
            else:
                _thread.start_new_thread(self.__scroll, (val, color, delay, id))
    
    def show(self, images, delay=500, color=None):
        if self.current_show == images:
            return
        else:
            self.current_show = images
        
        id = self.__get_id()
        if id == -1:
            return

        if color != None:
            color = self.__convert_color(color)
        if isinstance(images, str):
            images = Image(images)

        if isinstance(images, Image):
            self.__show(images, color, id) # single image
        elif isinstance(images, list) and (isinstance(images[0], Image) or isinstance(images[0], list)):
            # list of images
            for i in images:
                if self.queue[id]:
                    break
                self.__show(i, color, id)
                sleep_ms(delay)
        elif isinstance(images, list) and (isinstance(images[0], int)):
            # image is an array
            self.__show(images, color, id)
            sleep_ms(delay)

        if self.queue.get(id) != None:
            del self.queue[id]
        self.current_show = None

    def show_graph(self, value=0, max=0, color=Red):
        id = self.__get_id()
        if id == -1:
            return

        if max == 0:
            max = 100
        if value > max:
            value = max

        leds = int((value*25)/max) # convert % to no of leds / 25 leds
        rows = int(leds/5)
        cols = int(leds%5)

        self.clear()

        color = self.__convert_color(color)

        for r in range(rows):
            for c in range(5):
                if self.queue[id]:
                    break
                self.Led.LoadXY(c, 4-r, color)
        order = [2, 1, 3, 0, 4]
        for c in range(cols):
            if self.queue[id]:
                break
            self.Led.LoadXY(order[c], 4-rows, color)

        self.Led.Show()
        if self.queue.get(id) != None:
            del self.queue[id]
        self.current_show = None

    def set_pixel(self, x=0, y=0, color=Red):
        new_color = self.__convert_color(color)
        self.Led.LoadXY(x, y, new_color)
        self.Led.Show()

    def clear_pixel(self, x=0, y=0):
        self.Led.LoadXY(x, y, Black)
        self.Led.Show()

    def set_all(self, color):
        color = self.__convert_color(color)
        self.Led.fill(color)
        self.Led.Show()

    def set_brightness(self, brightness):
        if brightness < 0:
            brightness = 0
        if brightness > 100:
            brightness = 100

        self.brightness = brightness
        #TODO: update led with new brightness

    def clear(self):
        self.Led.fill((0, 0, 0))
        self.Led.Show()
        self.current_show = None

