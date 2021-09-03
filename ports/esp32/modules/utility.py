import machine
import time
from setting import *

i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21))

def say(message) :
    message = ROBOT_MESSAGE_SIGN + str(message) + ROBOT_MESSAGE_SIGN
    print(message)


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def translate(value, left_min, left_max, right_min, right_max):
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min
    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)
    # Convert the 0-1 range into a value in the right range.
    return round(right_min + value_scaled * right_span)


# wait for a condition, which is a function that trigger the event to check
# Ex: wait_for(lambda: ultrasonic.distance_cm(1) < 10)
# or wait_for(lambda: btn_onboard.is_pressed())
def wait_for(condition):
    while not condition():
        time.sleep_ms(50)
    return

class TimerCounter:
    def __init__(self):
        self.timer_begin = 0

    def reset(self):
        self.timer_begin = time.ticks_ms()

    def get(self):
        return time.ticks_diff(time.ticks_ms(), self.timer_begin)

timer = TimerCounter()