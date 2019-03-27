import time

import paho.mqtt.client as mqtt

from logger import log
from smart_grid_messaging import *


# Mysensors protocol types
# ref https://www.mysensors.org/download/serial_api_20
class MySenTypes:
    S_CUSTOM = 23
    V_VAR1 = 24
    V_VAR2 = 25
    V_VAR3 = 26
    V_VAR4 = 27
    V_VAR5 = 28
    V_RGB = 40

    @staticmethod
    def types():
        return vars(MySenTypes).values()

    @staticmethod
    def my_sen_type_to_smart_grid_type(mysen):
        d = {
            MySenTypes.S_CUSTOM: MessageTypes.TABLE_CONNECTED,
            MySenTypes.V_VAR2: MessageTypes.MODULE_PLACED,
            MySenTypes.V_VAR3: MessageTypes.NEIGHBOR_CHANGED
        }
        return d.get(mysen, -1)


class MySenCommands:
    PRESENT, SET, REQ, INTERNAL, STREAM = range(5)

    @staticmethod
    def types():
        return vars(MySenCommands).values()


class MySenMessage(object):

    def __init__(self, node_id, child_id, command, ack, type, payload):
        self.node_id = node_id
        self.child_id = child_id
        self.command = command
        self.ack = ack
        self.type = type
        self.payload = int(payload) if payload.isdigit() else payload

    def __repr__(self):
        return 'command {0}, type {1}, payload {2}'.format(self.command, self.type, self.payload)


class GatewayConnector(object):

    def __init__(self, message_func):
        self.message_func = message_func
        self.mqtt_topic_subscribe = 'sendToPc/#'         # '/#' to subscribe on all devices connected
        self.mqtt_topic_publish = 'getFromPc/0/0/0/0/0'     #To enable received by devices connected
        self.mqtt_client = self.create_mqtt_client()
    
    def create_mqtt_client(self):
        #Configure the client mqtt
        client = mqtt.Client()
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = self.handle_incoming_message
        mqtt_client.connect('localhost', 1883)
        mqtt_client.loop_start()
        return client
    
    def on_connect(client, userdata, flags, rc):
        # rc is the error code returned when connecting to the broker

        log('Connected on MQTT broker!'+str(rc))
        client.subscribe(mqtt_topic_subscribe)
    
    def send_serial_message(self, table_section_id, payload, command, type, child_id=0):
        message = '{0};{1};{2};0;{3};{4}\n'.format(
            table_section_id, child_id, command, type, payload)
        self.mqtt_client.publish(self.mqtt_topic_publish, message)

    def handle_incoming_message(self, client, userdata, data_line):
        message = self.validate_data(data_line)
        if message.node_id is 0:
            log('from gateway: ', message)
        elif message.command in MySenCommands.types() and message.type in MySenTypes.types():
            s_message = SmartMessage(
                MySenTypes.my_sen_type_to_smart_grid_type(message.type),
                (message.node_id, message.child_id, message.payload)
            )
            self.message_func(s_message)
        else:
            log('Unknown message received ' + data_line)

    @staticmethod
    def validate_data(data_line):
        data_line = data_line.decode('utf-8')
        data_array = data_line.split(';')

        # Check if data contains 6 elements and ends with \n
        if len(data_array) is not 6 or data_line[-1] != '\n':
            return None

        # Check if each data is a digit except last (which is the payload)
        for data in data_array[:5]:
            if not data.isdigit():
                return None

        # Return message object
        return MySenMessage(
            int(data_array[0]),
            int(data_array[1]),
            int(data_array[2]),
            int(data_array[3]),
            int(data_array[4]),
            data_array[5].rstrip()  # strip newline
        )

    def start_serial_read(self):
        while 1:
          continue


if __name__ == "__main__":

    def msg_func(msg):
        log(msg)


    gw_conn = GatewayConnector(msg_func)
    gw_conn.start_serial_read()
