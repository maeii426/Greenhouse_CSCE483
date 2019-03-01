#!/usr/bin/env python
"""
OLD, DEPRICATED, DO NOT USE. FOR REFERENCE ONLY
"""
"""
# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault, Sean McClain, Andrew Kirfman                      #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./output_gateway.py                                                    #
# Description: This module takes tasks from the Queue in our database and      #
# issues directions for the various actuators accordingly                      #
#                                                                              #
# NOTE: in the queue table, the "action" field should be formatted as follows: #
# -colons "," seperating each data item                                        #
# -begin with the action type, followed by parameters                          #
# -each item should have a label and a value, a la JSON-ish format             #
# -all action items MUST have an "action" field within them                    #
# -EXAMPLE= "action:relaySwitch,relayId:123,relay:2,state:False"               #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #
import sys
import thread
import time
from datetime import datetime

sys.path.append("./static/python")
import helper_functions

sys.path.append("./static/python/actuators")
import relay_actuator


# ---------------------------------------------------------------------------- #
# Functions                                                                    #
# ---------------------------------------------------------------------------- #

def action_relay_switch(task, greenhouseId):
    helper_functions.enforce_dict_conformity(task, ["relayId", "state"])
    port = helper_functions.execute_SQL_oneoff("SELECT portNumber FROM RelayOut WHERE relayId=%s;", (task["relayId"],))[0][0]
    helper_functions.safe_start_thread(relay_actuator.state_set, (port, task["relay"], task["state"] == "True"))
    
#main task delegation function
def delegate_task(task, greenhouseId):
    task = helper_functions.dictify(task)
    helper_functions.enforce_dict_conformity(task, ["action"])
    
    action = task["action"]
    
    #add valid actions as needed
    if action == "relaySwitch":
        action_relay_switch(task, greenhouseId)
    else:
        raise Exception("queue task action unknown\naction: %s" % action)
        
def main_dequeue_loop():
    sampling_interval = 15 # seconds
    while True:
        #TODO: make these DB Calls use the same connection rather than reconnecting each time -Aaron
        
        #get data from queue
        tasks = helper_functions.execute_SQL_oneoff("SELECT * FROM RequestQueue;", ())
        
        if len(tasks) != 0:
            #log data
            helper_functions.execute_SQL_oneoff("INSERT INTO RequestLog (action, unixTimestampRequested, greenhouseId) SELECT * FROM RequestQueue;", ())
            
            #delete from Queue
            helper_functions.execute_SQL_oneoff("TRUNCATE RequestQueue;", ())
            
            #decide what to do with tasks
            for row in tasks:
                if len(row) != 0:
                    task = row[0]
                    unixTimestampRequested = int(row[1])
                    greenhouseId = [2]
                    delegate_task(task, greenhouseId)
                    completed_timestamp = int(1000*time.time())
                    helper_functions.execute_SQL_oneoff("UPDATE RequestLog SET unixTimestampCompleted=%s WHERE unixTimestampRequested=%s;", (completed_timestamp, unixTimestampRequested))
                
        time.sleep(sampling_interval)

# ---------------------------------------------------------------------------- #
# Program                                                                      #
# ---------------------------------------------------------------------------- #

def main():
    main_dequeue_loop()
        
if __name__ == "__main__":
    main()
"""





