from setting import *
from machine import Pin

S1_IN_S2_OUT = const(0)
S1_OUT_S2_IN = const(1)
S1_OUT_S2_OUT = const(2)
S1_IN_S2_IN = const(3)

class LineFinder:
    def __init__(self):
        pass

    def _reset_port(self, port):
        if port < 0 or port > 5:
            print('Port not supported')
        self.port = port
        self.left_pin = Pin(PORTS_DIGITAL[port][0], mode=Pin.IN, pull=None)
        self.right_pin = Pin(PORTS_DIGITAL[port][1], mode=Pin.IN, pull=None)

    def read(self, port):
        if port != self.port:
            self._reset_port(port)

        if self.left_pin.value() and not self.right_pin.value():
            # detect line on left side
            return S1_IN_S2_OUT
        elif not self.left_pin.value() and self.right_pin.value():
            # detect line on right side
            return S1_OUT_S2_IN
        elif not self.left_pin.value() and not self.right_pin.value():
            # detect line on none side
            return S1_OUT_S2_OUT
        elif self.left_pin.value() and self.right_pin.value():
            # detect line on both side
            return S1_IN_S2_IN
        else:
            # detect error
            return -1

line_finder = LineFinder()