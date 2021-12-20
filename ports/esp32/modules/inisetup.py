import uos
from flashbdev import bdev


def check_bootsec():
    buf = bytearray(bdev.ioctl(5, 0))  # 5 is SEC_SIZE
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time

    while 1:
        print(
            """\
The filesystem appears to be corrupted. If you had important data there, you
may want to make a flash snapshot to try to recover it. Otherwise, perform
factory reprogramming of MicroPython firmware (completely erase flash, followed
by firmware programming).
"""
        )
        time.sleep(3)


def setup():
    check_bootsec()
    print("Performing initial setup")
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, "/")
    with open("boot.py", "w") as f:
        f.write(
            """\
# This file is executed on every boot (including wake-boot from deepsleep)
import machine, esp, gc, time, os
from led import led_onboard
from _thread import start_new_thread

esp.osdebug(None)
machine.freq(240000000)

led_onboard.show(0, (0, 0, 0))

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
        print('Remove main.py...')
        try:
            os.remove('main.py')
        except OSError:  # remove failed
            pass

        try:
            os.stat('main.py')
            print('...failed.')
        except OSError:  # stat failed
            print('...OK.')
        
        print('Reset now...')
        machine.reset()

def blink_status_led():
    global stop_blink_thread
    status_led_on = 1
    while True:
        if status_led_on:
            led_onboard.show(0, (255, 0, 0))
        else:
            led_onboard.show(0, (0, 0, 0))
        status_led_on = 1 - status_led_on
        time.sleep_ms(100)
        if stop_blink_thread:
            led_onboard.show(0, (255, 0, 0))
            return

stop_blink_thread = False
start_new_thread(blink_status_led, ())

from global_objects import *

robot.stop_all()
ble.start()

stop_blink_thread = True
speaker.play(POWER_UP, wait=False)

__main_exists = False

try:
    os.stat('main.py')
    print('User program exists. No need to run default program')
    __main_exists = True
except OSError:  # stat failed
    pass

print('xBot firmware version:', VERSION)
print('Ready to connect')
motion.calibrateZ()
gc.collect()

if not __main_exists:
    # run default code
    from ir_receiver import *

    KEY_NONE = const(0)
    KEY_UP = const(1)
    KEY_DOWN = const(2)
    KEY_LEFT = const(3)
    KEY_RIGHT = const(4)

    KEY_S1_CLOSE = const(20)
    KEY_S1_OPEN = const(21)

    mode = ROBOT_MODE_DO_NOTHING
    mode_changed = False
    current_speed = 80
    key = KEY_NONE
    ble_connected = False

    def button_callback():
        global mode, mode_changed
        if mode == ROBOT_MODE_DO_NOTHING:
            mode = ROBOT_MODE_AVOID_OBS
        elif mode == ROBOT_MODE_AVOID_OBS:
            mode = ROBOT_MODE_FOLLOW
        elif mode == ROBOT_MODE_FOLLOW:
            mode = ROBOT_MODE_LINE_FINDER
        elif mode == ROBOT_MODE_LINE_FINDER:
            mode = ROBOT_MODE_DO_NOTHING
        
        mode_changed = True
        time.sleep_ms(100)
        print('mode changed by button')

    btn_onboard.on_pressed = button_callback

    def ir_callback(cmd, addr, ext):
        global mode, mode_changed, current_speed, key
        if cmd == IR_REMOTE_A:
            mode = ROBOT_MODE_DO_NOTHING
            mode_changed = True
        elif cmd == IR_REMOTE_B:
            mode = ROBOT_MODE_AVOID_OBS
            mode_changed = True
        elif cmd == IR_REMOTE_C:
            mode = ROBOT_MODE_LINE_FINDER
            mode_changed = True
        elif cmd == IR_REMOTE_D:
            mode = ROBOT_MODE_FOLLOW
            mode_changed = True
        elif cmd == IR_REMOTE_E:
            key = KEY_S1_CLOSE
        elif cmd == IR_REMOTE_F:
            key = KEY_S1_OPEN
        elif cmd == IR_REMOTE_UP:
            key = KEY_UP
        elif cmd == IR_REMOTE_DOWN:
            key = KEY_DOWN
        elif cmd == IR_REMOTE_LEFT:
            key = KEY_LEFT
        elif cmd == IR_REMOTE_RIGHT:
            key = KEY_RIGHT
        elif cmd == IR_REMOTE_1:
            current_speed = 20
        elif cmd == IR_REMOTE_2:
            current_speed = 25
        elif cmd == IR_REMOTE_3:
            current_speed = 30
        elif cmd == IR_REMOTE_4:
            current_speed = 40
        elif cmd == IR_REMOTE_5:
            current_speed = 50
        elif cmd == IR_REMOTE_6:
            current_speed = 60
        elif cmd == IR_REMOTE_7:
            current_speed = 70
        elif cmd == IR_REMOTE_8:
            current_speed = 80
        elif cmd == IR_REMOTE_9:
            current_speed = 100

        if mode_changed:
            print('mode changed by IR remote')

    ir_rx.on_received(ir_callback)

    def on_ble_connected_callback():
        global ble_connected
        ble_connected = True

    ble.on_connected(on_ble_connected_callback)

    def on_ble_disconnected_callback():
        global ble_connected, current_speed
        ble_connected = False
        current_speed = 80

    ble.on_disconnected(on_ble_disconnected_callback)


    def on_ble_message_name_value_receive_callback(name, value):
        global current_speed, key, ble_key_received

        if name == 'F':
            robot.forward(value)
        elif name == 'B':
            robot.backward(value)
        elif name == 'L':
            robot.turn_left(value/1.5)
        elif name == 'R':
            robot.turn_right(value/1.5)
        if name == 'FL':
            robot.move(4, value/1.5)
        elif name == 'BL':
            robot.move(6, value/1.5)
        elif name == 'FR':
            robot.move(2, value/1.5)
        elif name == 'BR':
            robot.move(8, value/1.5)
        elif name == 'S':
            current_speed = 80
            robot.stop()
        elif name in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8']:
            index = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8'].index(name)
            servo.position(index, value)

    ble.on_receive_msg("name_value", on_ble_message_name_value_receive_callback)

    try:
        while True :
            if mode_changed:
                if mode == ROBOT_MODE_DO_NOTHING:
                    led_onboard.show(0, LED_COLOR_DO_NOTHING)
                    key = KEY_NONE
                elif mode == ROBOT_MODE_AVOID_OBS:
                    led_onboard.show(0, LED_COLOR_AVOID_OBS)
                elif mode == ROBOT_MODE_FOLLOW:
                    led_onboard.show(0, LED_COLOR_FOLLOW)
                elif mode == ROBOT_MODE_LINE_FINDER:
                    led_onboard.show(0, LED_COLOR_LINE_FINDER)
                mode_changed = False

            if mode == ROBOT_MODE_DO_NOTHING:
                if not ble_connected:
                    if key != KEY_NONE:
                        if key == KEY_UP:
                            robot.forward(current_speed)
                        elif key == KEY_DOWN:
                            robot.backward(current_speed)
                        elif key == KEY_LEFT:
                            robot.turn_left(current_speed/1.5)
                        elif key == KEY_RIGHT:
                            robot.turn_right(current_speed/1.5)
                        elif key == KEY_S1_CLOSE:
                            servo.rotate(0, -1, 5, servo.position(0)-5)
                        elif key == KEY_S1_OPEN:
                            servo.rotate(0, 1, 5, servo.position(0)+5)

                        key = KEY_NONE
                    else:
                        robot.stop()

                    time.sleep_ms(100)

            elif mode == ROBOT_MODE_AVOID_OBS:
                robot.run_mode_obs(False)

            elif mode == ROBOT_MODE_FOLLOW:
                robot.run_mode_follow(False)

            elif mode == ROBOT_MODE_LINE_FINDER:
                robot.run_mode_linefinder(False)
                
    except KeyboardInterrupt:
        print('Default mode stopped by app')
    finally:
        robot.stop()
        btn_onboard.on_pressed = None
        ir_rx.on_received(None)
        ir_rx.stop()
        ble.on_receive_msg("name_value", None)
        ble.on_connected(None)
        ble.on_disconnected(None)
        del mode, mode_changed, current_speed, ble_connected, key, on_ble_message_name_value_receive_callback, on_ble_connected_callback, on_ble_disconnected_callback, button_callback
        gc.collect()
"""
        )
    return vfs
