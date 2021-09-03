import machine, time
import pcf8574

from setting import PORTS_DIGITAL
from utility import say

class LineArray:
    def __init__(self, port, address=0x23):
        self.address = address
        if port < 0 or port > 5:
            print('Port not supported')
        self._reset_port(port)

    def _reset_port(self, port):
        self.port = port
        # Grove port: GND VCC SCL SDA
        scl_pin = machine.Pin(PORTS_DIGITAL[port][0])
        sda_pin = machine.Pin(PORTS_DIGITAL[port][1])
        try:
            self.i2c_pcf = machine.SoftI2C(scl = scl_pin, sda = sda_pin)
            self.pcf = pcf8574.PCF8574(self.i2c_pcf, self.address)
        except:
            self.pcf = None
            say('Line finder array not found')
    
    def read(self, port, index=None):
        
        if port != self.port:
            self._reset_port(port)

        # 0 white, 1 black
        if self.pcf == None:
            return 0

        if index == None:
            return (self.pcf.pin(0), self.pcf.pin(1), self.pcf.pin(2), self.pcf.pin(3))

        return self.pcf.pin(index)

line_array = LineArray(0)