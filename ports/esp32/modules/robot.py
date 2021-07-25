from math import fabs
import random
import time, gc

from setting import *
from utility import *

from motor import motor
from servo import servo
from speaker import *
from led import led_onboard
from ultrasonic import ultrasonic
from line_array import line_array
from motion import motion


class Robot:
    def __init__(self):
        self._robot_mode = ROBOT_MODE_DO_NOTHING
        self._previous_robot_mode = ROBOT_MODE_DO_NOTHING
        self._speed = 50

    #-------------------MODE CONTROL---------------------#

    def change_mode(self, new_mode):
        if self._robot_mode == new_mode or new_mode == ROBOT_MODE_DO_NOTHING:
            self._previous_robot_mode = self._robot_mode
            self._robot_mode = ROBOT_MODE_DO_NOTHING
            self.stop()
        else:
            self._previous_robot_mode = self._robot_mode
            self._robot_mode = new_mode

    def process_mode(self):
        if self._robot_mode == ROBOT_MODE_DO_NOTHING:
            robot.stop()
            return

        elif self._robot_mode == ROBOT_MODE_AVOID_OBS:
            self.run_mode_obs(False)

        elif self._robot_mode == ROBOT_MODE_FOLLOW:
            self.run_mode_follow(False)

        elif self._robot_mode == ROBOT_MODE_LINE_FINDER:
            self.run_mode_linefinder(False)

#--------------------------------------ALL ENGINE FEATURES, COMMANDS--------------------------------------------------------------------------------- 
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

            self.stop()
        except KeyboardInterrupt:
            self.stop()
            speaker.stop()

    def run_mode_obs(self, wait=True):
        try:
            while True:
                distance = ultrasonic.distance_cm()
                if distance < 25:
                    i = random.randint(1, 2)
                    if i == 1:
                        self.turn_right(70)
                    else:
                        self.turn_left(70)
                    time.sleep(0.4)
                else:
                    self.forward(70)
                    time.sleep(0.1)
                if not wait:
                    return
        except KeyboardInterrupt:
            self.stop()

    def run_mode_follow(self, wait=True):
        try:
            while True:
                distance_sonic = ultrasonic.distance_cm()
                if distance_sonic < 15:
                    self.backward(70)
                elif (distance_sonic > 50) or (distance_sonic < 25):
                    self.stop()
                else:
                    self.forward(70)
            
                if wait == False:
                    return

                time.sleep(0.2)
        except KeyboardInterrupt:
            self.stop()

    def run_mode_linefinder(self, wait=True, speed=30):
        if speed == None:
            speed = self._speed
        
        #0:  robot is stopping, no direction
        #4:  robot is finding line
        #-0.5: heavy left backward  #0.5 heavy left forward
        #-1: left backward          #1: left forward
        #-1.5: light left backward  #1.5: light left forward
        #-2: backward               #2: forward
        #-2.5: heavy right backward #2.5: heavy right forward
        #-3: right backward         #3: right forward
        #-3.5: light right backward #3.5: light right forward
        m_dir = 4

        # normal factor for turn   
        # forward_div = [[-1/3, 1], [0, 1], [1/2, 1]] #heavy, normal, light forward factor for left and right speed
        # backward_div = [[-2/3, 1/2], [-1/2, 1/2], [0, 1/2]] #heavy, normal, light backward factor for left and right speed
        # strong factor to force turning
        forward_div = [[-1, 1], [-0.5, 1], [0, 1]] #heavy, normal, light forward factor for left and right speed
        backward_div = [[-1.5, 1/2], [-1, 1/2], [-0.5, 1/2]] #heavy, normal, light backward factor for left and right speed, it's always greater than forward factor
        
        stop_back = True #when robot turns back and meet a sign need to stop first
        delay_time_back = 0 #delay time before do next command
        stop_forward = True #when robot move forward and dont meet any sign then stop first        
        delay_time_forward = 0 #delay time before do next command
        tone = True #make sound beep when robot out of line
        tone_wait = False #use thread or not

        i_step = -1
        t_one_step = 2.5e9 #step time for a straight line 2.5s
        t_step_decrease = 0.5e9 #decrease time after full a map 0.5s
        t_step = t_one_step         
        sqrt_2 = 1.4142 #use for calc distance of cross line: sqrt of 2
        
        search_map =[ [0, 1], [-90, 1], [-135, 2*sqrt_2], [135, 1], [90, 1],
        [-90, 1], [-90, 1], [-135, 2*sqrt_2], [135, 1], [135, sqrt_2],
        [-90, sqrt_2], [-90, sqrt_2], [-90, sqrt_2], [-135, 1] ]

        t_limit_none_found = 1e9 # limit time used for no found when go back or forward
        calib_count = 1 # count variable used for calc time
        calib_time = 100e6 #100 milliseconds        

        now = 0
        try:                
            while True:
                now = line_array.read(0)

                #no found any line
                if now == (0, 0, 0, 0):
                    if m_dir == 4: #finding a line sign
                        if i_step < 0 or time.time_ns() - t_start_finding > search_map[i_step][1] * t_step: #start of map or time out for this step
                            i_step = i_step + 1
                            if i_step >= len(search_map): #loop map
                                i_step = 0
                                t_step = t_step - t_step_decrease #decrease time step
                                if t_step <= t_step_decrease: #not found anything
                                    self.stop

                            if search_map[i_step][0] > 0: #turn right
                                self.turn_right_angle(search_map[i_step][0], speed)
                            else:
                                if search_map[i_step][0] < 0: #turn left
                                    self.turn_left_angle(-search_map[i_step][0], speed)
                            self.stop()                            
                            motion.begin()
                            self.__prepare_calibration(speed)
                            self.set_wheel_speed(speed, speed) #run forward
                            calib_count = 1
                            t_start_finding = time.time_ns()
                        else:
                            if time.time_ns() - t_start_finding >= calib_count * calib_time: #every calib step time
                                self.__calibrate_speed()
                                calib_count = calib_count + 1

                    elif m_dir <= 0:
                        if m_dir == 0:
                            self.set_wheel_speed(speed, speed)
                        #else robot is runing backward => still back

                        if time.time_ns() - t_backward_point > t_limit_none_found: #forward and backward still not found then change to find mode
                            m_dir = 4
                            i_step = -1
                            t_step = t_one_step                        
                    else:
                        if stop_forward:
                            self.stop()
                            time.sleep_ms(delay_time_forward)
                        if tone:
                            speaker.play(['C4:0.5'], tone_wait)

                        if m_dir == 2: 
                            m_dir = -2 #backward
                            self.set_wheel_speed(-speed, -speed)
                        else:
                            if (m_dir < 2):
                                i = int(m_dir*2 - 1)
                                self.set_wheel_speed(speed * backward_div[i][0], speed * backward_div[i][1])
                            else:
                                i = int((m_dir-2)*2 - 1)
                                self.set_wheel_speed(speed * backward_div[i][1], speed * backward_div[i][0])
                            m_dir = -m_dir
                        t_backward_point = time.time_ns()
                #found a sign of line
                else:
                    if m_dir < 0 and stop_back: #it's runing back then stop
                        self.stop()
                        m_dir = 0                        
                        time.sleep_ms(delay_time_back)
                    elif (now[1], now[2]) == (1, 1):
                        m_dir = 2 #forward
                        self.set_wheel_speed(speed, speed)
                    else:
                        if (now[0], now[1]) == (1, 1): 
                            m_dir = 1 #left forward
                        elif (now[2], now[3]) == (1, 1): 
                            m_dir = 3 #right forward
                        elif now[1] == 1: 
                            m_dir = 1.5 #light left forward
                        elif now[2] == 1: 
                            m_dir = 3.5 #light right forward
                        elif now[0] == 1: 
                            m_dir = 0.5 #heavy left forward
                        elif now[3] == 1: 
                            m_dir = 2.5 #heavy right forward

                        if m_dir < 2:
                            i = int(m_dir*2 - 1)
                            self.set_wheel_speed(speed * forward_div[i][0], speed * forward_div[i][1])                        
                        else:
                            i = int((m_dir-2)*2 - 1)
                            self.set_wheel_speed(speed * forward_div[i][1], speed * forward_div[i][0])

                if wait == False:
                    return
        except KeyboardInterrupt:
            self.stop()
            gc.collect()

    def run_mode_rotation(self):
        motor.speed(0, 100)
        motor.speed(1, -100)

    def run_by_drawing(self, index=0, angle_nodes=None, time_nodes=None, t_step=2.5e3):
        # sqrt_2 = 1.4142 #use for calc distance of cross line: sqrt of 2
        
        # search_map =[ [0, 1], [-90, 1], [-135, 2*sqrt_2], [135, 1], [90, 1],
        # [-90, 1], [-90, 1], [-135, 2*sqrt_2], [135, 1], [135, sqrt_2],
        # [-90, sqrt_2], [-90, sqrt_2], [-90, sqrt_2], [-135, 1] ]

        # angle_nodes = []
        # time_nodes = []
        # for i in range(len(search_map)):
        #     angle_nodes.append(search_map[i][0])
        #     time_nodes.append(search_map[i][1] * t_step)

        n = len(angle_nodes)

        self.stop()
        turn_speed = 30
        run_speed = 30
        say('B')
        try:
            while index < n:
                if angle_nodes[index] > 0:                
                    self.__turn_angle(angle_nodes[index], True, turn_speed)
                else:
                    if angle_nodes[index] < 0:
                        self.__turn_angle(-angle_nodes[index], False, turn_speed)
                say(index)
                self.__go_straight(run_speed, time_nodes[index]*1e-3)
                index = index + 1
            self.stop()
        except KeyboardInterrupt:
            self.stop()
            say('E')

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

    def __prepare_calibration(self, speed=30):
        self.m1_speed = speed
        self.m2_speed = speed
        self.mins = -100
        self.maxs = 100
        self.flag = 0 # -1 left, 1 right
        self.err_side = 0 # -1 left, 1 right
        self.z_pre = 0 # previous angle

    def __calibrate_speed(self, error=1, distance=10):
        motion.update()
        z = motion.get_angle_Z()
        if z > 180:
            z = z - 360
        if not self.flag: # wait to know where side is wrong
            if abs(z) > error:
                if z > 0:
                    self.mins = self.m1_speed
                    self.maxs = self.m1_speed + distance
                    self.m2_speed = self.maxs
                else:                        
                    self.mins = self.m1_speed - distance
                    self.maxs = self.m1_speed
                    self.m2_speed = self.mins
                self.set_wheel_speed(self.m1_speed, self.m2_speed)                    
                self.flag = abs(z)/z
                self.err_side = self.flag
        elif abs(z) > 0.5:
            if z > 0.5:
                if z < self.z_pre and self.m2_speed == self.maxs and self.flag > 0:
                    if self.err_side > 0:
                        self.maxs -= 1
                    else:
                        self.maxs -= 0.5
                    if self.maxs < self.mins:
                        self.maxs = self.mins                            
                    self.m2_speed = self.maxs
                    self.set_wheel_speed(self.m1_speed, self.m2_speed)
                    self.flag = -self.flag                        
                elif self.m2_speed < self.maxs:
                    self.m2_speed += 1
                    self.m2_speed = max(min(self.maxs, self.m2_speed), self.mins)
                    self.set_wheel_speed(self.m1_speed, self.m2_speed)                    
                # print(round(z*100)/100, self.m2_speed, self.mins, self.maxs)
            if z < -0.5:
                if z > self.z_pre and self.m2_speed == self.mins and self.flag < 0:
                    if self.err_side < 0:                            
                        self.mins += 1
                    else:
                        self.mins += 0.5
                    if self.mins > self.maxs:
                        self.mins = self.maxs
                    self.m2_speed = self.mins
                    self.set_wheel_speed(self.m1_speed, self.m2_speed)
                    self.flag = -self.flag                        
                elif self.m2_speed > self.mins:
                    self.m2_speed -= 1
                    self.m2_speed = max(min(self.maxs, self.m2_speed), self.mins)
                    self.set_wheel_speed(self.m1_speed, self.m2_speed)
                # print(round(z*100)/100, self.m2_speed, self.mins, self.maxs)
        self.z_pre = z

    def __go_straight(self, speed=None, t=None, forward=True, need_calib=False):
        if speed == None:
            speed = self._speed
            
        if speed < 0 or speed > 100 or t == None or (t != None and t < 0):
            return

        speed = max(min(90, speed), 10) # because distance = 10
        self.stop()
        time.sleep_ms(1000)
        if need_calib:
            motion.calibrate()

        if forward == False:
            speed = -speed

        t = t * 1e9
        t0 = time.time_ns()

        self.__prepare_calibration(speed)
        motion.begin()
        self.set_wheel_speed(speed, speed)
        while time.time_ns() - t0 < t:
            self.__calibrate_speed()

        self.stop()

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

    def __turn_angle(self, angle, right=True, speed=30, need_calib=False, error=1):
        if speed > 30:
            speed = 30
        if angle < 30:
            speed = 25
        #can not turn with 360 degree in real, 359 is maximum
        if angle > 359:
            angle = 359
        if angle < 1:
            angle = 1

        self.stop()
        time.sleep_ms(500)
        if need_calib:
            motion.calibrate()

        z0 = 0.0
        t0 = time.time_ns()
        t_start = t0

        self.__turn(right, speed)
        t_speed_changed = t0
        z_speed_changed = z0

        motion.begin()
        while motion.get_angle_Z(right) > 180 or motion.get_angle_Z(right) < 1:
            motion.update()
        
        while motion.get_angle_Z(right) + error < angle and (time.time_ns() - t_start) < 2e9:
            motion.update()
            z_now = motion.get_angle_Z(right)
            t_now = time.time_ns()
            angle_to_target = angle - z_now

            delta_S = z_now - z0
            delta_T = t_now - t0            
            delta_V = delta_S / delta_T

            delta_V_changed = (z_now - z_speed_changed)/(t_now - t_speed_changed)
            if delta_V > 15e-8: #Delta speed value by detla angle (distance) / delta time that robot can control the precise angle, 100ms for 15 degree
                if angle_to_target < 15: #(15 * delta_V / 15e-8) : #15 is degree value that robot can control with speed: 15e-8
                    speed = 10
                    self.__turn(right, speed)
                    t_speed_changed = t_now
                    z_speed_changed = z_now
                else:
                    if delta_V > 40e-8: #Delta speed value is too fast need to slow down, 100ms for 40 degree
                        speed -= (speed - 10) / (angle_to_target / delta_S)
                        if speed < 10:
                            speed = 10
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

        self.stop()
        print("Time(ms):", (time.time_ns() - t_start) * 1e-6, motion.get_angle_Z(right))

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
    
    def stop(self):
        self.set_wheel_speed(0, 0)

    def stop_all(self):
        self.change_mode(ROBOT_MODE_DO_NOTHING)
        self.stop()
        speaker.stop()
        for i in range(8):
            servo.release(i)

robot = Robot()