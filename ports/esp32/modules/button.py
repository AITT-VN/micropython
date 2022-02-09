from time import sleep_ms, ticks_ms
from machine import Pin

class Button:

    def __init__(self, pin_id):
        self.pin = Pin(pin_id, Pin.IN, Pin.PULL_UP)
        self.irq = self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self.__irq_sc)
        self.presses = 0
        self.last_press = 0
        self.on_pressed = None
        self.on_pressed_ab = None

    def __irq_sc(self, p):
        if p.value():
            return

        now = ticks_ms()
        if now < self.last_press or (now-self.last_press)>150:
            self.presses += 1
            # check if one button pressed or both
            if self.on_pressed_ab != None:
                # check if other button also pressed or not
                import yolobit
                other_btn = None
                if self == yolobit.button_a:
                    other_btn = yolobit.button_b
                else:
                    other_btn = yolobit.button_a

                last_time = ticks_ms()
                while (ticks_ms() - last_time) < 50:
                    if other_btn.pin.value() == 0:
                        if self.on_pressed_ab != -1:
                            self.on_pressed_ab()
                        return
                    sleep_ms(1)
            if self.on_pressed != None:
                self.on_pressed()

        self.last_press = ticks_ms()

    def close(self):
        self.irq.trigger(0)

    def get_presses(self):
        count = self.presses
        self.presses = 0
        return count

    def is_pressed(self):
        if self.pin.value() == 0:
            # check if other button also pressed or not
            import yolobit
            other_btn = None
            if self == yolobit.button_a:
                other_btn = yolobit.button_b
            else:
                other_btn = yolobit.button_a

            last_time = ticks_ms()
            while (ticks_ms() - last_time) < 50:
                if other_btn.pin.value() == 0:
                    return False
                sleep_ms(1)

            return True
        else:
            return False

    
    def is_pressed_ab(self):
        if self.pin.value() == 0:
            import yolobit
            other_btn = None
            if self == yolobit.button_a:
                other_btn = yolobit.button_b
            else:
                other_btn = yolobit.button_a
            sleep_ms(100)
            if other_btn.pin.value() == 0:
                return True
            else:
                return False
        else:
            return False

    def was_pressed(self):
        return self.presses != 0

def on_a_pressed():
    print('On A pressed')

def on_b_pressed():
    print('On B pressed')

def on_ab_pressed():
    print('On A+B pressed')

def unit_test():
    print('The unit test code is as follows')
    try:
        button_a = Button(35)
        button_b = Button(14)
        button_a.on_pressed = on_a_pressed
        button_b.on_pressed = on_b_pressed
        button_a.on_pressed_ab = on_ab_pressed; button_b.on_pressed_ab = -1;

        while True:
            if button_a.is_pressed():
                print('A pressed')
                sleep_ms(300)
            if button_b.is_pressed():
                print('B pressed')
                sleep_ms(300)
            if button_a.is_pressed_ab():
                print('A+B pressed')
                sleep_ms(300)
            #print('button_a was_pressed ', button_a.was_pressed())
            #print('button_a is_pressed ', button_a.is_pressed())
            #print('button_a get_presses ', button_a.get_presses())
    finally:
        button_a.close()
        button_b.close()


if __name__ == '__main__':
    unit_test()
