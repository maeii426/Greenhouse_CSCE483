#!usr/bin/env python
# For command line arguments on linux devices

#DO NOT USE THIS OUTSIDE OF output_helper.py!!!!!! -Aaron

import sys
import socket
	
def setup(port, relayid):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('',11000))
	
	s.settimeout(120)
	try:
		s.listen(1)
		c, addr = s.accept()
		s.settimeout(None)
		c.settimeout(None)
		c.sendall('Hello')
		
		waiting = True
		while waiting:
			message = c.recv(32)
			if message:
				waiting = False
				
		info = str(port) + ":" + str(relayid)
		c.sendall(info)
		
		response = True
		message = ''
		while response:
			message = c.recv(16)
			if message:
				response = False
		
		c.close
		s.close
		return message
	except socket.timeout:
		return 'timeout'
