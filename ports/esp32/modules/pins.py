from machine import Pin, ADC, DAC, TouchPad, PWM, time_pulse_us
from utility import *

class Pins():

    def __init__(self, pin, adc_pin=None):
        self.pin = pin
        if adc_pin == None:
            self.adc_pin = pin
        else:
            self.adc_pin = adc_pin
        self.adc = None

    def write_digital(self, v):
        if self.pin in [34, 35, 36, 37, 38, 39]:
            print("This pin is not supported for digital writing")
            return None
        if self.pin in [21, 22]:
            print("This pin is for I2C only")
            return None
        Pin(self.pin, Pin.OUT).value(v)

    def read_digital(self):
        if self.pin in [21, 22]:
            print("This pin is for I2C only")
            return 0
        return Pin(self.pin, Pin.IN).value()

    def read_analog(self, ATTN=ADC.ATTN_11DB):
        if self.adc_pin not in range(32,40):
            print("This pin is not supported for analog reading")
            return None
        if self.adc_pin != self.pin:
            Pin(self.pin, Pin.IN) # reset digital pin joined with this adc pin
        if self.adc is None:
            self.adc = ADC(Pin(self.adc_pin, Pin.IN))
            self.adc.atten(ATTN)
        return self.adc.read()

    def write_analog(self, value):
        if self.pin in [34, 35, 36, 37, 38, 39]:
            print("This pin is not supported for analog writing")
            return None
        if self.pin in [21, 22]:
            print("This pin is for I2C only")
            return None
        PWM(Pin(self.pin), freq=50, duty=value)

    def write_dac(self, value):
        if self.pin not in [25,26]:
            print("This pin is not supported for DAC")
            return None
        DAC(Pin(self.pin)).write(value)

    def is_touched(self):
        return TouchPad(Pin(self.pin)).read() < 200
    
    def pulse_in(self, value, time_out=500000):
        if self.pin in [34, 35, 36, 37, 38, 39]:
            print("This pin is not supported for pulse in")
            return 0
        if self.pin in [21, 22]:
            print("This pin is for I2C only")
            return 0

        if value != 0 and value != 1:
            value = 1
        return time_pulse_us(Pin(self.pin, Pin.IN), value, time_out)
    
    def servo_write(self, value):
        if self.pin in [34, 35, 36, 37, 38, 39]:
            print("This pin is not supported for servo analog writing")
            return None
        if self.pin in [21, 22]:
            print("This pin is for I2C only")
            return None

        if value < 0 or value > 180:
            print("Invalid angle. Must be from 0 to 180 degree")
            return
        # duty for servo is between 25 - 125
        #duty = 25 + int((value/2)) # 25 + (value/180)*(115-25)
        duty = 25 + int((value/180)*100)
        PWM(Pin(self.pin), freq=50, duty=duty)

    def set_pull(self, value):
        if self.pin in [21, 22]:
            print("This pin is for I2C only")
            return
        mode = None
        if value == 'up':
            mode = Pin.PULL_UP
        elif value == 'down':
            mode = Pin.PULL_DOWN
        Pin(self.pin).init(Pin.IN, mode)

pin11 = Pins(PORTS_DIGITAL[0][0], PORTS_ADC[0][0])
pin12 = Pins(PORTS_DIGITAL[0][1], PORTS_ADC[0][1])
pin21 = Pins(PORTS_DIGITAL[1][0], PORTS_ADC[1][0])
pin22 = Pins(PORTS_DIGITAL[1][1], PORTS_ADC[1][1])
pin31 = Pins(PORTS_DIGITAL[2][0], PORTS_ADC[2][0])
pin32 = Pins(PORTS_DIGITAL[2][1], PORTS_ADC[2][1])
pin41 = Pins(PORTS_DIGITAL[3][0], PORTS_ADC[3][1])
pin42 = Pins(PORTS_DIGITAL[3][1], PORTS_ADC[3][1])
pin51 = Pins(PORTS_DIGITAL[4][0], PORTS_ADC[4][0])
pin52 = Pins(PORTS_DIGITAL[4][1], PORTS_ADC[4][1])
pin61 = Pins(PORTS_DIGITAL[5][0], PORTS_ADC[5][0])
pin62 = Pins(PORTS_DIGITAL[5][1], PORTS_ADC[5][1])