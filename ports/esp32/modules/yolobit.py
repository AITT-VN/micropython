import machine

from time import sleep_ms, sleep, ticks_ms as running_time

from lis3dh import LIS3DH_I2C
import accelerometer

from utility import *

################### yolo:bit functions ###########################
reset = machine.reset

################### Pins functions ###########################
import pins

pin0 = pins.Pins(32)
pin1 = pins.Pins(33)
pin2 = pins.Pins(27, 39)
pin3 = pins.Pins(2)
pin4 = pins.Pins(15)
pin5 = pins.Pins(35)
pin6 = pins.Pins(12)
pin7 = pins.Pins(25)
pin10 = pins.Pins(26)
pin11 = pins.Pins(14)
pin12 = pins.Pins(13)
pin13 = pins.Pins(18)
pin14 = pins.Pins(19)
pin15 = pins.Pins(23)
pin16 = pins.Pins(5)
pin19 = pins.Pins(22)
pin20 = pins.Pins(21)
if DEV_VERSION >= 4:
    pin8 = pin13
    pin9 = pin15
else:
    pin8 = pins.Pins(17)
    pin9 = pins.Pins(16)

################### Display functions ###########################
import display
Image = display.Image
display = display.Display()
display.set_all((0, 0, 0))

################### Button functions ###########################
import button
button_a = button.Button(35)
button_b = button.Button(14)

################### Temperature sensor functions ##################
import temperature
temperature_sensor = temperature.Temperature(34)
temperature = temperature_sensor.temperature

################### Light sensor functions ###########################
import light
light_sensor = light.Light(36)
light_level = light_sensor.read

################### Accelerometer sensor functions ###########################
from machine import Pin

__i2c = None

try:
    from machine import SoftI2C
    __i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=200000)
except Exception as e:
    print("SoftI2C not exist. Using old I2C", e)
    from machine import I2C
    __i2c = I2C(scl=Pin(22), sda=Pin(21), freq=200000)

try:
    __sensor = LIS3DH_I2C(__i2c, address=25)
    accelerometer = accelerometer.Direction(__sensor)
except Exception as e:
    print("LIS3DH Error", e)

################### Utilitiy functions ###########################
def translate(value, left_min, left_max, right_min, right_max):
    # Figure out how 'wide' each range is
    left_span = left_max - left_min
    right_span = right_max - right_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - left_min) / float(left_span)

    # Convert the 0-1 range into a value in the right range.
    return right_min + (value_scaled * right_span)
