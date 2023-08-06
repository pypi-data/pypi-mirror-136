"""Module on data handling"""

import numpy as np
from os.path import dirname, realpath
import sys
import csv as csv

from . import network as nw


##### code to get filename. 
path1=dirname(realpath(sys.argv[0])) ## get path of the current directory.
	
def load_HFSS_CSV(filename, parameter = 's',Z0=50):
	'''Function to load data in the csv file with filename. Currently loading of only S parameters is loaded.'''
	##### code to get filename. 
	path=dirname(realpath(sys.argv[0])) ## get path of the current directory.
	
	fullname = path+'/'+filename

	
	with open(fullname, newline='') as csvfile: # Read Real S. 
		reader = csv.DictReader(csvfile)
		#for row in reader:
			#print(row)
			#print('=========')
		#print(reader.fieldnames)
		
		freq = []
		S11_re = []
		S12_re = []
		S21_re = []
		S22_re = []
		S11_im = []
		S12_im = []
		S21_im = []
		S22_im = []
		
		for row in reader:
			#freq.append(row['Freq [GHz]'])
			freq.append(float(row['Freq [GHz]']))
			S11_re.append(float(row['re(S(1,1)) []']))
			S12_re.append(float(row['re(S(1,2)) []']))
			S21_re.append(float(row['re(S(2,1)) []']))
			S22_re.append(float(row['re(S(2,2)) []']))

			S11_im.append(float(row['im(S(1,1)) []']))
			S12_im.append(float(row['im(S(1,2)) []']))
			S21_im.append(float(row['im(S(2,1)) []']))
			S22_im.append(float(row['im(S(2,2)) []']))
		


	S11 = np.array(S11_re) + 1j*np.array(S11_im)
	S12 = np.array(S12_re) + 1j*np.array(S12_im)
	S21 = np.array(S21_re) + 1j*np.array(S21_im)
	S22 = np.array(S22_re) + 1j*np.array(S22_im)

	freq = np.array(freq)*1e9
	
	print('Loaded '+filename)
	
	return nw.Network(S11,S12,S21,S22,parameter=parameter,Z0=Z0,omega=2*np.pi*freq)
	
