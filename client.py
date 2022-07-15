import threading
import time
import random
import socket
import sys
import csv

# *** THIS CLIENT CODE REPRESENTS THE DNS ***

# client first connects to the root sever
def rs_client(rs_hostname, rsListenPort):
	try:
	  	# TCP/IP socket
		rs_cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print("[C]: DNS client socket created")
	except socket.error as err:
	  	print('socket open error: {} \n'.format(err))

	# get the host of the rs one
	rs_host_addr = socket.gethostbyname(rs_hostname)
	
	print("[C]: DNS Server IP address is {}".format(rs_host_addr))

	# connect to the server on local machine
	rs_server_binding = (rs_host_addr, rsListenPort)
	rs_cs.connect(rs_server_binding)
	
	# get the host names
	domain_list = open("classified_dns.csv")
	csvreader = csv.reader(domain_list)
	heads = next(csvreader)

	
	# send the host to the server
	for domain in csvreader:
		print("[C]: Data sent to server: ", domain[0].lower())
		rs_cs.sendall(domain[0].lower().encode('utf-8'))
		time.sleep(2)

		# Receive data from server, hit or miss
		data_from_server = rs_cs.recv(1024).decode('utf-8').strip()
		print("[C]: Data received from server: ", data_from_server)
		time.sleep(2)
	

		
	# close the client socket and file pointers
	rs_cs.close()
	domain_list.close()
	#out_file.close()

# will only run if script run from command line, not if imported
if __name__ == "__main__":

	# should haave three args rsport = 1, tsport = 2
	rs_hostname = sys.argv[1]
	rs_port = int(sys.argv[2])

	rs_client(rs_hostname, rs_port)

	

