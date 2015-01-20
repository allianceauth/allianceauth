#!/bin/bash
trigger=5.00
load=`cat /proc/loadavg | awk '{print $1}'`
response=`echo | awk -v T=$trigger -v L=$load 'BEGIN{if ( L > T){ print "greater"}}'`
if [[ $response = "greater" ]]
then
killall screen
sleep 8m
bash /home/allianceserver/allianceauth/start_bg_tasks.sh
fi
