import machine
import binascii
from micropython import const
import ujson, gc

CHIP_ID = binascii.hexlify(machine.unique_id()).decode('ascii')
PREFIX_NAME = 'ohstem-'
PRODUCT_TYPE = 'yolobit'
PRODUCT_NAME = PREFIX_NAME + PRODUCT_TYPE + '-' + CHIP_ID[-4:]
VERSION = '1.11'

if gc.mem_free() > 1000000:
    DEV_VERSION = 4 # Yolo:Bit version 4 and newer has 4MB RAM
else:
    DEV_VERSION = 3

# timeout for programming mode
PROGRAMMING_MODE_TIMEOUT = const(10000)

CMD_CTRL_D = const(0x04)
CMD_SYS_PREFIX = const(0x11)
CMD_PROG_START_PREFIX = const(0x12)
CMD_PROG_END_PREFIX = const(0x13)

CMD_USR_MSG_PREFIX = const(0x15) # for user message sent via BLE

# version command 
CMD_FIRMWARE_INFO = const(0x00)

ROBOT_DATA_RECV_SIGN = '\x06' # data sign for app receives infor from device (only using for system)

BTN_A_PIN = const(35)
BTN_B_PIN = const(14)
RGB_LED_PIN = const(4)

device_config = {}

# load config file
try:
    f = open('config.json', 'r')
    device_config = ujson.loads(f.read())
    f.close()
except Exception:
    print('Failed to load config file')

# if error found or missing information => start config mode
if device_config.get('device_name', False):
    print('Finish loading config file')
    PRODUCT_NAME = PREFIX_NAME + device_config['device_name']
    # chars limit for start ble name is 22
    PRODUCT_NAME = PRODUCT_NAME[0:22]

def save_config():
    global device_config
    print('Save config file...')
    print(device_config)
    f = open('config.json', 'w')
    f.write(ujson.dumps(device_config))
    f.close()
    print('..done')

def get_device_name():
    return PRODUCT_NAME

def get_device_serial():
    return CHIP_ID