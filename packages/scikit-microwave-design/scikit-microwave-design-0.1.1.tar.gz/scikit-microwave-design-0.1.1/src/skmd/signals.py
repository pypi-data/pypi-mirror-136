import numpy as np


def unit_step(t):
    """ Takes time as argument and returns a unit-step function """
    return 1*(t>=0)

def dirac_delta(t,Delta=1e-3):
	
	x_t = (1/Delta)*(unit_step(t+Delta/2) - unit_step(t-Delta/2) )
	return x_t

def Fourier_Transfrom(x_t,t):
	""" Computes CTFT using FFT algorithm.
	Frequency and amplitude are scaled appropriately.
	It is assumed that the time varible is equispaced.
	Numpy FFT algorithm is used to compute the Fourier Transfrom,
	therefore it is also assumed that the signal is periodic in time
	with a period T_range. 
	Note that you should define the time from -T_range/2 to +T_range/2"""
	
	N_pts = np.size(x_t)
	T_range = t.max() - t.min()
	
	delta_t = T_range/N_pts
	
	X_fft = np.fft.fft(x_t)
	X_fft = np.fft.fftshift(X_fft)
	X_omega = X_fft*delta_t
	
	omega = (2*np.pi/delta_t)*np.fft.fftshift(np.fft.fftfreq(N_pts))
	#omega = (2*np.pi/delta_t)*np.fft.fftfreq(N_pts)
	
	return X_omega, omega
	
def Inverse_Fourier_Transform(X_omega,omega):
	"""Computes and returns continuous inverse Fourier Transfrom using numpy
	ifft function. Time and frequency are scaled appropriately."""
	
	omega_range = omega.max() - omega.min()
	delta_omega = omega_range/np.size(omega)
	
	x_t_ifft = np.fft.ifft(np.fft.fftshift(X_omega))*omega_range/(2*np.pi)
	t_ifft = (2*np.pi/delta_omega)*np.fft.fftshift(np.fft.fftfreq(np.size(omega)))
	return x_t_ifft, t_ifft

