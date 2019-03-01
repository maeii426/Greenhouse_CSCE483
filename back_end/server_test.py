#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developer: Andrew Kirfman                                                    #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./server_test.py                                                       #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
# Standard Library Includes                                                    #
# ---------------------------------------------------------------------------- #

import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import sys
import logging
import copy
import MySQLdb
import smtplib
import random
import string
import time
import thread
import pexpect
from tornado.options import define, options, parse_command_line
from email.mime.text import MIMEText

# ---------------------------------------------------------------------------- #
# User Defined Includes                                                        #
# ---------------------------------------------------------------------------- #

sys.path.append("./static/python")
import helper_functions
import input_gateway
import queue_manager
import output_gateway
import output_helper
from helper_functions import scream

from static_handlers import LoginHandler, ErrorHandler, CreateAccountHandler
from static_handlers import CredentialRecoveryHandler, OverviewScreenHandler
from static_handlers import ProgramFileHandler, FaviconFileHandler, DeleteGreenhouseHandler
from static_handlers import CreateGreenhouseHandler, EditGreenhouseHandler, AddComponentHandler
from greenhouse_database import greenhouse_database
from greenhouse_email import send_email
from data_containers import upload_website_state

sys.path.append("./static/python/actuators")
import relay_actuator
import initialize_pi

# ---------------------------------------------------------------------------- #
# Global Variables                                                             #
# ---------------------------------------------------------------------------- #

# Current Database Parameters
DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASSWD="password"
DB_PRIMARY_DATABASE="greenhouse"

# Maintain a global object that all of the websocket handlers may call
current_greenhouse_database = None

# Email address for the server admin
ADMIN_EMAIL = "andrew.kirfman@tamu.edu"

#other globals
sampling_interval = 5000

# Holds the table names along with server interaction names of all of our database tables.  
# The first element in the tuple is the name that the server is expecting to see in the
# websocket message, and the second is the name of the corresponding database table
RELAY_NAME = ("Relay", "RelayOut")
SOLENOID_NAME = ("Solenoid", "SolenoidOut")
LIGHT_NAME = ("Light", "LightOut")
VENTILATION_NAME = ("Ventilation", "VentilationOut")
SOIL_NAME = ("Soil", "SoilSensors")
LOCATION_NAME = ("Location", "Location")
PH_SENSOR_NAME = ("pHSensor", "pHSensors")
WATER_LEVEL_SENSOR_NAME = ("waterLevelSensor", "WaterLevelSensors")
WATER_TEMP_SENSOR_NAME = ("waterTempSensor", "WaterTempSensors")
AIR_HUMIDITY_SENSOR_NAME = ("airHumiditySensor", "HumiditySensors")
AIR_TEMP_SENSOR_NAME = ("airTempSensor", "AirTempSensors")
LIGHT_SENSOR_NAME = ("lightSensor", "LightSensors")
PH_DATA_NAME = ("pHData", "pHData")


# ---------------------------------------------------------------------------- #
# Command Line Arguments                                                       #
# ---------------------------------------------------------------------------- #

# Import Command Line Arguments
define("port", default=8888, help="Run on the given port", type=int)
define("logger", default="", help="Define the current logging level", type=str)

# ---------------------------------------------------------------------------- #
# Console/File Logger                                                          #
# ---------------------------------------------------------------------------- #

print_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
# Websocket Handlers                                                           #
# ---------------------------------------------------------------------------- #

class LoginWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self, _):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        """
        This function validates the user's logon information information.

        It should be called when they press the logon button with a username
        and a password.
        """

        print_logger.debug("Message Received: %s" % str(message))

        if "ValidateLogin" in message:
            message = message.split(":")
            
            if len(message) != 3 or message[0] != "ValidateLogin":
                print_logger.error("Unknown client-side error while validating username")
                self.write_message("ValidationFalied:UnknownError")
                return
                
            username = message[1]
            password = message[2]
            
            database_result = current_greenhouse_database.issue_db_command("SELECT username, password "
                + "FROM Users")
            
            success = False
            
            for database_tuple in database_result:
                if username == database_tuple[0] and password in database_tuple[1]:
                    print_logger.debug("Sending message: ValidationSucceeded")
                    self.write_message("ValidationSucceeded")
                    return
            
            if success is False:
                print_logger.debug("Sending Message: ValidationSucceeded")
                self.write_message("ValidationFailed")
        else:
            print_logger.error("Unknown Message Received")
            return


class ErrorWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self, _):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Page: 404, Message Received: %s" % str(message))

        if "SubmitReport" in message:
            message = message.split(":")

            # Clean the text
            for i in range(0, len(message)):
                message[i] = message[i].strip()

            if len(message) >= 2 and message[0] == "SubmitReport":
                final_message = ""

                for i in range(0, len(message)):
                    if i is not 0:
                        if i != 1:
                            final_message = final_message + ":" + str(message[i])
                        else:
                            final_message = final_message + str(message[i])

                final_message = "Greenhouse Error Report:\n\n" + final_message
                print_logger.debug("Sending Email: %s" % final_message.replace("\n", ""))
                send_email("Greenhouse Error Report", final_message, ADMIN_EMAIL)
            else:
                print_logger.warning("Page: 404, Invalid Message.")
        else:
            print_logger.warning("Page: 404, Invalid Message.")

class CreateAccountWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Page: create_new_account, Message Received: %s" % str(message))

        # If here, The user is starting the account creation process
        if "ValidateUsername" in message:
            # Split the message into multiple pieces
            message = message.split(":")

            # Perform some basic error checking
            if message[0] != "ValidateUsername":
                print_logger.error("Unknown client-side error while validating username")
                self.write_message("ValidationFalied:UnknownError")
                return

            if len(message) != 6:
                print_logger.error("Unknown client-side error while validating username")
                self.write_message("ValidationFailed:UnknownError")
                return

            # Issue a command to the database to ensure that the requested
            # username isn't already there
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Users"
                + " WHERE username='%s';" % message[1].strip())

            # Something went wrong with the database. Return an error
            if database_result is False:
                print_logger.error("Could not perform select of database")
                self.write_message("ValidationFailed:Username")
                return

            # If the username isn't found, insert it into the Users table
            if len(database_result) == 0:
                print_logger.debug("Requested username not found in database.")

                username = message[1]
                fname = message[2]
                lname = message[3]
                email = message[4]
                password = message[5]

                print_logger.debug("Inserting new username, %s, into the database" % (username))
                database_result = current_greenhouse_database.issue_db_command("INSERT "\
                    + "INTO Users VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                    % (username, fname, lname, email, password))

                # Make sure that the insert proceeds successfully
                if len(database_result) != 0 or database_result is False:
                    print_logger.error("Could not insert new user into the database")
                    self.write_message("ValidationFailed:UnknownError")
                    return

                print_logger.debug("New user inserted successfully")
                self.write_message("ValidationSucceeded")

            # If a username already exists in the database, return an error back to the user
            else:
                print_logger.warning("Name already exists in the database")
                self.write_message("ValidationFailed:Username")

        # If here, the user wants to insert a new phone number into their account
        elif "InsertPhone" in message:
            message = message.split(":")

            if len(message) != 3:
                print_logger.error("Unknown client-side error while inserting phone number")
                return

            if message[0] != "InsertPhone":
                print_logger.error("Unknown client-side error while inserting phone number")
                return

            username = message[1]
            number = message[2]

            # The combo username phone is primary key so there is no need to check it
            # to make sure that the number isn't already in the database
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO PhoneNumbers"
                + " VALUES(\"%s\", \"%s\")" % (username, number))

            if database_result is False:
                print_logger.error("Something went wrong in inserting the given phone number")
            else:
                # If we made it here, then the phone number made it into the table
                print_logger.debug("Phone number, %s, for user, %s, inserted into table successfully"\
                    % (number, username))

        # If here, the user wants to insert a new address into their account
        elif "InsertAddress" in message:
            message = message.split(":")

            if len(message) < 2:
                print_logger.error("Unknown client-side error while inserting address")
                return

            if message[0] != "InsertAddress":
                print_logger.error("Unknown client-side error while inserting address")
                return

            final_message = ""
            for i in range(1, len(message)):
                final_message = final_message + str(message[i])

            final_message = final_message.split("|")

            if len(final_message) != 8:
                print_logger.error("Incorrect number of address elements")
                return

            username = final_message[0]
            number = final_message[1]
            street = final_message[2]
            city = final_message[3]
            zip_code = final_message[4]
            state = final_message[5]
            isGreenhouse = final_message[6]

            if isGreenhouse == "yes":
                isGreenhouse = "TRUE"
            else:
                isGreenhouse = "FALSE"

            isResidence = final_message[7]

            if isResidence == "yes":
                isResidence = "TRUE"
            else:
                isResidene = "FALSE"

            database_result = current_greenhouse_database.issue_db_command("INSERT INTO Addresses"\
                + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s, %s);"\
                % (username, number, street, city, zip_code, state, isGreenhouse, isResidence))

            if database_result == False:
                print_logger.error("Could not insert new address into the database.")
                return


class CredentialRecoveryWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True

    def open(self):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Credential Recovery, Message Received: %s" % message)

        if "recover-email" in message:
            message = message.split(":")
            address = message[1]
            
            #generate new (temporary) password
            newpass = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
            
            #make sure email is associated with a known user
            username = database_result = current_greenhouse_database.issue_db_command("SELECT username FROM Users WHERE emailAddress='%s'" % (address))
            print_logger.debug("Username corresponding to email %s: %s" % (address, str(username)))

            if not database_result: 
                self.write_message("email-lookup-failure")
                print_logger.error("Could not find email address")
                return
            username = database_result[0]
            username = username[0]
            
            #update Database
            database_result = current_greenhouse_database.issue_db_command("UPDATE Users SET password='%s' WHERE emailAddress='%s'" % (newpass, address))
            
            #send email
            subject = "sGreen Credential Recovery"
            message = "Howdy!\n\n"
            message += "You have selected to reset your password\n"
            message += "Username: " + username + "\n"
            message += "Password: " + newpass
            send_email(subject, message, address)
            
            self.write_message("email-sent")
            return


class OverviewScreenWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True
    def open(self):
        pass
        
    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Overview Screen, Message Received: %s" % message)
        
        
        # Check in the database in order to see if the user has greenhouses
        if "HasGreenhouses:" in message:
            message = message.split(":")
            
            if message[0] != "HasGreenhouses":
                print_logger.error("Malformed input message from overview screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from overview screen handler.")
                return
            
            username = message[1]
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE username = '%s';" % username)
            
            if database_result is False:
                print_logger.error("Something went wrong with the greenhouse lookup for User: %s" % username)
            
            if len(database_result) == 0:
                self.write_message("UserHasNoGreenhouses")
            else:
                greenhouse_ids = ""
                first = True
                for greenhouse in database_result:
                    if first is True:
                        greenhouse_ids = greenhouse_ids + str(greenhouse[0])
                        first = False
                    else:
                        greenhouse_ids = greenhouse_ids + ":" + str(greenhouse[0])
    
                print_logger.debug("User: %s. Current greenhouse configuration: %s" % (username, greenhouse_ids))
    
                self.write_message("UserHasGreenhouses:%s" % greenhouse_ids)
        elif "SendInitialConfiguration" in message:
            # Figure out what greenhouse they want configuration for
            message = message.split(":")
            greenhouse_id = message[1]

            # --------------------------------------------------------------- #
            # Send Relays                                                     #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, RELAY_NAME[0], RELAY_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send Solenoids                                                  #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, SOLENOID_NAME[0], SOLENOID_NAME[1], greenhouse_id)

            # --------------------------------------------------------------- #
            # Send Lights                                                     #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, LIGHT_NAME[0], LIGHT_NAME[1], greenhouse_id)
                
            # --------------------------------------------------------------- #
            # Send Ventilation                                                #
            # --------------------------------------------------------------- #
        
            upload_website_state(self, current_greenhouse_database, VENTILATION_NAME[0], VENTILATION_NAME[1], greenhouse_id)
                    
            # --------------------------------------------------------------- #
            # Send SoilSensors                                                #
            # --------------------------------------------------------------- #

            upload_website_state(self, current_greenhouse_database, SOIL_NAME[0], SOIL_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send Location                                                   #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, LOCATION_NAME[0], LOCATION_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send pHSensor                                                   #
            # --------------------------------------------------------------- #            
            
            upload_website_state(self, current_greenhouse_database, PH_SENSOR_NAME[0], PH_SENSOR_NAME[1], greenhouse_id)

            # --------------------------------------------------------------- #
            # Send waterLevelSensors                                          #
            # --------------------------------------------------------------- #  
            
            upload_website_state(self, current_greenhouse_database, WATER_LEVEL_SENSOR_NAME[0], WATER_LEVEL_SENSOR_NAME[1], greenhouse_id)

            # --------------------------------------------------------------- #
            # Send waterTempSensors                                           #
            # --------------------------------------------------------------- #  
            
            upload_website_state(self, current_greenhouse_database, WATER_TEMP_SENSOR_NAME[0], WATER_TEMP_SENSOR_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send airHumiditySensor                                          #
            # --------------------------------------------------------------- # 
            
            upload_website_state(self, current_greenhouse_database, AIR_HUMIDITY_SENSOR_NAME[0], AIR_HUMIDITY_SENSOR_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send airTempSensor                                              #
            # --------------------------------------------------------------- # 
            
            upload_website_state(self, current_greenhouse_database, AIR_TEMP_SENSOR_NAME[0], AIR_TEMP_SENSOR_NAME[1], greenhouse_id)
            # --------------------#
            # Send pH data        #
            # --------------------#
            upload_website_state(self, current_greenhouse_database, PH_DATA_NAME[0], PH_DATA_NAME[1], greenhouse_id)
            
            # --------------------#
            # Send LightSensor    #
            # --------------------#
            upload_website_state(self, current_greenhouse_database, LIGHT_SENSOR_NAME[0], LIGHT_SENSOR_NAME[1], greenhouse_id)
            
        elif "actuateActuator" in message:
            """
            to   : all
            from : Aaron
            msg  : Expected format of message for changing an actuator is
             format  ---> "actuateActuator:(greenhouseId):(actuatorId):(outTable):(state)"
             example ---> "actuateActuator:69:SolenoidOut:2:True"
            """
            
            command = message.split(":")
            if len(command) == 5:
                greenhouse_id = command[1]
                actuator_id = command[2]
                out_table = command[3]
                state = (command[4].lower() == "true")
                print state
                #TODO: True is here temporarily for manual control
                if True or not output_helper.greenhouse_on_auto(greenhouse_id):
                    print state

                    print "ATTEMPTING TO CHANGE STATE OF A RELAY TO: %s" % state
                    output_helper.actuate_relay(actuator_id, out_table, state)
                    self.write_message("TaskDone:True:%s" % greenhouse_id)
                else:
                    scream("actuateActuator problem : GREENHOUSE IS ON AUTOMATIC CONTROL\nmessage : %s" % message)
                    self.write_message("TaskDone:False:GREENHOUSE IS ON AUTOMATIC CONTROL")
            else:
                scream("actuateActuator was formatted wrong (probably wrong length) : %s" % message)
                self.write_message("TaskDone:False:wrong length")
        elif "SwitchMode:" in message:
            """
            This give user sudo permission to mess with the greenhouse control
            SwitchMode:(greenhouseId):(boolean)
            """
            command = message.split(":")
            greenhouse_id = command[1]
            boolean = command[2].lower()
            helper_functions.execute_SQL_oneoff("UPDATE GreenhouseStatus SET automaticControl=%s WHERE greenhouseId=%s", (boolean, greenhouse_id))
            self.write_message("GreenhouseModeUpdate:%s:%s" % (boolean, greenhouse_id))
            
        elif "GetMode:" in message:
            """
            GetMode:(greenhouseId)
            return value is true if the greenhouse is on automatic control
            """
            command = message.split(":")
            greenhouse_id = command[1]
            print helper_functions.execute_SQL_oneoff("SELECT automaticControl FROM GreenhouseStatus WHERE greenhouseId=%s", (greenhouse_id,))
            boolean = helper_functions.execute_SQL_oneoff("SELECT automaticControl FROM GreenhouseStatus WHERE greenhouseId=%s", (greenhouse_id,))[0][0]
            self.write_message("GreenhouseModeStatus:%s:%s" % (boolean, greenhouse_id))
            
        elif "GetRecentReading:" in message:
            """
            GetRecentReading:(sensorType):(greenhouseId):(sensorId)
            Valid sensorTypes (case sensitive):
                AirTemp
                Humidity
                Light
                Soil
                pH
                WaterLevel
                WaterTemp
            
            response:
                RecentReading:(sensorType):(greenhouseId):(sensorId):(reading)
            """
            command = message.split(":")
            sensor_type = command[1]
            greenhouse_id = command[2]
            sensor_id = command[3]
            reading = helper_functions.get_recent_reading(sensor_type, greenhouse_id, sensor_id)
            self.write_message("recentReading:%s:%s:%s:%s" % (sensor_type, greenhouse_id, sensor_id, reading))
        else:
            # Things and stuff here!!!  
            pass

class CreateGreenhouseWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True
    def open(self):
        pass
    
    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Page: create_greenhouse, Message Received: %s" % str(message))
        
        if "HasGreenhouses:" in message:
            message = message.split(":")
            
            if message[0] != "HasGreenhouses":
                print_logger.error("Malformed input message from create greenhouse screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from create greenhouse screen handler.")
                return
            
            username = message[1]
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE username = '%s';" % username)
            
            if database_result is False:
                print_logger.error("Something went wrong with the greenhouse lookup for User: %s" % username)
            
            if len(database_result) == 0:
                self.write_message("UserHasNoGreenhouses")
            else:
                greenhouse_ids = ""
                first = True
                for greenhouse in database_result:
                    if first is True:
                        greenhouse_ids = greenhouse_ids + str(greenhouse[0])
                        first = False
                    else:
                        greenhouse_ids = greenhouse_ids + ":" + str(greenhouse[0])
    
                print_logger.debug("User: %s. Current greenhouse configuration:%s" % (username, greenhouse_ids))
    
                self.write_message("UserHasGreenhouses:%s" % greenhouse_ids)
        elif "SendGreenhouseInfo" in message:
            message = message.split(":")
            
            if message[0] != "SendGreenhouseInfo":
                print_logger.error("Malformed input message from create greenhouse screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from create greenhouse screen handler.")
                return
            
            greenhouse_id = message[1]
            
            # --------------------------------------------------------------- #
            # Send Address                                                    #
            # --------------------------------------------------------------- #
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE greenhouseId = '%s';" % greenhouse_id)
            print_logger.debug(database_result)
            
            address = ""
            first = True
            for s in database_result[0]:
                if first is True:
                    address = address + str(s)
                    first = False
                else:
                    address = address + ":" + str(s)
            
            self.write_message("GreenhouseAddress:%s" % address)
            
            # --------------------------------------------------------------- #
            # Send Relays                                                     #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, RELAY_NAME[0], RELAY_NAME[1], greenhouse_id)
            
        elif "CreateGreenhouse" in message:
            message = message.split(":")
            
            if message[0] != "CreateGreenhouse":
                print_logger.error("Malformed input message from create greenhouse screen handler.")
                return
            
            if len(message) != 7:
                print_logger.error("Malformed input message from create greenhouse screen handler.")
                return
            
            username = message[1]
            number = message[2]
            street = message[3]
            city = message[4]
            zip_code = message[5]
            state = message[6]
            
            # Assign appropriate greenhouseId
            id_list = []
            greenhouse_id = 1
            database_result = current_greenhouse_database.issue_db_command("SELECT greenhouseId FROM Greenhouses;")
            for res in database_result:
                id_list.append(int(res[0]))

            foundId = False
            while foundId is False:
                if greenhouse_id in id_list:
                    greenhouse_id = greenhouse_id + 1
                else:
                    foundId = True
            
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO Greenhouses"\
                + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                % (greenhouse_id, username, number, street, city, zip_code, state))

            if database_result == False:
                print_logger.error("Could not insert new greenhouse into the database.")
                return
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Addresses WHERE "\
                + "username = \"%s\" AND houseNumber = \"%s\" AND street = \"%s\" AND city = \"%s\" AND zip = \"%s\" AND state = \"%s\";"\
                % (username, number, street, city, zip_code, state))
            
            if database_result is not False:
                database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Addresses WHERE "\
                    + "username = \"%s\" AND houseNumber = \"%s\" AND street = \"%s\" AND city = \"%s\" AND zip = \"%s\" AND state = \"%s\" AND isGreenhouse = TRUE;"\
                    % (username, number, street, city, zip_code, state))
                    
                if database_result is False:
                    database_result = current_greenhouse_database.issue_db_command("UPDATE Addresses SET isGreenhouse = TRUE WHERE "\
                        + "username = \"%s\" AND houseNumber = \"%s\" AND street = \"%s\" AND city = \"%s\" AND zip = \"%s\" AND state = \"%s\";"\
                        % (username, number, street, city, zip_code, state))
                        
                    if database_result == False:
                        print_logger.error("Could not update address in the database.")
                        return
            else:
                database_result = current_greenhouse_database.issue_db_command("INSERT INTO Addresses"\
                    + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", TRUE, FALSE);"\
                    % (username, number, street, city, zip_code, state))
    
                if database_result == False:
                    print_logger.error("Could not insert new address into the database.")
                    return
                
            self.write_message("Reload")
        else:
            pass
        
class EditGreenhouseWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True
    def open(self):
        pass
    
    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Edit Greenhouse, Message Received: %s" % message)
        
        # Check in the database in order to see if the user has greenhouses
        if "HasGreenhouses:" in message:
            message = message.split(":")
            
            if message[0] != "HasGreenhouses":
                print_logger.error("Malformed input message from edit greenhouse screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from edit greenhouse screen handler.")
                return
            
            username = message[1]
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE username = '%s';" % username)
            
            if database_result is False:
                print_logger.error("Something went wrong with the greenhouse lookup for User: %s" % username)
            
            if len(database_result) == 0:
                self.write_message("UserHasNoGreenhouses")
            else:
                greenhouse_ids = ""
                first = True
                for greenhouse in database_result:
                    if first is True:
                        greenhouse_ids = greenhouse_ids + str(greenhouse[0])
                        first = False
                    else:
                        greenhouse_ids = greenhouse_ids + ":" + str(greenhouse[0])
    
                print_logger.debug("User: %s. Current greenhouse configuration: %s" % (username, greenhouse_ids))
    
                self.write_message("UserHasGreenhouses:%s" % greenhouse_ids)
        elif "SendInitialConfiguration" in message:
            # Figure out what greenhouse they want configuration for
            message = message.split(":")
            greenhouse_id = message[1]

            # --------------------------------------------------------------- #
            # Send Relays                                                     #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, RELAY_NAME[0], RELAY_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send Solenoids                                                  #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, SOLENOID_NAME[0], SOLENOID_NAME[1], greenhouse_id)

            # --------------------------------------------------------------- #
            # Send Lights                                                     #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, LIGHT_NAME[0], LIGHT_NAME[1], greenhouse_id)
                
            # --------------------------------------------------------------- #
            # Send Ventilation                                                #
            # --------------------------------------------------------------- #
        
            upload_website_state(self, current_greenhouse_database, VENTILATION_NAME[0], VENTILATION_NAME[1], greenhouse_id)
                    
            # --------------------------------------------------------------- #
            # Send SoilSensors                                                #
            # --------------------------------------------------------------- #

            upload_website_state(self, current_greenhouse_database, SOIL_NAME[0], SOIL_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send Location                                                   #
            # --------------------------------------------------------------- #
            
            upload_website_state(self, current_greenhouse_database, LOCATION_NAME[0], LOCATION_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send pHSensor                                                   #
            # --------------------------------------------------------------- #            
            
            upload_website_state(self, current_greenhouse_database, PH_SENSOR_NAME[0], PH_SENSOR_NAME[1], greenhouse_id)

            # --------------------------------------------------------------- #
            # Send waterLevelSensors                                          #
            # --------------------------------------------------------------- #  
            
            upload_website_state(self, current_greenhouse_database, WATER_LEVEL_SENSOR_NAME[0], WATER_LEVEL_SENSOR_NAME[1], greenhouse_id)

            # --------------------------------------------------------------- #
            # Send waterTempSensors                                           #
            # --------------------------------------------------------------- #  
            
            upload_website_state(self, current_greenhouse_database, WATER_TEMP_SENSOR_NAME[0], WATER_TEMP_SENSOR_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send airHumiditySensor                                          #
            # --------------------------------------------------------------- # 
            
            upload_website_state(self, current_greenhouse_database, AIR_HUMIDITY_SENSOR_NAME[0], AIR_HUMIDITY_SENSOR_NAME[1], greenhouse_id)
            
            # --------------------------------------------------------------- #
            # Send airTempSensor                                              #
            # --------------------------------------------------------------- # 
            
            upload_website_state(self, current_greenhouse_database, AIR_TEMP_SENSOR_NAME[0], AIR_TEMP_SENSOR_NAME[1], greenhouse_id)
            
        else:
            # Things and stuff here!!!  
            pass
    
class DeleteGreenhouseWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True
    def open(self):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Page: delete_greenhouse, Message Received: %s" % str(message))
        
        if "HasGreenhouses:" in message:
            message = message.split(":")
            
            if message[0] != "HasGreenhouses":
                print_logger.error("Malformed input message from delete greenhouse screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from delete greenhouse screen handler.")
                return
            
            username = message[1]
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE username = '%s';" % username)
            
            if database_result is False:
                print_logger.error("Something went wrong with the greenhouse lookup for User: %s" % username)
            
            if len(database_result) == 0:
                self.write_message("UserHasNoGreenhouses")
            else:
                greenhouse_ids = ""
                first = True
                for greenhouse in database_result:
                    if first is True:
                        greenhouse_ids = greenhouse_ids + str(greenhouse[0])
                        first = False
                    else:
                        greenhouse_ids = greenhouse_ids + ":" + str(greenhouse[0])
    
                print_logger.debug("User: %s. Current greenhouse configuration:%s" % (username, greenhouse_ids))
    
                self.write_message("UserHasGreenhouses:%s" % greenhouse_ids)
        elif "SendGreenhouseInfo" in message:
            message = message.split(":")
            
            if message[0] != "SendGreenhouseInfo":
                print_logger.error("Malformed input message from delete greenhouse screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from delete greenhouse screen handler.")
                return
            
            greenhouse_id = message[1]
            
            # --------------------------------------------------------------- #
            # Send Address                                                    #
            # --------------------------------------------------------------- #
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE greenhouseId = '%s';" % greenhouse_id)
            print_logger.debug(database_result)
            
            address = ""
            first = True
            for s in database_result[0]:
                if first is True:
                    address = address + str(s)
                    first = False
                else:
                    address = address + ":" + str(s)
            
            self.write_message("GreenhouseAddress:%s" % address)
            
        elif "RemoveGreenhouse" in message:
            message = message.split(":")
            
            if message[0] != "RemoveGreenhouse":
                print_logger.error("Malformed input message from delete greenhouse screen handler.")
                return
            
            if len(message) != 2:
                print_logger.error("Malformed input message from delete greenhouse screen handler.")
                return
            
            current_greenhouse_database.issue_db_command("DELETE FROM Greenhouses WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM GreenhouseStatus WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM WaterLevelData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM LightData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM AirTempData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM SoilData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM WaterTempData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM HumidityData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM pHData WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM RelayOut WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM SolenoidOut WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM WaterHeaterOut WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM LightOut WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM VentilationOut WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM LightSensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM HumiditySensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM AirTempSensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM SoilSensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM pHSensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM WaterLevelSensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM WaterTempSensors WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM Location WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM RequestLog WHERE greenhouseId = '%s';" % message[1])
            current_greenhouse_database.issue_db_command("DELETE FROM GlobalMapping WHERE greenhouseId = '%s';" % message[1])
            
            self.write_message("Reload")

        else:
            pass

class AddComponentWsHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, _):
        return True
    def open(self):
        pass

    @tornado.web.asynchronous
    def on_message(self, message):
        print_logger.debug("Page: add_component, Message Received: %s" % str(message))
        
        if "HasGreenhouses:" in message:
            message = message.split(":")
            
            if message[0] != "HasGreenhouses":
                print_logger.error("Malformed input message from add component screen handler.")
                return
            
            username = message[1]
            
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE username = '%s';" % username)
            
            if database_result is False:
                print_logger.error("Something went wrong with the greenhouse lookup for User: %s" % username)
            
            if len(database_result) == 0:
                self.write_message("UserHasNoGreenhouses")
            else:
                greenhouse_ids = ""
                id_list = []
                first = True
                for greenhouse in database_result:
                    if first is True:
                        greenhouse_ids = greenhouse_ids + str(greenhouse[0])
                        id_list.append(int(greenhouse[0]))
                        first = False
                    else:
                        greenhouse_ids = greenhouse_ids + ":" + str(greenhouse[0])
                        id_list.append(int(greenhouse[0]))
                        
                master_response = ''
                master_first = True
                for greenhouse_id in id_list:
                    if master_first:
                        master_response = master_response + str(greenhouse_id)
                        master_first = False
                    else:
                        master_response = master_response + ":" + str(greenhouse_id)
                    
                    # --------------------------------------------------------------- #
                    # Send Address                                                    #
                    # --------------------------------------------------------------- #
                    
                    database_result = current_greenhouse_database.issue_db_command("SELECT * FROM Greenhouses WHERE greenhouseId = '%s';" % greenhouse_id)
                    
                    address = ""
                    first = True
                    for s in database_result[0]:
                        if first is True:
                            address = address + str(s)
                            first = False
                        else:
                            address = address + ":" + str(s)
                            
                    uninit_relays = 0
                    locations = 0
                    database_result = current_greenhouse_database.issue_db_command("SELECT numberOfChannels FROM UninitializedRelay WHERE greenhouseId = '%s';" % greenhouse_id)
                    if database_result != False:
                        for res in database_result:
                            uninit_relays = uninit_relays + int(res[0])
                            
                    database_result = current_greenhouse_database.issue_db_command("SELECT locationId FROM Location WHERE greenhouseId = '%s';" % greenhouse_id)
                    if database_result != False:
                        for res in database_result:
                            if res != 'hydroponic':
                                locations = locations + 1
                                
                    master_response = master_response + ":" + address + ":" + str(uninit_relays) + ":" + str(locations)
                            
    
                print_logger.debug("User: %s. Current greenhouse configuration:%s" % (username, greenhouse_ids))
                self.write_message("UserHasGreenhouses:%s" % master_response)
            
        elif "SetupPi" in message:
            message = message.split(":");
            greenhouse_id = message[1]
            
            port_list = []
            port = 11001
            database_result = current_greenhouse_database.issue_db_command("SELECT portNumber FROM UninitializedRelay;")
            if database_result != False:
                for res in database_result:
                    port_list.append(int(res[0]))
            database_result = current_greenhouse_database.issue_db_command("SELECT portNumber FROM RelayOut;")
            if database_result != False:
                for res in database_result:
                    port_list.append(int(res[0]))

            foundId = False
            while foundId is False:
                if port in port_list:
                    port = port + 1
                else:
                    foundId = True
                
            id_list = []
            relay_id = 1
            database_result = current_greenhouse_database.issue_db_command("SELECT relayId FROM UninitializedRelay;")
            print_logger.debug(database_result)
            if database_result != False:
                for res in database_result:
                    id_list.append(int(res[0]))
            database_result = current_greenhouse_database.issue_db_command("SELECT relayId FROM RelayOut;")
            if database_result != False:
                for res in database_result:
                    id_list.append(int(res[0]))
                    
            foundId = False
            while foundId is False:
                if relay_id in id_list:
                    relay_id = relay_id + 1
                else:
                    foundId = True
             
            channels = initialize_pi.setup(port, relay_id)
            if channels == 'timeout':
                return
            
            pi_ip = ''
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO UninitializedRelay"\
                + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                % (relay_id, pi_ip, port, channels, greenhouse_id))
                
            if database_result == False:
                print_logger.error("Could not insert new address into the database.")
                return
            
            self.write_message("success:relay:" + str(channels))
            
        elif "CreateLocation" in message:
            message = message.split(":");
            greenhouse_id = message[1]    
            
            loc_id = 1
            id_list = []
            database_result = current_greenhouse_database.issue_db_command("SELECT locationId FROM Location;")
            if database_result != False:
                for res in database_result:
                    id_list.append(int(res[0]))

            foundId = False
            while foundId is False:
                if loc_id in id_list:
                    loc_id = loc_id + 1
                else:
                    foundId = True
                    
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO Location"\
                + " VALUES(\"%s\", \"%s\", \"%s\");"\
                % (message[2], loc_id, greenhouse_id))
                
                
            if database_result == False:
                print_logger.error("Could not insert new address into the database.")
                return
            else:
                self.write_message("MakeWarning:location:%s:%s" % (message[2], loc_id))
                
        elif "CreateSolenoid" in message:
            message = message.split(":");
            greenhouse_id = message[1]    
            
            if len(message) < 4:
                print_logger.error("Need to map to at least one location")
                return
            
            #current_greenhouse_database.issue_db_command("DROP TABLE UninitializedRelay;")
            #current_greenhouse_database.issue_db_command("DROP TABLE RelayOut;")
            
            sol_id = 1
            sol_list = []
            database_result = current_greenhouse_database.issue_db_command("SELECT actuatorId FROM SolenoidOut;")
            if database_result != False:
                for res in database_result:
                    sol_list.append(int(res[0]))

            foundId = False
            while foundId is False:
                if sol_id in sol_list:
                    sol_id = sol_id + 1
                else:
                    foundId = True
                    
            relay_id = 0
            channel_id = 0
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM UninitializedRelay WHERE greenhouseId = '%s';" % greenhouse_id)
            print_logger.debug(database_result)
            if database_result != False:
                relay_id = database_result[0][0]
                piIp = database_result[0][1]
                port = database_result[0][2]
                channel_id = database_result[0][3]
                if channel_id == 1:
                    current_greenhouse_database.issue_db_command("DELETE FROM UninitializedRelay WHERE relayId = '%s';" % relay_id)
                else:
                    new_num = int(channel_id) - 1
                    current_greenhouse_database.issue_db_command("UPDATE UninitializedRelay SET numberOfChannels = \"%s\" WHERE relayId = \"%s\" AND piIp = \"%s\" AND portNumber = \"%s\" AND greenhouseId = \"%s\";"\
                        % (new_num, relay_id, piIp, port, greenhouse_id))
                relay_exists = current_greenhouse_database.issue_db_command("SELECT * FROM RelayOut WHERE relayId = '%s';" % relay_id)
                if len(relay_exists) == 0:
                    database_result = current_greenhouse_database.issue_db_command("INSERT INTO RelayOut"\
                        + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                        % (relay_id, piIp, port, "1", greenhouse_id))
                else:
                    get_channels = current_greenhouse_database.issue_db_command("SELECT numberOfChannels FROM RelayOut WHERE relayId = '%s';" % relay_id)
                    print_logger.debug(get_channels)
                    num_channels = int(get_channels[0])
                    current_greenhouse_database.issue_db_command("UPDATE RelayOut SET numberOfChannels = \"%s\" WHERE relayId = \"%s\" AND piIp = \"%s\" AND portNumber = \"%s\" AND greenhouseId = \"%s\";"\
                        % (str(num_channels+1), relay_id, piIp, port, greenhouse_id))
            else:
                return
                    
            sol_type = message[2]
            
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO SolenoidOut"\
                + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                % (sol_id, sol_type, relay_id, channel_id, greenhouse_id, "off", "0"))
            
            for loc in message[3:]:
                database_result = current_greenhouse_database.issue_db_command("INSERT INTO LocationMapping"\
                    + " VALUES(\"%s\", \"%s\", \"%s\");"\
                    % (loc, sol_id, greenhouse_id))
                    
            return_message = "MakeWarning:A new solenoid has been added to relay %s on channel %s." % (relay_id, channel_id)
            self.write_message(return_message)
        
        elif "CreateLight" in message:
            message = message.split(":");
            greenhouse_id = message[1]  
            
            light_id = 1
            light_list = []
            database_result = current_greenhouse_database.issue_db_command("SELECT actuatorId FROM LightOut;")
            if database_result != False:
                for res in database_result:
                    light_list.append(int(res[0]))

            foundId = False
            while foundId is False:
                if light_id in light_list:
                    light_id = light_id + 1
                else:
                    foundId = True
            
            relay_id = 0
            channel_id = 0
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM UninitializedRelay WHERE greenhouseId = '%s';" % greenhouse_id)
            if database_result != False or len(database_result) > 0:
                relay_id = database_result[0][0]
                piIp = database_result[0][1]
                port = database_result[0][2]
                channel_id = database_result[0][3]
                if channel_id == 1:
                    current_greenhouse_database.issue_db_command("DELETE FROM UninitializedRelay WHERE relayId = '%s';" % relay_id)
                else:
                    new_num = int(channel_id) - 1
                    current_greenhouse_database.issue_db_command("UPDATE UninitializedRelay SET numberOfChannels = \"%s\" WHERE relayId = \"%s\" AND piIp = \"%s\" AND portNumber = \"%s\" AND greenhouseId = \"%s\";"\
                        % (new_num, relay_id, piIp, port, greenhouse_id))
                relay_exists = current_greenhouse_database.issue_db_command("SELECT * FROM RelayOut WHERE relayId = '%s';" % relay_id)
                if len(relay_exists) == 0:
                    database_result = current_greenhouse_database.issue_db_command("INSERT INTO RelayOut"\
                        + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                        % (relay_id, piIp, port, "1", greenhouse_id))
                else:
                    get_channels = current_greenhouse_database.issue_db_command("SELECT numberOfChannels FROM RelayOut WHERE relayId = '%s';" % relay_id)
                    print_logger.debug(get_channels)
                    num_channels = int(get_channels[0][0])
                    current_greenhouse_database.issue_db_command("UPDATE RelayOut SET numberOfChannels = \"%s\" WHERE relayId = \"%s\" AND piIp = \"%s\" AND portNumber = \"%s\" AND greenhouseId = \"%s\";"\
                        % (str(num_channels+1), relay_id, piIp, port, greenhouse_id))
            else:
                return
            
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO LightOut"\
                + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                % (light_id, relay_id, channel_id, greenhouse_id, "off"))
                
            return_message = "MakeWarning:A new light has been added to relay %s on channel %s." % (relay_id, channel_id)
            self.write_message(return_message)
        
        elif "CreateVent" in message:
            message = message.split(":");
            greenhouse_id = message[1]  
            
            vent_id = 1
            vent_list = []
            database_result = current_greenhouse_database.issue_db_command("SELECT actuatorId FROM VentilationOut;")
            if database_result != False:
                for res in database_result:
                    vent_list.append(int(res[0]))

            foundId = False
            while foundId is False:
                if vent_id in vent_list:
                    vent_id = vent_id + 1
                else:
                    foundId = True
            
            relay_id = 0
            channel_id = 0
            database_result = current_greenhouse_database.issue_db_command("SELECT * FROM UninitializedRelay WHERE greenhouseId = '%s';" % greenhouse_id)
            print_logger.debug(database_result)
            if database_result != False:
                relay_id = database_result[0][0]
                piIp = database_result[0][1]
                port = database_result[0][2]
                channel_id = database_result[0][3]
                if channel_id == 1:
                    current_greenhouse_database.issue_db_command("DELETE FROM UninitializedRelay WHERE relayId = '%s';" % relay_id)
                else:
                    new_num = int(channel_id) - 1
                    current_greenhouse_database.issue_db_command("UPDATE UninitializedRelay SET numberOfChannels = \"%s\" WHERE relayId = \"%s\" AND piIp = \"%s\" AND portNumber = \"%s\" AND greenhouseId = \"%s\";"\
                        % (new_num, relay_id, piIp, port, greenhouse_id))
                relay_exists = current_greenhouse_database.issue_db_command("SELECT * FROM RelayOut WHERE relayId = '%s';" % relay_id)
                if len(relay_exists) == 0:
                    database_result = current_greenhouse_database.issue_db_command("INSERT INTO RelayOut"\
                        + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                        % (relay_id, piIp, port, "1", greenhouse_id))
                else:
                    get_channels = current_greenhouse_database.issue_db_command("SELECT numberOfChannels FROM RelayOut WHERE relayId = '%s';" % relay_id)
                    print_logger.debug(get_channels)
                    num_channels = int(get_channels[0])
                    current_greenhouse_database.issue_db_command("UPDATE RelayOut SET numberOfChannels = \"%s\" WHERE relayId = \"%s\" AND piIp = \"%s\" AND portNumber = \"%s\" AND greenhouseId = \"%s\";"\
                        % (str(num_channels+1), relay_id, piIp, port, greenhouse_id))
            else:
                return
            
            database_result = current_greenhouse_database.issue_db_command("INSERT INTO VentilationOut"\
                + " VALUES(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");"\
                % (vent_id, relay_id, channel_id, greenhouse_id, "off"))
                
            return_message = "MakeWarning:A new fan has been added to relay %s on channel %s." % (relay_id, channel_id)
            self.write_message(return_message)
        
        
        elif "SendGreenhouseInfo" in message:
            message = message.split(":");
            greenhouse_id = message[1] 
            
            id_list = []
            database_result = current_greenhouse_database.issue_db_command("SELECT locationId FROM Location WHERE greenhouseId = '%s';" % greenhouse_id)
            
            response = ''
            first = True;
            if database_result != False:
                for s in database_result:
                    if first is True:
                        response = response + str(s[0])
                        first = False
                    else:
                        response = response + ":" + str(s[0])
                        
            self.write_message("Details:" + str(greenhouse_id) + ":" + str(response));
        else:
            pass

# ---------------------------------------------------------------------------- #
# Master Handler List                                                          #
# ---------------------------------------------------------------------------- #


settings = {}
handlers = [
    (r'/', LoginHandler),
    (r'/ws_login(.*)', LoginWsHandler),
    (r'/404', ErrorHandler),
    (r'/ws_404(.*)', ErrorWsHandler),
    (r'/create_account', CreateAccountHandler),
    (r'/ws_create_account', CreateAccountWsHandler),
    (r'/credential_recovery', CredentialRecoveryHandler),
    (r'/ws_credential_recovery', CredentialRecoveryWsHandler),
    (r'/static/(.*)', ProgramFileHandler, {'path' : './static'}),
    (r'/favicon.ico', FaviconFileHandler, {'path' : './'}),
    (r'/overview_screen', OverviewScreenHandler),
    (r'/ws_overview_screen', OverviewScreenWsHandler),
    (r'/delete_greenhouse', DeleteGreenhouseHandler),
    (r'/ws_delete_greenhouse', DeleteGreenhouseWsHandler),
    (r'/edit_greenhouse', EditGreenhouseHandler),
    (r'/ws_edit_greenhouse', EditGreenhouseWsHandler),
    (r'/create_greenhouse', CreateGreenhouseHandler),
    (r'/ws_create_greenhouse', CreateGreenhouseWsHandler),
    (r'/add_component', AddComponentHandler),
    (r'/ws_add_component', AddComponentWsHandler)
    ]
    
def initialize_controllers():
    child=pexpect.spawn('ssh pi@192.168.1.101')
    child.expect('password:')
    child.sendline('raspberry')
    child.expect('$')
    child.sendline('sudo reboot')
    child.expect('$')
    child.close()
    
    child=pexpect.spawn('ssh pi@192.168.1.108')
    child.expect('password:')
    child.sendline('raspberry')
    child.expect('$')
    child.sendline('sudo reboot')
    child.expect('$')
    child.close()
# ---------------------------------------------------------------------------- #
# Initialization Commands                                                      #
# ---------------------------------------------------------------------------- #

app = tornado.web.Application(handlers, **settings)

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)

    # Set the logger verbosity
    if options.logger == "qq":
        print_logger.setLevel(logging.CRITICAL)
    elif options.logger == "q":
        print_logger.setLevel(logging.ERROR)
    elif options.logger == "":
        print_logger.setLevel(logging.WARNING)
    elif options.logger == "v":
        print_logger.setLevel(logging.INFO)
    elif options.logger == "vv":
        print_logger.setLevel(logging.DEBUG)
    else:
        print_logger.setLevel(logging.WARNING)
    
    # Initialize the database object
    current_greenhouse_database = greenhouse_database()

    # Connect to the database
    current_greenhouse_database.connect()

    # REMOVE THIS LATER
    current_greenhouse_database.clean_tables()

    # Make sure all of the tables are where they should be.
    current_greenhouse_database.check_tables()
    
    current_greenhouse_database.construct_dummy_database()
    """
    #ask relays nicely to reset themselves
    initialize_controllers()
    print "=============================="
    print "waiting for pi's to restart..."
    print "=============================="
    time.sleep(60)
    """
    #start I/O threads, DO THESE NEARLY LAST (just before IOLoop start)
    helper_functions.safe_start_thread(input_gateway.main, (), True)
    print "====input gateway started===="
    helper_functions.safe_start_thread(output_gateway.main, (), True)
    print "====output gateway started===="
    
    tornado.ioloop.IOLoop.instance().start()
