import skmd.circuit
import skmd.data
import skmd.extract
import skmd.network
import skmd.plot
import skmd.structure 
import skmd.signals


__version__ = '00.01.01'


EPSILON_0 = 8.8541878128e-12 # F/m
MU_0 = 1.25663706212e-6 # H/m
VELOCITY_OF_LIGHT = 299792458.0
OPEN = network.np.finfo(float).max
#SHORT = 1/network.np.finfo(float).max
SHORT = network.np.finfo(float).tiny
EPS = network.np.finfo(float).eps


MILLI = 1e-3
MICRO = 1e-6
NANO = 1e-9
PICO = 1e-12

GIGA = 1e9
MEGA = 1e6
KILO = 1e3


def omega2f(omega):
	"""Takes frequency in radians/second and return in Hz"""
	return omega/(2*network.np.pi)


def f2omega(f):
	"""Takes frequency in Hz and returns in radians/second"""
	return 2*network.np.pi*f
	
	
def dB_mag(S):
	"""Takes an S-parameter in normal scale and returns
	20*log10(|S|)."""
	return 20*network.np.log10(network.np.abs(S))
	
	
	
	
