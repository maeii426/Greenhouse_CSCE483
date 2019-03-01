#!/usr/bin/env python

# ---------------------------------------------------------------------------- #
# Developers: Aaron Ayrault                                                    #
# Project: CSCE-483 Smart Greenhouse                                           #
#                                                                              #
# File: ./database_inserter.py                                                 #
# Description: defines greenhouse parameters in the DB                         #
# ---------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------- #
#  Includes                                                                    #
# ---------------------------------------------------------------------------- #
import sys

sys.path.append("./static/python")
import helper_functions
from helper_functions import execute_SQL_oneoff

#-------------------
# Functions
#-------------------

def mahapatras_greenhouse():
    helper_functions.scream("now initializing mahapatra's greenhouse")
    
    #username, firstname, lastname, email, password
    execute_SQL_oneoff("INSERT INTO Users VALUES('mahapatra', 'Rabi', 'Mahapatra', 'default', 'password')")
    
    #greenhouseId, username, housenumber, street, city, zip, state
    execute_SQL_oneoff("INSERT INTO Greenhouses VALUES('3', 'mahapatra', '3504', 'Graz Dr.', 'College Station', '77840', 'TX')")
    
    execute_SQL_oneoff("INSERT INTO GreenhouseStatus VALUES('3', 'true')")
    
    #type, locationId, greenhouseId
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '301', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '302', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '303', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '304', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '305', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '306', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '307', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '308', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '309', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '310', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '311', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '312', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('pot', '313', '3')")
    execute_SQL_oneoff("INSERT INTO Location VALUES('hydroponic', '314', '3')")
    
    #relayId, piIp, portNumber, numberOfChannels, greenhouseId
    #realy 31 is the solenoid controller
    #relay 32 is the lights controller and ventilation
    execute_SQL_oneoff("INSERT INTO RelayOut VALUES('31', '192.168.0.101', '11001', '8', '3')")
    execute_SQL_oneoff("INSERT INTO RelayOut VALUES('32', '192.168.0.108', '11002', '8', '3')")
    
    #actuatorId, solenoidType, relayId, channelId, greenhouseId, state
    #solenoids 10-15 are for soil pots
    #solenoid 16 is for the hydroponic tower
    #solenoid 17 is the main one
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('10', 'maindrip',   '31', '1', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('11', 'drip',       '31', '2', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('12', 'drip',       '31', '3', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('13', 'drip',       '31', '4', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('14', 'drip',       '31', '5', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('15', 'drip',       '31', '6', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('16', 'drip',       '31', '7', '3', 'off', '0')")
    execute_SQL_oneoff("INSERT INTO SolenoidOut VALUES('17', 'hydroponic', '31', '8', '3', 'off', '0')")
    
    #locationId, actuatorId, greenhouseId
    #mapping for the solenoids
    #most solenoids support 2 pots (except solenoid 15 which does 3)
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('301', '16', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('302', '16', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('303', '11', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('304', '11', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('305', '12', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('306', '12', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('307', '13', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('308', '15', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('309', '14', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('310', '14', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('311', '15', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('312', '15', '3')")
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('313', '16', '3')")
    
    #hydroponic tower location
    execute_SQL_oneoff("INSERT INTO LocationMapping VALUES('314', '17', '3')")
    
    #actuatorId, relayId, channelId, greenhouseId, state
    execute_SQL_oneoff("INSERT INTO VentilationOut VALUES('18', '32', '1', '3', 'off')")
    execute_SQL_oneoff("INSERT INTO VentilationOut VALUES('19', '32', '2', '3', 'off')")
    execute_SQL_oneoff("INSERT INTO VentilationOut VALUES('20', '32', '3', '3', 'off')")
    execute_SQL_oneoff("INSERT INTO VentilationOut VALUES('21', '32', '4', '3', 'off')")
    
    #actuatorId, relayId, channelId, greenhouseId, state
    execute_SQL_oneoff("INSERT INTO LightOut VALUES('22', '32', '5', '3', 'off')")
    execute_SQL_oneoff("INSERT INTO LightOut VALUES('23', '32', '6', '3', 'off')")
    execute_SQL_oneoff("INSERT INTO LightOut VALUES('24', '32', '7', '3', 'off')")
    
    #greenhouseId, actuatorType, actuatorId
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'FAN', '18')")
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'FAN', '19')")
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'FAN', '20')")
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'FAN', '21')")
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'LIGHT', '22')")
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'LIGHT', '23')")
    execute_SQL_oneoff("INSERT INTO GlobalMapping VALUES('3', 'LIGHT', '24')")
    
    #sensorId, greenhouseId
    execute_SQL_oneoff("INSERT INTO AirTempSensors  VALUES('31', '3')")
    execute_SQL_oneoff("INSERT INTO HumiditySensors VALUES('31', '3')")
    execute_SQL_oneoff("INSERT INTO LightSensors    VALUES('31', '3')")
    
    #sensorId, locationId, greenhouseId
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('34', '301', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('35', '302', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('36', '303', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('37', '304', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('38', '305', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('39', '306', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('40', '307', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('41', '308', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('42', '309', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('43', '310', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('44', '311', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('45', '312', '3')")
    execute_SQL_oneoff("INSERT INTO SoilSensors VALUES('46', '313', '3')")
    
    #sensorId, locationId, greenhouseId
    execute_SQL_oneoff("INSERT INTO pHSensors         VALUES('47', '314', '3')")
    
    #sensorId, locationId, greenhouseId
    execute_SQL_oneoff("INSERT INTO WaterLevelSensors VALUES('47', '314', '3')")
    
    #sensorId, locationId, greenhouseId
    execute_SQL_oneoff("INSERT INTO WaterTempSensors  VALUES('47', '314', '3')")
    
    #--------------
    
    #sensorId, reading, unix_timestamp, greenhouseId
    #execute_SQL_oneoff("INSERT INTO LightData VALUES('31', '50', '1234567', '3')")
