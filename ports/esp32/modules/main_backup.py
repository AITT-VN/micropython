from setting import *
from button import btn_onboard
from led import led_onboard
from ir_receiver import *
from robot import robot

mode = ROBOT_MODE_DO_NOTHING
mode_changed = False

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
        robot.stop()
    
    mode_changed = True
    print('mode changed by button')

btn_onboard.on_pressed = button_callback

def ir_callback(cmd, addr, ext):
    global mode, mode_changed
    if cmd == IR_REMOTE_A:
        mode = ROBOT_MODE_DO_NOTHING
        led_onboard.show(0, LED_COLOR_DO_NOTHING)
        robot.stop()
        mode_changed = True
    elif cmd == IR_REMOTE_B:
        mode = ROBOT_MODE_AVOID_OBS
        led_onboard.show(0, LED_COLOR_AVOID_OBS)
        mode_changed = True
    elif cmd == IR_REMOTE_C:
        mode = ROBOT_MODE_LINE_FINDER
        led_onboard.show(0, LED_COLOR_LINE_FINDER)
        mode_changed = True
    elif cmd == IR_REMOTE_D:
        mode = ROBOT_MODE_FOLLOW
        led_onboard.show(0, LED_COLOR_FOLLOW)
        mode_changed = True

    if mode_changed:
      print('mode changed by IR remote')

ir_rx.on_received(ir_callback)

try:
    while True :
        if mode_changed:
            robot.change_mode(mode)
            mode_changed = False

        if mode != ROBOT_MODE_DO_NOTHING:
            robot.process_mode()
            if mode != ROBOT_MODE_LINE_FINDER:
                time.sleep_ms(50)
        else:
          if ir_rx.get_code() == IR_REMOTE_UP:
              robot.forward(100)
          elif ir_rx.get_code() == IR_REMOTE_DOWN:
              robot.backward(100)
          elif ir_rx.get_code() == IR_REMOTE_LEFT:
              robot.turn_left(50)
          elif ir_rx.get_code() == IR_REMOTE_RIGHT:
              robot.turn_right(50)
          else:
              robot.stop()
          ir_rx.clear_code()
          time.sleep_ms(100)
except:
    robot.stop()
    btn_onboard.on_pressed = None
    ir_rx.on_received(None)
    ir_rx.stop()
    gc.collect()