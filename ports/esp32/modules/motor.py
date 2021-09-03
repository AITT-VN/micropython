import time
import pca9685
from utility import *

class DCMotors:
    def __init__(self, i2c, address=0x40, freq=50):
        self.pca9685 = pca9685.PCA9685(i2c, address)
        self.pca9685.freq(freq)

        self.m1_speed = 0
        self.m2_speed = 0

    def _pin(self, pin, value=None):
        if value is None:
            return bool(self.pca9685.pwm(pin)[0])
        if value:
            self.pca9685.pwm(pin, 4096, 0)
        else:
            self.pca9685.pwm(pin, 0, 0)

    def speed(self, index, value=None):
        #_DC_MOTORS = ((10, 12, 11), (15, 13, 14))
        if index == 0:
            pwm, in2, in1 = (10, 12, 11)
        else:
            pwm, in2, in1 = (15, 13, 14)

        if value is None:
            value = self.pca9685.duty(pwm)
            if self._pin(in2) and not self._pin(in1):
                value = -value
            return value
            
        value = max(min(100, value),-100)

        if index == 0 :
          self.m1_speed = value
        else:
          self.m2_speed = value

        if value > 0:
            # Forward
            self._pin(in2, False)
            self._pin(in1, True)
        elif value < 0:
            # Backward
            self._pin(in1, False)
            self._pin(in2, True)
        else:
            # Release
            self._pin(in1, False)
            self._pin(in2, False)
        self.pca9685.duty(pwm, int(translate(abs(value), 0, 100, 0, 3500))) # use 3500 to limit robot speed (save battery) while pca9685 max pwm is 4095

motor = DCMotors(i2c)