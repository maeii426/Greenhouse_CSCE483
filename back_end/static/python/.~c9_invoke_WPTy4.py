#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman                                                    #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./greenhouse_database.py                                               #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #

import sys
import logging
import MySQLdb
import time

sys.path.append("./static/python")
import helper_functions
import database_inserter

# ---------------------------------------------------------------------------- #
# Global Variables                                                             #
# ---------------------------------------------------------------------------- #

# Current Database Parameters
DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASSWD="password"
DB_PRIMARY_DATABASE="greenhouse"

# ---------------------------------------------------------------------------- #
# Console/File Logger                                                          #
# ---------------------------------------------------------------------------- #

print_logger = logging.getLogger(__name__)
print_logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------- #
# Database Call Level Interface                                                #
# ---------------------------------------------------------------------------- #

class greenhouse_database(object):
    def __init__(self):
        self.initialized = False
        self.database_object = None

        print_logger.debug("Database object initialized successfully.")

    def connect(self):
        print_logger.debug("Connecting to database: %s" % DB_PRIMARY_DATABASE)
        self.database_object = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWD)

        # Attempt to use the existing greenhouse database
        current_pointer = self.database_object.cursor()

        try:
            current_pointer = self.database_object.cursor()
            current_pointer.execute("USE %s;" % DB_PRIMARY_DATABASE)

            print_logger.debug("Greenhouse database used successfully.")
        except Exception:
            print_logger.debug("Greenhouse database use failed.  Attempting to create.")

            # The database doesn't exist, create it
            try:
                current_pointer = self.database_object.cursor()
                result = current_pointer.execute("CREATE DATABASE %s;" % DB_PRIMARY_DATABASE)

                print_logger.debug("Created the greenhouse database.")

                current_pointer = self.database_object.cursor()
                result = current_pointer.execute("USE %s" % DB_PRIMARY_DATABASE)

                print_logger.debug("Greenhouse database used successfully.")
            except Exception:
                print_logger.error("Could not create or use the greenhouse database.")
                sys.exit(1)

        # Database object is now up and running
        print_logger.debug("Connected to database successfully.")
        self.initialized = True

    def disconnect(self):
        # Close the cursor first
        self.database_object.cursor().close()

        # Close the database object
        self.database_object.close()

        # The database objet is no longer initialized
        self.initialized = False

        print_logger.debug("Successfully disconnected from the database.")

    def issue_db_command(self, cmd, silent = False):
        """
        Issue a generic command denoted by cmd to the database.  Performs basic
        error checking and loggs the result.  Returns the result of the command
        False if it failed.
        """

        print_logger.debug("Issuing command: %s" % str(cmd))

        if self.initialized is False:
            print_logger.error("Database not initialized.")
            return

        current_pointer = self.database_object.cursor()

        try:
            # Execute the command
            current_pointer.execute(cmd)

            self.database_object.commit()

            return current_pointer.fetchall()
        except Exception as error:
            if silent is False:
                print_logger.error("Could not execute command: ")
                print_logger.error("  - Error Message: %s" % str(error[1]))
                print_logger.error("  - Failed Command: %s" % str(cmd))
            else:
                print_logger.debug("Could not execute command: ")
                print_logger.debug("  - Error Message; %s" % str(error[1]))
                print_logger.debug("  - Failed Command: %s" % str(cmd))

            return False

    def check_tables(self):
        """
        Make sure that every table in the database is where it should be.
        If there are any problems, rerun the commands
        """

        print_logger.debug("Checking tables for consistency.")

        # ------------------------------------------------------------------- #
        # Users Table                                                         #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: Users.")
        command_result = self.issue_db_command("SELECT * FROM Users;", True)

        if command_result is False:
            print_logger.debug("Users table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE Users(\n\
                username          VARCHAR(100),\n\
                firstName         VARCHAR(30),\n\
                lastName          VARCHAR(30),\n\
                emailAddress    VARCHAR(50),\n\
                password        VARCHAR(50),\n\
                PRIMARY KEY(username));", True)

            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM Users;")
            if command_result is False:
                print_logger.error("Could not create table: Users.")
                sys.exit(1)
        else:
            print_logger.debug("Users table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # Insert Default User                                                 #
        # ------------------------------------------------------------------- #
        
        self.issue_db_command("INSERT "\
                    + "INTO Users VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                    % ("default", "default fname", "default lname", "hjkhjk@hjkh.com", "default"), True)
        
        # ------------------------------------------------------------------- #
        # Addresses Table                                                     #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: Addresses.")
        command_result = self.issue_db_command("SELECT * FROM Addresses;", True)

        if command_result is False:
            print_logger.debug("Addresses table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE Addresses(\n\
                username     VARCHAR(100),\n\
                houseNumber  VARCHAR(15),\n\
                street       VARCHAR(100),\n\
                city         VARCHAR(50),\n\
                zip          VARCHAR(15),\n\
                state        VARCHAR(10),\n\
                isGreenhouse Boolean,\n\
                isResidence  Boolean,\n\
                PRIMARY KEY(username, houseNumber, street, city));", True)

            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM Addresses;", True)
            if command_result is False:
                print_logger.error("Could not create table: Addresses.")
                sys.exit(1)
        else:
            print_logger.debug("Addresses table exists in the database.")

        # ------------------------------------------------------------------- #
        # Greenhouses Table                                                   #
        # ------------------------------------------------------------------- #

        print_logger.debug("Checking table: Greenhouses")
        command_result = self.issue_db_command("SELECT * FROM Greenhouses;", True)
        
        if command_result is False:
            print_logger.debug("Greenhouses table does not exist in the database.")
            command_result = self.issue_db_command("CREATE TABLE Greenhouses(\n\
                greenhouseId    VARCHAR(10),\n\
                username        VARCHAR(100),\n\
                houseNumber     VARCHAR(15),\n\
                street          VARCHAR(100),\n\
                city            VARCHAR(50),\n\
                zip             VARCHAR(15),\n\
                state           VARCHAR(10),\n\
                PRIMARY KEY(greenhouseId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM Greenhouses;", True)
            if command_result is False:
                print_logger.error("Could not create table: Greenhouses.")
                sys.exit(1)
        else:
            print_logger.debug("Greenhouses table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # GreenhouseStatus Table                                              #
        # ------------------------------------------------------------------- #

        print_logger.debug("Checking table: GreenhouseStatus")
        command_result = self.issue_db_command("SELECT * FROM GreenhouseStatus;", True)
        
        if command_result is False:
            print_logger.debug("GreenhouseStatus table does not exist in the database.")
            command_result = self.issue_db_command("CREATE TABLE GreenhouseStatus(\n\
                greenhouseId      VARCHAR(10),\n\
                automaticControl  VARCHAR(10),\n\
                PRIMARY KEY(greenhouseId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM GreenhouseStatus;", True)
            if command_result is False:
                print_logger.error("Could not create table: GreenhouseStatus.")
                sys.exit(1)
        else:
            print_logger.debug("GreenhouseStatus table exists in the database.")

        # ------------------------------------------------------------------- #
        # PhoneNumbers Table                                                  #
        # ------------------------------------------------------------------- #

        print_logger.debug("Checking Table: PhoneNumbers.")
        command_result = self.issue_db_command("SELECT * FROM PhoneNumbers;", True)

        if command_result is False:
            print_logger.debug("PhoneNumbers table does not exist in the database.  Creating...")
            command_result = self.issue_db_command("CREATE TABLE PhoneNumbers(\n\
                username VARCHAR(100),\n\
                number   VARCHAR(10),\n\
                PRIMARY KEY(username, number))", True)

            command_result = self.issue_db_command("SELECT * FROM PhoneNumbers;")
            if command_result is False:
                print_logger.error("Could not create table: PhoneNumbers.")
                sys.exit(1)
        else:
            print_logger.debug("PhoneNumbers table exists in the database.")

        # ------------------------------------------------------------------- #
        # WaterLevelData Table                                                #
        # ------------------------------------------------------------------- #

        print_logger.debug("Checking Table: WaterLevelData.")
        command_result = self.issue_db_command("SELECT * FROM WaterLevelData;", True)

        if command_result is False:
            print_logger.debug("WaterLevelData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE WaterLevelData(\n\
                sensorId        VARCHAR(30),\n\
                locationId      VARCHAR(30),\n\
                reading         VARCHAR(30),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10))", True)

            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM WaterLevelData;")
            if command_result is False:
                print_logger.error("Could not create table: WaterLevelData")
                sys.exit(1)
        else:
            print_logger.debug("WaterLevelData table exists in the database.")
            
        # ------------------------------------------------------------------- #
        # LightData Table                                                     #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: LightData.")
        command_result = self.issue_db_command("SELECT * FROM LightData", True)
        
        if command_result is False:
            print_logger.debug("LightData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE LightData(\n\
                sensorId        VARCHAR(30),\n\
                reading         VARCHAR(30),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10))", True)
        
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM LightData;", True)
            if command_result is False:
                print_logger.error("Could not create table: LightData.")
                sys.exit(1)
        else:
            print_logger.debug("LightData table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # AirTempData Table                                                   #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: AirTempData.")
        command_result = self.issue_db_command("SELECT * FROM AirTempData;", True)
        
        if command_result is False:
            print_logger.debug("AirTempData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE AirTempData(\n\
                sensorId        VARCHAR(30),\n\
                reading         VARCHAR(30),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10))", True)
        
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM AirTempData;", True)
            if command_result is False:
                print_logger.error("Could not create table: AirTempData.")
                sys.exit(1)
        else:
            print_logger.debug("AirTempData table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # SoilData Table                                                      #
        # ------------------------------------------------------------------- #

        print_logger.debug("Checking Table: SoilData.")
        command_result = self.issue_db_command("SELECT * FROM SoilData;", True)

        if command_result is False:
            print_logger.debug("SoilData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE SoilData(\n\
                sensorId        VARCHAR(30),\n\
                locationId      VARCHAR(30),\n\
                reading         VARCHAR(30),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10))", True)

            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM SoilData;")
            if command_result is False:
                print_logger.error("Could not create table: SoilData.")
                sys.exit(1)
        else:
            print_logger.debug("SoilData table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # WaterTempData Table                                                 #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: WaterTempData.")
        command_result = self.issue_db_command("SELECT * FROM WaterTempData;", True)
        
        if command_result is False:
            print_logger.debug("WaterTempData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE WaterTempData(\n\
                sensorId        VARCHAR(10),\n\
                locationId      VARCHAR(30),\n\
                reading         VARCHAR(20),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM WaterTempData;", True)
            if command_result is False:
                print_logger.error("Could not create table: WaterTempData.")
                sys.exit(1)
        else:
            print_logger.debug("WaterTempData table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # HumidityData Table                                                  #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: HumidityData.")
        command_result = self.issue_db_command("SELECT * FROM HumidityData;", True)
        
        if command_result is False:
            print_logger.debug("HumidityData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE HumidityData(\n\
                sensorId        VARCHAR(30),\n\
                reading         VARCHAR(30),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10))", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM HumidityData;", True)
            if command_result is False:
                print_logger.error("Could not create table: HumidityData.")
                sys.exit(1)
        else:
            print_logger.debug("HumidityData table exists in the database.")
            
        # ------------------------------------------------------------------- #
        # pHData Table                                                        #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: pHData.")        
        command_result = self.issue_db_command("SELECT * FROM pHData;", True)
        
        if command_result is False:
            print_logger.debug("pHData table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE pHData(\n\
                sensorId        VARCHAR(10),\n\
                locationId      VARCHAR(10),\n\
                reading         VARCHAR(20),\n\
                unixTimestamp   VARCHAR(30),\n\
                greenhouseId    VARCHAR(10));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM pHData;", True)
            if command_result is False:
                print_logger.error("Could not create table: pHData.")
                sys.exit(1)
        else:
            print_logger.debug("pHData table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # RelayOut Table                                                      #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: RelayOut.")
        command_result = self.issue_db_command("SELECT * FROM RelayOut;", True)
        
        if command_result is False:
            print_logger.debug("RelayOut table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE RelayOut(\n\
                relayId         VARCHAR(10),\n\
                piIp            VARCHAR(20),\n\
                portNumber      VARCHAR(10),\n\
                numberOfChannels VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(relayId));", True)
        
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM RelayOut;", True)
            if command_result is False:
                print_logger.error("Could not create table: RelayOut.")
                sys.exit(1)
        else:
            print_logger.debug("RelayOut table exists in the database.")
            
        # ------------------------------------------------------------------- #
        # UninitializedRelay Table                                            #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: UninitializedRelay.")
        command_result = self.issue_db_command("SELECT * FROM UninitializedRelay;", True)
        
        if command_result is False:
            print_logger.debug("UninitializedRelay table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE UninitializedRelay(\n\
                relayId         VARCHAR(10),\n\
                piIp            VARCHAR(20),\n\
                portNumber      VARCHAR(10),\n\
                numberOfChannels VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(relayId));", True)
        
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM UninitializedRelay;", True)
            if command_result is False:
                print_logger.error("Could not create table: UninitializedRelay.")
                sys.exit(1)
        else:
            print_logger.debug("UninitializedRelay table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # SolenoidOut Table                                                   #
        # ------------------------------------------------------------------- #       
        
        print_logger.debug("Checking Table: SolenoidOut.")
        command_result = self.issue_db_command("SELECT * FROM SolenoidOut;", True)
        
        if command_result is False:
            print_logger.debug("SolenoidOut table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE SolenoidOut(\n\
                actuatorId      VARCHAR(10),\n\
                solenoidType    VARCHAR(20),\n\
                relayId         VARCHAR(10),\n\
                channelId       VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                state           VARCHAR(10),\n\
                PRIMARY KEY(actuatorId));", True)
                
            # Test the newly created table
            commamnd_result = self.issue_db_command("SELECT * FROM SolenoidOut;", True);
            if command_result is False:
                print_logger.error("Could not create table: SolenoidOut.")
                sys.exit(1)
        else:
            print_logger.debug("SolenoidOut table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # WaterHeaterOut Table                                                #
        # ------------------------------------------------------------------- #       
        
        print_logger.debug("Checking Table: WaterHeaterOut.")
        command_result = self.issue_db_command("SELECT * FROM WaterHeaterOut;", True)
        
        if command_result is False:
            print_logger.debug("WaterHeaterOut table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE WaterHeaterOut(\n\
                actuatorId      VARCHAR(10),\n\
                relayId         VARCHAR(10),\n\
                channelId       VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                state           VARCHAR(10),\n\
                PRIMARY KEY(actuatorId));", True)
                
            # Test the newly created table
            commamnd_result = self.issue_db_command("SELECT * FROM WaterHeaterOut;", True);
            if command_result is False:
                print_logger.error("Could not create table: WaterHeaterOut.")
                sys.exit(1)
        else:
            print_logger.debug("WaterHeaterOut table exists in the database.")
            
        # ------------------------------------------------------------------- #
        # LightOut Table                                                      #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: LightOut.")
        command_result = self.issue_db_command("SELECT * FROM LightOut;", True)
        
        if command_result is False:
            print_logger.debug("LightOut table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE LightOut(\n\
                actuatorId      VARCHAR(10),\n\
                relayId         VARCHAR(10),\n\
                channelId       VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                state           VARCHAR(10),\n\
                PRIMARY KEY(actuatorId));", True)
                
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM LightOut;", True)
            if command_result is False:
                print_logger.error("Could not create table: LightOut.")
                sys.exit(1)
        else:
            print_logger.debug("LightOut table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # VentilationOut Table                                                #
        # ------------------------------------------------------------------- #        
        
        print_logger.debug("Checking Table: VentilationOut.")
        command_result = self.issue_db_command("SELECT * FROM VentilationOut;", True)
        
        if command_result is False:
            print_logger.debug("VentilationOut table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE VentilationOut(\n\
                actuatorId      VARCHAR(10),\n\
                relayId         VARCHAR(10),\n\
                channelId       VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                state           VARCHAR(10),\n\
                PRIMARY KEY(actuatorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM VentilationOut;", True)
            if command_result is False:
                print_logger.error("Could not create table: VentilationOut.")
                sys.exit(1)
        else:
            print_logger.debug("VentilationOut table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # LightSensors Table                                                  #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: LightSensors.")
        command_result = self.issue_db_command("SELECT * FROM LightSensors;", True)
        
        if command_result is False:
            print_logger.debug("LightSensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE LightSensors(\n\
                sensorId        VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM LightSensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: LightSensors.")
                sys.exit(1)
        else:
            print_logger.debug("LightSensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # HumiditySensors Table                                               #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: HumiditySensors.")
        command_result = self.issue_db_command("SELECT * FROM HumiditySensors;", True)
        
        if command_result is False:
            print_logger.debug("HumiditySensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE HumiditySensors(\n\
                sensorId        VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM HumiditySensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: HumiditySensors.")
                sys.exit(1)
        else:
            print_logger.debug("HumiditySensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # AirTempSensors Table                                               #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: AirTempSensors.")
        command_result = self.issue_db_command("SELECT * FROM AirTempSensors;", True)
        
        if command_result is False:
            print_logger.debug("AirTempSensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE AirTempSensors(\n\
                sensorId        VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM AirTempSensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: AirTempSensors.")
                sys.exit(1)
        else:
            print_logger.debug("AirTempSensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # SoilSensors Table                                                   #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: SoilSensors.")
        command_result = self.issue_db_command("SELECT * FROM SoilSensors;", True)
        
        if command_result is False:
            print_logger.debug("SoilSensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE SoilSensors(\n\
                sensorId        VARCHAR(10),\n\
                locationId      VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM SoilSensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: SoilSensors.")
                sys.exit(1)
        else:
            print_logger.debug("SoilSensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # pHSensors Table                                                     #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: pHSensors.")
        command_result = self.issue_db_command("SELECT * FROM pHSensors;", True)
        
        if command_result is False:
            print_logger.debug("pHSensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE pHSensors(\n\
                sensorId        VARCHAR(10),\n\
                locationId      VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM pHSensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: pHSensors.")
                sys.exit(1)
        else:
            print_logger.debug("pHSensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # WaterLevelSensors Table                                             #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: WaterLevelSensors.")
        command_result = self.issue_db_command("SELECT * FROM WaterLevelSensors;", True)
        
        if command_result is False:
            print_logger.debug("WaterLevelSensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE WaterLevelSensors(\n\
                sensorId        VARCHAR(10),\n\
                locationId      VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM WaterLevelSensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: WaterLevelSensors.")
                sys.exit(1)
        else:
            print_logger.debug("WaterLevelSensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # WaterTempSensors Table                                              #
        # ------------------------------------------------------------------- #
            
        print_logger.debug("Checking Table: WaterTempSensors.")
        command_result = self.issue_db_command("SELECT * FROM WaterTempSensors;", True)
        
        if command_result is False:
            print_logger.debug("WaterTempSensors table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE WaterTempSensors(\n\
                sensorId        VARCHAR(10),\n\
                locationId      VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(sensorId));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM WaterTempSensors;", True)
            if command_result is False:
                print_logger.error("Could not create table: WaterTempSensors.")
                sys.exit(1)
        else:
            print_logger.debug("WaterTempSensors table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # Location Table                                                      #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: Location.")
        command_result = self.issue_db_command("SELECT * FROM Location;", True)
        
        if command_result is False:
            print_logger.debug("Location table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE Location(\n\
                type            VARCHAR(30),\n\
                locationId      VARCHAR(10),\n\
                greenhouseId    VARCHAR(10),\n\
                PRIMARY KEY(locationId, ));", True)
            
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM Location;", True)
            if command_result is False:
                print_logger.error("Could not create table: Location.")
                sys.exit(1)
        else:
            print_logger.debug("Location table exists in the database.")
            
        # ------------------------------------------------------------------- #
        # RequestLog Table                                                    #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: RequestLog.")
        command_result = self.issue_db_command("SELECT * FROM RequestLog;", True)
        
        if command_result is False:
            print_logger.debug("RequestLog table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE RequestLog(\n\
                action                   VARCHAR(255),\n\
                unixTimestampRequested   VARCHAR(30),\n\
                unixTimestampCompleted   VARCHAR(30),\n\
                greenhouseId             VARCHAR(10));", True)
                
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM RequestLog;", True)
            if command_result is False:
                print_logger.error("Could not create table RequestLog.")
        else:
            print_logger.debug("RequestLog table exists in the database.")
        
        # ------------------------------------------------------------------- #
        # LocationMapping Table                                               #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: LocationMapping.")
        command_result = self.issue_db_command("SELECT * FROM LocationMapping;", True)
        
        if command_result is False:
            print_logger.debug("LocationMapping table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE LocationMapping(\n\
                locationId      VARCHAR(10),\n\
                actuatorId      VARCHAR(10),\n\
                greenhouseId    VARCHAR(10));", True)
                
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM LocationMapping;", True)
            if command_result is False:
                print_logger.error("Could not create table LocationMapping.")
                sys.exit(1)
        else:
            print_logger.debug("LocationMapping table exists in the database.")
            
        # ------------------------------------------------------------------- #
        # GlobalMapping Table                                                 #
        # ------------------------------------------------------------------- #
        
        print_logger.debug("Checking Table: GlobalMapping.")
        command_result = self.issue_db_command("SELECT * FROM GlobalMapping;", True)
        
        if command_result is False:
            print_logger.debug("GlobalMapping table does not exist in the database. Creating...")
            command_result = self.issue_db_command("CREATE TABLE GlobalMapping(\n\
                greenhouseId      VARCHAR(10),\n\
                actuatorType      VARCHAR(10),\n\
                actuatorId        VARCHAR(10));", True)
                
            # Test the newly created table
            command_result = self.issue_db_command("SELECT * FROM GlobalMapping;", True)
            if command_result is False:
                print_logger.error("Could not create table GlobalMapping.")
                sys.exit(1)
        else:
            print_logger.debug("GlobalMapping table exists in the database.")
        
        
    def clean_tables(self):
        """
        This function wipes out all of the existing tables in the database.
        """

        print_logger.warning("PURGING DATABASE TABLES!")
        self.issue_db_command("DROP TABLE Users;", True)
        self.issue_db_command("DROP TABLE Greenhouses;", True)
        self.issue_db_command("DROP TABLE Addresses;", True)
        self.issue_db_command("DROP TABLE PhoneNumbers;", True)
        
        self.issue_db_command("DROP TABLE AirTempSensors;", True)
        self.issue_db_command("DROP TABLE HumiditySensors;", True)
        self.issue_db_command("DROP TABLE LightSensors;", True)
        self.issue_db_command("DROP TABLE SoilSensors;", True)
        self.issue_db_command("DROP TABLE pHSensors;", True)
        self.issue_db_command("DROP TABLE WaterLevelSensors;", True)
        self.issue_db_command("DROP TABLE WaterTempSensors;", True)
        
        self.issue_db_command("DROP TABLE AirTempData;", True)
        self.issue_db_command("DROP TABLE HumidityData;", True)
        self.issue_db_command("DROP TABLE LightData;", True)
        self.issue_db_command("DROP TABLE SoilData;", True)
        self.issue_db_command("DROP TABLE pHData;", True)
        self.issue_db_command("DROP TABLE WaterLevelData;", True)
        self.issue_db_command("DROP TABLE WaterTempData;", True)
        
        self.issue_db_command("DROP TABLE RelayOut;", True)
        self.issue_db_command("DROP TABLE UnintializedRelay;", True)
        self.issue_db_command("DROP TABLE LightOut;", True)
        self.issue_db_command("DROP TABLE VentilationOut;", True)
        self.issue_db_command("DROP TABLE SolenoidOut;", True)
        self.issue_db_command("DROP TABLE WaterHeaterOut;", True)
        
        self.issue_db_command("DROP TABLE Location;", True)
        self.issue_db_command("DROP TABLE RequestLog;", True)
        self.issue_db_command("DROP TABLE LocationMapping;", True)
        self.issue_db_command("DROP TABLE GlobalMapping;", True)
        self.issue_db_command("DROP TABLE GreenhouseStatus;", True)
    
    def construct_dummy_database(self):
        """
        This function sets up a dummy state for the website to be test against
        """
    
        # Create greenhouse 1 & 2for the default user
        
        self.issue_db_command("INSERT INTO Greenhouses VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"\
            % ("1", "default", "8413", "Meadowview st.", "Rowlett", "75088", "TX"))
            
        self.issue_db_command("INSERT INTO Greenhouses VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"\
            % ("2", "default", "950", "Colgate Dr. Apt 110", "College Station", "77840", "TX"))
        
        self.issue_db_command("INSERT INTO GreenhouseStatus VALUES('1', 'True')")
        self.issue_db_command("INSERT INTO GreenhouseStatus VALUES('2', 'True')")
        
        
        # Add two relays connected to this circuit
        self.issue_db_command("INSERT INTO RelayOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("1", "192.168.0.1", "11000", "4", "1"))
        
        
        self.issue_db_command("INSERT INTO RelayOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("2", "192.168.0.15", "10001", "8", "1"))
        
        self.issue_db_command("INSERT INTO RelayOut VALUES(\
            \"%s\",\"%s\",\"%s\",\"%s\",\"%s\");"
            % ("3", "192.168.0.23", "10001", "8", "2"))
        
        
        # Add five solenoids connected to this greenhouse
        
        # Notes: Each drip irrigation solenoid needs to have a type.  
        # So far, I can think of three types:
        #  - drip (for small drip irrigation solenoids)
        #  - mainDrip  (for the input to the drip irrigation system)
        #  - hydroponic (a switch for an individual hydroponic tower)
        
        
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("1", "drip", "1", "1", "1", "off"))
      
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("2", "drip", "1", "2", "1", "off"))
            
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("3", "drip", "1", "3", "1", "off"))
            
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("4", "drip", "1", "4", "1", "off"))
        
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("5", "mainDrip", "2", "1", "1", "off"))
        
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("6", "hydroponic", "2", "6", "1", "off"))
        
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("7", "mainDrip", "3", "1", "2", "off"))
        
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("8", "drip", "3", "2", "2", "off"))
        
        self.issue_db_command("INSERT INTO SolenoidOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("9", "drip", "3", "3", "2", "off"))
            
        # Add two light strips
        self.issue_db_command("INSERT INTO LightOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("1", "2", "2", "1", "off"))
        
        self.issue_db_command("INSERT INTO LightOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("2", "2", "7", "1", "off"))
        
        # Add a single ventilation system
        self.issue_db_command("INSERT INTO VentilationOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
            % ("1", "2", "8", "1", "off"))
        
        # Add a few soil moisture sensors
        """
        self.issue_db_command("INSERT INTO SoilSensors VALUES(\
            \"%s\", \"%s\", \"%s\");" % ("1", "1", "1"))
            
        self.issue_db_command("INSERT INTO SoilSensors VALUES(\
            \"%s\", \"%s\", \"%s\");" % ("101", "1", "1"))
        """
        self.issue_db_command("INSERT INTO SoilSensors VALUES(\
            \"%s\", \"%s\", \"%s\");" % ("15", "1", "1"))
        """
        self.issue_db_command("INSERT INTO SoilSensors VALUES(\
            \"%s\", \"%s\", \"%s\");" % ("103", "1", "1"))
    
        self.issue_db_command("INSERT INTO SoilSensors VALUES(\
            \"%s\", \"%s\", \"%s\");" % ("104", "1", "1"))
        """
        # Add some locations.  
        
        # Note: This table allows a type field.  
        # Possible values that I've come up with so far:
        #  - pot
        #  - <Add more here!>
        
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "1", "1"))
        
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "2", "1"))
        
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "3", "1"))
        
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "4", "1"))

        # 
        # ADD DUMMY DATA VALUES TOO!!!
        #
        
        #data for testing -Aaron
        self.issue_db_command("INSERT INTO AirTempSensors VALUES(567, 2)")
        self.issue_db_command("INSERT INTO HumiditySensors VALUES(678, 2)")
        self.issue_db_command("INSERT INTO LightSensors VALUES(789, 2)")
        
        self.issue_db_command("INSERT INTO pHSensors VALUES(69, 124, 1)")
        self.issue_db_command("INSERT INTO pHSensors VALUES(70, 124, 2)")
        #end of testing data -Aaron
            
        # Add a single relay connected to this greenhouse
            
        # Add three solenoids to this greenhouse
        
            
        # Add three light strips
        self.issue_db_command("INSERT INTO LightOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("3", "3", "4", "2", "off"))
        
        self.issue_db_command("INSERT INTO LightOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("4", "3", "5", "2", "off"))
            
        self.issue_db_command("INSERT INTO LightOut VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
            % ("5", "3", "6", "2", "off"))
            
        # Add some locations
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "5", "2"))
        
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "6", "2"))
            
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "7", "2"))
            
        self.issue_db_command("INSERT INTO Location VALUES(\
            \"%s\", \"%s\", \"%s\");"
            % ("pot", "8", "2"))
        
        """
        self.issue_db_command("INSERT INTO SoilData VALUES(1, 1, 900, 100000, 2);", True)
        self.issue_db_command("INSERT INTO SoilData VALUES(1, 1, 1020, 100001, 2);", True)
        self.issue_db_command("INSERT INTO SoilData VALUES(4, 1, 900, 100000, 2);", True)
        self.issue_db_command("INSERT INTO SoilData VALUES(4, 1, 700, 100001, 2);", True)
        """
        #
        #
        # Potentially add data here too!
        #
        #
        
        # Map locations to their actuators
        self.issue_db_command("INSERT INTO LocationMapping VALUES(\
            \"%s\", \"%s\", \"%s\")"\
            % ("1", "1", "2"), True)
            
        self.issue_db_command("INSERT INTO LocationMapping VALUES(\
            \"%s\", \"%s\", \"%s\")"\
            % ("1", "2", "2"), True)
            
        # Map locations to their actuators
        self.issue_db_command("INSERT INTO LocationMapping VALUES(\
            \"%s\", \"%s\", \"%s\")"\
            % ("1", "3", "2"), True)
            
        self.issue_db_command("INSERT INTO LocationMapping VALUES(\
            \"%s\", \"%s\", \"%s\")"\
            % ("1", "4", "2"), True)
        
        # self.issue_db_command("INSERT INTO pHdata VALUES(\
        #     \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
        #     % ("1", "1", "8", "4", "1"), True)
            
        # self.issue_db_command("INSERT INTO pHdata VALUES(\
        #     \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
        #     % ("1", "1", "8", "4", "1"), True)
            
        # self.issue_db_command("INSERT INTO pHdata VALUES(\
        #     \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"
        #     % ("1", "1", "8", "4", "2"), True)
        
        # Map locations to their actuators
        self.issue_db_command("INSERT INTO UninitialzedRelay VALUES(\
            \"%s\", \"%s\", \"%s\", \"%s\", \"%s\")"\
            % ("1", "1", "2", "3", "4"), True)
            
        try:
            database_inserter.mahapatras_greenhouse()
        except Exception as e:
            print e
            helper_functions.scream("Mahapatra's greenhouse DB failure.")