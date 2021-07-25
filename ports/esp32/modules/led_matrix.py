import time
import tm1640
import machine
from setting import *
from utility import *

class Image:
    HEART = [0x00,0x00,0x00,0x0c,0x1e,0x3e,0x7e,0xfc, 0xfc,0x7e,0x3e,0x1e,0x0c,0x00,0x00,0x00]
    SMILE = [0x00,0x00,0x00,0x3c,0x42,0x91,0xa5,0xa1, 0xa1,0xa5,0x91,0x42,0x3c,0x00,0x00,0x00]
    SAD = [0x00,0x00,0x00,0x3c,0x42,0x81,0xa5,0x91, 0x91,0xa5,0x81,0x42,0x3c,0x00,0x00,0x00]
    CONFUSED = [0x00,0x00,0x00,0x3c,0x42,0x91,0xa5,0x91, 0x91,0xa5,0x91,0x42,0x3c,0x00,0x00,0x00]
    ARROW_N = [0x00,0x00,0x00,0x00,0x08,0x0c,0x06,0xff, 0xff,0x06,0x0c,0x08,0x00,0x00,0x00,0x00]
    ARROW_E = [0x00,0x00,0x00,0x00,0x18,0x18,0x18,0x18, 0xdb,0x7e,0x3c,0x18,0x00,0x00,0x00,0x00]
    ARROW_S = [0x00,0x00,0x00,0x00,0x10,0x30,0x60,0xff, 0xff,0x60,0x30,0x10,0x00,0x00,0x00,0x00]
    ARROW_W = [0x00,0x00,0x00,0x00,0x18,0x3c,0x7e,0xdb, 0x18,0x18,0x18,0x18,0x00,0x00,0x00,0x00]
    TRIANGLE = [0x80,0xc0,0xe0,0xf0,0xf8,0xfc,0xfe,0xff, 0xff,0xfe,0xfc,0xf8,0xf0,0xe0,0xc0,0x80]
    SQUARE = [0x00,0x00,0x00,0x00,0xff,0xff,0xff,0xff, 0xff,0xff,0xff,0xff,0x00,0x00,0x00,0x00]

    CHAR = {
        'a': [0x00,0x00,0x30,0x4a,0x4a,0x3c,0x40,0x00], 
        'b': [0x00,0x00,0x7e,0x48,0x48,0x30,0x00,0x00], 
        'c': [0x00,0x00,0x38,0x44,0x44,0x44,0x00,0x00], 
        'd': [0x00,0x00,0x30,0x48,0x48,0x7e,0x00,0x00], 
        'e': [0x00,0x00,0x3c,0x4a,0x4a,0x4c,0x00,0x00], 
        'f': [0x00,0x00,0x08,0x7c,0x0a,0x0a,0x00,0x00], 
        'g': [0x00,0x00,0x4c,0x52,0x52,0x3e,0x00,0x00], 
        'h': [0x00,0x00,0x7e,0x08,0x08,0x70,0x00,0x00], 
        'i': [0x00,0x00,0x00,0x7a,0x00,0x00,0x00,0x00], 
        'j': [0x00,0x00,0x20,0x40,0x40,0x3e,0x00,0x00], 
        'k': [0x00,0x00,0x7e,0x18,0x24,0x42,0x00,0x00], 
        'l': [0x00,0x00,0x00,0x7e,0x40,0x40,0x00,0x00], 
        'm': [0x00,0x78,0x04,0x78,0x04,0x78,0x00,0x00], 
        'n': [0x00,0x00,0x7c,0x04,0x04,0x78,0x00,0x00], 
        'o': [0x00,0x00,0x38,0x44,0x44,0x38,0x00,0x00], 
        'p': [0x00,0x00,0x7e,0x12,0x12,0x0c,0x00,0x00], 
        'q': [0x00,0x00,0x0c,0x12,0x12,0x7e,0x00,0x00], 
        'r': [0x00,0x00,0x7c,0x02,0x02,0x04,0x00,0x00], 
        's': [0x00,0x00,0x48,0x54,0x54,0x24,0x00,0x00], 
        't': [0x00,0x00,0x04,0x3e,0x44,0x40,0x00,0x00], 
        'u': [0x00,0x00,0x3c,0x40,0x40,0x7c,0x00,0x00], 
        'v': [0x00,0x00,0x1c,0x20,0x40,0x20,0x1c,0x00], 
        'w': [0x00,0x00,0x3c,0x40,0x30,0x40,0x3c,0x00], 
        'x': [0x00,0x00,0x6c,0x10,0x10,0x6c,0x00,0x00], 
        'y': [0x00,0x00,0x06,0x48,0x48,0x3e,0x00,0x00], 
        'z': [0x00,0x00,0x22,0x52,0x4a,0x46,0x00,0x00], 
        'A': [0x00,0x7c,0x7e,0x13,0x13,0x7e,0x7c,0x00], 
        'B': [0x00,0x7f,0x7f,0x49,0x49,0x7f,0x3e,0x00], 
        'C': [0x00,0x3e,0x7f,0x63,0x63,0x63,0x00,0x00], 
        'D': [0x00,0x7f,0x7f,0x41,0x63,0x3e,0x1c,0x00], 
        'E': [0x00,0x7f,0x7f,0x49,0x49,0x49,0x00,0x00], 
        'F': [0x00,0x7f,0x7f,0x09,0x09,0x09,0x09,0x00], 
        'G': [0x00,0x3e,0x7f,0x41,0x49,0x49,0x3b,0x00], 
        'H': [0x00,0x7f,0x7f,0x08,0x08,0x7f,0x7f,0x00], 
        'I': [0x00,0x00,0x41,0x7f,0x7f,0x41,0x00,0x00], 
        'J': [0x00,0x20,0x40,0x41,0x3f,0x01,0x00,0x00], 
        'K': [0x00,0x7f,0x7f,0x1c,0x36,0x63,0x41,0x00], 
        'L': [0x00,0x7f,0x7f,0x60,0x60,0x60,0x00,0x00], 
        'M': [0x00,0x7f,0x03,0x06,0x06,0x03,0x7f,0x00], 
        'N': [0x00,0x7f,0x7e,0x0c,0x18,0x3f,0x7f,0x00], 
        'O': [0x00,0x3e,0x7f,0x63,0x63,0x7f,0x3e,0x00], 
        'P': [0x00,0x7f,0x71,0x11,0x1f,0x0e,0x00,0x00], 
        'Q': [0x00,0x3e,0x41,0x41,0x51,0x21,0x5e,0x00], 
        'R': [0x00,0x7f,0x7f,0x19,0x39,0x6f,0x46,0x00], 
        'S': [0x00,0x46,0x4f,0x49,0x49,0x79,0x31,0x00], 
        'T': [0x00,0x03,0x03,0x7f,0x7f,0x03,0x03,0x00], 
        'U': [0x00,0x3f,0x7f,0x60,0x60,0x7f,0x3f,0x00], 
        'V': [0x00,0x1f,0x3f,0x60,0x60,0x3f,0x1f,0x00], 
        'W': [0x00,0x3f,0x60,0x10,0x10,0x60,0x3f,0x00], 
        'X': [0x00,0x63,0x36,0x1c,0x1c,0x36,0x63,0x00], 
        'Y': [0x00,0x07,0x0c,0x78,0x78,0x0c,0x07,0x00], 
        'Z': [0x00,0x63,0x73,0x7b,0x6f,0x67,0x63,0x00], 
        '0': [0x00,0x3e,0x63,0x41,0x41,0x63,0x3e,0x00],
        '1': [0x00,0x40,0x42,0x7f,0x7f,0x40,0x40,0x00],
        '2': [0x00,0x62,0x73,0x59,0x49,0x6f,0x66,0x00],
        '3': [0x00,0x22,0x63,0x49,0x49,0x7f,0x36,0x00],
        '4': [0x18,0x1c,0x16,0x53,0x7f,0x7f,0x50,0x00],
        '5': [0x00,0x27,0x67,0x45,0x45,0x7d,0x39,0x00], 
        '6': [0x00,0x3c,0x7e,0x4b,0x49,0x79,0x30,0x00],
        '7': [0x00,0x03,0x03,0x71,0x79,0x0f,0x07,0x00],
        '8': [0x00,0x36,0x7f,0x49,0x49,0x7f,0x36,0x00],
        '9': [0x00,0x06,0x4f,0x49,0x69,0x3f,0x1e,0x00],
        '.': [0x00,0x00,0x00,0x60,0x60,0x00,0x00,0x00],
        '+': [0x00,0x10,0x10,0x7c,0x10,0x10,0x00,0x00],
        '-': [0x00,0x00,0x10,0x10,0x10,0x10,0x00,0x00],
        '*': [0x00,0x2a,0x1c,0x3e,0x1c,0x2a,0x00,0x00],
        '/': [0x00,0x40,0x20,0x10,0x08,0x04,0x02,0x00],
        ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
        '!': [0x00,0x00,0x00,0x5e,0x00,0x00,0x00,0x00],
        '@': [0x00,0x3e,0x41,0x4d,0x55,0x51,0x5f,0x00],
        '#': [0x14,0x14,0x7f,0x14,0x7f,0x14,0x14,0x00],
        '$': [0x00,0x24,0x2a,0x7f,0x2a,0x12,0x00,0x00],
        '%': [0x00,0x46,0x26,0x10,0x08,0x64,0x62,0x00],
        '^': [0x00,0x00,0x08,0x04,0x02,0x04,0x08,0x00],
        '&': [0x00,0x36,0x49,0x49,0x36,0x20,0x50,0x00],
        '(': [0x00,0x00,0x00,0x3e,0x41,0x00,0x00,0x00],
        ')': [0x00,0x00,0x00,0x41,0x3e,0x00,0x00,0x00],
        '_': [0x00,0x40,0x40,0x40,0x40,0x40,0x40,0x00],
        '=': [0x00,0x00,0x50,0x50,0x50,0x50,0x00,0x00],
        '|': [0x00,0x00,0x00,0x7f,0x00,0x00,0x00,0x00],
        '[': [0x00,0x00,0x7f,0x41,0x41,0x00,0x00,0x00],
        ']': [0x00,0x00,0x00,0x41,0x41,0x7f,0x00,0x00],
        '{': [0x00,0x00,0x08,0x36,0x41,0x00,0x00,0x00],
        '}': [0x00,0x00,0x00,0x41,0x36,0x08,0x00,0x00],
        ':': [0x00,0x00,0x00,0x66,0x66,0x00,0x00,0x00],
        ';': [0x00,0x00,0x00,0x56,0x26,0x00,0x00,0x00],
        ',': [0x00,0x00,0x00,0x48,0x30,0x00,0x00,0x00],
        '<': [0x00,0x00,0x10,0x28,0x44,0x00,0x00,0x00],
        '>': [0x00,0x00,0x00,0x44,0x28,0x10,0x00,0x00], 
        '?': [0x00,0x00,0x02,0xb1,0x09,0x06,0x00,0x00],
        '~': [0x00,0x30,0x08,0x08,0x10,0x20,0x20,0x18],
        '`': [0x00,0x00,0x02,0x04,0x08,0x00,0x00,0x00],
    }

    FULL = [0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff]
    NONE = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
    PADDING = [0x00,0x00,0x00,0x00]

class LedMatrix:
    def __init__(self, port):
        self._reset_port(port)
        self.list_dis_num = []
        self.list_scroll = []
        self.list_scroll_temp = []
        self.list_show = []

    def _reset_port(self, port):
        self.port = port
        # Grove port: GND VCC S2 (CLK) S1 (DIN)
        dio_pin = machine.Pin(PORTS_DIGITAL[port][0])
        clk_pin = machine.Pin(PORTS_DIGITAL[port][1])
        self.tm1640 = tm1640.TM1640(clk=clk_pin, dio=dio_pin)
    
    def _check_port(self, port):
        if port != self.port:
            self._reset_port(port)

    def _scroll_image(self, image, dir=0, delay=100):
        self.list_scroll.extend(image)
        self.list_scroll_temp.extend(image)
        
        if dir == 0:
            #scroll right to left
            for i in range(8):
                self.list_scroll.pop(0)
                self.list_scroll.append(Image.PADDING[0])
                self.tm1640.write(self.list_scroll)
                time.sleep_ms(delay)
            
            for i in range(16):
                temp = self.list_scroll_temp[i]
                self.list_scroll.pop(0)
                self.list_scroll.append(temp)
                self.tm1640.write(self.list_scroll)
                time.sleep_ms(delay)
        else:
            #scroll left to right 
            for i in range(16):
                temp = Image.PADDING[0]
                self.list_scroll.pop()
                self.list_scroll.insert(0, temp)
                self.tm1640.write(self.list_scroll)
                time.sleep_ms(delay)
            for i in range(15, -1, -1):
                temp = self.list_scroll_temp[i]
                self.list_scroll.pop()
                self.list_scroll.insert(0, temp)
                self.tm1640.write(self.list_scroll)
                time.sleep_ms(delay)
        self.list_scroll.clear()
        self.list_scroll_temp.clear()
    
    def _check_len(self, port, input):
        if len(input) > 2:
            self.scroll(port, input, 0, 100)
        else:
            if len(input) == 1:
                self.list_show.extend(Image.PADDING)
                self.list_show.extend(Image.CHAR[input])
                self.list_show.extend(Image.PADDING)
                self.tm1640.write(self.list_show)
                self.list_show.clear()
            else:
                for data in input:
                    self.list_show.extend(Image.CHAR[data])
                self.tm1640.write(self.list_show)
                self.list_show.clear()

    def scroll(self, port, input, dir = 0, delay = 100):
        # check port 
        self._check_port(port)

        if type(input) is list:
            self._scroll_image(input, dir, delay)
        else:
            output = str(input)  
            self.list_scroll.extend(Image.NONE)         
            for data in output:
                self.list_scroll.extend(Image.CHAR[data])
            
            self.list_scroll.extend(Image.NONE)
            len_str =  len(output)
            count = len_str*8 + 18 
            self.list_scroll_temp.clear()
            if dir == 0:
                while count > 0:
                    count = count - 1               
                    self.list_scroll_temp.extend(self.list_scroll[0:16])
                    self.list_scroll.pop(0)
                    self.list_scroll.append(Image.PADDING[0])
                    self.tm1640.write(self.list_scroll_temp)
                    self.list_scroll_temp.clear()
                    time.sleep_ms(delay)
            else:
                while count > 0:
                    count = count - 1
                    self.list_scroll_temp.extend(self.list_scroll[(len_str*8 + 16):(len_str*8 + 32)])
                    self.list_scroll.pop()
                    self.list_scroll.insert(0, Image.PADDING[0])
                    self.tm1640.write(self.list_scroll_temp)
                    self.list_scroll_temp.clear()
                    time.sleep_ms(delay)

            self.list_scroll.clear()

    def show(self, port, input):
        #check port
        self._check_port(port)

        if type(input) is list:
            self.tm1640.write(input)
        else:
            output = str(input)
            self._check_len(port, output)

    def clear(self, port):
        #check port
        self._check_port(port)
        self.tm1640.write(Image.NONE)

led_matrix = LedMatrix(2)