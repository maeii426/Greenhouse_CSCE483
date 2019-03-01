# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault, Sean McClain, Andrew Kirfman                      #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./helper_functions.py                                                  #
# Description: This module contains useful helper functions                    #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #

import MySQLdb
import sys
import thread

# ---------------------------------------------------------------------------- #
# Global Variables                                                             #
# ---------------------------------------------------------------------------- #

# Current Database Parameters
DB_HOST="localhost"
DB_USER="root"
DB_PASSWD="password"
DB_PRIMARY_DATABASE="greenhouse"

# ---------------------------------------------------------------------------- #
# Helper Functions                                                             #
# ---------------------------------------------------------------------------- #

#"arguments" should be a tuple.
#Note that this creates a new DB connection each time, and thus is for 
#infrequent usage.
def execute_SQL_oneoff(statement, arguments=()):
    db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWD)
    cursor = db.cursor()
    cursor.execute("USE %s;" % DB_PRIMARY_DATABASE)
    cursor.execute(statement, arguments)
    data = cursor.fetchall()
    db.commit()
    print("SQL Command: " + str(cursor._executed))
    db.close()
    return data

#starts a thread around a try block
#only use this for critical threads, as it will end the program if the thread fails
#if "critical" is true, this thread will end the program if it doesnt execute properly
def safe_start_thread(function, arguments=(), critical=False):
    try:
        thread.start_new_thread(function, arguments)
    except Exception as e:
        print str(e)
        print "Error: unable to start thread"
        if critical:
            print "critical thread failed, killing program..."
            sys.exit(1)

#convert string to dictionary
#THIS STRING CANT HAVE } OR { IN IT UNLESS THOSE ARE BEGENNING AND ENDING CHARACTERS
def dictify(instr):
    instr = instr.replace("{", "")
    instr = instr.replace("}", "")
    instr = instr.replace(", ", ",")
    aslist = [item.split(':') for item in instr.split(',')]
    asdict = {}
    for entry in aslist:
        asdict[entry[0]] = entry[1]
    return asdict
    
#makes sure a dictionary conforms to a given schema
#"schema" should be a list/array of strings that should be keys in the dictionary
#"throws" should be set to False if you want this to merely *check* whether the dictionary conforms and return a boolean
def enforce_dict_conformity(indict, schema, throws=True):
    for key in schema:
        if key not in indict.keys():
            if throws:
                raise Exception("dictionary has no '%s' field" % key)
            else:
                return False
    return True
    
#screams something to the output window for debugging
def scream(string):
    print "=================OUTPUT================="
    print str(string)
    print "=================OUTPUT================="

#gets the most recent reading for a sensor
#sensor type must be the same as they are in the DB without an *Out or *Data at the end
def get_recent_reading(sensor_type, greenhouse_id, sensor_id):
    table_name = sensor_type + "Data"
    sql_statement = "SELECT reading FROM TABLENAME WHERE unixTimestamp=(SELECT MAX(unixTimestamp * 1) FROM TABLENAME WHERE sensorId=%s AND greenhouseId=%s);"
    sql_statement = sql_statement.replace("TABLENAME", table_name)
    reading = execute_SQL_oneoff(sql_statement, (sensor_id, greenhouse_id))
    print reading
    if reading == ((None,),) or reading == None or reading == ():
        return reading
    return reading[0][0]