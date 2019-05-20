#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This is part of the TIMEleSS tools
http://timeless.texture.rocks/

Copyright (C) S. Merkel, Universite de Lille, France

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""


# System functions, to manipulate command line arguments
import sys
import argparse
import os.path

# Parsing tools
from TIMEleSS.general import multigrainOutputParser

# Simple mathematical operations
import numpy

# Rely on ImageD11 for recalculating the peak positions on detector
from ImageD11 import transform
from ImageD11 import parameters

# Plotting routines
import matplotlib
import platform
if platform.system() == 'Linux':
	matplotlib.use('GTK3Agg')
import matplotlib.pyplot as plt

# Access to the toolbar buttons in MathPlotLib
from matplotlib.backend_bases import NavigationToolbar2, Event

# Dialog to configure plot
import Tkinter
import tkSimpleDialog
from PyQt4.QtGui import (QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog)

# Various matplotlib tricks to adapt the GUI to what we want
#
# Access the forward and backward keys in mathplotlib and use them to move between grains
# Inspired from 
# - https://stackoverflow.com/questions/14896580/matplotlib-hooking-in-to-home-back-forward-button-events
# - https://stackoverflow.com/questions/37506260/adding-an-item-in-matplotlib%C2%B4s-toolbar
#
# Click on peak and get information on h,k,l, diffraction angles, and indexing errors
#

def new_forward(self, *args, **kwargs):
	s = 'forward_event'
	event = Event(s, self)
	event.foo = 100
	self.canvas.callbacks.process(s, event)
	# forward(self, *args, **kwargs) # If you wanted to still call the old forward event

def new_backward(self, *args, **kwargs):
	s = 'backward_event'
	event = Event(s, self)
	event.foo = 100
	self.canvas.callbacks.process(s, event)
	# backward(self, *args, **kwargs) # If you wanted to still call the old backward event

def configure_plot(self, *args, **kwargs):
	s = 'configure_event'
	event = Event(s, self)
	self.canvas.callbacks.process(s, event)

NavigationToolbar2.forward = new_forward
NavigationToolbar2.back = new_backward
NavigationToolbar2.configure = configure_plot

NavigationToolbar2.toolitems = (
	('Home', 'Reset original view', 'home', 'home'), 
	('Back', 'Previous grain', 'back', 'back'), 
	('Forward', 'Next grain', 'forward', 'forward'), 
	(None, None, None, None), 
	('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'), 
	('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'), 
	(None, None, None, None), 
	('Configure', 'Configure', 'subplots', 'configure'), # Replacing the subplots configuration with my own configure_plot
	(None, None, None, None), 
	('Save', 'Save the figure', 'filesave', 'save_figure'))


class configurePlotDialog(QDialog):

	def __init__(self, parent=None):
		super(configurePlotDialog, self).__init__(parent)
		# Create widgets
		self.edit = QLineEdit("Write my name here")
		self.button = QPushButton("Show Greetings")
		# Create layout and add widgets
		layout = QVBoxLayout()
		layout.addWidget(self.edit)
		layout.addWidget(self.button)
		# Set dialog layout
		self.setLayout(layout)
		# Add button signal to greetings slot
		self.button.clicked.connect(self.greetings)

	# Greets the user
	def greetings(self):
		print ("Hello %s" % self.edit.text())



#################################################################
#
# Class definition
#
#################################################################

class plotGrainWindow:
	
	# Comment from John if we want to include peak intensity and peak shapes
	# Plot peaks from FLT, max intensity, sigs  sigf  sigo are sigmas calculated from the second moment
	# !! a +1 is added in the moment calculation to avoid 0 width peaks (returns sqrt(variant + 1))
	
	def __init__(self):
		self.imageD11Pars = "";		# ImageD11 parameters
		self.grains = "";			# Indexed grains
		self.ngrains = 0;			# Number of indexed grains
		self.peaksflt = "";			# Extraction from FLT file
		self.idlist = "";			# List of peak ID, to easily relate indexed peaks and flt information
		self.graintoplot = 0;		# Which grain is being plotted
		self.plotisset = False;		# Did we start a plot window?
		self.fig = ""				# Figure in which to plot
		self.annotation = ""		# Annotation in the figure
		self.whatoplot = "svsf"			# Choice of "etavsttheta", "omegavsttheta", default (svsf)

	"""
	Parse input files
	
	Parameters
	- gsfile: name of grainspotter log file
	- FLT: name of flt file
	- par: name of ImageD11 par file
	"""
	def parseInputFiles(self, gsfile, FLT, par):
		self.imageD11Pars = parameters.read_par_file(par)

		self.grains = multigrainOutputParser.parse_GrainSpotter_log(gsfile)
		print ("Parsed grains from %s" % gsfile)
		self.ngrains =  len(self.grains)
		print ("Number of grains: %d" % self.ngrains)
		
		[self.peaksflt,self.idlist,self.header] = multigrainOutputParser.parseFLT(FLT)
		print ("Parsed peaks from %s" % FLT)
		print ("Number of peaks: %d" % len(self.peaksflt))
	
	
	"""
	Set a starting plot type
	
	Parameters:
	- plot: choice of "etavsttheta", "omegavsttheta", default "svsf"
	
	"""
	def setPlotType(self, plot):
		self.whatoplot = plot
	
	"""
	Ask for a grain number and start plotting
	
	To be called after "parseInputFiles" and, maybe "setPlotType"
	"""
	def selectGrainAndPlot(self):
		test=False
		while (test==False):
			txt = raw_input("Grain number (1-%d, 0 to stop) ? " % self.ngrains)
			try:
				self.graintoplot = int(txt)-1
				if (self.graintoplot == -1):
					return
				if ((self.graintoplot<0) or (self.graintoplot>self.ngrains)):
					print ("Input should be between 1 and %d" % self.ngrains)
				else:
					self.plotGrainData()
					test = True
			except ValueError:
				print ("Input is wrong" )

	"""
	Extracts necessary data and calls for a plot
	
	Before calling this function, input file should have been read, type of plot should have been decided, and grain to look at should have been decided as well.
	
	Can be called after plotting if one wants to change the grain or the type of plot
	"""
	def plotGrainData(self):
		grain = self.grains[self.graintoplot]
		peaks = grain.getPeaks()
		npeaks = len(peaks)
		# Will hold predicted peak positions, ttheta, eta, omega
		tthetaPred = numpy.zeros(npeaks)
		etaPred =  numpy.zeros(npeaks)
		omegaPred = numpy.zeros(npeaks)
		# Will hold measured peak positions, f, s, and omega
		fsmeasured = numpy.zeros([2,npeaks])
		omegaexp = numpy.zeros([npeaks])
		# Filling up the array
		i = 0
		for peak in peaks:
			tthetaPred[i] = peak.getTThetaPred()
			etaPred[i] = peak.getEtaPred()
			omegaPred[i] = peak.getOmegaPred()
			try:
				index = self.idlist.index(peak.getPeakID())
				fsmeasured[1,i] = self.peaksflt[index]['fc']
				fsmeasured[0,i] = self.peaksflt[index]['sc']
				omegaexp[i] = self.peaksflt[index]['omega']
			except IndexError:
				print "Failed to locate peak ID %d which was found in grain %s" % (peak.getPeakID(), grain.getName())
				return
			i += 1
			
		# eta vs 2 theta 
		if (self.whatoplot == "etavsttheta"):
			# Calculating 2theta and eta for experimental peaks
			(tthetaexp, etaexp) = transform. compute_tth_eta(fsmeasured, **self.imageD11Pars.parameters)
			# Bringing eta into 0-360 range instead of -180-180
			etaexp = etaexp % 360
			# Preparing information to add diffraction rings
			ringstth = numpy.unique(tthetaPred)
			rings = []
			for tth in ringstth:
				eta = numpy.array([0.,180.,360.])
				ttheta = numpy.full((len(eta)), tth)
				omega = numpy.full((len(eta)), 0.)
				rings.append([eta,ttheta])
			# Ready to plot
			self.makeThePlot("Grain %s" % (self.graintoplot+1), '2theta (degrees)', 'eta (degrees)', tthetaexp, etaexp, tthetaPred, etaPred,rings)
			
		# omega vs 2 theta 
		elif (self.whatoplot == "omegavsttheta"):
			# Calculating 2theta and eta for experimental peaks
			(tthetaexp, etaexp) = transform.compute_tth_eta(fsmeasured, **self.imageD11Pars.parameters)
			# Bringing eta into 0-360 range instead of -180-180
			etaexp = etaexp % 360
			# Preparing information to add diffraction rings
			ringstth = numpy.unique(tthetaPred)
			rings = []
			omegam = min(min(omegaexp),min(omegaPred))
			omegaM = max(max(omegaexp),max(omegaPred))
			for tth in ringstth:
				omega = numpy.array([omegam-1.,omegaM+1.])
				ttheta = numpy.full((len(omega)), tth)
				rings.append([omega,ttheta])
			# Ready to plot, using multithreading to be able to have multiple plots, did not work!!
			self.makeThePlot("Grain %s" % (self.graintoplot+1), '2theta (degrees)', 'omega (degrees)', tthetaexp, omegaexp, tthetaPred, omegaPred, rings)
		
		# s vs f (as on detector)
		else:
			# Calculating predicted peak positions from angles
			(fpred, spred) = transform.compute_xyz_from_tth_eta(tthetaPred, etaPred, omegaPred, **self.imageD11Pars.parameters)
			# Preparing information to add diffraction rings
			ringstth = numpy.unique(tthetaPred)
			rings = []
			for tth in ringstth:
				eta = numpy.arange(0., 362., 2.)
				ttheta = numpy.full((len(eta)), tth)
				omega = numpy.full((len(eta)), 0.)
				rings.append(transform.compute_xyz_from_tth_eta(ttheta, eta, omega, **self.imageD11Pars.parameters))
			# Ready to plot
			self.makeThePlot("Grain %s" % (self.graintoplot+1), 'f (pixels)', 's (pixels)', fsmeasured[0,:], fsmeasured[1,:], spred, fpred, rings)

	"""
	Prepares a plot with matplotlib
	
	Parameters
		- title
		- xlabel
		- ylabel
		- xmeasured: list of measured x positions of peaks
		- ymeasured: list of measured y positions of peaks
		- xpred: list of predicted x positions of peaks
		- ypred: list of predictedy positions of peaks
		- list of 2theta rings to plot, for each ring, 2 elements list of y and list of x (y comes first)
	"""
	def makeThePlot(self,title, xlabel, ylabel, xmeasured, ymeasured, xpred, ypred, rings=""):
		# Preparing a plot window and event processing
		if (not self.plotisset):
			self.fig = plt.figure()     
			self.fig.canvas.mpl_connect('forward_event', self.handle_forward)
			self.fig.canvas.mpl_connect('backward_event', self.handle_backward)
			self.fig.canvas.mpl_connect('configure_event', self.handle_configure)
			self.fig.canvas.mpl_connect('pick_event', self.onpick) 
		else:
			self.fig.clear()
		# Plotting diffraction rings
		for ring in rings:
			plt.plot(ring[1], ring[0], color='black', linestyle='solid', linewidth=0.5, alpha=0.5)
		# Adding indexed peaks
		g1 = plt.scatter(xmeasured, ymeasured, s=60,  marker='o', facecolors='r', edgecolors='r')
		g2 = plt.scatter(xpred, ypred, s=80,  marker='s', facecolors='none', edgecolors='b', picker=5) # Picker to allow users to pick on a point
		# Title and labels
		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.title(title, loc='left')
		# Legend
		plt.legend([g1, g2], ['Measured', 'Predicted'],
              loc = 'upper right', ncol = 2, scatterpoints = 1,
              frameon = True, markerscale = 1,
              borderpad = 0.2, labelspacing = 0.2, bbox_to_anchor=(1., 1.1))
		# Ready to plot
		if (not self.plotisset):
			self.plotisset = True
			plt.show()
		else:
			self.annotation = ""
			self.fig.canvas.draw()
			self.fig.canvas.flush_events()

	def handle_configure(self,evt):
		# Tested various ways of dealing with dialogs. Not very satisfied. Need to move the app into a GUI
		# Create and show the form
		#dialog = configurePlotDialog()
		#dialog.show()
		#root = Tkinter.Tk()
		#d = ConfigurePlotDialog(root, self.graintoplot, self.whatoplot)
		#root.withdraw()
		#print d.result

	"""
	Event processing when left arrow is click (move to previous grain)
	"""
	def handle_backward(self,evt):
		self.graintoplot = (self.graintoplot-1) % self.ngrains
		self.plotGrainData()

	"""
	Event processing when right arrow is click (move to next grain)
	"""
	def handle_forward(self,evt):
		self.graintoplot = (self.graintoplot+1) % self.ngrains
		self.plotGrainData()

	"""
	Picking events on data in plot
	- Locates the peak that is being selected
	- Pulls out indexing information for this peak (h, k, l, predicted and measured angles)
	- Displays information in the plot, next to the peak
	
	Parameters
		event
	"""
	def onpick(self,event):
		# Locating peak
		thisdataset = event.artist
		index = event.ind
		posX = (thisdataset.get_offsets())[index][0][0]
		posY = (thisdataset.get_offsets())[index][0][1]
		# Extracting indexing info for this peak
		grain = self.grains[self.graintoplot]
		peaks = grain.getPeaks()
		peak = peaks[index[0]]
		tthetaPred = peak.getTThetaPred()
		etaPred = peak.getEtaPred()
		omegaPred = peak.getOmegaPred()
		tthetaMeas = peak.getTThetaMeasured()
		etaMeas = peak.getEtaMeasured()
		omegaMeas = peak.getOmegaMeasured()
		hkl = peak.getHKL()
		# Preparing text
		text = "Peak (%d,%d,%d)\nttheta = (%.1f, %.1f, %.1f)\neta = (%.1f, %.1f, %.1f)\nomega = (%.1f, %.1f, %.1f)\n(pred., meas., diff.)" % (hkl[0], hkl[1], hkl[2], tthetaPred, tthetaMeas, tthetaPred-tthetaMeas, etaPred, etaMeas, etaPred-etaMeas, omegaPred, omegaMeas, omegaPred - omegaMeas)
		# Clearing annotation if there is one already
		if (self.annotation != ""):
			self.annotation.remove()
		# Add the peak information to the plot
		self.annotation = plt.text(posX, posY, text, fontsize=9, bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 1., 1.), alpha=0.9))
		self.fig.canvas.draw()
	
	# TODO: use the configure button to allow changing what is plotted (could be s vs omega, for instance)


#################################################################
#
# Main subroutines
#
#################################################################

class MyParser(argparse.ArgumentParser):
	"""
	Extend the regular argument parser to show the full help in case of error
	"""
	def error(self, message):
		
		sys.stderr.write('\nError : %s\n\n' % message)
		self.print_help()
		sys.exit(2)


def main(argv):
	"""
	Main subroutine
	"""
	
	parser = MyParser(usage='%(prog)s [options] parfile.prm GSFile.log FLT.flt', description="Compares predicted and measured peak positions for a grain after indexing. Can plot as an image, in pixels, or with eta or omega vs. 2theta\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('par',  help="ImageD11 parameter file (required)")
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('FLT',  help="FLT file used to generate g-vectors for indexing (required)")
	
	# Other arguments
	parser.add_argument('-p', '--plot', type=int, choices=range(1, 4), required=False, help="""What do you want to plot ?
    1 for s vs f in pixels (i.e. diffraction image), 2 for eta vs. 2 theta, 3 for omega vs. 2 theta. Default is 1.""", default=1)

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	FLT = args['FLT']
	par = args['par']
	p = args['plot']
	
	
	plotWindow = plotGrainWindow()
	test = plotWindow.parseInputFiles(gsfile, FLT, par)
	if (p==2):
		plotWindow.setPlotType("etavsttheta")
	elif (p==3):
		plotWindow.setPlotType("omegavsttheta")
	plotWindow.selectGrainAndPlot()
	
	# Create the Qt Application (we need to embed the plot inside an application to fire dialogs)
	# app = QApplication(sys.argv)
	
	# Run the main Qt loop
	# sys.exit(app.exec_())
	


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


