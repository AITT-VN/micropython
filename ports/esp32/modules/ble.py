import os, time, struct
import bluetooth

from setting import *

from bleuart import BLEUART
from blerepl import BLEREPL

ble_o = bluetooth.BLE()

class BLE:
    def __init__(self):
        self._ble_uart = BLEUART(ble_o)
        self._ble_repl = BLEREPL(self)
        os.dupterm(self._ble_repl)
        self._rx_repl_buffer = bytearray()
        self._rx_usr_cmd_buffer = bytearray()

        # used to register callback for system command handling 
        self._on_received_sys_cmd = None
        self._callbacks = {}
        self._callbacks['number'] = {}
        self._callbacks['string'] = {}
        self._callbacks['name_value'] = {}
        
        # flag to know if device is in programming mode
        self._programming_mode = False
        # record time when flag is on, to turn off if stay on too long
        self._programming_mode_start_time = time.ticks_ms()

        self._ble_uart.irq(self._message_handler)

    # start bluetooth and advertise itself in peripheral mode
    def start(self, name=PRODUCT_NAME):
        self._ble_uart.start(name)

    # stop bluetooth
    def stop(self):
        self._ble_uart.stop()

    def _message_handler(self, data):
        if len(data) == 0:
            return

        try:
            if data[0] <= CMD_CTRL_D:
                # process ctrl A B C D
                self._rx_repl_buffer += data
                os.dupterm_notify(None)
            elif data[0] == CMD_SYS_PREFIX:
                # system defined command sent from app
                self._process_sys_cmd(data[1:])
            elif data[0] == CMD_PROG_START_PREFIX:
                # start flag of programming mode sent from app
                # when app sends new code to execute, app will send Ctrl + C to stop running code
                # and this may cause exception and deactivate dupterm
                # so we reset repl every time receiving new code to fix the issue
                self._ble_repl.reset_repl()

                self._programming_mode = True
                self._programming_mode_start_time = time.ticks_ms()
                if len(data) > 1:
                    self._rx_repl_buffer += data[1:]
                    os.dupterm_notify(None)
            elif data[0] == CMD_PROG_END_PREFIX:
                # end flag of programming mode sent from app
                self._programming_mode = False
            elif data[0] == CMD_USR_MSG_PREFIX:
                # user defined command sent from custom dashboard or other device
                #self._rx_usr_cmd_buffer = data[1:]
                #sz = len(self._rx_usr_cmd_buffer)
                result = data[1:]
                self._on_received_msg(result.decode('utf-8'))
            else:
                if self._programming_mode:
                    if time.ticks_ms() - self._programming_mode_start_time < PROGRAMMING_MODE_TIMEOUT:
                        self._rx_repl_buffer += data
                        os.dupterm_notify(None)
                    else:
                        # programming mode turned off too long, maybe problem happened
                        self._programming_mode = False
                        self._rx_usr_cmd_buffer = data
                else:
                    # ignore other message
                    pass
        except Exception as e:
            print('BLE crashed. Error:')
            print(e)

    def _process_sys_cmd(self, cmd):
        if cmd[0] == CMD_FIRMWARE_INFO:
            self._ble_uart.write_periph(ROBOT_DATA_RECV_SIGN + 'prd/' + PRODUCT_TYPE + '/' + VERSION + '/' + ROBOT_DATA_RECV_SIGN)
        else:
            if self._on_received_sys_cmd != None:
                self._on_received_sys_cmd(cmd)
            else:
                pass # ignore undefined command

    def _on_received_msg(self, msg):
        msg = str(msg)
        if self._callbacks['name_value']:
            name_value = msg.split('=')
            if len(name_value) > 1:
                try:
                    if '.' not in name_value[1]:
                        val = int(name_value[1])
                    else:
                        val = float(name_value[1])

                    self._callbacks['name_value'](name_value[0], val)
                    return
                except:
                    pass
        if self._callbacks['number']:
            try:
                if '.' not in msg:
                    number = int(msg)
                else:
                    number = float(msg)

                self._callbacks['number'](number)
                return
            except:
                pass

        if self._callbacks['string']:
            self._callbacks['string'](msg)

    def has_repl_data(self): # only used by blerepl
        return len(self._rx_repl_buffer)

    def get_repl_data(self, sz=None): # only used by blerepl
        if not sz:
            sz = len(self._rx_repl_buffer)
        result = self._rx_repl_buffer[0:sz]
        self._rx_repl_buffer = self._rx_repl_buffer[sz:]
        return result

    def on_received_sys_cmd(self, callback):
        self._on_received_sys_cmd = callback

    def on_receive_msg(self, type, callback):
        if type not in ['string', 'number', 'name_value']:
            print('Invalid event type')
            return

        self._callbacks[type] = callback

    def send(self, data):
        if not isinstance(data, bytearray) and not isinstance(data, str):
            data = str(data)
        self._ble_uart.send(struct.pack('B',CMD_USR_MSG_PREFIX) + data)

    def send_value(self, name, value):
        name = str(name)
        value = str(value)
        self._ble_uart.send(struct.pack('B',CMD_USR_MSG_PREFIX) + name + '=' + value)

    def send_periph(self, data): # only used for peripheral mode, not exposed to user
        self._ble_uart.write_periph(data)

    # scan and connect to device which has given name 
    # used for central mode, exposed to user
    def connect(self, device):
        not_found = False

        def on_scan(addr_type, addr, name):
            #print(addr_type, addr, name)
            if addr_type is not None:
                self._ble_uart.connect()
            else:
                nonlocal not_found
                not_found = True
                print("No peripheral found.")

        self._ble_uart.scan(name=device, callback=on_scan)

        # Wait for scan completed and connection established
        timeout = 150
        while not self._ble_uart.is_connected() and timeout > 0:
            time.sleep_ms(100)
            if not_found:
                return False
            timeout -= 1

        if timeout == 0:
            print("Failed to scan and connect to periph device")
            return False

        return True

    # connect to any nearby ble device
    # used for central mode, exposed to user
    def connect_nearby(self):
        not_found = False

        def on_scan(addr_type, addr, name):
            #print(addr_type, addr, name)
            if addr_type is not None:
                self._ble_uart.connect()
            else:
                nonlocal not_found
                not_found = True
                print("No peripheral found.")

        self._ble_uart.scan(name='', callback=on_scan)

        # Wait for scan completed and connection established
        timeout = 150
        while not self._ble_uart.is_connected() and timeout > 0:
            time.sleep_ms(100)
            if not_found:
                return False
            timeout -= 1

        if timeout == 0:
            print("Failed to scan and connect to periph device")
            return False

        return True
    
    def is_connected(self):
        return self._ble_uart.is_connected()

    def disconnect(self):
        self._ble_uart.disconnect_central()
        self._ble_uart.disconnect_periph()

    def on_connected(self, callback):
        self._ble_uart.on_connected = callback

    def on_disconnected(self, callback):
        self._ble_uart.on_disconnected = callback

ble = BLE() 