import time
import math
from utility import *
from motor import motor

PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47
TEMP_OUT_H   = 0X41

class Motion:
    def __init__(self, i2c, address=0x68):
        self._i2c = i2c
        self._addr = address

        #Close the sleep mode
        #Write to power management register to wake up mpu6050
        self.__register(PWR_MGMT_1, 0)

        #configurate the digital low pass filter
        self.__register(CONFIG, 1)

        
        #set the gyro scale to 500 deg/s: 250 deg/s (131) --> 0x00, 500 deg/s (65.5) --> 0x08, 1000 deg/s (32.8) --> 0x10, 2000 deg/s (16.4)--> 0x18
        self.__register(GYRO_CONFIG, 0x08)
        self.scaleFactorGyro = 500.0 / 32768.0 #for 500 deg/s, check data sheet 65.536

        #set the accelerometer scale to 4g: 2g (16384)--> 0x00, 4g (8192)--> 0x08, 8g (4096) --> 0x10, 16g (2048)--> 0x18
        self.__register(ACCEL_CONFIG, 0x08)
        self.scaleFactorAccel = 4.0 / 32768.0 #for 4g, check data sheet

        #Set interrupt enable register to 0 .. disable interrupts
        #self.__register(INT_ENABLE, 0x00)

        self.calibrate()

    def __register(self, reg, data): #Write the registor of i2c device.
        self._i2c.start()
        self._i2c.writeto(self._addr, bytearray([reg, data]))
        self._i2c.stop()

    def __bytes_toint(self, firstbyte, secondbyte):
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def __read_raw_data(self, addr, size):
        self._i2c.start()
        try:
            a = self._i2c.readfrom_mem(self._addr, addr, size)
        except:
            time.sleep_ms(10)
            try:
                a = self._i2c.readfrom_mem(self._addr, addr, size)
            except:
                a = [0] * size

        self._i2c.stop()
        return a

    def __get_raw_value(self, name=None):
        if name == None:
            raw_ints = self.__read_raw_data(ACCEL_XOUT_H, 14)
            vals = {}
            vals["AcX"] = self.__bytes_toint(raw_ints[0], raw_ints[1])
            vals["AcY"] = self.__bytes_toint(raw_ints[2], raw_ints[3])
            vals["AcZ"] = self.__bytes_toint(raw_ints[4], raw_ints[5])
            vals["Tmp"] = self.__bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
            vals["GyX"] = self.__bytes_toint(raw_ints[8], raw_ints[9])
            vals["GyY"] = self.__bytes_toint(raw_ints[10], raw_ints[11])
            vals["GyZ"] = self.__bytes_toint(raw_ints[12], raw_ints[13])
            return vals

        a = [0,0]
        if (name == 'GyZ'):
            a = self.__read_raw_data(GYRO_ZOUT_H, 2)
        elif name == 'GyY':
            a = self.__read_raw_data(GYRO_YOUT_H, 2)
        elif name == 'GyX':
            a = self.__read_raw_data(GYRO_XOUT_H, 2)
        elif name == 'AcX':
            a = self.__read_raw_data(ACCEL_XOUT_H, 2)
        elif name == 'AcY':
            a = self.__read_raw_data(ACCEL_YOUT_H, 2)
        elif name == 'AcZ':
            a = self.__read_raw_data(ACCEL_ZOUT_H, 2)
        return self.__bytes_toint(a[0], a[1])
    
    def __get_value(self, name=None, n_sample=1, sleep=0):
        if name == None:
            vals = {}
            vals['AcX'] = vals['AcY'] = vals['AcZ'] = vals['GyX'] = vals['GyY'] = vals['GyZ'] = 0.0 
            for i in range(n_sample):
                data = self.__get_raw_value()
                vals['AcX'] += data['AcX'] * self.scaleFactorAccel / n_sample
                vals['AcY'] += data['AcY'] * self.scaleFactorAccel / n_sample
                vals['AcZ'] += data['AcZ'] * self.scaleFactorAccel / n_sample
                vals['GyX'] += data['GyX'] * self.scaleFactorGyro / n_sample
                vals['GyY'] += data['GyY'] * self.scaleFactorGyro / n_sample
                vals['GyZ'] += data['GyZ'] * self.scaleFactorGyro / n_sample
                if sleep:
                    time.sleep_ms(sleep)
            return vals
        val = 0.0
        for i in range(n_sample):
            val += self.__get_raw_value(name) / n_sample
            if sleep:
                time.sleep_ms(sleep)

        if name == 'AcX' or name == 'AcY' or name == 'AcZ':
            val = val * self.scaleFactorAccel
        else:
            val = val * self.scaleFactorGyro

        return val

    def begin(self):
        self.angleZ = 0.0
        self.update_time = time.time_ns()
        self.dt = 0.0
    
    def calibrate(self, n_sample=5000): #calibrate for gyroZ only
        self.gyroZoffs = self.__get_value('GyZ', n_sample)

    def calibrate_all(self, n_sample=5000, sleep=0): #calibrate for z angle only
        data = self.__get_value(None, n_sample, sleep)
        self.acXoffs = data['AcX']
        self.acYoffs = data['AcY']
        self.acZoffs = data['AcZ']
        self.gyroXoffs = data['GyX']
        self.gyroYoffs = data['GyY']
        self.gyroZoffs = data['GyZ']

        
    def update(self):
        t_now = time.time_ns()
        gyrZ = self.__get_value('GyZ') - self.gyroZoffs
        dt = (t_now - self.update_time) * 1e-9
        self.update_time = t_now
        self.dt += dt

        self.angleZ = self.angleZ + gyrZ * dt
        self.angleZ = self.angleZ - 360 * math.floor(self.angleZ / 360)

    def begin_all(self):
        self.angleX = 0.0
        self.angleY = 0.0
        self.angleZ = 0.0
        self.dt = 0.0
        self.update_time = time.time_ns()
    def update_all(self):
        t_now = time.time_ns()
        data = self.__get_value()
        #The accelerometer data is reliable only on the long term, so a "low pass" filter has to be used.
        #The gyroscope data is reliable only on the short term, as it starts to drift on the long term.
        accX = data['AcX']
        accY = data['AcY']
        accZ = data['AcZ']
        gyrX = data['GyX'] - self.gyroXoffs
        gyrY = data['GyY'] - self.gyroYoffs
        gyrZ = data['GyZ'] - self.gyroZoffs

        ax = math.atan2(accX, math.sqrt( math.pow(accY, 2) + math.pow(accZ, 2) ) ) * 180 / 3.1415926
        ay = math.atan2(accY, math.sqrt( math.pow(accX, 2) + math.pow(accZ, 2) ) ) * 180 / 3.1415926
        az = math.atan2(math.sqrt( math.pow(accX, 2) + math.pow(accY, 2) ), accZ ) * 180 / 3.1415926
        
        dt = (t_now - self.update_time) * 1e-9
        self.update_time = t_now
        self.dt += dt

        if accZ > 0:
          self.angleX = self.angleX - gyrY * dt
          self.angleY = self.angleY + gyrX * dt
        else :
          self.angleX = self.angleX + gyrY * dt
          self.angleY = self.angleY - gyrX * dt

        self.angleZ = self.angleZ + gyrZ * dt

        # complementary filter
        # set 0.5sec = tau = dt * A / (1 - A)
        # so A = tau / (tau + dt)
        filter_coefficient = 0.5 / (0.5 + dt)
        self.angleX = self.angleX * filter_coefficient + ax * (1 - filter_coefficient)
        self.angleY = self.angleY * filter_coefficient + ay * (1 - filter_coefficient)         
        self.angleZ = self.angleZ * filter_coefficient + az * (1 - filter_coefficient)         
        
        self.angleZ = self.angleZ - 360 * math.floor(self.angleZ / 360)
        self.accelerometer =  math.sqrt(accX*accX + accY*accY + accZ*accZ)

    def get_accelerometer(self):
        return self.accelerometer

    def get_angle_X(self):      
        return self.angleX

    def get_angle_Y(self):
        return self.angleY

    def get_angle_Z(self, right=True): #by default angleZ returns value from 0 to 360 in anti-clockwise
        z = self.angleZ
        if right: #right is clockwise
            z = 360 - self.angleZ

        return z
    
    def get_gyro_roll(self):
        return self.__get_value('GyX', 10)

    def get_gyro_pitch(self):
        return self.__get_value('GyY', 10)

    def get_gyro_yaw(self):
        return self.__get_value('GyZ', 10)

    def get_accel(self, name):
        if name == 'x':
            return self.get_accel_x()
        if name == 'y':
            return self.get_accel_y()
        return self.get_accel_z()

    def get_accel_x(self):
        return self.__get_value('AcX', 10)

    def get_accel_y(self):
        return self.__get_value('AcY', 10)

    def get_accel_z(self):
        return self.__get_value('AcZ', 10)

    def is_shaked(self, shake_threshold = 0.05):
        data = self.__get_value(None, 10)
        accX = data['AcX']
        accY = data['AcY']
        accZ = data['AcZ']
        return abs((math.sqrt(accX * accX + accY * accY + accZ * accZ) - 1)) > shake_threshold

motion = Motion(i2c)