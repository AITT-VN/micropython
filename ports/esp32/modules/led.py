from neopixel import NeoPixel
from machine import Pin

__NEOPIXEL_PIN = const(12)

class RGBLed:
    def __init__(self, pin, num_leds):
        self._np = NeoPixel(Pin(pin), num_leds, 3, 1)
        self._num_leds = num_leds

    def show(self, index, color):
        if index == 0:
            for i in range(self._num_leds):
                self._np[i] = color
            self._np.write()
        elif (index > 0) and (index <= self._num_leds) :
            self._np[index - 1] = color
            self._np.write()

    def off(self, index):
        self.show(index, (0, 0, 0))

led_onboard = RGBLed(__NEOPIXEL_PIN, 2)