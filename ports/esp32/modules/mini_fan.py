from setting import *
from machine import Pin, PWM

class MiniFan:
    def __init__(self):
        self.port = None

    def _reset_port(self, port):
        self.port = port
        self.in_a = PWM(Pin(PORTS_DIGITAL[port][0]), freq=50, duty=0)
        self.in_b = PWM(Pin(PORTS_DIGITAL[port][1]), freq=50, duty=0)

    def speed(self, port, speed):
        if speed < -100 or speed > 100:
            return

        if port != self.port:
            self._reset_port(port)

        if speed > 0:
            self.in_a.duty(speed*10)
            self.in_b.duty(0)
        else:
            self.in_a.duty(0)
            self.in_b.duty(-speed*10)

mini_fan = MiniFan()