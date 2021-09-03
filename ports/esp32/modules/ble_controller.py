''' 
Remote controller message format:

Header	Address	Length	Command	Buttons	Analog-Joystick 	Reserved  Checksum
1 Bytes	1 Byte	1 Byte	1 Byte	2 Bytes	12 Bytes	        1 Byte	  1 Byte

1.Header: 0x14
2.Address: 0x01
3.Length: 0x15 (20 bytes)
4.Command: 0x01 when something was pressed down and 0x00 when nothing was pressed down
5.Buttons: status of 14 buttons including 4 dpad + A B X Y + 4 top push buttons L1 L2 R1 R2 + SELECT START
6.Analog joystick: represent the motion of two joysticks
7.Reserved bytes: reserved for future developed functions, default "0x00"
8.Checksum: xor checking, used to check the integrality and correctness of the data

Buttons 2 bytes combined as below table (0=Unpressed, 1=Pressed):
    UP  DOWN  LEFT  RIGHT X   Y   A   B   L1  L2  R1  R2  UNUSED  UNUSED  UNUSED  UNUSED
    0   0     0     0     0   0   0   0   0   0   0   0   0       0       0       0     => 0000 0000 0000 0000 => 0x00 0x00
    1   0     0     0     0   0   0   0   0   0   0   0   0       0       0       0     => 1000 0000 0000 0000 => 0x80 0x00
    0   0     0     0     1   0   0   0   1   0   0   1   0       0       0       0     => 0000 1000 1001 0000 => 0x08 0x90

Analog joysticks 12 bytes combined as below
    byte 0 = joystick 1 x axis (-100 to 100, 0=center)
    byte 1 = joystick 1 y axis (-100 to 100, 0=center)
    byte 2 = joystick 1 calculated distance (0-100)
    byte 3&4 = joystick 1 angle (0-359)
    byte 5 = joystick 1 calculated direction (1-8)
        # calculate direction based on angle
        #         90(3)
        #   135(4) |  45(2)
        # 180(5)---+----Angle=0(direction=1)
        #   225(6) |  315(8)
        #         270(7)


    byte 6 = joystick 2 x axis (-100 to 100, 0=center)
    byte 7 = joystick 2 y axis (-100 to 100, 0=center)
    byte 8 = joystick 2 calculated distance (0-100)
    byte 9&10 = joystick 2 angle (0-359)
    byte 11 = joystick 2 calculated direction (1-8)
'''

from micropython import const
from struct import pack, unpack

# create checksum for message from bytes array
def _checksum(data):
  result = 0
  for el in data:
      result ^= el
  return result

class BLEController():
    def __init__(self):
        self._raw_state = None
        self._decoded_state = None
        self.on_received = None

    def decode(self, data):
        #self._print_raw(data)
        #print(len(data))
        if len(data) != data[2]:
            print('Invalid message length')
            return
        # check the checksum
        if data[19] != _checksum(data[0:19]):
            print('Invalid message checksum')
            return

        self._raw_state = data

        self._decoded_state = {
            'UP': data[4] >> 7,
            'DOWN': (data[4] & 0b01111111) >> 6,
            'LEFT': (data[4] & 0b00111111) >> 5,
            'RIGHT': (data[4] & 0b00011111) >> 4,
            'X': (data[4] & 0b00001111) >> 3,
            'Y': (data[4] & 0b00000111) >> 2,
            'A': (data[4] & 0b00000011) >> 1,
            'B': (data[4] & 0b00000001),
            'L1': data[5] >> 7,
            'L2': (data[5] & 0b01111111) >> 6,
            'R1': (data[5] & 0b00111111) >> 5,
            'R2': (data[5] & 0b00011111) >> 4,
            'SELECT': (data[5] & 0b00111111) >> 3,
            'START': (data[5] & 0b00011111) >> 2,
            'J1_X': unpack('b', bytearray([data[6]]))[0],
            'J1_Y': unpack('b', bytearray([data[7]]))[0],
            'J1_DISTANCE': data[8],
            'J1_ANGLE': unpack('h', data[9:11])[0],
            'J1_DIRECTION': data[11],
            'J2_X': unpack('b', bytearray([data[12]]))[0],
            'J2_Y': unpack('b', bytearray([data[13]]))[0],
            'J2_DISTANCE': data[14],
            'J2_ANGLE': unpack('h', data[15:17])[0],
            'J2_DIRECTION': data[17],
        }

        if self.on_received != None:
            self.on_received()

    def _print_raw(self, data):
        print(' '.join('{:02x}'.format(x) for x in data))

    def get_joystick(self, joystick_pos):
        if self._decoded_state == None:
            return 0
        else:
            return self._decoded_state[joystick_pos]
    
    def get_key_pressed(self, button):
        if self._decoded_state == None:
            return 0
        else:
            return self._decoded_state[button]
    
    def get_raw_message(self):
        return self._raw_state

    def clear(self):
        self._raw_code = None
        self._decoded_state = None

ble_controller = BLEController()