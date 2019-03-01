#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault, Sean McClain, Andrew Kirfman                      #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./input_gateway.py                                                     #
# Description: This file stores incoming data from the arduinos into the       #
# database, and also routes manipulator information to actuator controlling    #
# arduinos. It should be ran as a cron task                                    #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #
import socket
import sys
import thread
import serial
import time
import MySQLdb
from datetime import datetime

sys.path.append("./static/python")
import helper_functions
import configuration


# ---------------------------------------------------------------------------- #
# Global Variables                                                             #
# ---------------------------------------------------------------------------- #

PORT = 30001

# ---------------------------------------------------------------------------- #
# Functions                                                                    #
# ---------------------------------------------------------------------------- #

#many of the global data tables have EXACTLY the same format. this function inserts
#into those tables in a standardized way
def insert_global_reading(reading, greenhouse_id, data_table_name):
    unix_timestamp = int(1000*time.time()) #in ms
    sensor_table_name = data_table_name.replace("Data", "Sensors")
    #get sensor id
    sql_statement = "SELECT sensorId FROM TABLENAME WHERE greenhouseId=%s;"
    sql_statement = sql_statement.replace("TABLENAME", sensor_table_name)
    sensor_id = helper_functions.execute_SQL_oneoff(sql_statement, (str(greenhouse_id),))
    if sensor_id == () or sensor_id == None:
        return
    sensor_id = sensor_id[0][0]
    #store db entry
    sql_statement = "INSERT INTO TABLENAME VALUES(%s, %s, %s, %s);"
    sql_statement = sql_statement.replace("TABLENAME", data_table_name)
    helper_functions.execute_SQL_oneoff(sql_statement, (sensor_id, reading, str(unix_timestamp), greenhouse_id))

#many of the local data tables have EXACTLY the same format. this function inserts
#into those tables in a standardized way
def insert_local_reading(reading, sensor_id, data_table_name):
    unix_timestamp = int(1000*time.time()) #in ms
    sensor_table_name = data_table_name.replace("Data", "Sensors")
    #get location id
    sql_statement = "SELECT locationId FROM TABLENAME WHERE sensorId=%s;"
    sql_statement = sql_statement.replace("TABLENAME", sensor_table_name)
    location_id = helper_functions.execute_SQL_oneoff(sql_statement, (str(sensor_id),))
    if location_id == () or location_id == None:
        return
    location_id = location_id[0][0]
    #get location id
    sql_statement = "SELECT greenhouseId FROM TABLENAME WHERE sensorId=%s;"
    sql_statement = sql_statement.replace("TABLENAME", sensor_table_name)
    greenhouse_id = helper_functions.execute_SQL_oneoff(sql_statement, (str(sensor_id),))[0][0]
    #store db entry
    sql_statement = "INSERT INTO TABLENAME VALUES(%s, %s, %s, %s, %s);"
    sql_statement = sql_statement.replace("TABLENAME", data_table_name)
    helper_functions.execute_SQL_oneoff(sql_statement, (sensor_id, location_id, reading, str(unix_timestamp), greenhouse_id))

#this function parses through the incomig data and determines what function to
#use to store the data in the database
def delegate(data):
    data = str(data).split(":")
    length = len(data)
    
    #if data conforms to global readings it will have 5 length
    #if it is a normal reading, it will have 3 length
    if length == 5:
        if data[0] == "GLOBAL":
            insert_global_reading(data[2], data[1], "LightData")
            insert_global_reading(data[3], data[1], "AirTempData")
            insert_global_reading(data[4], data[1], "HumidityData")
        elif data[0] == "HYDRO":
            insert_local_reading(data[2], data[1], "pHData")
            insert_local_reading(data[3], data[1], "WaterTempData")
            insert_local_reading(data[4], data[1], "WaterLevelData")
        else:
            msg = "invalid socket message with key: %s: \n%s" % (str(data[0]), str(data))
            raise Exception(msg)
    elif length == 3:
        if data[0] == "SOIL": 
            insert_local_reading(data[2], data[1], "SoilData")
        else:
            msg = "invalid socket message with key: %s: \n%s" % (str(data[0]), str(data))
            raise Exception(msg)
    else:
        msg = "invalid socket message length (%s) on message: \n%s" % (str(length), str(data))
        raise Exception(msg)
        

# ---------------------------------------------------------------------------- #
# Program                                                                      #
# ---------------------------------------------------------------------------- #
def main():
    connection = None
    # Initialize & bind socket to port 30001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket to SO_REUSEADDR (tells kernel to reuse local socket in TIME_WAIT state,
    # without waiting for its natural timeout to expire)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = ('', PORT) #MAKE SURE THE FIRST ARGUMENT IS EMPTY
    sock.bind(server_address)
        
    # Listen for incoming message
    sock.listen(1)
    helper_functions.safe_start_thread(configuration.main, ())
    print "=======STARTED CONFIGURATION========="
    try:
        while True:
            connection, client_address = sock.accept()
            while True:
                data = connection.recv(1024) #cloud9 thinks this is an error. it's not.
                if data:
                    try:
                        helper_functions.scream("GotData:\n" + data)
                        helper_functions.safe_start_thread(delegate, (data.strip("\r\n"),))
                    except Exception as e:
                        print e
                else:
                    break
    except Exception as e:
        print "input gateway socket failed, " + str(e)
    finally:
        if not (connection == None):
            connection.close()

if __name__ == "__main__":
    main()