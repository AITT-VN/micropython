from machine import Pin
from neopixel import NeoPixel

class Pixel(NeoPixel):

    def __init__(self):
        self.Min, self.Max, self.Sum = 0, 5, 25
        NeoPixel.__init__(self, Pin(4), self.Sum)

    def LoadXY(self, X, Y, RGB):
        if self.Min <= X and X < self.Max and self.Min <= Y and Y < self.Max:
            self[int(X) + int(Y) * self.Max] = RGB # left and top is (0, 0)
        else:
            print('Pixel Load Over Limit')        

    def LoadPos(self, Pos, RGB):
        if self.Min <= Pos and Pos < self.Sum:
            self[Pos] = RGB
        else:
            print('Pixel Load Over Limit')        

    def Show(self):
        self.write()

