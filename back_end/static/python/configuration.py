#!/usr/bin/env python
import socket
import sys
import MySQLdb
from os import rename
from datetime import datetime

sys.path.append("./static/python")
import helper_functions

NEXBOX_USER = "greenhouse"
NEXBOX_PASSWD = "password"
GREENHOUSE_PORT = 30002

DB_HOST="127.0.0.1"
DB_USER="root"
DB_PASSWD="password"
DB_PRIMARY_DATABASE="greenhouse"

def retrieve(greenhouse_id):
    try:
        sensor_id = helper_functions.execute_SQL_oneoff("SELECT MAX(sensorId * 1) FROM SoilSensors;")[0][0]
        sensor_id = str(int(sensor_id) + 1)
        node_id = str((int(sensor_id) % 254))
        node_family = str(int(sensor_id) // 255)
        
        location_id = str(int(helper_functions.execute_SQL_oneoff("SELECT MAX(locationId * 1) FROM SoilSensors;")[0][0]) + 1)
        
        helper_functions.execute_SQL_oneoff("INSERT INTO SoilSensors VALUES(%s, %s, %s);", (sensor_id, location_id, greenhouse_id))
        return (node_id, node_family)
        
    except Exception as e:
        print "Exception: %s" % str(e) 

def main():
    # Initialize & bind socket to port 30002
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', GREENHOUSE_PORT)
    sock.bind(server_address)
        
    # Listen for incoming message
    sock.listen(1)
    try:
        while True:
            print >> sys.stderr, 'waiting for a connection'
            connection, client_address = sock.accept()
            while True:
                client_data = connection.recv(64)
                if client_data:
                    client_data = client_data.strip("\r\n").split(":")
                    if client_data[0] == "ARDUINO":
                        info = retrieve(client_data[1])
                        print "arduino requested data:%s:%s" % info
                        message = "%s:%s" % info
                        connection.sendall(message)
                else:
                    break
    finally:
        connection.close()

if __name__ == "__main__":
    main()
