import machine
import binascii
from micropython import const

CHIP_ID = binascii.hexlify(machine.unique_id()).decode('ascii')
PRODUCT_NAME = 'xbot-' + CHIP_ID[-4:]

VERSION = '0.9'

#DEBUG_MODE = True
DEBUG_MODE = False

PORTS_DIGITAL = [(18, 19), (4, 5), (13, 14), (16, 17), (32, 33), (25, 26)]
PORTS_ADC = [(-1, -1), (-1, -1), (-1, -1), (39, 36), (32, 33), (34, 35)]

# timeout for programming mode
PROGRAMMING_MODE_TIMEOUT = const(10000)

CMD_CTRL_D = const(0x04)
CMD_SYS_PREFIX = const(0x11)
CMD_PROG_START_PREFIX = const(0x12)
CMD_PROG_END_PREFIX = const(0x13)

# version command 
CMD_VERSION = const(0x00)

# running commands
CMD_STOP = const(0x01)
CMD_RUN_F = const(0x02) # move forward
CMD_RUN_B = const(0x03) # move backward
CMD_RUN_L = const(0x04) # turn left forward
CMD_RUN_R = const(0x05) # turn right forward
CMD_RUN_LB = const(0x06) # turn left backward
CMD_RUN_RB = const(0x07) # turn right backward
CMD_DRIVE = const(0x10) # move by direction

# dc motor & servo command
CMD_MOTOR_SPEED = const(0x20) # set speed of motor
CMD_SERVO_POS = const(0x25) # set servo position
CMD_ROBOT_SPEED = const(0x2A) # set robot default speed

# speaker commands
CMD_SPEAKER_BEEP = const(0x30) # play beep sound

CMD_SPEAKER_TONE = const(0x36) # play a tone

# led commands
CMD_LED_COLOR = const(0x40) # change led color

# module commands
CMD_ULTRASONIC_SENSOR = const(0x60)
CMD_LINE_SENSOR = const(0x66)


LED_COLOR_IDLE = (255, 0, 0)
LED_COLOR_BT_CONNECTED = (0, 0, 255)

LED_COLOR_DO_NOTHING = (255, 0, 0)
LED_COLOR_AVOID_OBS = (0, 255, 0)
LED_COLOR_FOLLOW = (0, 0, 255)
LED_COLOR_LINE_FINDER = (255, 255, 255)

ROBOT_MODE_DO_NOTHING = const(0)
ROBOT_MODE_MOTOR_STOP = const(1)
ROBOT_MODE_DANCING = const(2)
ROBOT_MODE_AVOID_OBS = const(3)
ROBOT_MODE_FOLLOW = const(4)
ROBOT_MODE_LINE_FINDER = const(5)

ROBOT_SIGN_MESSAGE = '\x09'