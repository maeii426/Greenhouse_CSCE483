#!usr/bin/env python
# For command line arguments on linux devices

#DO NOT USE THIS OUTSIDE OF output_helper.py!!!!!! -Aaron
#LISTEN TO AARON!!!!! -Jason
#YOU ONLY BIND IT ONCE!!!!! -Andrew
#I DID NOT KNOW THAT!!!!!! -Margaret

import sys
import socket
import copy

s = {'11001' : None, '11002' : None}

def state_set(port, relay, state):
	if port not in s.keys():
		A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		A.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		A.bind(('',int(port)))
		
		s.update({str(port) : A})
	
	if port in s.keys() and s[str(port)] is None:
		A = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		A.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		A.bind(('',int(port)))
		
		s[str(port)] = A
	
	s[str(port)].settimeout(15)
	try:
		s[str(port)].listen(1)
		c, addr = s[str(port)].accept()
		s[str(port)].settimeout(None)
		c.settimeout(None)
		c.sendall('Hello')
		
		waiting = True
		while waiting:
			message = c.recv(16)
			if message:
				print message
				waiting = False
				
		if state == True:
			relay_change = relay + ' 1'
		else:
			relay_change = relay + ' 0'
		c.sendall(relay_change)
		
		response = True
		message = ''
		while response:
			message = c.recv(64)
			if message:
				response = False
		
		c.sendall("quit")
		
		c.close
		return message
	except socket.timeout:
		return 'timeout'