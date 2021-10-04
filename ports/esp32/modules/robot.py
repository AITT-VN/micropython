import random
import time, gc

from setting import *
from utility import *

from motor import motor
from servo import servo
from speaker import *
from ultrasonic import *
from line_array import line_array
from motion import motion

class Robot:
    def __init__(self):
        self._speed = 50

    def run_mode_dancing(self):
        try:
            speaker.play(JINGLE_BELLS, wait=False) #WHEELS_ON_BUS)
            for i in range(4):
                self.forward(50)
                time.sleep(0.5)
                self.backward(50)
                time.sleep(0.5)

            for i in range(4):
                self.turn_left(50)
                time.sleep(0.3)
                self.turn_right(50)
                time.sleep(0.3)
                self.turn_right(50)
                time.sleep(0.3)
                self.turn_left(50)
                time.sleep(0.3)

            for i in range(4):
                self.forward(50)
                time.sleep(0.5)
                self.backward(50)
                time.sleep(0.5)
                self.turn_left(50)
                time.sleep(0.3)
                self.turn_right(50)
                time.sleep(0.3)
                self.turn_right(50)
                time.sleep(0.3)
                self.turn_left(50)
                time.sleep(0.3)

        finally:
            self.stop()
            speaker.stop()
            gc.collect()

    def run_mode_obs(self, wait=True):
        while True:
            distance = ultrasonic.distance_cm()
            if distance < 30:
                i = random.randint(1, 2)
                if i == 1:
                    self.turn_right(60)
                else:
                    self.turn_left(60)
                time.sleep(0.4)
            else:
                self.forward(60)
                time.sleep(0.1)

            if not wait:
                return

    def run_mode_follow(self, wait=True, speed=40):
        while True:
            d_us = ultrasonic.distance_cm()

            if d_us < 15:
                self.backward(speed)
            elif d_us < 30:
                self.stop()
            elif d_us < 50:
                self.forward(speed)
            else:
                self.stop()
            
            time.sleep_ms(50)
            if not wait:
                return            

    def run_mode_linefinder(self, wait=True, speed=40):
        speed_factors = [ 
            [1, 1], [0.5, 1], [0, 1], [-0.5, 0.5], 
            [-2/3, -2/3], [0, 1], [-0.5, 0.5], [-0.7, 0.7] 
        ] #0: forward, 1: light turn, 2: normal turn, 3: heavy turn, 4:  backward, 5: strong light turn, 6: strong normal turn, 7: strong heavy turn

        if wait or not hasattr(self, 'm_dir'):
            self.m_dir = -1 #no found
            self.i_lr = 0 #0 for left, 1 for right
            self.t_finding_point = time.time_ns()
                
        while True:
            now = line_array.read(0)
            
            if now == 0 or now == (0, 0, 0, 0): #no line found
                if self.m_dir == -1:
                    self.stop()
                else:
                    if self.m_dir < 4:                            
                        self.m_dir += 4 #change to go backward or stronger turn
                        self.set_wheel_speed( speed * speed_factors[self.m_dir][self.i_lr], speed * speed_factors[self.m_dir][1-self.i_lr] )
                        self.t_finding_point = time.time_ns()
                    else:
                        if time.time_ns() - self.t_finding_point > 3e9: #go backward and strong turn still not found then stop after 3s
                            self.m_dir = -1
                            self.stop()
            else:
                if (now[1], now[2]) == (1, 1):
                    if self.m_dir == 0:
                        self.set_wheel_speed(speed, speed) #if it is running straight before then robot should speed up now           
                    else:
                        self.m_dir = 0 #forward
                        self.set_wheel_speed(speed * 2/3, speed * 2/3) #just turn before, shouldn't set high speed immediately, speed up slowly
                else:
                    if (now[0], now[1]) == (1, 1): 
                        self.m_dir = 2 #left normal turn
                        self.i_lr = 0
                    elif (now[2], now[3]) == (1, 1): 
                        self.m_dir = 2 #right normal turn
                        self.i_lr = 1
                    elif now == (1, 0, 1, 0): 
                        if self.m_dir != -1:
                            self.m_dir = 1
                            self.i_lr = 0
                    elif now == (0, 1, 0, 1): 
                        if self.m_dir != -1:
                            self.m_dir = 1
                            self.i_lr = 1
                    elif now == (1, 0, 0, 1): 
                        if self.m_dir != -1:
                            self.m_dir = 0
                            self.i_lr = 0
                    elif now[1] == 1: 
                        self.m_dir = 1 #left light turn
                        self.i_lr = 0
                    elif now[2] == 1:
                        self.m_dir = 1 #right light turn
                        self.i_lr = 1
                    elif now[0] == 1: 
                        self.m_dir = 3 #left heavy turn
                        self.i_lr = 0
                    elif now[3] == 1: 
                        self.m_dir = 3 #right heavy turn
                        self.i_lr = 1

                    self.set_wheel_speed( speed * speed_factors[self.m_dir][self.i_lr], speed * speed_factors[self.m_dir][1-self.i_lr] )

            if not wait:
                return

    def run_mode_rotation(self):
        motor.speed(0, 100)
        motor.speed(1, -100)

    def run_by_drawing(self, index=0, angle_nodes=None, time_nodes=None):
        n = len(angle_nodes)

        self.stop()
        turn_speed = 30
        run_speed = 40
        self.__send_infor('B')
        try:
            while index < n:
                if angle_nodes[index] > 0:                
                    self.__turn_angle(angle_nodes[index], True, turn_speed)
                else:
                    if angle_nodes[index] < 0:
                        self.__turn_angle(-angle_nodes[index], False, turn_speed)
                self.__send_infor(index)
                self.__go_straight(run_speed, time_nodes[index]*1e-3)
                index = index + 1
        finally:
            self.__send_infor('E')
            self.stop()
            gc.collect()

    #------------------------------ROBOT PRIVATE MOVING METHODS--------------------------#

    def __go(self, forward=True, speed=None, t=None, straight=False):
        if speed == None:
            speed = self._speed

        if speed < 0 or speed > 100 or (t != None and t < 0):
            return

        if straight == True :
            return self.__go_straight(speed, t, forward)
        else:
            if forward:
                # stop first if robot is moving backard
                if motor.m1_speed < 0 and motor.m2_speed < 0:
                    robot.stop()
                    time.sleep_ms(300)

                self.set_wheel_speed(speed, speed)
            else:
                # stop first if robot is moving forward
                if motor.m1_speed > 0 and motor.m2_speed > 0:
                    robot.stop()
                    time.sleep_ms(300)

                self.set_wheel_speed(-speed, -speed)

            if t != None :
                time.sleep(t)
                self.stop()

    def __calibrate_speed(self, speed, error=0.2, error_rotate=10, speed_factor=3):
        motion.updateZ()
        z = motion.get_angleZ()
        if abs(z) >= 360:
            z = (abs(z) - 360) * z / abs(z)
        if abs(z) > 180:
            z = z - 360 * z / abs(z)
        if abs(z) > error:
            if abs(z) > error_rotate:
                self.set_wheel_speed(30 * z / abs(z), -30 * z / abs(z))
            self.set_wheel_speed(speed + z * speed_factor, speed - z * speed_factor)

    def __go_straight(self, speed=None, t=None, forward=True, sleep_t=10, need_calib=False):
        if speed == None:
            speed = self._speed
            
        if speed < 0 or speed > 100 or t == None or (t != None and t < 0):
            return

        try:
            self.stop()
            if need_calib:
                motion.calibrateZ()

            if forward == False:
                speed = -speed

            motion.begin()
            self.set_wheel_speed(speed, speed)
            t0 = time.time_ns()
            while time.time_ns() - t0 < t*1e9:
                self.__calibrate_speed(speed)
                time.sleep_ms(sleep_t)

        finally:
            self.stop()
            gc.collect()

    def __turn_backward(self, right=True, speed=None, t=None):
        if speed == None:
            speed = self._speed
            
        if speed < 0 or speed > 100 or (t != None and t < 0):
            return

        if right:
            self.set_wheel_speed(-speed, -speed/2)
        else:
            self.set_wheel_speed(-speed/2, -speed)            

        if t != None :
            time.sleep(t)
            self.stop()

    def __turn(self, right=True, speed=30, t=None):
        if speed == None:
            speed = self._speed
            
        if speed < 0 or speed > 100 or (t != None and t < 0):
            return

        if right:
            self.set_wheel_speed(speed, -speed)
        else:
            self.set_wheel_speed(-speed, speed)

        if t != None :
            time.sleep(t)
            self.stop()

    def __turn_angle(self, angle, right=True, speed=30, error=2, need_calib=False):
        if speed > 30:
            speed = 30

        if angle < 30:
            speed = 25

        try:
            self.stop()
            if need_calib:
                motion.calibrateZ()

            z0 = 0.0
            t0 = time.time_ns()
            t_start = t0
            limit_time = int((angle + 359) / 360) * 3e9

            self.__turn(right, speed)
            t_speed_changed = t0
            z_speed_changed = z0

            motion.begin()
            while (time.time_ns() - t_start) < limit_time:
                motion.updateZ()
                z_now = motion.get_angleZ(True)
                if z_now + error >= angle:
                    break
                
                t_now = time.time_ns()
                angle_to_target = angle - z_now

                delta_S = z_now - z0
                delta_T = t_now - t0            
                delta_V = delta_S / delta_T

                delta_V_changed = (z_now - z_speed_changed)/(t_now - t_speed_changed)
                if delta_V > 15e-8: #Delta speed value by detla angle (distance) / delta time that robot can control the precise angle, 100ms for 15 degree
                    if angle_to_target < 15: #(15 * delta_V / 15e-8) : #15 is degree value that robot can control with speed: 15e-8
                        speed = 15
                        self.__turn(right, speed)
                        t_speed_changed = t_now
                        z_speed_changed = z_now
                    else:
                        if delta_V > 40e-8: #Delta speed value is too fast need to slow down, 100ms for 40 degree
                            speed -= (speed - 15) / (angle_to_target / delta_S)
                            if speed < 15:
                                speed = 15
                            self.__turn(right, speed)
                            t_speed_changed = t_now
                            z_speed_changed = z_now
                else:          
                    if delta_V_changed < 3e-8 and t_now - t_speed_changed > 1e8 and speed < 30 : #Robot is moving too slow, 100ms for 3 degree
                        speed += 5
                        self.__turn(right, speed)
                        t_speed_changed = t_now
                        z_speed_changed = z_now

                z0 = z_now
                t0 = t_now

        finally:
            self.stop()
            gc.collect()

    def __send_infor(self, data):
        print(ROBOT_DATA_RECV_SIGN + 'data/' + str(data) + '/' + ROBOT_DATA_RECV_SIGN)

    #------------------------------ROBOT PUBLIC DRIVING METHODS--------------------------#

    def forward(self, speed=None, t=None, straight=False):
        self.__go(True, speed, t, straight)

    def backward(self, speed=None, t=None, straight=False):
        self.__go(False, speed, t, straight)

    def turn_left(self, speed=None, t=None):
        self.__turn(False, speed, t)

    def turn_right(self, speed=None, t=None):
        self.__turn(True, speed, t)
    
    def turn_left_backward(self, speed=None, t=None):
        self.__turn_backward(False, speed, t)

    def turn_right_backward(self, speed=None, t=None):
        self.__turn_backward(True, speed, t)

    def turn_left_angle(self, angle, speed=30, need_calib=False):
        self.__turn_angle(angle, False, speed, need_calib)

    def turn_right_angle(self, angle, speed=30, need_calib=False):
        self.__turn_angle(angle, True, speed, need_calib)

    def move(self, dir, speed=None):

        # calculate direction based on angle
        #         90(3)
        #   135(4) |  45(2)
        # 180(5)---+----Angle=0(dir=1)
        #   225(6) |  315(8)
        #         270(7)

        if speed == None:
            speed = self._speed

        if dir == 1:
            self.turn_right(speed/2)

        elif dir == 2:
            self.set_wheel_speed(speed, speed/2)

        elif dir == 3:
            self.forward(speed)

        elif dir == 4:
            self.set_wheel_speed(speed/2, speed)

        elif dir == 5:
            self.turn_left(speed/2)

        elif dir == 6:
            self.set_wheel_speed(-speed/2, -speed)
      
        elif dir == 7:
            self.backward(speed)

        elif dir == 8:
            self.set_wheel_speed(-speed, -speed/2)

        else:
            self.stop()

    def set_wheel_speed(self, left_wheel_speed, right_wheel_speed):
        motor.speed(0, int(left_wheel_speed))
        motor.speed(1, int(right_wheel_speed))

    def set_speed(self, speed):
        if speed < 0 or speed > 100 :
            return

        self._speed = speed
        
    def get_speed(self):
        return self._speed
    
    def stop(self):
        self.set_wheel_speed(0, 0)

    def stop_all(self):
        self.stop()
        speaker.stop()
        for i in range(8):
            servo.release(i)

robot = Robot()