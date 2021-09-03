from time import sleep_ms, ticks_ms
from machine import Pin
from micropython import const

class Button:

    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
        self.irq = self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.__irq_sc)
        self.presses = 0
        self.last_press = 0
        self.on_pressed = None

    def __irq_sc(self, p):
        if p.value():
            return
 
        now = ticks_ms()
        if now < self.last_press or (now-self.last_press) > 150:
            self.presses += 1
            # check if one button pressed or both
            if self.on_pressed != None:
                self.on_pressed()
        self.last_press = ticks_ms()

    def is_pressed(self):
        if self.pin.value() == 0:
            last_time = ticks_ms()
            while (ticks_ms() - last_time) < 50:
                sleep_ms(1)
            return True
        else:
            return False

btn_onboard = Button(23) # onboard button connected to pin 23 