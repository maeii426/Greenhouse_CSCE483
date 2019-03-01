#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault, Sean McClain, Andrew Kirfman                      #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./output_gateway.py                                                    #
# Description: This module monitors the recent readings in the Data tables and #
# then delegates tasks to the actuators based on the latest readings.          #
#                                                                              #
# NOTE: we are taking advantage of the fact that all output actuators are      #
# controlled by relays.                                                        #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #
import sys
import time
import traceback
from datetime import datetime

sys.path.append("./static/python")
import helper_functions
from helper_functions import scream

from output_helper import actuate_global_relay
from output_helper import actuate_local_relay
from output_helper import greenhouse_on_auto
from output_helper import get_greenhouse

# ---------------------------------------------------------------------------- #
# Helper Functions                                                             #
# ---------------------------------------------------------------------------- #

#gets the most recent readings from all unique sensorId's given a Data table 
def get_recent_readings(table_name):
    sql_statement = "SELECT * FROM TABLENAME AS s1 WHERE unixTimestamp = (SELECT MAX(unixTimestamp * 1) FROM TABLENAME AS s2 WHERE s1.sensorId = s2.sensorId);"
    sql_statement = sql_statement.replace("TABLENAME", table_name)
    #scream(helper_functions.execute_SQL_oneoff(sql_statement, ()))
    return helper_functions.execute_SQL_oneoff(sql_statement, ())

#returns the lastOnTime for a solenoid 
def solenoid_last_on_time(location_id):
    actuator_id = helper_functions.execute_SQL_oneoff("SELECT actuatorId FROM LocationMapping WHERE locationId=%s;", (location_id,))[0][0]
    last_on_time = helper_functions.execute_SQL_oneoff("SELECT lastOnTime FROM SolenoidOut WHERE actuatorId=%s", (actuator_id,))[0][0]
    print last_on_time
    last_on_time = int(last_on_time)
    return last_on_time

def get_actuator_id(location_id):
    return helper_functions.execute_SQL_oneoff("SELECT actuatorId FROM LocationMapping WHERE locationId=%s;", (location_id,))[0][0]

# ---------------------------------------------------------------------------- #
# Functions                                                                    #
# ---------------------------------------------------------------------------- #
"""
NOTE
from : Aaron
to   : Aaron
msg  : remember, for global data, the reading is the 2nd item in a row (index 1)
 but for local data, the reading is the 3rd item (index 2)
"""

def monitor_loop():
    while True:
        time_now = str(datetime.now().strftime('%H:%M:%S'))
        print "=================STARTING MONITOR CYCLE (%s)=============================" % time_now
        
        #airtemp
        sample_period = 15 #seconds
        preferred_airtemp = 25 #in celsius
        readings = get_recent_readings("AirTempData")
        for row in readings:
            try:
                if not greenhouse_on_auto(row[3]): continue
                reading = int(row[1])
                if reading > preferred_airtemp:
                    print "HERE IS WHERE I WILL TURN ON THE FANS FOR GREENHOUSE %s" % row[3]
                else:
                    print "HERE IS WHERE I WILL TURN OFF THE FANS FOR GREENHOUSE %s" % row[3]
                actuate_global_relay(row[3], "FAN", "VentilationOut", (reading > preferred_airtemp))
            except Exception as e:
                scream("airtemp monitoring exception caught\n%s" % str(e))
                traceback.print_exc()
        
        #light level
        minimum_lightlevel = 100 #reading from light sensor, ranges from 0 to 1024
        dusk_hour = 20 #8:00 PM
        dawn_hour = 5  #5:00 AM
        readings = get_recent_readings("LightData")
        try:
            if not greenhouse_on_auto('3'): continue
            #reading = int(row[1])
            current_hour = datetime.now().hour
            if (current_hour > dusk_hour or current_hour < dawn_hour):
                print "HERE IS WHERE I WILL TURN ON THE LIGHTS FOR GREENHOUSE %s" % '3'
            else:
                print "HERE IS WHERE I WILL TURN OFF THE LIGHTS FOR GREENHOUSE %s" % '3'
            actuate_global_relay('3', "LIGHT", "LightOut", (current_hour > dusk_hour or current_hour < dawn_hour))
        except Exception as e:
            scream("lightlevel monitoring exception caught\n%s" % str(e))
            traceback.print_exc()
            
        #soil moisture
        maximum_dryness = 900 #reading from soil moisture sensor, ranges from 0 to 1024 (1024 == DRYER THAN YOUR MOM)
        readings = get_recent_readings("SoilData")
        for row in readings:
            unix_timestamp = int(1000*time.time()) #in ms
            try:
                if not greenhouse_on_auto(get_greenhouse(row[1])): continue
                
                #if location was watered in the last 10 mins, dont water
                if (int(unix_timestamp) - int(solenoid_last_on_time(row[1])) < 1000*60*10): 
                    print "location %s was watered in the last 10 mins, dont water" % row[1]
                    continue
                
                reading = int(row[2])
                if reading > maximum_dryness:
                    print "HERE IS WHERE I WILL TURN ON THE WATER FOR SOIL LOCATION %s for 20 seconds" % row[1]
                
                if (reading > maximum_dryness):
                    actuate_local_relay(row[1], "SolenoidOut", True)
                    time.sleep(20)
                    actuate_local_relay(row[1], "SolenoidOut", False)
                    helper_functions.execute_SQL_oneoff("UPDATE SolenoidOut SET lastOnTime=%s WHERE actuatorId=%s", (unix_timestamp, get_actuator_id(row[1])))
                    
            except Exception as e:
                scream("soilmoisture monitoring exception caught\n%s" % str(e))
                traceback.print_exc()    
            
        #water level
        maximum_dryness = 800 #reading from soil moisture sensor, ranges from 0 to 1024 (1024 == DRY -> water is low)
        readings = get_recent_readings("WaterLevelData")
        for row in readings:
            unix_timestamp = int(1000*time.time()) #in ms
            try:
                if not greenhouse_on_auto(get_greenhouse(row[1])): continue
                
                #if location was watered in the last 10 mins, dont water
                if (int(unix_timestamp) - int(solenoid_last_on_time(row[1])) < 1000*60*10): 
                    print "location %s was watered in the last 10 mins, dont water" % row[1]
                    continue
                
                reading = int(row[2])
                if reading > maximum_dryness:
                    print "HERE IS WHERE I WILL TURN ON THE WATER FOR HYDROPONIC LOCATION %s" % row[1]
                else:
                    print "HERE IS WHERE I WILL TURN OFF THE WATER FOR HYDROPONIC LOCATION %s" % row[1]
                #actuate_local_relay(row[1], "SolenoidOut", (reading > maximum_dryness))
                if (reading > maximum_dryness):    
                    actuate_local_relay(row[1], "SolenoidOut", True)
                    time.sleep(15)
                    actuate_local_relay(row[1], "SolenoidOut", False)
            except Exception as e:
                scream("waterlevel monitoring exception caught\n%s" % str(e))
                traceback.print_exc()
            
        print "=================ENDING MONITOR CYCLE (ON STANDBY)=================="
        time.sleep(sample_period)
        
    helper_functions.scream("ENDED MONITOR LOOP, NOOOOOOO!!!!")

# ---------------------------------------------------------------------------- #
# Program                                                                      #
# ---------------------------------------------------------------------------- #

def main():
    while True:
        try:
            monitor_loop()
        except Exception as e:
            scream("output gateway exception, restarting in 5 seconds\n%s" % str(e))
            traceback.print_exc()
            time.sleep(5)
    """
    helper_functions.safe_start_thread(monitor_airtemp_loop, ())
    helper_functions.safe_start_thread(monitor_humidity_loop, ())
    helper_functions.safe_start_thread(monitor_light_loop, ())
    helper_functions.safe_start_thread(monitor_soil_loop, ())
    helper_functions.safe_start_thread(monitor_ph_loop, ())
    helper_functions.safe_start_thread(monitor_waterlevel_loop, ())
    helper_functions.safe_start_thread(monitor_watertemp_loop, ())
    """
    
if __name__ == "__main__":
    main()






