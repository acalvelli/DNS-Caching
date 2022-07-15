import random
import string
import tldextract
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


# stop: 200,50,50,30
# start: 0
# col: 1,2,3,4 (csv column reading from)
def plot_thresholds(start, stop, col):

    # read the csv, plot, each iteration plot the percentage

    d = 1
    indices = np.arange(start, stop + d, d).tolist() # tracks the current thresholds

    one_time = [] # keeps track of the number of urls under threshold
    re_used = []
    
    
    res = pd.read_csv("domains.csv")
   
    
    for i in range(len(indices)):
        curr_threshold = indices[i]
        one_time.append(0)
        re_used.append(0)
        once = 0
        mult = 0
        
        # count how many are below the threshold
        # loop over evvery row in the csv minus the header
        for j in range(len(res) - 1):
            # this gets the jth col (url) and the colth column (this changes)
            #print(res.iloc[j,col])
            # gets total number of one time or multiple used
            if(res.iloc[j,6] == 1):
                once += 1
            else:
                mult += 1
                
            # graphs represent the number of once and multi use domains BENEATH threshold
            if(res.iloc[j,col] < curr_threshold):
                if(res.iloc[j,6] == 0):
                    re_used[i] += 1
                else:
                    one_time[i] += 1
        

        # average to get percentage
        one_time[i] /= once
        re_used[i] /= mult

        
        
    x_axis = indices

    plt.ylabel("CDF")
    plt.plot(x_axis, one_time, label="one-time")
    plt.plot(x_axis, re_used, label="re-used")
    plt.legend()
    plt.show()
    


# generate a random dns query
def generate_domain(n):
	
	# write suspected one-time dns to this file
	one_timers = open("random_domains.txt", "w+")
	
	suf = ['.com','.net','.org','.txt','.co','.us','.edu','.ru']
	
	# how many queries to generate
	for x in range(0,n):
		# randomly generate a choice
		suffix = random.choice(suf)
		
		# up to 63 characters
		length = random.randrange(0,100)
		# random domain name of alphanumeric, ., - characters
		domain = (''.join(random.choice(string.ascii_lowercase + string.digits +"." + "-") for i in range(length)))
		domain += suffix
		
		one_timers.write(domain +"\n")


	one_timers.close()
	
	
# compute the shannon entropy score
def shannon_entropy(string):
	
	stList = list(string)
	alphabet = list(set(stList)) # list of symbols in string
	freqList = []
	for symbol in alphabet:
		ctr = 0
		for sym in stList:
			if sym == symbol:
				ctr += 1
		freqList.append(float(ctr) / len(stList))
	#print("Freq alphabet:" , freqList)
	
	# calculate shannon
	ent = 0.0
	for freq in freqList:
		ent = ent + (freq * math.log(freq,2))
	ent = -ent
	#print("shannon entropy:" , ent)
	return ent

	
# create a csv of all the pulled urls
def generate_csv():
	# open up the csv with the urls and the classification
	domains = open("classified_dns.csv")
	csvreader = csv.reader(domains)
	heads = next(csvreader)
	
	# header for csv exporting
	header = ['url','domain length','longest subdomain','format fields','unusual length', 'entropy', 'one time']
	info = []
	
	for d in csvreader:
		data = []
		
		# extract the fields
		sub = tldextract.extract(d[0])
		subdomain = sub.subdomain
		domain = sub.domain
		full_query = d[0]
		
		# get all the fields
		domain_length = len(domain.encode("utf-8"))
		sub_length = len (subdomain.encode("utf-8"))
		format_fields = full_query.count('-') + full_query.count('.') # do you need to subtract one?
		unusual_len_fields = 0
		
		#  split the string by . or -
		fields = re.split('\.|-', full_query)
		for f in fields: 
			length_field = len(f.encode("utf-8"))
			if(length_field >= 10 or length_field <= 3):
				unusual_len_fields += 1
		
		# push to array to write to file
		# ALSO NEED IP?
		data.append(full_query.strip())
		data.append(domain_length)
		data.append(sub_length)
		data.append(format_fields)
		data.append(unusual_len_fields)
		entropy=shannon_entropy(d[0])
		data.append(entropy)
		data.append(d[1])
		
		# add to overall list
		info.append(data)
		
	# to this file, write all of the information for the queried domain names
	with open('domains.csv', 'w', encoding='UTF8', newline='') as f:
		writer = csv.writer(f)
		# write the header
		writer.writerow(header)

		# write multiple rows
		writer.writerows(info)

	f.close()
	domains.close()
	
# read the two csv and compare the cache rates, for same thresholds as the paper
def determine_cache():
# read the csv, plot, each iteration plot the percentage


	one_time_omit = 0
	one_time_kept = 0
	mult_omit = 0
	mult_kept = 0


	server_res = pd.read_csv("server_results2.csv")
	actual_res = pd.read_csv("classified_dns.csv")
   
            
	# count how many are below the threshold
	# loop over evvery row in the csv minus the header
	for j in range(len(server_res) - 1):
		# this gets the jth col (url) and the colth column (this changes)
		# gets total number of one time or multiple used
		
		# if server thinks one time
		if(server_res.iloc[j,1] == 1):
			if(actual_res.iloc[j,1] == 1):
				one_time_omit += 1
			else:
				mult_omit += 1
		# server thinks multiple 
		else:
			if(actual_res.iloc[j,1] == 1):
				one_time_kept += 1
			else:
				mult_kept += 1
			


	# percentage of one timers correctly omitted from cache
	one_time_omit /= 1000
	one_time_kept /= 1000
	mult_omit /= 1000
	mult_kept /= 1000

        
        
	print("otk: ", one_time_kept)
	print("oto:" , one_time_omit)
	print("mo:" , mult_omit)
	print("mk: ", mult_kept)

	
# will only run if script run from command line, not if imported
if __name__ == "__main__":

	#generate_domain(500) # only do this the first time
	#generate_csv()
	#plot_thresholds(0, 200, 1)
	determine_cache()
