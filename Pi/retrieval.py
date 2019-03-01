import socket
import sys
import serial
import serial.tools.list_ports
import time
import ConfigParser

CONFIG_PATH = "/home/pi/GreenhouseConfiguration.txt"
ARDUINO_SERIAL_PATH = "/dev/ttyUSB0"
BAUD_RATE = 9600
GREENHOUSE_ID = 1
GREENHOUSE_IP = "127.0.0.1"
GREENHOUSE_PORT = 0

def send_data(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (GREENHOUSE_IP, GREENHOUSE_PORT)
    sock.connect(server_address)
    sock.sendall(data)
    sock.close()

def main():
    try:
	global GREENHOUSE_ID
	global GREENHOUSE_IP
	global GREENHOUSE_PORT
	global CONFIG_PATH
	global ARDUINO_SERIAL_PATH
	config = ConfigParser.ConfigParser()
	config.readfp(open(CONFIG_PATH))
	GREENHOUSE_ID = config.get('Properties', 'GREENHOUSE_ID')
	GREENHOUSE_IP = config.get('Properties', 'GREENHOUSE_IP')
	GREENHOUSE_PORT = config.get('Properties', 'GREENHOUSE_PORT')
	ports = serial.tools.list_ports.comports()
	for p in ports:
		if "Linux Foundation" in p[1]:
			ARDUINO_SERIAL_PATH = p[0]
			
    arduino = serial.Serial(ARDUINO_SERIAL_PATH, BAUD_RATE, timeout=.1)

    while True:
        data = arduino.readline().strip()
        if data:
			new_string = ""
			data = data.split(':')
			if (data[0] == "GLOBAL"):
				data[1] = GREENHOUSE_ID

			for d in data[:-1]:
				new_string += d
				new_string += ":"
			new_string += data[len(data)-1]
			print new_string		
	        send_data(new_string)
	        
    except Exception as e:
        print str(e)

if __name__ == "__main__":
    main()
