#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault, Sean McClain, Andrew Kirfman                      #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./output_helper.py                                                     #
# Description: this file holds helper functions (mostly used by the            #
# output_gateway) so that it is easy to update actuators' states               #
#                                                                              #
# NOTE: this is basically just a set of wrappers for relay_actuator.py         #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Library Includes                                                             #
# ---------------------------------------------------------------------------- #
import sys

sys.path.append("./static/python")
import helper_functions
from helper_functions import scream

sys.path.append("./static/python/actuators")
import relay_actuator

# ---------------------------------------------------------------------------- #
# Helper Functions                                                             #
# ---------------------------------------------------------------------------- #

#given the port of a relay, update the entry in the *Out table accordingly
def update_actuator_state(actuator_id, out_table, state):
    boolean = (str(state).lower() == "true")
    string = "on" if state else "off"
    sql_statement = "UPDATE TABLENAME SET state=%s WHERE actuatorId=%s;"
    sql_statement = sql_statement.replace("TABLENAME", out_table)
    #scream(sql_statement)
    helper_functions.execute_SQL_oneoff(sql_statement, (string, actuator_id))

def actuator_state_match(actuator_id, out_table, state):
    sql_statement = "SELECT state FROM TABLENAME WHERE actuatorId=%s"
    sql_statement = sql_statement.replace("TABLENAME", out_table)
    result = helper_functions.execute_SQL_oneoff(sql_statement, (actuator_id,))[0][0]
    result = (not(result == "off"))
    return (result == state)

# ---------------------------------------------------------------------------- #
# Functions                                                                    #
# ---------------------------------------------------------------------------- #

#given an actuator id, flip the relay to the desired state
def actuate_relay(actuator_id, out_table, state):
    state = (str(state).lower() == "true")
    if actuator_state_match(actuator_id, out_table, state):
        print "actuator %s already %s" % (actuator_id, state)
        return
    else:
        print "actuator %s needs to be switched" % actuator_id
    sql_statement = "SELECT channelId, relayId FROM TABLENAME WHERE actuatorId=%s"
    sql_statement = sql_statement.replace("TABLENAME", out_table)
    relay, relay_id = helper_functions.execute_SQL_oneoff(sql_statement, (actuator_id,))[0]
    port = helper_functions.execute_SQL_oneoff("SELECT portNumber FROM RelayOut WHERE relayId=%s;", (relay_id,))[0][0]
    scream("ATTEMPTING TO ACTUATE (%s) WITH ACTUATORID %s to %s" % (str(out_table).replace("Out", ""), actuator_id, state))
    relay_actuator.state_set(port, relay, state)
    update_actuator_state(actuator_id, out_table, state)
    

#figures out the actuator_id for a global actuator and makes a call to flip the relay
#out_table should be the table to look in for the relay ("LightOut")
def actuate_global_relay(greenhouse_id, actuator_type, out_table, state):
    actuator_ids = helper_functions.execute_SQL_oneoff("SELECT actuatorId FROM GlobalMapping WHERE greenhouseId=%s AND actuatorType=%s;", (greenhouse_id, actuator_type))
    for actuator_id in actuator_ids:
        actuate_relay(actuator_id[0], out_table, state)

#figures out the actuator_id for a local actuator and makes a call to flip the relay
#out_table should be the table to look in for the relay ("SolenoidOut")
def actuate_local_relay(location_id, out_table, state):
    actuator_id = helper_functions.execute_SQL_oneoff("SELECT actuatorId FROM LocationMapping WHERE locationId=%s;", (location_id,))[0][0]
    actuate_relay(actuator_id, out_table, state)

#determines whether a greenhouse is currently under automatic control
#note, if it hasnt been initalized in the DB, it will assume its on automatic
def greenhouse_on_auto(greenhouse_id):
    bool_str = helper_functions.execute_SQL_oneoff("SELECT automaticControl FROM GreenhouseStatus WHERE greenhouseId=%s;", (greenhouse_id,))
    if bool_str == () or bool_str == None or bool_str == "":
        return True
    bool_str = bool_str[0][0]
    return (bool_str.lower() == "true")

#gets greenhouse id given a location id
def get_greenhouse(location_id):
    return helper_functions.execute_SQL_oneoff("SELECT greenhouseId FROM LocationMapping WHERE locationId=%s;", (location_id,))[0][0]
