from machine import Timer
import time
from sprite import *

class Game:
    def __init__(self):
        self._timer = None
        self.reset()

    def reset(self):
        self._sprites = []
        self._screen_state = [[[0, 0, 0, 0]] * GAME_SCREEN_ROWS for i in range(GAME_SCREEN_COLS)]
        self._status = GAME_STATUS_RUNNING
        self._result = GAME_RESULT_NONE
        self.life = 0
        self.score = 0
        self._tick = 0
        self._countdown_ms = 0
        self._is_countdown = False
        screen_clear()
        if self._timer == None:     
            self._timer = Timer(1)
            self._timer.init(period=GAME_FPMS, mode=Timer.PERIODIC, callback=self._render)
    

    def restart(self):
        self._screen_state = [[[0, 0, 0, 0]] * GAME_SCREEN_ROWS for i in range(GAME_SCREEN_COLS)]
        self._status = GAME_STATUS_RUNNING
        self._result = GAME_RESULT_NONE
        self.life = 0
        self.score = 0
        self._tick = 0
        self._countdown_ms = 0
        self._is_countdown = False
        screen_clear()

    def create_sprite(self, x, y, color=COLOR_RED):
        self._sprites.append(Sprite(x, y, color))
        return self._sprites[-1]

    def start_countdown(self, ms):
        self._countdown_ms = ms
        self._is_countdown = True
    
    def is_time_up(self):
        if self._is_countdown and self._countdown_ms <= 0:
            return True
        return False
        
    def is_over(self):
        return self._status == GAME_STATUS_OVER

    def is_paused(self):
        return self._status == GAME_STATUS_PAUSED

    def is_running(self):
        return self._status == GAME_STATUS_RUNNING

    def is_failed(self):
        return self._result == GAME_RESULT_FAILED

    def is_won(self):
        return self._result == GAME_RESULT_WIN

    def fail(self):
        self._result = GAME_RESULT_FAILED

    def pass_fail(self):
        self._result = GAME_RESULT_NONE

    def win(self):
        self._status = GAME_STATUS_END
        self._result = GAME_RESULT_WIN
        
        t_delay = 150
        full = [0] * (GAME_SCREEN_COLS * GAME_SCREEN_ROWS)        
        screen_clear()
        time.sleep_ms(t_delay)

        d = min(GAME_SCREEN_COLS, GAME_SCREEN_ROWS)
        d2 = int(d/2)
        x = int(GAME_SCREEN_COLS / 2)
        y = int(GAME_SCREEN_ROWS / 2)
        for i in range((d2 + 1) * 2 - d, d + 1, 2):
            xx = x - (i-1)
            yy = y - (i-1)
            x1 = x
            y1 = y
            xx1 = xx
            yy1 = yy

            for j in range(i):
                y1 = y - j
                yy1 = yy + j
                full[x1 * GAME_SCREEN_ROWS + y1] = 1
                full[xx1 * GAME_SCREEN_ROWS + yy1] = 1
                screen_show(full, COLOR_PURPLE)
                time.sleep_ms(t_delay)
            for j in range(1, i-1, 1):                
                x1 = x - j
                xx1 = xx + j
                full[x1 * GAME_SCREEN_ROWS + y1] = 1
                full[xx1 * GAME_SCREEN_ROWS + yy1] = 1
                screen_show(full, COLOR_PURPLE)
                time.sleep_ms(t_delay)
            x += 1
            y += 1
        screen_scroll("WIN-WIN-WIN")

    def game_over(self):
        self._status = GAME_STATUS_OVER
        self._result = GAME_RESULT_FAILED

        t_delay = 150
        full = [1] * (GAME_SCREEN_COLS * GAME_SCREEN_ROWS)
        for i in range(3):
            screen_show(full)
            time.sleep_ms(t_delay)
            screen_clear()
            time.sleep_ms(t_delay)
        screen_show(full)
        d = min(GAME_SCREEN_COLS, GAME_SCREEN_ROWS)
        d2 = int(d/2)
        x = int(GAME_SCREEN_COLS / 2)
        y = int(GAME_SCREEN_ROWS / 2)
        for i in range((d2 + 1) * 2 - d, d + 1, 2):
            xx = x - (i-1)
            yy = y - (i-1)
            x1 = x
            y1 = y
            xx1 = xx
            yy1 = yy

            for j in range(i):
                y1 = y - j
                yy1 = yy + j
                full[x1 * GAME_SCREEN_ROWS + y1] = 0
                full[xx1 * GAME_SCREEN_ROWS + yy1] = 0
                screen_show(full)
                time.sleep_ms(t_delay)
            for j in range(1, i-1, 1):                
                x1 = x - j
                xx1 = xx + j
                full[x1 * GAME_SCREEN_ROWS + y1] = 0
                full[xx1 * GAME_SCREEN_ROWS + yy1] = 0
                screen_show(full)
                time.sleep_ms(t_delay)
            x += 1
            y += 1
        screen_scroll("GAMEOVER-GAMEOVER-GAMEOVER")

    def pause(self):
        self._status = GAME_STATUS_PAUSED

    def resume(self):
        self._status = GAME_STATUS_RUNNING

    def stop(self):
        self._status = GAME_STATUS_END
        screen_clear()
        self._sprites.clear()
        if self._timer != None:
            self._timer.deinit()
            self._timer = None
        
    def _render(self, id):
        if self._status != GAME_STATUS_RUNNING:
            return

        if self._is_countdown and self._countdown_ms > 0:
            self._countdown_ms -= GAME_FPMS
        i = 0
        while i < len(self._sprites):
            if self._sprites[i].is_deleted():
                self._sprites.pop(i)
            else:
                i += 1

        new_screen = [[[0, 0, 0, 0]] * GAME_SCREEN_ROWS for i in range(GAME_SCREEN_COLS)]
        if len(self._sprites) > 0:
            for sprite in self._sprites:
                if pos_in_screen(sprite.x, sprite.y) and sprite.color != COLOR_BLACK and sprite.brightness > 0 :
                    #top priority for non-blink
                    if new_screen[sprite.x][sprite.y][0] == 0 or sprite.blink < new_screen[sprite.x][sprite.y][1]:
                        new_screen[sprite.x][sprite.y] = [1, sprite.blink, sprite.color, sprite.brightness]

        for x in range(GAME_SCREEN_COLS):
            for y in range(GAME_SCREEN_ROWS):
                if self._screen_state[x][y] != new_screen[x][y] or new_screen[x][y][1] > 0:
                    if new_screen[x][y][0] == 0:
                        screen_clear_pixel(x, y)
                    else:
                        if new_screen[x][y][1] > 0:          
                            blink_ms = int(new_screen[x][y][1] / GAME_FPMS) * GAME_FPMS
                            if blink_ms == 0:
                                blink_ms = GAME_FPMS

                            if self._tick % (blink_ms + GAME_LED_ON_BLINK_DELAY) == 0:
                                screen_set_pixel(x, y, new_screen[x][y][2], new_screen[x][y][3])
                                
                            elif (self._tick + blink_ms) % (blink_ms + GAME_LED_ON_BLINK_DELAY) == 0:
                                screen_clear_pixel(x, y)

                        else:
                            screen_set_pixel(x, y, new_screen[x][y][2], new_screen[x][y][3])
                            
        self._screen_state = new_screen
        self._tick += GAME_FPMS

game = Game()