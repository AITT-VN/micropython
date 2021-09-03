from micropython import const
import os, machine, io

_MP_STREAM_POLL = const(3)
_MP_STREAM_POLL_RD = const(0x0001)

# Simple buffering stream to support the dupterm requirements.
class BLEREPL(io.IOBase):
    def __init__(self, uart):
        self._uart = uart
        self._tx_buf = bytearray()

    def _on_rx(self):
        # Needed for ESP32.
        if hasattr(os, "dupterm_notify"):
            os.dupterm_notify(None)

    def read(self, sz=None):
        return self._uart.get_repl_data(sz)

    def readinto(self, buf):
        avail = self._uart.get_repl_data(len(buf))
        if not avail:
            return None
        for i in range(len(avail)):
            buf[i] = avail[i]
        return len(avail)

    def ioctl(self, op, arg):
        if op == _MP_STREAM_POLL:
            if self._uart.has_repl_data():
                return _MP_STREAM_POLL_RD
        return 0

    def _flush(self):
        data = self._tx_buf[0:100]
        self._tx_buf = self._tx_buf[100:]
        self._uart.send_periph(data)
        if self._tx_buf:
            schedule_in(self._flush)

    def write(self, buf):
        empty = not self._tx_buf
        self._tx_buf += buf

        if empty:
            schedule_in(self._flush)
    
    def reset_repl(self):
        os.dupterm(self)
        schedule_in(self._flush)

_timer = machine.Timer(0)

# Batch writes into 30ms intervals.
_DELAY_MS = const(30)
def schedule_in(handler):
    def _wrap(_arg):
        handler()

    _timer.init(mode=machine.Timer.ONE_SHOT, period=_DELAY_MS, callback=_wrap)