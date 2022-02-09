from time import sleep_ms
from machine import ADC, Pin

class Light():

    def __init__(self, pin):
        self.adc = ADC(Pin(pin, Pin.IN))

    def read(self):
        self.adc.atten(ADC.ATTN_2_5DB)  # 0-1.34V
        self.adc.width(ADC.WIDTH_10BIT)
        light_value = self.adc.read()
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)

        if light_value < 50:
            light_value = light_value * 10 #500
        elif light_value < 150:
            light_value = light_value * 5 # 700
        elif light_value < 350:
            light_value = light_value * 2.5 # 800
        elif light_value < 650:
            light_value = light_value * 1.5 # 900
        elif light_value < 950:
            light_value = light_value * 1.2 # 1023
        else:
            light_value = light_value * 1.1 # 1023

        if light_value > 1023:
            light_value = 1023
        #print('Now is ' + str(l) + '    ' + str(f) + '    ' + str(int(f/10.23)))
        return int(light_value/10.23)

    # result = 1 => up, 0 => state down.
    def get_state(self):
        return self.read() > 5


def unit_test():
    print('\n\
        light = Light(36)\n\
        while True:\n\
            print(light.read())\n\
                print(light.get_state())\n\
            sleep_ms(200)\n\
    ')
    light = Light(36)
    while True:
        print(light.read())
        print(light.get_state())
        sleep_ms(200)

if __name__ == '__main__':
    unit_test()
