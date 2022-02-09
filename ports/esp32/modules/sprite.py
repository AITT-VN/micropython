import esp
from micropython import const

from yolobit import *

GAME_FPMS = 50
GAME_LED_ON_BLINK_DELAY = 200

GAME_STATUS_START = const(0)
GAME_STATUS_RUNNING = const(1)
GAME_STATUS_PAUSED = const(2)
GAME_STATUS_OVER = const(3)
GAME_STATUS_END = const(4)

GAME_RESULT_NONE = const(0)
GAME_RESULT_FAILED = const(1)
GAME_RESULT_WIN = const(2)

GAME_DIR_RIGHT = const(1)
GAME_DIR_TOP_RIGHT = const(2)
GAME_DIR_TOP = const(3)
GAME_DIR_TOP_LEFT = const(4)
GAME_DIR_LEFT = const(5)
GAME_DIR_BOTTOM_LEFT = const(6)
GAME_DIR_BOTTOM = const(7)
GAME_DIR_BOTTOM_RIGHT = const(8)

GAME_EDGE_LEFT = const(0)
GAME_EDGE_TOP = const(1)
GAME_EDGE_RIGHT = const(2)
GAME_EDGE_BOTTOM = const(3)

GAME_SCREEN_COLS = 5
GAME_SCREEN_ROWS = 5

COLOR_RED = [255, 0, 0]
COLOR_BLACK = [0, 0, 0]
COLOR_BLUE = [0, 0, 255]
COLOR_PURPLE = [128, 0, 128]

def screen_scroll(val, color=COLOR_BLUE, delay=200):
    display.scroll(val, color, delay)

def screen_show(image, color=COLOR_RED, brightness=100):
    display.set_brightness(brightness)

    display.show(image, 0, color)

def screen_clear():
    display.clear()

def screen_set_pixel(x, y, color=COLOR_RED, brightness=100):
    display.set_brightness(brightness)

    display.set_pixel(x, y, color)

def screen_clear_pixel(x, y):
    display.clear_pixel(x, y)

def pos_in_screen(x, y):
    return (0 <= x < GAME_SCREEN_COLS) and (0 <= y < GAME_SCREEN_ROWS)

class Sprite:
    def __init__(self, x, y, color=COLOR_RED):
        self.x = x
        self.y = y
        self.color = color
        self.dir = GAME_DIR_RIGHT
        if DEV_VERSION >= 4: # v4 and up using small led 2020
            self.brightness = 20
        else: # v3 and previous versions using big led 5050
            self.brightness = 50
        self.blink = 0
        self._stay_in_screen = False
        self._is_delete = False
    
    def move_by(self, step):
        if self.dir == GAME_DIR_RIGHT:
            self.x += step
        elif self.dir == GAME_DIR_TOP_RIGHT:
            self.x += step
            self.y -= step
        elif self.dir == GAME_DIR_TOP:
            self.y -= step
        elif self.dir == GAME_DIR_TOP_LEFT:
            self.x -= step
            self.y -= step
        elif self.dir == GAME_DIR_LEFT:
            self.x -= step
        elif self.dir == GAME_DIR_BOTTOM_LEFT:
            self.x -= step
            self.y += step
        elif self.dir == GAME_DIR_BOTTOM:
            self.y += step
        else:
            self.x += step
            self.y += step
        
        if self._stay_in_screen:
            if self.x >= GAME_SCREEN_COLS:
                self.x = GAME_SCREEN_COLS - 1
            elif self.x < 0:
                self.x = 0
            if self.y >= GAME_SCREEN_ROWS:
                self.y = GAME_SCREEN_ROWS - 1
            elif self.y < 0:
                self.y = 0

    def is_in_screen(self):
        return pos_in_screen(self.x, self.y)

    def turn(self, dir, angle):
        if dir == 0:
            self.dir += int(angle / 45)
        else:
            self.dir -= int(angle / 45)

        self.dir = (self.dir + 8) % 8
        if self.dir == 0:
            self.dir = GAME_DIR_BOTTOM_RIGHT

    #Same position
    def is_touching(self, other_sprite):
        if self.x == other_sprite.x and self.y == other_sprite.y:
            return True
        return False

    #4 sides
    def is_touching_side(self, other_sprite):
        if self.x == other_sprite.x and abs(self.y - other_sprite.y) == 1:
            return True
        if self.y == other_sprite.y and abs(self.x - other_sprite.x) == 1:
            return True
        return False

    #4 corners
    def is_touching_corner(self, other_sprite):
        if abs(self.x - other_sprite.x) == 1 and abs(self.y - other_sprite.y) == 1:
            return True
        return False

    def stay_in_screen(self, value):
        self._stay_in_screen = value

    def revert_direction(self):
        self.dir = (self.dir + 4) % 8
        if self.dir == 0:
            self.dir = GAME_DIR_BOTTOM_RIGHT

    # GAME_EDGE_LEFT: |<-- self
    # GAME_EDGE_RIGHT: self -->|
    def reflect_direction(self, edge=GAME_EDGE_LEFT):
        if edge == GAME_EDGE_LEFT:
            if self.dir == GAME_DIR_LEFT:
                self.dir += 4
            elif self.dir == GAME_DIR_TOP_LEFT:
                self.dir -= 2
            elif self.dir == GAME_DIR_BOTTOM_LEFT:
                self.dir += 2

        elif edge == GAME_EDGE_TOP:
            if self.dir == GAME_DIR_TOP:
                self.dir += 4
            elif self.dir == GAME_DIR_TOP_RIGHT:
                self.dir -= 2
            elif self.dir == GAME_DIR_TOP_LEFT:
                self.dir += 2

        elif edge == GAME_EDGE_RIGHT:
            if self.dir == GAME_DIR_RIGHT:
                self.dir += 4
            elif self.dir == GAME_DIR_BOTTOM_RIGHT:
                self.dir -= 2
            elif self.dir == GAME_DIR_TOP_RIGHT:
                self.dir += 2

        elif edge == GAME_EDGE_BOTTOM:
            if self.dir == GAME_DIR_BOTTOM:
                self.dir += 4
            elif self.dir == GAME_DIR_BOTTOM_LEFT:
                self.dir -= 2
            elif self.dir == GAME_DIR_BOTTOM_RIGHT:
                self.dir += 2
            
        self.dir = self.dir % 8
        if self.dir == 0:
            self.dir = GAME_DIR_BOTTOM_RIGHT

    #change direction when this sprite same postion with the other sprite which is moving. They were changed direction together
    def bounce_if_on_sprite(self, other_sprite):
        if not self.is_touching(other_sprite):
            return other_sprite

        if self.dir == other_sprite.dir:
            self.revert_direction()
        else:
            temp = self.dir
            self.dir = other_sprite.dir
            other_sprite.dir = temp
        return other_sprite

    #change direction when this sprite same postion with the other sprite which is stopping
    def bounce_if_on_stop_sprite(self, other_sprite):
        if not self.is_touching(other_sprite):
            return        
        self.revert_direction()

    def is_touching_edge(self):
        return self.x <= 0 or self.y <= 0 or self.x >= GAME_SCREEN_COLS - 1 or self.y >= GAME_SCREEN_ROWS - 1

    def bounce_if_on_edge(self):
        if not self.is_touching_edge():
            return
        #4 edge corners:

        #top right
        if self.x >= GAME_SCREEN_COLS - 1 and self.y <= 0 and (self.dir == GAME_DIR_TOP_RIGHT or self.dir == GAME_DIR_TOP or self.dir == GAME_DIR_RIGHT):
            self.revert_direction()
        #top left
        elif self.x <= 0 and self.y <= 0 and (self.dir == GAME_DIR_TOP_LEFT or self.dir == GAME_DIR_TOP or self.dir == GAME_DIR_LEFT):
            self.revert_direction()
        #bottom left
        elif self.x <= 0 and self.y >= GAME_SCREEN_ROWS - 1 and (self.dir == GAME_DIR_BOTTOM_LEFT or self.dir == GAME_DIR_BOTTOM or self.dir == GAME_DIR_LEFT):
            self.revert_direction()
        #bottom right
        elif self.x >= GAME_SCREEN_COLS - 1 and self.y >= GAME_SCREEN_ROWS - 1 and (self.dir == GAME_DIR_BOTTOM_RIGHT or self.dir == GAME_DIR_BOTTOM or self.dir == GAME_DIR_RIGHT):
            self.revert_direction()

        #4 edge sides:

        #right
        elif self.x >= GAME_SCREEN_COLS - 1:
            self.reflect_direction(GAME_EDGE_RIGHT)
        
        #top
        elif self.y <= 0:
            self.reflect_direction(GAME_EDGE_TOP)

        #left
        elif self.x <= 0:
            self.reflect_direction(GAME_EDGE_LEFT)
        
        #bottom
        elif self.y >= GAME_SCREEN_ROWS - 1:
            self.reflect_direction(GAME_EDGE_BOTTOM)

    def delete(self):
        self._is_delete = True

    def is_deleted(self):
        return self._is_delete
