import threading
import time
import random
import socket
import sys
import tldextract
import string
import re
import struct
import datetime
import csv


MAX_CACHE_SIZE = 100
	

# finds the oldest element in the cache by timestamp and removes it
def remove_oldest(cache):

	max_time = datetime.datetime.min
	remove = ''
	
	for key, value in cache.items():
		if(value[1] > max_time):
			remove = key
	
	# remove the oldest element
	cache.pop(remove, None)

	return cache


def rs_server(rsListenPort, max_d_len, max_sd_len, max_ff, max_uf_len):
	# this is the root server
	try: 
	  rs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket.SOCK_DGRAM for udp
	  print("[S]: DNS Server socket created")
	except socket.error as err:
	  print('DNS socket open error: {}\n'.format(err))
	  exit()

	# set the fields for client connection
	rs_host = socket.gethostname()
	print("[S]: DNS Server host name is {}".format(rs_host))
	rs_host_ip = (socket.gethostbyname(rs_host))
	print("[S]: DNS Server IP address is {}".format(rs_host_ip))
	
	
	rs_server_binding = (rs_host_ip, rsListenPort)
	rs_socket.bind(rs_server_binding)
	rs_socket.listen(1)
	

	# cache is a dictionary of {domain name, ip address}
	cache = {}
	findings = []
		
	# globals used for changing numbers and graphing
	global MAX_CACHE_SIZE
	

	# wait for client connection
	while True:
		cli_conn, cli_addr = rs_socket.accept()
		print ("[S]: Got a connection request from a client at {}".format(cli_addr))

		# receive data from client
		try:
			while True:
			
				prediction = []
				
				# host name
				data_from_client = cli_conn.recv(1024)
				
				# no more data	
				if not data_from_client:
					print("[RS]: Received all data.")
					break
					
				# parse the data: comes in form google.com, etc. 
				url_from_client = data_from_client.decode("utf-8").strip()

				# break url into parts
				sub = tldextract.extract(url_from_client)
				domain = sub.domain
				subdomain = sub.subdomain
				full_query = url_from_client
				
				# add url to the csv
				prediction.append(full_query.strip())
				
				# 1): Check length of domain name in bytes < 100 bytes
				domain_length = len(domain.encode("utf-8"))
				#print(domain, " : ", domain_length)
				
				
				if(domain_length > max_d_len):
					print(domain, " exceeds ", max_d_len, " bytes") # do not add to cache
					prediction.append(1)

				else:
				# 2) check length of the longest subdomain < 30 bytes
					subdomain_length = len(subdomain.encode("utf-8"))

					if(subdomain_length > max_sd_len):
						print(subdomain, " exceeds ", max_sd_len, " bytes")
						prediction.append(1)
						
					# 3) check number of format fields (. or -) < 10
					else:
						# start at 2 because suffix + domain .'s
						format_fields = 0
						format_fields += full_query.count('-') + full_query.count('.')
						#print("number of format fields: ", format_fields)
						
						if(format_fields > max_ff):
							print(full_query, " exceeds ", max_ff, " fields")
							prediction.append(1)
							
						# 4) check fields w/  unusual lengths >= 10 or <= 3 is <= 5							
						else:
							unusual_len_fields = 0
							#  split the string by . or -
							fields = re.split('\.|-', full_query)
							for f in fields: 
								length_field = len(f.encode("utf-8"))
								if(length_field >= 10 or length_field <= 3):
									unusual_len_fields += 1
									
							#print("number unusual length fields: ", unusual_len_fields)
							if(unusual_len_fields > max_uf_len):
								print(unusual_len_fields, " unusual len fields exceeds ", max_uf_len)
								prediction.append(1)
							# passed all the critera and add to the cache
							else:
								
								# randomly generate an IP address
								ip = socket.inet_ntoa(struct.pack('>I', random.randint(1,0xffffffff)))
								ct = datetime.datetime.now()
								#print("add to cache at ", ct)
								
								# check cache size, if over then remove oldest element
								if(len(cache) + 1 >= MAX_CACHE_SIZE):
									print("removing oldest element...")
									cache = remove_oldest(cache)
								# should this be the domain or full query?
								cache[full_query] = (ip, ct)
								prediction.append(0)

					
				# looks up in dictionary, if find sends it back
				print("[S]: Done with ", url_from_client)
				# add the url and 0 or 1 to the overall list

				findings.append(prediction)

				message = url_from_client + " is finished" 
				cli_conn.sendall(message.encode("utf-8"))
	

				
		
		# Close the server socket
		finally:
			time.sleep(2)
			print("[S]: Closing server socket.")
			rs_socket.close()
			print("printing cache: ", cache)
			
			# write results to csv
			# to this file, write all of the information for the queried domain names
			with open('server_results2.csv', 'w', encoding='UTF8', newline='') as f:
				writer = csv.writer(f)

				h = ['url', 'once-used']
				writer.writerow(h)
				writer.writerows(findings)
				
			f.close()		
			exit()
		

# will only run if script run from command line, not if imported
if __name__ == "__main__":

	# this port should be the same as running in client
	rs_port = int(sys.argv[1])
	# these numbers defined by paper (100,30,10,5)
	rs_server(rs_port, 35, 5, 7, 5)
	
