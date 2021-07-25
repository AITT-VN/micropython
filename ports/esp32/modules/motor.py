import time
import pca9685
from utility import *

_DC_MOTORS = ((10, 12, 11), (15, 13, 14))
MAX_PWM_VALUE = const(3500) # use to limit robot speed, pca9685 max pwm is 4095

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
        pwm, in2, in1 = _DC_MOTORS[index]
        if value is None:
            value = self.pca9685.duty(pwm)
            if self._pin(in2) and not self._pin(in1):
                value = -value
            return value

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
        self.pca9685.duty(pwm, int(translate(abs(value), 0, 100, 0, MAX_PWM_VALUE)))

motor = DCMotors(i2c)