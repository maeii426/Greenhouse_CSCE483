#!/usr/bin/env python

#DEPRICATED, DO NOT USE
#WE WILL NOW USE ONLY OUTPUT_GATEWAY
"""
# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault, Sean McClain, Andrew Kirfman                      #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./queue_manager.py                                                     #
# Description: This module looks at recently stored sensor information and     #
# determines if actions need to be done. If so, it puts actions into the       #
# Request Queue                                                                #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #
import sys
import thread
import time
import MySQLdb
from os import rename
from datetime import datetime

sys.path.append("./static/python")
import helper_functions

# ---------------------------------------------------------------------------- #
# Functions                                                                    #
# ---------------------------------------------------------------------------- #

# if last reading of moistness is greater than "max_dryness", put command in 
# queue to water plant via solenoid attached relay
def monitor_soil_moisture_loop():
    max_dryness = 800
    sampling_interval = 15 # seconds
    while True:
        readings = helper_functions.execute_SQL_oneoff("SELECT * FROM SoilData AS s1 WHERE unixTimestamp = (SELECT MAX(unixTimestamp * 1) FROM SoilData AS s2 WHERE s1.sensorId = s2.sensorId);", ())
        print("recent readings: " + str(readings))
        for reading in readings:
            print("Queuing up order to water plant attached to sensor " + str(reading[0]))
            
            #queue water plant command
            locationId = reading[1]
            actuatorId = helper_functions.execute_SQL_oneoff("SELECT actuatorId FROM LocationMapping WHERE locationId=%s;", (locationId,))[0][0]
            relay, relayId = helper_functions.execute_SQL_oneoff("SELECT channelId, relayId FROM SolenoidOut WHERE actuatorId=%s", (actuatorId,))[0]
            boolean = int(reading[2]) > max_dryness
            command = "action:relaySwitch,relayId:%s,relay:%s,state:%s" % (relayId, relay, boolean)
            timestamp = str(int(1000*time.time()))
            greenhouseId = reading[4]
            helper_functions.execute_SQL_oneoff("INSERT INTO RequestQueue VALUES(%s, %s, %s);", (command, timestamp, greenhouseId))
        time.sleep(sampling_interval)

def monitor_water_level_loop():
    pass

def monitor_light_level_loop():
    pass

def monitor_air_temp_loop():
    pass

def monitor_water_temp_loop():
    pass

def monitor_humidity_level_loop():
    pass

def monitor_ph_level_loop():
    pass

# ---------------------------------------------------------------------------- #
# Program                                                                      #
# ---------------------------------------------------------------------------- #

def main():
    helper_functions.safe_start_thread(monitor_soil_moisture_loop)
    helper_functions.safe_start_thread(monitor_water_level_loop)
    helper_functions.safe_start_thread(monitor_light_level_loop)
    helper_functions.safe_start_thread(monitor_air_temp_loop)
    helper_functions.safe_start_thread(monitor_water_temp_loop)
    helper_functions.safe_start_thread(monitor_humidity_level_loop)
    helper_functions.safe_start_thread(monitor_ph_level_loop)
    
if __name__ == "__main__":
    main()
"""





