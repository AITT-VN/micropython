# Author: qiren123
# This file is part of MicroPython MIDI Music
# Copyright (c) 2018 qiren123
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#
import _thread
from machine import Pin, PWM
from utime import sleep_ms
from utility import *

BIRTHDAY = [
    'c4:4', 'c:1', 'd:4', 'c:4', 'f', 'e:8', 'c:3', 'c:1', 'd:4', 'c:4', 'g',
    'f:8', 'c:3', 'c:1', 'c5:4', 'a4', 'f', 'e', 'd', 'a#:3', 'a#:1', 'a:4',
    'f', 'g', 'f:8'
]

TWINKLE = ['C5:2', 'C5:2', 'G5:2', 'G5:2', 'A5:2', 'A5:2', 'G5:4', 'F5:2', 'F5:2', 'E5:2', 'E5:2', 
'D5:2', 'D5:2', 'C5:4', 'G5:2', 'G5:2', 'F5:2', 'F5:2', 'E5:2', 'E5:2', 'D5:4', 'G5:2', 'G5:2', 'F5:2', 'F5:2', 
'E5:2', 'E5:2', 'D5:4','C5:2', 'C5:2', 'G5:2', 'G5:2', 'A5:2', 'A5:2', 'G5:4', 'F5:2', 'F5:2', 'E5:2', 'E5:2', 
'D5:2', 'D5:2', 'C5:4']


JINGLE_BELLS = ['E5:2', 'E5:2', 'E5:4', 'E5:2', 'E5:2', 'E5:4', 'E5:2', 'G5:2', 'C5:2', 'R:1', 'D5:1', 'E5:8', 'F5:2', 'F5:2',
'F5:2', 'R:1', 'F5:1', 'F5:2', 'E5:2', 'E5:2', 'E5:1', 'E5:1', 'E5:2', 'D5:2', 'D5:2', 'E5:2', 'D5:4', 'G5:4',
'E5:2', 'E5:2', 'E5:4', 'E5:2', 'E5:2', 'E5:4', 'E5:2', 'G5:2', 'C5:2', 'R:1', 'D5:1', 'E5:8', 'F5:2', 'F5:2',
'F5:2', 'R:1', 'F5:1', 'F5:2', 'E5:2', 'E5:2', 'E5:1', 'E5:1', 'G5:2', 'G5:2', 'F5:2', 'D5:2', 'C5:8']

WHEELS_ON_BUS = ['C5:2', 'R:0.1', 'F5:2', 'F5:1', 'F5:1', 'F5:2', 'A5:2', 'C6:2','A5:2', 'F5:2', 'R:0.75', 
'G6:2', 'E5:2', 'C5:3', 'R:0.25', 'C6:2', 'A5:2', 'F5:1.5', 'R:1',
'C5:2', 'R:0.1', 'F5:2', 'F5:1', 'F5:1', 'F5:2', 'A5:2', 'C6:2','A5:2', 'F5:2', 'R:0.75',
'G6:3', 'R:0.1', 'C5:2', 'C5:2', 'F5:1']

CHASE = [
    'a4:1', 'b', 'c5', 'b4', 'a:2', 'r', 'a:1', 'b', 'c5', 'b4', 'a:2', 'r',
    'a:2', 'e5', 'd#', 'e', 'f', 'e', 'd#', 'e', 'b4:1', 'c5', 'd', 'c',
    'b4:2', 'r', 'b:1', 'c5', 'd', 'c', 'b4:2', 'r', 'b:2', 'e5', 'd#', 'e',
    'f', 'e', 'd#', 'e'
]

JUMP_UP = ['c5:1', 'd', 'e', 'f', 'g']

JUMP_DOWN = ['g5:1', 'f', 'e', 'd', 'c']

POWER_UP = ['g4:1', 'c5', 'e4', 'g5:2', 'e5:1', 'g5:3']

POWER_DOWN = ['g5:1', 'd#', 'c', 'g4:2', 'b:1', 'c5:3']

normal_tone = {
    'A1': 55, 'B1': 62, 'C1': 33, 'D1': 37, 'E1': 41, 'F1': 44, 'G1': 49,
    'A2': 110, 'B2': 123, 'C2': 65, 'D2': 73, 'E2': 82, 'F2': 87, 'G2': 98,
    'A3': 220, 'B3': 247, 'C3': 131, 'D3': 147, 'E3': 165, 'F3': 175, 'G3': 196,
    'A4': 440, 'B4': 494, 'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349, 'G4': 392,
    'A5': 880, 'B5': 988, 'C5': 523, 'D5': 587, 'E5': 659, 'F5': 698, 'G5': 784,
    'A6': 1760, 'B6': 1976, 'C6': 1047, 'D6': 1175, 'E6': 1319, 'F6': 1397, 'G6': 1568,
    'A7': 3520, 'B7': 3951, 'C7': 2093, 'D7': 2349, 'E7': 2637, 'F7': 2794, 'G7': 3135,
    'A8': 7040, 'B8': 7902, 'C8': 4186, 'D8': 4699, 'E8': 5274, 'F8': 5588, 'G8': 6271,
    'A9': 14080, 'B9': 15804
}

rising_tone = {
    'A1': 58, 'C1': 35, 'D1': 39, 'F1': 46, 'G1': 52,
    'A2': 117, 'C2': 69, 'D2': 78, 'F2': 93, 'G2': 104,
    'A3': 233, 'C3': 139, 'D3': 156, 'F3': 185, 'G3': 208,
    'A4': 466, 'C4': 277, 'D4': 311, 'F4': 370, 'G4': 415,
    'A5': 932, 'C5': 554, 'D5': 622, 'F5': 740, 'G5': 831,
    'A6': 1865, 'C6': 1109, 'D6': 1245, 'F6': 1480, 'G6': 1661,
    'A7': 3729, 'C7': 2217, 'D7': 2489, 'F7': 2960, 'G7': 3322,
    'A8': 7459, 'C8': 4435, 'D8': 4978, 'F8': 5920, 'G8': 6645,
    'A9': 14917
}

falling_tone = {
    'B1': 58, 'D1': 35, 'E1': 39, 'G1': 46, 'A1': 52,
    'B2': 117, 'D2': 69, 'E2': 78, 'G2': 93, 'A2': 104,
    'B3': 233, 'D3': 139, 'E3': 156, 'G3': 185, 'A3': 208,
    'B4': 466, 'D4': 277, 'E4': 311, 'G4': 370, 'A4': 415,
    'B5': 932, 'D5': 554, 'E5': 622, 'G5': 740, 'A5': 831,
    'B6': 1865, 'D6': 1109, 'E6': 1245, 'G6': 1480, 'A6': 1661,
    'B7': 3729, 'D7': 2217, 'E7': 2489, 'G7': 2960, 'A7': 3322,
    'B8': 7459, 'D8': 4435, 'E8': 4978, 'G8': 5920, 'A8': 6645,
    'B9': 14917
}

Letter = 'ABCDEFG#R'
class Speaker():
    lock = _thread.allocate_lock()

    def __init__(self):
        self.reset()
        self.playing = False
        self.stopped = True

    def set_tempo(self, ticks=4, bpm=120):
        self.duration = ticks
        self.bpm = bpm
        self.beat = 60000 / self.bpm / ticks
    def set_octave(self, octave=4):
        self.octave = octave
    def set_duration(self, duration=4):
        self.duration = duration
    def reset(self):
        self.set_duration()
        self.set_octave()
        self.set_tempo()
    def stop(self):
      #self.play(['r'])
      # try to stop within 500ms
      if not self.playing:
        return True
      else:
        self.playing = False     
      count = 0
      while not self.stopped and count < 500:
        sleep_ms(10)
        count += 10    
      if count < 500:
        return True # stop successfully
      else:
        return False # failed to stop due to something wrong

    def parse(self, tone, dict):
        time = self.beat * self.duration
        pos = tone.find(':')
        if pos != -1:
            time = self.beat * float(tone[(pos + 1):])
            tone = tone[:pos]
        freq, tone_size = 1, len(tone)
        if 'R' in tone:
            freq = 1
        elif tone_size == 1:
            freq = dict[tone[0] + str(self.octave)]
        elif tone_size == 2:
            freq = dict[tone]
            #self.set_octave(tone[1:])
        return int(freq), int(time)
    def midi(self, tone):
        pos = tone.find('#')
        if pos != -1:
            return self.parse(tone.replace('#', ''), rising_tone)
        pos = tone.find('B')
        if pos != -1 and pos != 0:
            return self.parse(tone.replace('B', ''), falling_tone)
        return self.parse(tone, normal_tone)
    def set_default(self, tone):
        pos = tone.find(':')
        if pos != -1:
            self.set_duration(float(tone[(pos + 1):]))
            tone = tone[:pos]
    def _play(self, tune, loop=False, pin=27, duration=None):
        if not self.stop():
            return      
        pwm = PWM(Pin(pin))
        try:
            if duration is None:
                self.set_default(tune[0])
            else:
                self.set_duration(duration)
            self.playing = True
            self.stopped = False           
            if loop:
                while True:
                    for tone in tune:
                        if not self.playing:
                            break                    
                        tone = tone.upper()  # all to upper
                        if tone[0] not in Letter:
                            continue                        
                        midi = self.midi(tone)
                        pwm.freq(midi[0])  # set frequency
                        pwm.duty(midi[1])  # set duty cycle
                        sleep_ms(midi[1])
            else:
                for tone in tune:
                    if not self.playing:
                        break                   
                    tone = tone.upper()  # all to upper
                    if tone[0] not in Letter:
                        continue                    
                    midi = self.midi(tone)
                    pwm.freq(midi[0])  # set frequency
                    pwm.duty(midi[1])  # set duty cycle
                    sleep_ms(midi[1])
        except Exception as e:
            printp(e)
        finally:
            pwm.duty(0)
            pwm.deinit()
            self.playing = False
            self.stopped = True    
    def play(self, tune, wait=False, loop=False, pin=27, duration=None):
        if not wait:
          _thread.start_new_thread(self._play, (tune, loop, pin, duration))
        else:
          self._play(tune, loop, pin, duration)
      
    def pitch(self, freq, tim, pin=27):
        try:
            pwm = PWM(Pin(pin))
            pwm.freq(freq)  # set frequency
            pwm.duty(tim)  # set duty cycle
            sleep_ms(tim)
        finally:
            pwm.deinit()

    def tone(self):
        self.play(['C5:2'])
 
    def play_a_song(self):
        import random
        b_C3_A0i_h_C3_A1t = random.randint(1, 5)
        if b_C3_A0i_h_C3_A1t == 1:
            self.play(JINGLE_BELLS, wait=False, loop=False)
        elif b_C3_A0i_h_C3_A1t == 2:
            self.play(BIRTHDAY, wait=False, loop=False)
        elif b_C3_A0i_h_C3_A1t == 3:
            self.play(TWINKLE, wait=False, loop=False)
        elif b_C3_A0i_h_C3_A1t == 4:
            self.play(WHEELS_ON_BUS, wait=False, loop=False)
        else:
            self.play(CHASE, wait=False, loop=False)

speaker = Speaker()