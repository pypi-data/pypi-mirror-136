"""Module containg functions on visualization"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rc('axes',labelsize=24)
mpl.rc('font',size=24)

def polar_plot_colored_line(theta,R,T,ax, color_axis=None, use_colormap='jet',linewidth=3,title_name=None):
		### Plots the line (x,y), with continuous color variation on the axis 'ax'.
		### according to values in T and colormap as use_colormap
		### Returns the color map and normalization scale. For plotting colorbar
		cmap=mpl.cm.get_cmap(use_colormap)
		#cmap=plt.get_cmap(use_colormap)
		
		vmin=T.min()
		vmax=T.max()
		
		norm=mpl.colors.Normalize(vmin=vmin, vmax=vmax)
		for count in range(len(T)-1):
			T0=( float(T[count]) + float(T[count+1]) )/2
			#ax.plot(x[count:count+2],y[count:count+2],color=cmap(norm(T0)),linewidth=linewidth)
			ax.plot(theta[count:count+2],R[count:count+2],color=cmap(norm(T0)),linewidth=linewidth)
			
		if color_axis != None: ## Adds color bar to the given axis. 
			#c_plot = mpl.colorbar.ColorbarBase(ax=color_axis, cmap=use_colormap, orientation="vertical",norm=norm)
			c_plot = mpl.colorbar.ColorbarBase(ax=color_axis, cmap=cmap, orientation="vertical",norm=norm)
			if title_name != None:
				c_plot.ax.set_title(title_name)
		return #use_colormap, norm  


def plot_colored_line(x,y,T,ax, color_axis=None, use_colormap='jet',linewidth=3,title_name=None,vmin=None,vmax=None):
    ### Plots the line (x,y), with continuous color variation on the axis 'ax'.
    ### according to values in T and colormap as use_colormap
    ### Returns the color map and normalization scale. For plotting colorbar
    cmap=mpl.cm.get_cmap(use_colormap)
    
    if vmin == None: ## Adds color bar to the given axis. 
        vmin=T.min()
        
    if vmax == None: ## Adds color bar to the given axis. 
        vmax=T.max()
        
    #vmin=T.min()
    #vmax=T.max()
    
    norm=mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    for count in range(len(T)-1):
        T0=( float(T[count]) + float(T[count+1]) )/2
        ax.plot(x[count:count+2],y[count:count+2],color=cmap(norm(T0)),linewidth=linewidth)
        
    if color_axis != None: ## Adds color bar to the given axis. 
        c_plot = mpl.colorbar.ColorbarBase(ax=color_axis, cmap=cmap, orientation="vertical",norm=norm)
        if title_name != None:
            c_plot.ax.set_title(title_name)
    return #use_colormap, norm  




class SnaptoCursor:
    """
    Like Cursor but the crosshair snaps to the nearest x, y point.
    For simplicity, this assumes that *x* is sorted.
    """

    def __init__(self, ax, x, y):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line
        self.x = x
        self.y = y
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        indx = min(np.searchsorted(self.x, x), len(self.x) - 1)
        x = self.x[indx]
        y = self.y[indx]
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('freq=%1.2f, S(dB)=%1.2f' % (x, y))
        print('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()



class SnaptoCursor_polar:
    """
    Dynamic data-points using cursor.
    """

    def __init__(self, ax, freq, S_p):
        self.ax = ax
        #self.lx = ax.axhline(color='k')  # the horiz line
        #self.ly = ax.axvline(color='k')  # the vert line
        self.freq = freq
        self.S_p = S_p
        self.S_p_phase = np.angle(S_p)
        self.S_p_mag = np.abs(S_p)
        # text location in axes coords
        #self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)
        self.pt, = self.ax.plot(np.pi/4,1,marker='*',markersize=20,color='k')
        #self.ax.plot(self.S_p_phase, self.S_p_mag)
        print('here')

    def mouse_move(self, event):
		
        if not event.inaxes:
            return
        
        		
        theta, R = event.xdata, event.ydata
        
        print('theta=%1.2f, R=%1.2f' % (theta, R))
        
        distance_polar_sq = (np.real(self.S_p) - R*np.cos(theta))**2 + (np.imag(self.S_p) - R*np.sin(theta))**2
        #distance_polar_sq = (np.real(self.S_p) - R*np.cos(theta))**2 + (np.imag(self.S_p) - R*np.sin(theta))**2
        
        indx = np.argmin(distance_polar_sq)
        
        #indx = min(np.searchsorted(self.theta, theta), len(self.theta) - 1)
        print(np.min(distance_polar_sq))
        print(indx)
        pt_S_phase = self.S_p_phase[indx]
        pt_S_mag = self.S_p_mag[indx]
        pt_freq = self.freq[indx] 
        
        self.pt.set_xdata(pt_S_phase)
        self.pt.set_ydata(pt_S_mag)
        
        # update the line positions
        #self.lx.set_ydata(y)
        #self.ly.set_xdata(x)

        #self.txt.set_text('freq=%1.2f, S(dB)=%1.2f' % (x, y))
        print('S = %1.2f' % pt_S_mag)
        #print('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.set_title('Freq = %1.2f, S = %1.2f $\\angle$ %1.2f$^\circ$' % (pt_freq,pt_S_mag,np.rad2deg(pt_S_phase)) )
        self.ax.figure.canvas.draw()


def plot_smith_chart(variable,S_p,fig,linewidth=5,use_colormap='hsv'):
	
	
	
	ax = fig.add_subplot(111,projection='polar')
	
	ax_cmap = fig.add_axes([0.9, 0.2, 0.05, 0.7])
	
	def smith_const_resistance(ax):
		theta = np.linspace(0,2*np.pi,100)
		for r in [0.2,0.5,1,2,5]:
			u = np.cos(theta)/(r+1) + r/(r+1)
			v = np.sin(theta)/(r+1)
			theta_R = np.arctan2(v,u) 
			R = np.sqrt(u**2 + v**2)
			ax.plot(theta_R,R,color=(0.2,0.2,0.2),linestyle='--')
		return
		
	def smith_const_reactance(ax):
		theta = np.linspace(0,2*np.pi,100)
		for x  in [-3,-1,1,3]:
			u = 1   + 2*np.cos(theta)/np.abs(x)
			v = 2/x + 2*np.sin(theta)/np.abs(x)
			theta_R = np.arctan2(v,u)
			R = np.sqrt(u**2 + v**2)
			ax.plot(theta_R,R,color=(0.4,0,0),linestyle=':')		
		
		

	smith_const_resistance(ax)  # Insert constant resistance circles.
	smith_const_reactance(ax)   # Insert constant reactance circles. 
	polar_plot_colored_line(np.angle(S_p),np.abs(S_p),variable,ax,color_axis=ax_cmap,linewidth=linewidth,use_colormap=use_colormap)
	ax.set_rlim([0,1.0])
	
	#snap_cursor_2 = SnaptoCursor_polar(ax, freq/1e9, 20*np.log10(NW_filter.

	
	return ax




def Dynamic_data_points(fig,ax,freq,S_p):
	snap_cursor_2 = SnaptoCursor_polar(ax,freq, S_p)
	return fig.canvas.mpl_connect('motion_notify_event', snap_cursor_2.mouse_move)

