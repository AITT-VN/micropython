# __init__.py Nonblocking IR blaster
# Runs on Pyboard D or Pyboard 1.x (not Pyboard Lite), ESP32 and RP2

# Released under the MIT License (MIT). See LICENSE.

# Copyright (c) 2020-2021 Peter Hinch
import gc
from machine import Pin
from esp32 import RMT

from micropython import const
from array import array
from time import ticks_us, ticks_diff

import micropython
micropython.alloc_emergency_exception_buf(100)

_TBURST = const(563)
_T_ONE = const(1687)
_ASIZE = const(68)

# Shared by NEC
_STOP = const(0)  # End of data

# IR abstract base class. Array holds periods in μs between toggling 36/38KHz
# carrier on or off. Physical transmission occurs in an ISR context controlled
# by timer 2 and timer 5. See TRANSMITTER.md for details of operation.
class IR_TX:
    _active_high = True  # Hardware turns IRLED on if pin goes high.
    _space = 0  # Duty ratio that causes IRLED to be off
    timeit = False  # Print timing info

    @classmethod
    def active_low(cls):
        raise ValueError('Cannot set active low on ESP32')

    def __init__(self, pin, verbose=False):
        self._rmt = RMT(0, pin=pin, clock_div=80, tx_carrier=(38000, 33, 1))
        # self._rmt = RMT(0, pin=pin, clock_div=80, carrier_freq=38000, carrier_duty_percent=33)  # 1μs resolution
        
        self._tcb = self._cb  # Pre-allocate
        self._arr = array('H', 0 for _ in range(_ASIZE))  # on/off times (μs)
        self._mva = memoryview(self._arr)
        # Subclass interface
        self.verbose = verbose
        self.carrier = False  # Notional carrier state while encoding biphase
        self.aptr = 0  # Index into array

    def _cb(self, t):  # T5 callback, generate a carrier mark or space
        t.deinit()
        p = self.aptr
        v = self._arr[p]
        if v == _STOP:
            self._ch.pulse_width_percent(self._space)  # Turn off IR LED.
            return
        self._ch.pulse_width_percent(self._space if p & 1 else self._duty)
        self._tim.init(prescaler=84, period=v, callback=self._tcb)
        self.aptr += 1

    # Public interface
    # Before populating array, zero pointer, set notional carrier state (off).
    def send(self, data, addr=0, validate=False):  # NEC: toggle is unused
        t = ticks_us()
        if validate:
            if addr > self.valid[0] or addr < 0:
                raise ValueError('Address out of range', addr)
            if data > self.valid[1] or data < 0:
                raise ValueError('Data out of range', data)

        self.aptr = 0  # Inital conditions for tx: index into array
        self.carrier = False
        self.tx(data, addr)  # Subclass populates ._arr
        # Initiate transmission
        self._rmt.write_pulses(tuple(self._mva[0 : self.aptr]), 1)
        if self.timeit:
            dt = ticks_diff(ticks_us(), t)
            print('Time = {}μs'.format(dt))
        gc.collect()

    def append(self, *times):  # Append one or more time peiods to ._arr
        for t in times:
            self._arr[self.aptr] = t
            self.aptr += 1
            self.carrier = not self.carrier  # Keep track of carrier state
            self.verbose and print('append', t, 'carrier', self.carrier)

    def add(self, t):  # Increase last time value (for biphase)
        assert t > 0
        self.verbose and print('add', t)
        # .carrier unaffected
        self._arr[self.aptr - 1] += t

    def _bit(self, b):
        self.append(_TBURST, _T_ONE if b else _TBURST)

    def tx(self, data, addr):  # Ignore toggle
        self.append(9000, 4500)
        if addr < 256:  # Short address: append complement
            addr |= ((addr ^ 0xff) << 8)
        for _ in range(16):
            self._bit(addr & 1)
            addr >>= 1
        data |= ((data ^ 0xff) << 8)
        for _ in range(16):
            self._bit(data & 1)
            data >>= 1
        self.append(_TBURST)

    def repeat(self):
        self.aptr = 0
        self.append(9000, 2250, _TBURST)
        # Initiate physical transmission.
        self._rmt.write_pulses(tuple(self._mva[0 : self.aptr]), start = 1)

ir_tx = IR_TX(Pin(2, Pin.OUT, value=0))

'''
def test():
    import time
    while True:
        ir_tx.send(0x25, 0x0010)  # address == 1, data == 25
        time.sleep(1)
'''