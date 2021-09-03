import machine
import struct
import time
from micropython import const

from setting import PORTS_DIGITAL
from utility import say

class SX1590def:
    RegInputDisableB  = const(0x00)
    RegInputDisableA  = const(0x01)
    RegPullUpB        = const(0x06)
    RegPullUpA        = const(0x07)
    RegOpenDrainB     = const(0x0A)
    RegOpenDrainA     = const(0x0B)
    RegPolarityB      = const(0x0C)
    RegPolarityA      = const(0x0D)
    RegDirB           = const(0x0E)
    RegDirA           = const(0x0F)
    RegDataB          = const(0x10)
    RegDataA          = const(0x11)
    RegInterruptMaskA = const(0x13)
    RegClock            = const(0x1E)
    RegMisc             = const(0x1F)
    RegLEDDriverEnableB = const(0x20)
    RegLEDDriverEnableA = const(0x21)

    RegReset   = const(0x7D)
    RegTest1   = const(0x7E)
    RegTest2   = const(0x7F)

    INTERNAL_CLOCK_2MHZ = const(2)
    ANALOG_OUTPUT = const(0x3)
    OUTPUT = const(2)
    INPUT_PULLUP = const(3)
    LedLinear = const(0)
    LedLogarithmic = const(1)
    SLAVE_ADDRESS = const(0x3E)
    HIGH = const(255)
    LOW  = const(0)
    pinRESET = const(-1)

    _REG_T_ON_0 = const(0x29)    #  RegTOn0 ON time register for I/O[0] 0000 0000
    _REG_I_ON_0 = const(0x2A)    #  RegIOn0 ON intensity register for I/O[0] 1111 1111
    _REG_OFF_0  = const(0x2B)    #  RegOff0 OFF time/intensity register for I/O[0] 0000 0000
    _REG_T_ON_1 = const(0x2C)    #  RegTOn1 ON time register for I/O[1] 0000 0000
    _REG_I_ON_1 = const(0x2D)    #  RegIOn1 ON intensity register for I/O[1] 1111 1111
    _REG_OFF_1  = const(0x2E)    #  RegOff1 OFF time/intensity register for I/O[1] 0000 0000
    _REG_T_ON_2 = const(0x2F)    #  RegTOn2 ON time register for I/O[2] 0000 0000
    _REG_I_ON_2 = const(0x30)    #  RegIOn2 ON intensity register for I/O[2] 1111 1111
    _REG_OFF_2  = const(0x31)    #  RegOff2 OFF time/intensity register for I/O[2] 0000 0000
    _REG_T_ON_3 = const(0x32)    #  RegTOn3 ON time register for I/O[3] 0000 0000
    _REG_I_ON_3 = const(0x33)    #  RegIOn3 ON intensity register for I/O[3] 1111 1111
    _REG_OFF_3  = const(0x34)    #  RegOff3 OFF time/intensity register for I/O[3] 0000 0000
    _REG_T_ON_4 = const(0x35)    #  RegTOn4 ON time register for I/O[4] 0000 0000
    _REG_I_ON_4 = const(0x36)    #  RegIOn4 ON intensity register for I/O[4] 1111 1111
    _REG_OFF_4  = const(0x37)    #  RegOff4 OFF time/intensity register for I/O[4] 0000 0000
    _REG_T_RISE_4  = const(0x38)    #  RegTRise4 Fade in register for I/O[4] 0000 0000
    _REG_T_FALL_4  = const(0x39)    #  RegTFall4 Fade out register for I/O[4] 0000 0000
    _REG_T_ON_5    = const(0x3A)    #  RegTOn5 ON time register for I/O[5] 0000 0000
    _REG_I_ON_5    = const(0x3B)    #  RegIOn5 ON intensity register for I/O[5] 1111 1111
    _REG_OFF_5     = const(0x3C)    #  RegOff5 OFF time/intensity register for I/O[5] 0000 0000
    _REG_T_RISE_5  = const(0x3D)    #  RegTRise5 Fade in register for I/O[5] 0000 0000
    _REG_T_FALL_5  = const(0x3E)    #  RegTFall5 Fade out register for I/O[5] 0000 0000
    _REG_T_ON_6    = const(0x3F)    #  RegTOn6 ON time register for I/O[6] 0000 0000
    _REG_I_ON_6    = const(0x40)    #  RegIOn6 ON intensity register for I/O[6] 1111 1111
    _REG_OFF_6     = const(0x41)    #  RegOff6 OFF time/intensity register for I/O[6] 0000 0000
    _REG_T_RISE_6  = const(0x42)    #  RegTRise6 Fade in register for I/O[6] 0000 0000
    _REG_T_FALL_6  = const(0x43)    #  RegTFall6 Fade out register for I/O[6] 0000 0000
    _REG_T_ON_7    = const(0x44)    #  RegTOn7 ON time register for I/O[7] 0000 0000
    _REG_I_ON_7    = const(0x45)    #  RegIOn7 ON intensity register for I/O[7] 1111 1111
    _REG_OFF_7     = const(0x46)    #  RegOff7 OFF time/intensity register for I/O[7] 0000 0000
    _REG_T_RISE_7  = const(0x47)    #  RegTRise7 Fade in register for I/O[7] 0000 0000
    _REG_T_FALL_7  = const(0x48)    #  RegTFall7 Fade out register for I/O[7] 0000 0000
    _REG_T_ON_8    = const(0x49)    #  RegTOn8 ON time register for I/O[8] 0000 0000
    _REG_I_ON_8    = const(0x4A)    #  RegIOn8 ON intensity register for I/O[8] 1111 1111
    _REG_OFF_8     = const(0x4B)    #  RegOff8 OFF time/intensity register for I/O[8] 0000 0000
    _REG_T_ON_9    = const(0x4C)    #  RegTOn9 ON time register for I/O[9] 0000 0000
    _REG_I_ON_9    = const(0x4D)    #  RegIOn9 ON intensity register for I/O[9] 1111 1111
    _REG_OFF_9     = const(0x4E)    #  RegOff9 OFF time/intensity register for I/O[9] 0000 0000
    _REG_T_ON_10   = const(0x4F)    #  RegTOn10 ON time register for I/O[10] 0000 0000
    _REG_I_ON_10   = const(0x50)    #  RegIOn10 ON intensity register for I/O[10] 1111 1111
    _REG_OFF_10    = const(0x51)    #  RegOff10 OFF time/intensity register for I/O[10] 0000 0000
    _REG_T_ON_11   = const(0x52)    #  RegTOn11 ON time register for I/O[11] 0000 0000
    _REG_I_ON_11   = const(0x53)    #  RegIOn11 ON intensity register for I/O[11] 1111 1111
    _REG_OFF_11    = const(0x54)    #  RegOff11 OFF time/intensity register for I/O[11] 0000 0000
    _REG_T_ON_12   = const(0x55)    #  RegTOn12 ON time register for I/O[12] 0000 0000
    _REG_I_ON_12   = const(0x56)    #  RegIOn12 ON intensity register for I/O[12] 1111 1111
    _REG_OFF_12    = const(0x57)    #  RegOff12 OFF time/intensity register for I/O[12] 0000 0000
    _REG_T_RISE_12 = const(0x58)    #  RegTRise12 Fade in register for I/O[12] 0000 0000
    _REG_T_FALL_12 = const(0x59)    #  RegTFall12 Fade out register for I/O[12] 0000 0000
    _REG_T_ON_13   = const(0x5A)    #  RegTOn13 ON time register for I/O[13] 0000 0000
    _REG_I_ON_13   = const(0x5B)    #  RegIOn13 ON intensity register for I/O[13] 1111 1111
    _REG_OFF_13    = const(0x5C)    #  RegOff13 OFF time/intensity register for I/O[13] 0000 0000
    _REG_T_RISE_13 = const(0x5D)    #  RegTRise13 Fade in register for I/O[13] 0000 0000
    _REG_T_FALL_13 = const(0x5E)    #  RegTFall13 Fade out register for I/O[13] 0000 0000
    _REG_T_ON_14   = const(0x5F)    #  RegTOn14 ON time register for I/O[14] 0000 0000
    _REG_I_ON_14   = const(0x60)    #  RegIOn14 ON intensity register for I/O[14] 1111 1111
    _REG_OFF_14    = const(0x61)    #  RegOff14 OFF time/intensity register for I/O[14] 0000 0000
    _REG_T_RISE_14 = const(0x62)    #  RegTRise14 Fade in register for I/O[14] 0000 0000
    _REG_T_FALL_14 = const(0x63)    #  RegTFall14 Fade out register for I/O[14] 0000 0000
    _REG_T_ON_15   = const(0x64)    #  RegTOn15 ON time register for I/O[15] 0000 0000
    _REG_I_ON_15   = const(0x65)    #  RegIOn15 ON intensity register for I/O[15] 1111 1111
    _REG_OFF_15    = const(0x66)    #  RegOff15 OFF time/intensity register for I/O[15] 0000 0000
    _REG_T_RISE_15 = const(0x67)    #  RegTRise15 Fade in register for I/O[15] 0000 0000
    _REG_T_FALL_15 = const(0x68)    #  RegTFall15 Fade out register for I/O[15] 0000 0000


    def __init__(self):

        self.RegIOn = [_REG_I_ON_0, _REG_I_ON_1, _REG_I_ON_2, _REG_I_ON_3,
                            _REG_I_ON_4, _REG_I_ON_5, _REG_I_ON_6, _REG_I_ON_7,
                            _REG_I_ON_8, _REG_I_ON_9, _REG_I_ON_10, _REG_I_ON_11,
                            _REG_I_ON_12, _REG_I_ON_13, _REG_I_ON_14, _REG_I_ON_15]

        self.RegTOn = [_REG_T_ON_0, _REG_T_ON_1, _REG_T_ON_2, _REG_T_ON_3,
                            _REG_T_ON_4, _REG_T_ON_5, _REG_T_ON_6, _REG_T_ON_7,
                            _REG_T_ON_8, _REG_T_ON_9, _REG_T_ON_10, _REG_T_ON_11,
                            _REG_T_ON_12, _REG_T_ON_13, _REG_T_ON_14, _REG_T_ON_15]


        self.RegOff = [_REG_OFF_0, _REG_OFF_1, _REG_OFF_2, _REG_OFF_3,
                            _REG_OFF_4, _REG_OFF_5, _REG_OFF_6, _REG_OFF_7,
                            _REG_OFF_8, _REG_OFF_9, _REG_OFF_10, _REG_OFF_11,
                            _REG_OFF_12, _REG_OFF_13, _REG_OFF_14, _REG_OFF_15]


        self.RegTRise = [0xFF, 0xFF, 0xFF, 0xFF,
                        _REG_T_RISE_4, _REG_T_RISE_5, _REG_T_RISE_6, _REG_T_RISE_7,
                        0xFF, 0xFF, 0xFF, 0xFF,
                        _REG_T_RISE_12, _REG_T_RISE_13, _REG_T_RISE_14, _REG_T_RISE_15]


        self.RegTFall = [0xFF, 0xFF, 0xFF, 0xFF,
                        _REG_T_FALL_4, _REG_T_FALL_5, _REG_T_FALL_6, _REG_T_FALL_7,
                        0xFF, 0xFF, 0xFF, 0xFF,
                        _REG_T_FALL_12, _REG_T_FALL_13, _REG_T_FALL_14, _REG_T_FALL_15]


class SX1509:
    defs = SX1590def()
    
    def __init__(self, port, addr=0x3e):
        # Grove port: GND VCC SCL SDA
        scl_pin = machine.Pin(PORTS_DIGITAL[port][0])
        sda_pin = machine.Pin(PORTS_DIGITAL[port][1])
        self._i2c = machine.SoftI2C(scl=scl_pin, sda=sda_pin)
        self._addr = addr
        self._buf1 = bytearray(2)
        if self._i2c.scan().count(addr) == 0:
            say('SX1509 not found')
            raise OSError('SX1509 not found at I2C addr {:#x}'.format(addr))

        tstReg = self._readWord(self.defs.RegInterruptMaskA) # This should return 0xFF00
        if tstReg == 0xFF00:
            # Set the clock to a default of 2MHz using internal
            self._clock(self.defs.INTERNAL_CLOCK_2MHZ)
        else:
            say("SX1509 init failed.")
            raise OSError("SX1509 init failed.")


    def _write(self, addr, val):
        self._i2c.writeto_mem(self._addr, addr, int(val).to_bytes(1, "little"))


    def _ledDriverInit(self, pin, freq=1, log=False):
        tempWord = 0
        tempByte = bytes(0)
        
        tempWord = self._readWord(self.defs.RegInputDisableB)
        tempWord |= (1<<pin)
        
        #Disable pull-up
        tempWord = self._readWord(self.defs.RegPullUpB)
        tempWord |= (1<<pin)        
        self._writeWord(addr=self.defs.RegPullUpB, val=tempWord)
        
        # Set direction to output (REG_DIR_B)
        tempWord = self._readWord(self.defs.RegDirB)
        tempWord &= ~(1<<pin); #0=output  
        self._writeWord(addr=self.defs.RegDirB, val=tempWord)

        # Enable oscillator (REG_CLOCK)
        tempByte = self._readByte(self.defs.RegClock)
        tempByte |= (1<<6) # Internal 2MHz oscillator part 1 (set bit 6)
        tempByte &= ~(1<<5)    # Internal 2MHz oscillator part 2 (clear bit 5)
        self._writeByte(self.defs.RegClock, tempByte)


    def _read(self, addr):
        readMem = self._i2c.readfrom_mem_into(self._addr, addr, self._buf1)
        return readMem


    def _pindir(self, pin, inOut):
        modeBit = False
        
        if ((inOut == self.defs.OUTPUT) or (inOut == self.defs.ANALOG_OUTPUT)):
            modeBit = False
        else:
            modeBit = True

        tempRegDir = self._readWord(addr=self.defs.RegDirB)
        if (modeBit):
            tempRegDir = (1<<pin)
        else:
            tempRegDir &= ~(1<<pin)

        self._writeWord(addr=self.defs.RegDirB, val=tempRegDir)

        # If INPUT_PULLUP was called, set up the pullup too:
        if (inOut == self.defs.INPUT_PULLUP):
            self._writePin(pin, self.defs.HIGH)
        
        if (inOut == self.defs.ANALOG_OUTPUT):
            self._ledDriverInit(pin)


    def pwm(self, pin, iOn):
        '''Write the on intensity of pin
        Linear mode: Ion = iOn
        Log mode: Ion = f(iOn)'''
        self._writeByte(self.defs.RegIOn[pin], iOn)


    def __pwm__nietgebruiken(self, index, on=None, off=None):
        if(on is None or off is None):
            data = self._i2c.readfrom_mem(self.addr, 0x06 + 4 * index, 4)
            return struct.unpack('<HH', data)
        data = struct.pack('<HH', on, off)
        self._i2c.writeto_mem(self.addr, 0x06 + 4 * index,  int(val).to_bytes(data, "little"))


    def debounceEnable(self, pin):
        debounceEnable = self._read(addr=self.defs.RegDebounceEnableB)
        debounceEnable |= (1<<pin)
        self._write(addr=self.defs.RegDEBOUNCE_ENABLE_B, val=debounceEnable)
        

    def reset(self, hard=True):        
        if(hard):
            regMisc = self._readWord(self.defs.RegMisc)            
            if (regMisc & (1<<2)):
                regMisc &= ~(1<<2)
                self._writeWord(self.defs.RegMisc, regMisc)
            
            rstPin = self.defs.pinRESET
            self.pinMode(rstPin, self.defs.OUTPUT)
            self.digitalWrite(rstPin, self.defs.LOW)
            time.delay_ms(1)
            self.digitalWrite(rstPin, self.defs.HIGH)
        else:            
            self._writeWord(self.defs.RegReset, 0x12)
            self._writeWord(self.defs.RegReset, 0x34)


    def _writeWord(self, addr, val):
        lsb = bytes(0)
        msb = bytes(0)
        msb = ((int(val) & 0xFF00) >> 8)
        lsb = (int(val) & 0xFF00)
        self._i2c.writeto_mem(self._addr, addr, lsb.to_bytes(1, "little"))
        self._i2c.writeto_mem(self._addr, addr, msb.to_bytes(1, "little"))


    def _writeByte(self, addr, val):
        self._i2c.writeto_mem(self._addr, addr, (val).to_bytes(1, "big"))

    def _readWord(self, addr):
        self._i2c.writeto(self._addr, (0).to_bytes(1, "big"))
        rec1 = self._i2c.readfrom_mem(self._addr, addr, 2)
        return struct.unpack('>H', rec1)[0]


    def _readByte(self, addr):
        val = self._i2c.readfrom_mem(self._addr, addr, 1)
        return val[0]

    def _configClock(self, oscSource= 2, oscPinFunction= 0, oscFreqOut= 0, oscDivider= 1):
        # RegClock constructed as follows:
        #  6:5 - Oscillator frequency souce
        #    00: off, 01: external input, 10: internal 2MHz, 1: reserved
        #  4 - OSCIO pin function
        #    0: input, 1 ouptut
        #  3:0 - Frequency of oscout pin
        #    0: LOW, 0xF: high, else fOSCOUT = FoSC/(2^(RegClock[3:0]-1))
        oscSource = (oscSource & 0b11) << 5 # 2-bit value, bits 6:5
        oscPinFunction = (oscPinFunction & 1)<<4 # 1-bit value bit 4
        oscFreqOut = (oscFreqOut & 0b1111) # 4-bit value, bits 3:0
        regClock = oscSource | oscPinFunction | oscFreqOut
        self._writeByte(self.defs.RegClock, regClock)
        
        # Config RegMisc[6:4] with oscDivider
        # 0: off, else ClkX = fOSC / (2^(RegMisc[6:4] -1))
        #oscDivider = constrain(oscDivider, 1, 7)
        _clkX = 2000000.0 / (1<<(oscDivider - 1)) #; # Update private clock variable
        oscDivider = (oscDivider & 0b111)<<4 #;  # 3-bit value, bits 6:4
        
        regMisc = self._readByte(self.defs.RegMisc)
        regMisc &= ~(0b111<<4)
        regMisc |= oscDivider
        self._writeByte(self.defs.RegMisc, regMisc)
    
    def _clock(self, oscSource= 2, oscPinFunction= 0, oscFreqOut= 0, oscDivider= 1):
        self._configClock(oscSource, oscPinFunction, oscFreqOut, oscDivider)


    def _pinDir(self, pin, inOut):
        modeBit = bytes(0)

        if ((inOut == self.defs.OUTPUT) or (inOut == self.defs.ANALOG_OUTPUT)):
            modeBit = False
        else:
            modeBit = True
            
        tempRegDir = self._readWord(addr=self.defs.RegDirB)
        if (modeBit):    
            tempRegDir |= (1<<pin)
        else:
            tempRegDir &= ~(1<<pin)
        
        self._writeWord(self.defs.RegDirB, tempRegDir)

        #If INPUT_PULLUP was called, set up the pullup too:
        if (inOut == self.defs.INPUT_PULLUP):
            self._writePin(pin, self.defs.HIGH)

        if (inOut == self.defs.ANALOG_OUTPUT):
            self._ledDriverInit(pin)

    def _readPin(self, pin):
        tempRegDir = self._readWord(addr=self.defs.RegDirB)
        # print("readPin:", pin ," tempRegDir=", tempRegDir)
        
        if (tempRegDir & (1<<pin)):  # If the pin is an input
            tempRegData = self._readWord(addr=self.defs.RegDataB)
            if (tempRegData & (1<<pin)):
                return 1
        return 0
    
    def _writePin(self, pin, highLow):
        tempRegDir = self._readWord(addr=self.defs.RegDirB)
        #print("_writePin. tempRegDir=", tempRegDir)

        if ((0xFFFF^tempRegDir)&(1<<pin)): #output mode
            tempRegData = self._readWord(self.defs.RegDataB)

            if (highLow):
                tempRegData |= (1<<pin)
            else:
                tempRegData &= ~(1<<pin)
            
            self._writeWord(self.defs.RegDataB, tempRegData)

    def pinMode(self, pin, inOut):
        self._pinDir(pin, inOut)

    def digitalRead(self, pin):
        return self._readPin(pin)
    
    def digitalWrite(self, pin, highLow):
        self._writePin(pin, highLow)

    def analogWrite(self, pin, iOn):
        self.pwm(pin, iOn)
