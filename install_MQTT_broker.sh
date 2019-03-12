#!/bin/bash

if [ `whoami` != 'root' ]
then
    echo 'Sorry, you must be a root'

else
    apt-get install mosquitto -y
    apt-get install mosquitto-clients -y
    echo "listener 1883" >> /etc/mosquitto/mosquitto.conf
    pip install paho-mqtt
    pip3 install paho-mqtt
fi
