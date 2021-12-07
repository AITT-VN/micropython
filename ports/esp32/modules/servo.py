import pca9685
import time

from utility import *

class Servos:
  def __init__(self, i2c, address=0x40, freq=50, min_us=400, max_us=2400, default_degrees=180):
    self.period = 1000000 / freq
    self.min_duty = self._us2duty(min_us)
    self.max_duty = self._us2duty(max_us)
    self.default_degrees = default_degrees
    self.freq = freq
    self.pca9685 = pca9685.PCA9685(i2c, address)
    self.pca9685.freq(freq)

    self.pos = []
    for i in range(8):
      self.pos.append(90)

  def _us2duty(self, value):
    return int(4095 * value / self.period)

  def position(self, index, degrees=None, max_degree=180):
    if index < 0 or index > 7:
      return
    
    if degrees == None:
      return self.pos[index]

    if degrees < 0 or degrees > max_degree:
      return

    # Lego servo 270 not working with 0 degree
    if degrees <= 1 and max_degree == 270:
      degrees = 1

    span = self.max_duty - self.min_duty
    duty = self.min_duty + span * degrees / max_degree
    duty = min(self.max_duty, max(self.min_duty, int(duty)))
    self.pca9685.duty(index, duty)
    self.pos[index] = degrees

  def rotate(self, index, change=2, sleep=10, limit=None, max_degree=180):
    if index < 0 or index > 7:
      return

    while True:
      new_pos = self.pos[index] + change

      if limit == None:
        if change <= 0:
          limit = 0
        else:
          limit = max_degree

      if (change <= 0 and new_pos < limit) or (change > 0 and new_pos > limit):
        return

      span = self.max_duty - self.min_duty
      duty = self.min_duty + span * new_pos / max_degree
      duty = min(self.max_duty, max(self.min_duty, int(duty)))
      self.pca9685.duty(index, duty)
      self.pos[index] = new_pos
      time.sleep_ms(sleep)

  def release(self, index):
    self.pca9685.duty(index, 0)

  def spin(self, index, speed):
    if index < 0 or index > 7 or speed < -100 or speed > 100:
      return
    
    if speed == 0:
      self.release(index)
      return

    degree = 90 - (speed/100)*90
    self.position(index, degree)

servo = Servos(i2c)