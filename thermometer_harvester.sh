#!/bin/bash
# based on http://www.d0wn.com/using-bash-and-gatttool-to-get-readings-from-xiaomi-mijia-lywsd03mmc-temperature-humidity-sensor/

readSensor () {

    bt=$(timeout 15 gatttool -b $mac --char-write-req -a 56 -n "0100" --listen)
    
    if [ -n "$bt" ]
    then
    	timestamp=$(date +"%s")
    	echo $timestamp $mac $bt >> ~/Temperaturen.csv
    	sleep 10s
    fi
}

mac="12:34:56:78:90:AB" #Room 1
readSensor
mac="12:34:56:78:90:AB" #Room 2
readSensor
