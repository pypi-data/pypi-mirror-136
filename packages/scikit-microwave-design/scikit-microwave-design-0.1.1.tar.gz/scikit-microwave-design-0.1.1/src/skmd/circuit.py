"""Module for circuit class"""

import numpy as np
from . import network as nw
from . import extract as ex



class Tx_line_Z0_gamma:
	"""Creates on object of the Transmission line.
	Attributes include: 
	- Lenght: l
	- Characteristics impedance: Z0
	- Propagation constant
	- Object of the class Network."""
	
	def __init__(self, l, Z0, gamma, NW = None, omega=None):
		self.l = l
		self.Z0 = Z0
		self.gamma = gamma
		self.omega = omega
		
		if NW is None:
			self.NW = nw.from_Tx_line(self.l,self.Z0,self.gamma,self.omega)
		else:
			self.NW = NW
		
		
	
		
	# End Class Tx_line_Z0_gamma


class Tx_line_RLCG_omega:
	"""Creates on object of the Transmission line.
	Attributes include: 
	- Lenght: l
	- R_by_l
	## Computes
	- Characteristics impedance: Z0
	- Propagation constant
	- Object of the class Network."""
	
	def __init__(self, l, R,L,C,G,omega):
		
		self.l = l
		
		self.R = R
		self.L = L
		self.C = C
		self.G = G
		
		self.omega = omega
		
		self.Z0, self.gamma = ex.Tx_line_Z0_gamma_from_RLCG(self.R,self.L,self.C,self.G,self.omega)
		
		self.NW = nw.from_Tx_line(self.l,self.Z0,self.gamma,self.omega)
	# End Class Tx_line_RLCG_omega
		
		
class PI_ckt:
	"""Creates an object of PI circuit. 
	Atrributed include:
	
	"""
	def __init__(self,Y1,Y2,Y3,NW=None,omega=None):
		""" Returns a network object for the following
						  ____
		o----------------|_Y3_|---------------------o
				   _|__         _|__
				  |_Y1_|       |_Y2_|
					|  			 |
		o-------------------------------------------o
		Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
		"""
		self.Y1 = Y1
		self.Y2 = Y2
		self.Y3 = Y3
		self.omega = omega
		
		
		A = 1 + Y2/Y3
		B = 1/Y3
		C = Y1 + Y2 + Y1*Y2/Y3
		D = 1 + Y1/Y3
		#self.NW = nw.Network(A, B, C, D,parameter='abcd',omega=omega)
		if NW is None:
			self.NW = nw.Network(A, B, C, D,parameter='abcd',omega=self.omega)
		else:
			self.NW = NW
	# End Class PI_ckt
		
class T_ckt:
	"""Creates an object of T circuit.
	Attributed include:
	
	"""
	def __init__(Z1,Z2,Z3,NW=None,omega=None):
		""" Returns a network object for the following
					____			____
		o----------|_Z1_|----------|_Z2_|-------o
							_|__         
						   |_Z3_|       
							 |  
		o--------------------------------------o
		Based on equations on Page-185, 'Microwave engineering' by D. M. Pozar
		"""
		
		self.Z1 = Z1
		self.Z2 = Z2
		self.Z3 = Z3
		self.omega = omega
		
		A = 1 + Z1/Z3
		B = Z1 + Z2 + Z1*Z2/Z3
		C = 1/Z3
		D = 1 + Z2/Z3
		
		if NW == None:
			self.NW = nw.Network(A, B, C, D,parameter='abcd',omega=self.omega)
		else:
			self.NW = NW
	# End Class T_ckt




