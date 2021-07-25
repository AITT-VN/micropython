import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import network

class Wifi:

    TOPIC_PREFIX = 'xbot/'

    def __init__(self):
        self.client = None
        self.message = ''
        self.topic = ''
        self.device_name = ''
        self.callbacks = {}

    def __on_receive_message(self, topic, msg):
        #print((str(topic), str(msg)))
        msg = msg.decode('ascii')
        topic = topic.decode('ascii')
        if callable(self.callbacks.get(topic)):
            self.callbacks.get(topic)(msg)

    def connect(self, ssid, password, device_name, mqtt_server='broker.hivemq.com', port=1883, username='', user_pass=''):
        try:
            machine.freq(80000000)
        except:
            pass
        client_id = str(ubinascii.hexlify(machine.unique_id())) + str(time.ticks_ms())
        station = network.WLAN(network.STA_IF)
        station.active(True)
        station.connect(ssid, password)

        while station.isconnected() == False:
            time.sleep_ms(100)

        print('Connected to Wifi')
        print('Got IP address: ')
        print(station.ifconfig())

        self.client = MQTTClient(client_id, mqtt_server, port, username, user_pass)
        self.client.set_callback(self.__on_receive_message)
        self.client.connect()
        self.device_name = device_name
        print('Connected to MQTT broker')

    def check_message(self):
        if self.client == None:
            return
        self.client.check_msg()
    
    def on_receive_message(self, topic, callback):
        full_topic = Wifi.TOPIC_PREFIX + self.device_name
        if str(topic):
            full_topic = full_topic + '/' + str(topic)

        self.callbacks[full_topic] = callback
        self.client.subscribe(full_topic)

    def send_message(self, device_name, message):
        if self.client == None:
            return
        topic_pub = Wifi.TOPIC_PREFIX + device_name
        self.client.publish(topic_pub, str(message))
    
    def log_data(self, topic, message):
        if self.client == None:
            return
        topic = Wifi.TOPIC_PREFIX + self.device_name + '/' + topic
        self.client.publish(topic, str(message))
  
def unit_test():    
    from machine import Pin
    import time
    wifi = Wifi()
    wifi.connect('Sandiego', '0988807067', 'myyolo')
    wifi.send_message('myyolo', 'Hello. I am yolobit')

    def process(msg):
      print(msg)

    wifi.on_receive_message('message', process)
    i = 0
    while True:
      wifi.check_message()        
      wifi.log_data('temp', i)
      i += 1
      time.sleep(1)

__wifi__ = Wifi()
connect = __wifi__.connect
check_message = __wifi__.check_message
send_message = __wifi__.send_message
log_data = __wifi__.log_data
on_receive_message = __wifi__.on_receive_message

if __name__ == '__main__':
    unit_test()

