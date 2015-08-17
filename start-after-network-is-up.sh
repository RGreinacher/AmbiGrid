#!/bin/bash

# autostart script for the Raspberry Pi; wait until the wifi is up
# set `sudo chmod +x ./start-after-network-is-up.sh`
# call this script in `/etc/rc.local`

while true ; do
   if ifconfig wlan0 | grep -q "inet addr:" ; then
      cd /home/pi/AmbiGrid/
      ./ambiGrid.py
      exit
   else
      sleep 5
   fi
done
