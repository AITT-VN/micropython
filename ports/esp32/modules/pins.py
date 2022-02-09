from utime import sleep_ms as sleep
from machine import Pin, ADC, DAC, TouchPad, PWM, time_pulse_us

class Pins():

    def __init__(self, pin, adc_pin=None):
        self.pin = pin
        if adc_pin == None:
            self.adc_pin = pin
        else:
            self.adc_pin = adc_pin
        self.adc = None
        self.pin_out = None
        self.pin_in = None
        self.pin_servo = None

    def write_digital(self, v):
        if self.pin in [34,35, 36, 37, 38, 39]:
            print("This pin is not supported for digital writing")
            return None
        if self.pin_out == None:
            self.pin_out = Pin(self.pin, Pin.OUT)
        self.pin_out.value(v)

    def read_digital(self):
        if self.pin_out != None:
            return self.pin_out.value()
        if self.pin_in == None:
            self.pin_in = Pin(self.pin, Pin.IN)
        return self.pin_in.value()

    def read_analog(self, ATTN = ADC.ATTN_11DB):
        if self.adc_pin not in range(32,40):
            print("This pin is not supported for analog reading")
            return None
        if self.adc is None:
            self.adc = ADC(Pin(self.adc_pin, Pin.IN))
            self.adc.atten(ATTN)
        
        if self.pin != self.adc_pin:
            Pin(self.pin, Pin.IN)

        return self.adc.read()

    def write_analog(self, value):
        if self.pin in [34,35, 36, 37, 38, 39]:
            print("This pin is not supported for analog writing")
            return None
        PWM(Pin(self.pin), freq=500, duty=value)

    def write_dac(self, value):
        if self.pin not in [25,26]:
            print("This pin is not supported for DAC")
            return None
        DAC(Pin(self.pin)).write(value)

    def is_touched(self):
        try: #Try getting Touch state
            ts = TouchPad(Pin(self.pin)).read()
        except: #If error, return True
            return True

        if ts < 400:
            return True
        else:
            return False

    def pulse_in(self, value, time_out=500000):
        if value != 0 and value != 1:
            value = 1
        return time_pulse_us(Pin(self.pin, Pin.IN), value, time_out)
    
    def servo_write(self, value, max=180):
        if self.pin in [34,35, 36, 37, 38, 39]:
            print("This pin is not supported for servo analog writing")
            return None
        if value < 0 or value > max:
            print("Servo position out of range. Must be from 0 to " + str(max) + " degree")
            return

        if not self.pin_servo:
            self.pin_servo = PWM(Pin(self.pin))

        # duty for servo is between 25 - 115
        #duty = 25 + int((value/2)) # 25 + (value/180)*(115-25)
        duty = 25 + int((value/max)*100)

        self.pin_servo.freq(50)
        self.pin_servo.duty(duty)
    
    def servo360_write(self, speed):
        if speed < -100 or speed > 100:
            return
        
        if not self.pin_servo:
            self.pin_servo = PWM(Pin(self.pin))
        
        self.pin_servo.freq(50)

        if speed == 0:
            self.pin_servo.duty(0)
            return

        degree = 90 - (speed/100)*90
        self.servo_write(degree)
    
    def servo_release(self):
        if self.pin in [34,35, 36, 37, 38, 39]:
            print("This pin is not supported for servo analog writing")
            return None
        if self.pin_servo:
            self.pin_servo.deinit()
            self.pin_servo = None

    def set_pull(self, value):
        mode = None
        if value == 'up':
            mode = Pin.PULL_UP
        elif value == 'down':
            mode = Pin.PULL_DOWN
        Pin(self.pin).init(Pin.IN, mode)

def unit_test():
    print('The unit test code is as follows')
    print('\n\
        pin13 = Pins(18)\n\
        pin1 = Pins(32)\n\
        pin21=Pins(34)\n\
        pin10=Pins(26)\n\
        pin5=Pins(35)\n\
        while True:\n\
        pin13.write_digital(1)\n\
        sleep(20)\n\
        pin13.write_digital(0)\n\
        sleep(480)\n\
        print(\'Please press P1\')\n\
        sleep(1000)\n\
        print(\'pin1(P1).is_touched()\', pin1.is_touched())\n\
        sleep(1000)\n\
        print(\'Please press A\')\n\
        sleep(1000)\n\
        print(\'pin5(P5).read_digital()\', pin5.read_digital())\n\
        print(\'the ADC converted values is \', pin21.read_analog(ADC.ATTN_11DB))\n\
        sleep(50)\n\
        for val in range(150,255,1):\n\
            pin10.write_analog(val)\n\
            sleep(10)\n\
        for val in range(255,150,-1):\n\
            pin10.write_analog(val)\n\
            sleep(10)\n\
    ')
    pin13 = Pins(18)
    pin0 = Pins(32)
    print('read digital: ', pin0.read_digital())
    sleep(1000)
    print('write digital 1')
    pin0.write_digital(1)
    sleep(1000)
    for i in range(10):
        print('read digital: ', pin0.read_digital())
        sleep(1000)
    print('write digital 0')
    pin0.write_digital(0)
    sleep(1000)
    for i in range(10):
        print('read digital: ', pin0.read_digital())
        sleep(1000)
    '''
    pin4=Pins(39)
    pin10=Pins(26)
    pin11=Pins(27)
    pin5=Pins(35)
    while True:
        pin13.write_digital(1)
        sleep(500)
        pin13.write_digital(0)
        sleep(500)
        print('Please touch P1')
        sleep(1000)
        print('pin1.is_touched()', pin1.is_touched())
        sleep(1000)
        print('Please press A')
        sleep(1000)
        print('pin5(P5).read_digital()', pin5.read_digital())
        print('the ADC converted values is ', pin4.read_analog())
        sleep(50)
        for val in range(0,255,1):
            pin10.write_dac(val)
            pin11.write_analog(val)
            sleep(10)
        for val in range(255,0,-1):
            pin10.write_dac(val)
            pin11.write_analog(val)
            sleep(10)
    '''

if __name__ == '__main__':
    unit_test()
