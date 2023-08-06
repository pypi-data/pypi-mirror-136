"""Module on extraction of network parameters"""
import numpy as np

from . import network as nw



def Tx_line_Z0_gamma_from_RLCG(R,L,C,G,omega):
	"""Computes the characteristic impedance and propagation constant gamma = alpha + j beta
	Input:-
	R := Series resistance per unit length
	G := Shunt resistance per unit length
	L := Series inductance per unit length
	C := Shunt capacitance per unit length
	omega := Frequency in radians per second 
	-----------------------------------------
	Output:-
	Z0 := Characteristic impedance
	gamma := Propagation constant
	"""
	Z0 = np.sqrt((R+1j*omega*L )/(G+1j*omega*C)) 
	gamma = np.sqrt((R+1j*omega*L )*(G+1j*omega*C))
	return Z0, gamma

def Tx_line_RLCG_from_Z0_gamma(Z0,gamma,C,G,omega):
	"""Computes the interconnect parameterf from characteristic impedance and propagation constant gamma = alpha + j beta
	Output:-
	R := Series resistance per unit length
	G := Shunt resistance per unit length
	L := Series inductance per unit length
	C := Shunt capacitance per unit length
	
	-----------------------------------------
	Input:-
	Z0 := Characteristic impedance
	gamma := Propagation constant
	omega := Frequency in radians per second 
	"""
	
	R_by_l = np.real(Z0*gamma)
	L_by_l = np.imag(Z0*gamma)/omega
	 
	G_by_l = np.real(gamma/Z0)
	C_by_l = np.imag(gamma/Z0)/omega
	
	Tx_parameters = {'R_by_l':R_by_l, 'L_by_l':L_by_l,'G_by_l':G_by_l,'C_by_l':C_by_l }
	
	return Tx_parameters


def Tx_line_from_NW(NW,l,omega=None):
	"""This function takes the following input paramters,
	NW := Object of Class Network
	l := length of the transmission line, in units of meter. Should be a scalar.
	Computes and returns the following,
	Z0 := Characteristics impedance of the transmission line. 
	gamma := propagation constant of the transmission line.
	
	If, frequency omega is also defined, then it also computes the following tuple. 
	R_by_l := Resistance per unit length
	L_by_l := Inductance per unit length
	C_by_l := Capacitance per unit length
	G_by_l := Conductance per unit length
	
	
	Returns a dictionary with above mentioned variable as keywords. 
	
	--------------------------------------------------------------------
	
	
	
	o--------------------------------------o
			Z0, \gamma = \alpha + j\beta
	o--------------------------------------o
	|<-------------- l ------------------->|
	
	Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
	"""
	Z0 = np.sqrt(NW.B/NW.C)
	gamma = (1/l)*np.arccosh(NW.A)
	
	#if not np.all(np.isnan(NW.omega)):
	if NW.omega is None:
		"""Frequency is defined in NW. This supersedes omega given in the function call"""
		omega = NW.omega
		
	#if not np.all(np.isnan(omega)):
	if omega is not None:
		"""The following will be executed if the frequency is defined in either NW or during the function call."""
		R_by_l = np.real(Z0*gamma)
		L_by_l = np.imag(Z0*gamma)/omega
		 
		G_by_l = np.real(gamma/Z0)
		C_by_l = np.imag(gamma/Z0)/omega
		
		Tx_parameters = {'Z0':Z0, 'gamma':gamma, 'R_by_l':R_by_l, 'L_by_l':L_by_l,'G_by_l':G_by_l,'C_by_l':C_by_l }
		
	else: 
		Tx_parameters = {'Z0':Z0, 'gamma':gamma,'R_by_l':None, 'L_by_l':None,'G_by_l':None,'C_by_l':None }
		
	
	return Tx_parameters




def T_model_from_NW(NW):
	"""Returns Z1, Z2, and Z3, computed from the [ABCD] parameters of
	the NW (object of Network Class). 
				____			____
	o----------|_Z1_|----------|_Z2_|-------o
						_|__         
					   |_Z3_|       
						 |  
	o--------------------------------------o"""
	
	Z3 = 1/NW.C
	Z1 = (NW.A-1)/NW.C
	Z2 = (NW.D-1)/NW.C
	return Z1, Z2, Z3

def PI_model_from_NW(NW):
	"""Returns Y1, Y2, and Y3, computed from the [ABCD] parameters of
	the NW (object of Network Class). 
					  ____
	o----------------|_Y3_|---------------------o
			   _|__         _|__
			  |_Y1_|       |_Y2_|
				|  			 |
	o-------------------------------------------o"""
	
	Y3 = 1/NW.B
	Y2 = (NW.A-1)/NW.B
	Y1 = (NW.D-1)/NW.C
	return Y1, Y2, Y3
