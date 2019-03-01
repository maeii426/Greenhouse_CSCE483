#!/usr/bin/env python
import io
import socket
import sys
import ConfigParser
from random import choice
from string import ascii_lowercase, digits

# File must be run inside of the ~/Test folder so that 'ino' is able to compile inside that destination folder.
CONFIG_PATH = "/home/pi/GreenhouseConfiguration.txt"
ARDUINO_FILE_LOC    = 'src/RF24Mesh_Test/RF24Mesh_Config.h'
NODEFAMILY          = 0    # Default nodeFamily in the instance where server is unable to be contacted
NODEID              = 1    # Default nodeID in the instance where server is unable to be contacted
SLEEP_INTERVAL      = 225  # Default sleep for 225*8 (30min) - 10 currently for testing
GREENHOUSE_IP	    = "127.0.0.1" # Greenhouse IP address
GREENHOUSE_PORT     = 0 # Greenhouse port

def modify():
	global NODEID
	global NODEFAMILY
	global SLEEP_INTERVAL
	CONFIG_VERSION = ''.join(choice(ascii_lowercase + digits) for i in range(3))
	
	with open(ARDUINO_FILE_LOC, 'r') as file:
		data = file.readlines()
		data[0] = '#define NODEFAMILY %s' % NODEFAMILY
		data[1] = '#define NODEID %s' % NODEID
		data[2] = '#define SLEEP_INTERVAL %s' % SLEEP_INTERVAL
		data[3] = '#define CONFIG_VERSION %s' % CONFIG_VERSION
		print data

def main():
	global NODEFAMILY
	global NODEID
	global SLEEP_INTERVAL
	global GREENHOUSE_IP
	global GREENHOUSE_PORT
	global CONFIG_PATH
	try:
		config = ConfigParser.ConfigParser()
		config.readfp(open(CONFIG_PATH))
		GREENHOUSE_IP = config.get('Properties', 'GREENHOUSE_IP')
		GREENHOUSE_PORT = config.get('Properties', 'GREENHOUSE_PORT')
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = (GREENHOUSE_IP, GREENHOUSE_PORT)
		sock.connect(server_address)
		message = "ARDUINO"
		sock.sendall(message)
		buf = sock.recv(64)
		buf = buf.split(':')
		if (len(buf) > 2):
			NODEFAMILY = buf[0]
			NODEID = buf[1]
			
		modify(server_address)
	finally:
		print >> sys.stderr, 'closing socket'
		sock.close()

if __name__ == "__main__":
	main()
