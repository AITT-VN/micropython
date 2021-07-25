import machine
import pcf8574
from setting import *

class FlameSensor:
    def __init__(self, address=0x20):
        self.address = address
        self.port = None

    def _reset_port(self, port):
        self.port = port
        # Grove port: GND VCC SCL SDA
        scl_pin = machine.Pin(PORTS_DIGITAL[port][0])
        sda_pin = machine.Pin(PORTS_DIGITAL[port][1])
        try:
            self.pcf = pcf8574.PCF8574(machine.SoftI2C(scl = scl_pin, sda = sda_pin), self.address)
        except:
            print('Flame sensor not found')
    
    def read(self, port):
        if port != self.port:
            self._reset_port(port)

        return (self.pcf.pin(0), self.pcf.pin(1), self.pcf.pin(2), self.pcf.pin(3), self.pcf.pin(4))

flame_sensor = FlameSensor()
