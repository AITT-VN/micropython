import gc
import uos
from flashbdev import bdev

try:
    if bdev:
        uos.mount(bdev, "/")
except OSError:
    import inisetup

    vfs = inisetup.setup()


# This file is executed on every boot (including wake-boot from deepsleep)
import machine, esp, gc, time
from led import led_onboard
from _thread import start_new_thread

esp.osdebug(None)
machine.freq(240000000)

config_btn = machine.Pin(23, machine.Pin.IN, machine.Pin.PULL_UP)

if config_btn.value() == 0:
    print('config button is pressed')
    # start while loop until btn is released
    press_begin = time.ticks_ms()
    press_duration = 0
    while config_btn.value() == 0:
        press_end = time.ticks_ms()
        press_duration = time.ticks_diff(press_end, press_begin)
        print(press_duration)
        if press_duration > 2000: # button pressed more than 2s
            break
        time.sleep_ms(100)

    # check how long it was pressed
    if press_duration > 2000:    
        # if more than 2 seconds => reset main.py
        for _ in range(3):
            led_onboard.show(0, (255, 0, 0))
            time.sleep_ms(50)
            led_onboard.show(0, (0, 0, 0))
            time.sleep_ms(50)

        print('Config button pressed longer than 2 seconds')
        print('Copying file main_backup.py to main.py...')
        file = open('main_backup.py','r')
        content = file.read()
        file.close()

        file = open("main.py","w")
        if file.write(content) == len(content):
            print('...Done')
        file.close()        
        print('Reset now...')
        machine.reset()

def blink_status_led():
    global stop_blink_thread
    status_led_on = 1
    while True:
        if status_led_on:
            led_onboard.show(0, (255, 69, 0))
        else:
            led_onboard.show(0, (0, 0, 0))
        status_led_on = 1 - status_led_on
        time.sleep_ms(50)
        if stop_blink_thread:
            led_onboard.show(0, (255, 0, 0))
            return

stop_blink_thread = False
start_new_thread(blink_status_led, ())

from global_objects import *
from ble import *
from robot import robot
from speaker import *

robot.stop_all()
ble.start()

stop_blink_thread = True
speaker.play(POWER_UP, wait=False)
print('xBot firmware version:', VERSION)
print('Ready to connect')
gc.collect()