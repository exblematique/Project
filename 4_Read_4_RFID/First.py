"""
Python MQTT Subscription client - No Username/Password
Thomas Varnish (https://github.com/tvarnish), (https://www.instructables.com/member/Tango172)
Written for my Instructable - "How to use MQTT with the Raspberry Pi and ESP8266"
"""
import paho.mqtt.client as mqtt

# Don't forget to change the variables for the MQTT broker!
mqtt_topic_receive = "sendToPc"
mqtt_topic_send = "getFromPc"
mqtt_broker_ip = "localhost"

client = mqtt.Client()

# These functions handle what happens when the MQTT client connects
# to the broker, and what happens then the topic receives a message
def on_connect(client, userdata, flags, rc):
    # rc is the error code returned when connecting to the broker
    print("Connected!"+str(rc))
    # Once the client has connected to the broker, subscribe to the topic
    client.subscribe(mqtt_topic_receive)
    
def on_message(client, userdata, msg):
    # This function is called everytime the topic is published to.
    # If you want to check each message, and do something depending on
    # the content, the code to do this should be run in this function

    ID_tag = str(msg.payload)

    for i in database:
       if i[1] == ID_tag:
           client.publish(mqtt_topic_send, i[0])
           print("Topic: "+ msg.topic + "\nMessage: " + ID_tag + "\nValue: " + i[0])
           return

    client.publish(mqtt_topic_send, 'This ID does not exist in database')
    print('This ID does not exist in database')

    
    

    # The message itself is stored in the msg variable
    # and details about who sent it are stored in userdata

def create_db_test():
    return [["p", "76447129"], ["y", "c0057329"], ["b", "e6b528f1"], ["g", "32ff7d11"]]


database = create_db_test()
# Here, we are telling the client which functions are to be run
# on connecting, and on receiving a message
client.on_connect = on_connect
client.on_message = on_message

# Once everything has been set up, we can (finally) connect to the broker
# 1883 is the listener port that the MQTT broker is using
client.connect(mqtt_broker_ip, 1883)


# Once we have told the client to connect, let the client object run itself
client.loop_forever()
client.disconnect()


