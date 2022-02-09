import time
from setting import *
import bluetooth
from micropython import const
from ble_broadcast import advertising_payload, decode_name

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)

_ADV_IND = const(0x00)
_ADV_DIRECT_IND = const(0x01)
_ADV_SCAN_IND = const(0x02)
_ADV_NONCONN_IND = const(0x03)

_UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX_CHAR_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX_CHAR_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")

_UART_TX = (
    _UART_TX_CHAR_UUID,
    bluetooth.FLAG_NOTIFY,
)
_UART_RX = (
    _UART_RX_CHAR_UUID,
    bluetooth.FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_SERVICE_UUID,
    (_UART_TX, _UART_RX),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_COMPUTER = const(128)

'''
# This class handle all bluetooth communication for robot. There are 2 modes:
# 1. Peripheral mode
# In this mode, device advertises itself with name and waits for other device 
# to connect to it, mostly used for ohstem app or remote controller or other device 
# connect to control it
#
# 2. Central mode
# In this mode, device will connect to other device, mostly used by user program to
# communication between 2 devices.
#
# The 2 modes are different so there are 2 set of functions for same operation like
# send data, process data and disconnect.

'''

class BLEUART:
    def __init__(self, ble_o, rxbuf=1024):
        self._ble = ble_o
        self._ble.active(True)
        self._ble.config(rxbuf=2048)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        # Increase the size of the rx buffer and enable append mode.
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = set()
        self._rx_buffer = bytearray()
        self._rx_none = bytearray()
        self._handler = None # callback for when new data is received
        self.on_connected = None # callback for when connected
        self.on_disconnected = None # callback for when disconnected
        self._name = None
        self._periph_connected = False

        self._last_sent = 0
        self._reset_central_mode()

    def _reset_central_mode(self):
        # Cached ble device name and address found from a successful scan.
        self._name_to_scan = None
        self._addr_type = None
        self._addr = None
        self._rssi = None

        # Callbacks for completion of various operations.
        # These reset back to None after being invoked.
        self._scan_callback = None
        self._conn_callback = None
        self._read_callback = None

        # Connected device.
        self._conn_central_handle = None
        self._start_central_handle = None
        self._end_central_handle = None
        self._tx_central_handle = None
        self._rx_central_handle = None

        self._central_connected = False

    def start(self, name=None, interval_us=100):
        # Optionally add services=[_UART_UUID], but this is likely to make the payload too large.
        if name != None:
            self._name = name
        self._ble.config(gap_name=self._name)
        self._payload = advertising_payload(name=self._name, appearance=_ADV_APPEARANCE_GENERIC_COMPUTER)
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def stop(self):
        self._ble.active(False)

    def irq(self, handler):
        self._handler = handler

    def _irq(self, event, data):
        ######## events for peripheral mode connection #############
        
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            self._periph_connected = True
            print('Connected by a central device')
            if self.on_connected:
                self.on_connected()

        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            self._periph_connected = False
            # Start advertising again to allow a new connection.
            self.start()
            print('Disconnected from central device')
            if self.on_disconnected:
                self.on_disconnected()

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                _val = self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler(_val)
        
        ######## events for central mode connection #############

        elif event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            print('Scan result: ', addr_type, addr, adv_type, rssi, adv_data)
            if adv_type in (_ADV_IND, _ADV_DIRECT_IND):
                _name_scanned = decode_name(adv_data) or "?"
                print('Found device: ', _name_scanned)
                if _name_scanned == self._name_to_scan:
                    print('Device found has name matched. Stop scanning and connect')
                    # Found a potential device, remember it and stop scanning.
                    self._addr_type = addr_type
                    self._addr = bytes(addr)  # Note: addr buffer is owned by caller so need to copy it.
                    self._ble.gap_scan(None)
                elif self._name_to_scan == None or self._name_to_scan == '': # scanning for nearby device case
                    # save for later
                    if self._rssi == None or self._rssi < rssi: # found nearer device
                        self._addr_type = addr_type
                        self._addr = bytes(addr)  # Note: addr buffer is owned by caller so need to copy it.
                        self._rssi = rssi

        elif event == _IRQ_SCAN_DONE:
            if self._scan_callback:
                if self._addr:
                    # Found a device during the scan (and the scan was explicitly stopped).
                    self._scan_callback(self._addr_type, self._addr, self._name_to_scan)
                    self._scan_callback = None
                else:
                    # Scan timed out.
                    self._scan_callback(None, None, None)

        elif event == _IRQ_PERIPHERAL_CONNECT:
            # Connect successful.
            print('Connected to periph device')
            conn_handle, addr_type, addr = data
            if addr_type == self._addr_type and addr == self._addr:
                self._conn_central_handle = conn_handle
                self._ble.gattc_discover_services(self._conn_central_handle)

        elif event == _IRQ_PERIPHERAL_DISCONNECT:
            # Disconnect (either initiated by us or the remote end).
            print('Disconnected to periph device')
            conn_handle, _, _ = data
            if conn_handle == self._conn_central_handle:
                # If it was initiated by us, it'll already be reset.
                self._reset_central_mode()
            if self.on_disconnected:
                self.on_disconnected()

        elif event == _IRQ_GATTC_SERVICE_RESULT:
            # Connected device returned a service.
            conn_handle, start_handle, end_handle, uuid = data
            #print("service", data)
            #print(uuid, _UART_SERVICE_UUID)
            if conn_handle == self._conn_central_handle and uuid == _UART_SERVICE_UUID:
                self._start_central_handle, self._end_central_handle = start_handle, end_handle
                self._central_connected = True

        elif event == _IRQ_GATTC_SERVICE_DONE:
            # Service query complete.
            if self._start_central_handle and self._end_central_handle:
                self._ble.gattc_discover_characteristics(
                    self._conn_central_handle, self._start_central_handle, self._end_central_handle
                )
            else:
                print("Failed to find uart service.")

        elif event == _IRQ_GATTC_CHARACTERISTIC_RESULT:
            # Connected device returned a characteristic.
            conn_handle, def_handle, value_handle, properties, uuid = data
            #print(uuid, _UART_RX_CHAR_UUID, _UART_TX_CHAR_UUID)
            if conn_handle == self._conn_central_handle and uuid == _UART_RX_CHAR_UUID:
                self._rx_central_handle = value_handle
            if conn_handle == self._conn_central_handle and uuid == _UART_TX_CHAR_UUID:
                self._tx_central_handle = value_handle

        elif event == _IRQ_GATTC_CHARACTERISTIC_DONE:
            # Characteristic query complete.
            if self._tx_central_handle is not None and self._rx_central_handle is not None:
                # We've finished connecting and discovering device, fire the connect callback.
                if self._conn_callback:
                    self._conn_callback()
                if self.on_connected:
                    self.on_connected()
            else:
                print("Failed to find uart rx characteristic.")

        #elif event == _IRQ_GATTC_WRITE_DONE:
        #    conn_handle, value_handle, status = data

        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, notify_data = data
            if conn_handle == self._conn_central_handle and value_handle == self._tx_central_handle:
                if self._handler:
                    self._handler(bytearray(notify_data))

    def send(self, data):
        if (time.ticks_ms() - self._last_sent) < 50: # avoid flooding send
            time.sleep_ms(50)
        if self._central_connected:
            # in central mode
            self.write_central(data)

        elif self._periph_connected:
            # in periph mode
            self.write_periph(data)
        else:
            return
        self._last_sent = time.ticks_ms()

    def write_periph(self, data): # send data, used for peripheral mode
        if not self._periph_connected:
            return
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._tx_handle, data)
    
    def write_central(self, v, response=False): # send data, used for central mode
        if not self._central_connected or self._conn_central_handle == None or self._rx_central_handle == None:
            # not connected yet
            return
        try:
            self._ble.gattc_write(self._conn_central_handle, self._rx_central_handle, v, 1 if response else 0)
        except:
            # something wrong when sending ble data which cannot be handled
            pass

    def disconnect_periph(self): # Disconnect, used for peripheral mode
        for conn_handle in self._connections:
            self._ble.gap_disconnect(conn_handle)
        self._connections.clear()

    def disconnect_central(self): # Disconnect, used for central mode
        if self._conn_central_handle is None:
            return
        self._ble.gap_disconnect(self._conn_central_handle)

    # Returns true if we've successfully connected and discovered characteristics.
    def is_connected(self):
        return self._central_connected or self._periph_connected

    # Find a device advertising the environmental sensor service.
    def scan(self, name, callback=None):
        self.disconnect_central()
        self._reset_central_mode()
        self._scan_callback = callback
        self._name_to_scan = name
        print('Scanning bluetooth devices...')
        self._ble.gap_scan(15000)

    # Connect to the specified device (otherwise use cached address from a scan).
    def connect(self, addr_type=None, addr=None, callback=None):
        self._addr_type = addr_type or self._addr_type
        self._addr = addr or self._addr
        self._conn_callback = callback
        if self._addr_type is None or self._addr is None:
            return False
        self._ble.gap_connect(self._addr_type, self._addr)
        return True
