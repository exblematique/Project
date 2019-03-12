#!/bin/bash

if [ `whoami` != 'root' ]
then
    echo 'Sorry, you must be a root'

else
    apt-get update && apt-get install python-pip python3-pip twine
    apt-get install mosquitto -y
    apt-get install mosquitto-clients -y
    pip2 install -r requirements.txt
    pip3 install -r requirements.txt
fi
