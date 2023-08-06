"""Module containing the basic Microwave netwrok object"""

import numpy as np

class Network:
	def __init__(self, p11, p12, p21, p22, parameter='abcd',Z0=50,omega=None):
		"""For conversion from ABCD <-> S, it is assumed that the network has equal and real characteristic impedance on both the ports."""
		#self.Z01 = Z01 # Terminating impedance at port-1 for conversion [ABCD] <-> [S]. 
		#self.Z02 = Z02 # Terminating impedance at port-2 for conversion [ABCD] <-> [S]. 
		self.Z0 = Z0
		self.omega = omega
		if self.omega is not None:
			self.freq = omega/(2*np.pi)
		else :
			self.freq = None
		
			
		if parameter == 's' or parameter == 'S':
			
			self.S11 = p11
			self.S12 = p12
			self.S21 = p21
			self.S22 = p22
			
			self.S_to_ABCD()
			#print('S defined')
		
		if parameter == 'abcd' or parameter == 'ABCD':
			
			self.A = p11
			self.B = p12
			self.C = p21
			self.D = p22
			
			
			self.ABCD_to_S()
			#print('ABCD defined')
		
	def ABCD_to_S(self,):
		self.S11 = (self.A + self.B/self.Z0 - self.C*self.Z0 - self.D)/(self.A + self.B/self.Z0 + self.C*self.Z0 + self.D)
		self.S12 = 2*(self.A*self.D - self.B*self.C)/(self.A + self.B/self.Z0 + self.C*self.Z0 + self.D)
		self.S21 = 2/(self.A + self.B/self.Z0 + self.C*self.Z0 + self.D)
		self.S22 = (-self.A + self.B/self.Z0 - self.C*self.Z0 + self.D)/(self.A + self.B/self.Z0 + self.C*self.Z0 + self.D)
		#print('computed ABCD to S')
		
	def S_to_ABCD(self,):
		self.A =        ((1+self.S11)*(1-self.S22) + self.S12*self.S21)/(2*self.S21)
		self.B =   self.Z0*  ((1+self.S11)*(1+self.S22) - self.S12*self.S21)/(2*self.S21)
		self.C = (1/self.Z0)*((1-self.S11)*(1-self.S22) - self.S12*self.S21)/(2*self.S21)
		self.D = 		((1-self.S11)*(1+self.S22) + self.S12*self.S21)/(2*self.S21)
		#print('computed S to ABCD')
		
	def input_admittance(self,YL):
		"""Returns the input admittance of a network at port-1, when Port-2 
		is terminated by YL
					 _______________
					|				|
		o-----------|---------------|-----------o
			 		|				|		   _|__
			 |-->	|	[ABCD]		|		  |_YL_|
			Yin		|				|			|
		o-----------|---------------|-----------o
					|_______________|
		YL should be of the same dimensions as A,B,C,D. Or YL can be a scalar.
		"""
		Yin = (self.C+self.D*YL)/(self.A+self.B*YL)
		return Yin
	
	def input_impedance(self,ZL):
		
		"""Returns the input impedance  of a network at port-1, when Port-2 
		is terminated by ZL
					 _______________
					|				|
		o-----------|---------------|-----------o
			 		|				|		   _|__
			 |-->	|	[ABCD]		|		  |_ZL_|
			Zin		|				|			|
		o-----------|---------------|-----------o
					|_______________|
		ZL should be of the same dimensions as A,B,C,D. Or ZL can be scalar. 
		"""
		Zin = (self.A*ZL + self.B)/(self.C*ZL + self.D)
		return Zin
		
	def input_reflection(self,ZL,Z0=50):
		"""Returns the reflection coefficient of a network at port-1, when Port-2 
		is terminated by ZL. The characteristic impedance of the input line Z0. By defalut Z0 is assumed to be 50 Ohm. 
					 _______________
					|				|
		o-----------|---------------|-----------o
			 		|				|		   _|__
		Z0	 |-->	|	[ABCD]		|		  |_ZL_|
			S11		|				|			|
		o-----------|---------------|-----------o
					|_______________|
		ZL should be of the same dimensions as A,B,C,D. Or ZL can be scalar. 
		"""
		Zin = (self.A*ZL + self.B)/(self.C*ZL + self.D)
		
		S11 = (Zin-Z0)/(Zin+Z0)
		
		return S11
		
		
	def __mul__(self, other):
		
		A1 = self.A
		A2 = other.A
		B1 = self.B
		B2 = other.B
		C1 = self.C
		C2 = other.C
		D1 = self.D
		D2 = other.D
		
		
		A = A1*A2 + B1*C2
		B = A1*B2 + B1*D2
		C = C1*A2 + D1*C2
		D = C1*B2 + D1*D2
		return Network(A,B,C,D,parameter='abcd',omega=self.omega)
       
        
	def __pow__(self,N):
		
		NW_cascade = self
		for itr in range(N-1):
			NW_cascade = NW_cascade*self
		return NW_cascade
		
	def __rshift__(self,other):
		"""De-embedding from left.
		NW1>>NW2. 'other' is NW2.
		Returns a network with [ABCD1]^-1 * [ABCD2]"""
		A1 = self.A
		A2 = other.A
		
		B1 = self.B
		B2 = other.B
		
		C1 = self.C
		C2 = other.C
		
		D1 = self.D
		D2 = other.D
		
		Delta_1 = A1*D1 - B1*C1
		
		A = ( D1*A2 - B1*C2)/Delta_1
		B = ( D1*B2 - B1*D2)/Delta_1
		C = (-C1*A2 + A1*C2)/Delta_1
		D = (-C1*B2 + A1*D2)/Delta_1
				
		return Network(A,B,C,D,parameter='abcd',omega=self.omega)
	
	def __lshift__(self,other):
		"""De-embedding from right.
		NW1<<NW2. 'other' is NW2.
		Returns a network with [ABCD1] * [ABCD2]^-1"""
		A1 = self.A
		A2 = other.A
		
		B1 = self.B
		B2 = other.B
		
		C1 = self.C
		C2 = other.C
		
		D1 = self.D
		D2 = other.D
		
		Delta_2 = A2*D2 - B2*C2
		
		A = ( A1*D2 - B1*C2)/Delta_2
		B = (-A1*B2 + B1*A2)/Delta_2
		C = ( C1*D2 - D1*C2)/Delta_2
		D = (-C1*B2 + D1*A2)/Delta_2
		
				
		return Network(A,B,C,D,parameter='abcd',omega=self.omega)
	# End class Network:
	
	

def from_Tx_line(l,Z0,gamma,omega=None):
	"""This function takes the following input paramters,
	l = length of the transmission line. Should be a scalar.
	Z0 = Characteristics impedance of the transmission line. Should be a scalar or an array of the same dimensions as beta.
	gamma = propagation constant of the transmission line. Should be the an array of the same dimensions as omega.
	--------------------------------------------------------------------
	The function returns the ABCD parameters of a transmission line section of length l.
	
	
	o--------------------------------------o
			Z0, \gamma = \alpha + j\beta
	o--------------------------------------o
	|<-------------- l ------------------->|
	
	Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
	"""
	
	A = np.cosh(gamma*l)
	B = Z0*np.sinh(gamma*l)
	C = (1/Z0)*np.sinh(gamma*l) 
	D = np.cosh(gamma*l)
	return Network(A, B, C, D,parameter='abcd',omega=omega)


def from_series_Z(Z,omega=None):
	""" Returns a network object for the following
	o-----------------|Z|--------------------o
					[ABCD]
	o----------------------------------------o
	Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
	"""
	A = np.ones_like(Z)
	B = Z
	C = np.zeros_like(Z)
	D = np.ones_like(Z)
	return Network(A, B, C, D,parameter='abcd',omega=omega)
	

def from_shunt_Y(Y,omega=None):
	""" Returns a network object for the following
	o--------------------------------------o
					   _|_
					  |_Y_|
						|
	o--------------------------------------o
	Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
	"""
	A = np.ones_like(Y)
	B = np.zeros_like(Y)
	C = Y
	D = np.ones_like(Y)
	return Network(A, B, C, D,parameter='abcd',omega=omega)


def from_PI_Y(Y1,Y2,Y3,omega=None):
	""" Returns a network object for the following
					  ____
	o----------------|_Y3_|---------------------o
			   _|__         _|__
			  |_Y1_|       |_Y2_|
				|  			 |
	o-------------------------------------------o
	Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
	"""
	A = 1 + Y2/Y3
	B = 1/Y3
	C = Y1 + Y2 + Y1*Y2/Y3
	D = 1 + Y1/Y3
	return Network(A, B, C, D,parameter='abcd',omega=omega)


def from_T_Z(Z1,Z2,Z3,omega=None):
	""" Returns a network object for the following
				____			____
	o----------|_Z1_|----------|_Z2_|-------o
						_|__         
					   |_Z3_|       
						 |  
	o--------------------------------------o
	Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
	"""
	A = 1 + Z1/Z3
	B = Z1 + Z2 + Z1*Z2/Z3
	C = 1/Z3
	D = 1 + Z2/Z3
	return Network(A, B, C, D,parameter='abcd',omega=omega)

#def Tx_line_par_to_Z0_gamma(R,G,L,C,omega):
	#"""Computes the characteristic impedance and propagation constant gamma = alpha + j beta
	#Input:-
	#R := Series resistance per unit length
	#G := Shunt resistance per unit length
	#L := Series inductance per unit length
	#C := Shunt capacitance per unit length
	#omega := Frequency in radians per second 
	#-----------------------------------------
	#Output:-
	#Z0 := Characteristic impedance
	#gamma := Propagation constant
	#"""
	#Z0 = np.sqrt((R+1j*omega*L )/(G+1j*omega*C)) 
	#gamma = np.sqrt((R+1j*omega*L )*(G+1j*omega*C))
	#return Z0, gamma

