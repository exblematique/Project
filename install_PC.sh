#!/bin/bash

if [ `whoami` != 'root' ]
then
    echo 'Sorry, you must be a root'

else
    apt-get update
    apt-get install python-pip python3-pip twine -y
    pip2 install -r requirements.txt
    pip3 install -r requirements.txt

    #Installing mosquitto broker :
    apt-get install mosquitto mosquitto-clients -y
    echo "listener 1883" >> /etc/mosquitto/mosquitto.conf
    pip install paho-mqtt
    pip3 install paho-mqtt
fi
