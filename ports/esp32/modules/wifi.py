import time
from umqttsimple import MQTTClient, MQTTException
import ubinascii
import machine
import network
from utility import *

class Wifi:

    TOPIC_PREFIX = 'ohstem/'

    def __init__(self):
        self.station = None
        self.ap = None
        self.client = None
        self.message = ''
        self.topic = ''
        self.device_name = ''
        self.callbacks = {}

    def __on_receive_message(self, topic, msg):
        #print('Received: ', msg, topic)
        msg = msg.decode('ascii')
        topic = topic.decode('ascii')
        
        if callable(self.callbacks.get(topic)):
            self.callbacks.get(topic)(msg)

    def connect_wifi(self, ssid, password, wait_for_connected=True):
        say('Connecting to WiFi...')
        self.station = network.WLAN(network.STA_IF)
        if self.station.active():
            self.station.active(False)
            time.sleep_ms(500)

        for i in range(5):
          try:
              self.station.active(True)
              self.station.connect(ssid, password)
              break
          except OSError:
              self.station.active(False)
              time.sleep_ms(500)
              if i == 4:
                  say('Failed to connect to WiFi')
                  raise Exception('Failed to connect to WiFi')

        if wait_for_connected:
            count = 0
            while self.station.isconnected() == False:
                count = count + 1
                if count > 150:
                    say('Failed to connect to WiFi')
                    raise Exception('Failed to connect to WiFi')
                time.sleep_ms(100)

            say('Wifi connected. IP:' + self.station.ifconfig()[0])

    def isconnected(self):
        return self.station.isconnected()

    def start_wifi(self, wifi_name, password=None):
        if password and len(password) < 8:
          say('Wifi password too short')
          return

        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(False)
        time.sleep_ms(100)
        self.ap.active(True)
        self.ap.config(essid=wifi_name, password=password, authmode=network.AUTH_WPA_WPA2_PSK)

        while self.ap.active() == False:
            time.sleep_ms(100)

        print('Connection successful')
        print(self.ap.ifconfig())

    def connect(self, ssid, password, device_name, mqtt_server='broker.emqx.io', port=1883, username='', user_pass=''):
        client_id = str(ubinascii.hexlify(machine.unique_id())) + str(time.ticks_ms())
        self.connect_wifi(ssid, password, True)
        self.client = MQTTClient(client_id, mqtt_server, port, username, user_pass)
        self.client.set_callback(self.__on_receive_message)
        try:
            self.client.connect()
        except MQTTException:
            say('Failed to connect to server')

        self.device_name = device_name
        say('Connected to server')

    def check_message(self):
        if self.client == None:
            return
        try:
          self.client.check_msg()
        except Exception as err:
          say('Check message failed')
          time.sleep_ms(500)
          raise err
    
    def on_receive_message(self, topic, callback):
        full_topic = Wifi.TOPIC_PREFIX + self.device_name
        if str(topic):
            full_topic = full_topic + '/' + str(topic)

        self.callbacks[full_topic] = callback
        self.client.subscribe(full_topic)

    def send_message(self, topic, message):
        if self.client == None:
            return
        topic_pub = Wifi.TOPIC_PREFIX + self.device_name + '/' + topic
        self.client.publish(topic_pub, str(message))
  
wifi = Wifi()

def unit_test():    
    wifi.connect('Sandiego2', '0988807067', 'myyolo')
    wifi.send_message('myyolo', 'Hello. I am yolobit')

    def process(msg):
      print(msg)

    wifi.on_receive_message('V1', process)
    wifi.on_receive_message('', process)
    i = 0
    while True:
      wifi.check_message()
      wifi.send_message('V1', i)
      i += 1
      time.sleep(1)

if __name__ == '__main__':
    unit_test()

