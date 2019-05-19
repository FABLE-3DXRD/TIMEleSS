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


################################################################
#
# Global variables. Set as global to allow interactive changes in plot
#
#################################################################

imageD11Pars = "";
grains = "";
ngrains = 0;
peaksflt = "";
idlist = "";
graintoplot = 0;
plotisset = False;
fig = ""
annotation = ""

#################################################################
#
# Trick to access the forward and backward keys in mathplotlib and use them to move between grains
# Inspired from https://stackoverflow.com/questions/14896580/matplotlib-hooking-in-to-home-back-forward-button-events
#
#################################################################

forward = NavigationToolbar2.forward # Old forward event
backward = NavigationToolbar2.back # Old backward event

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

NavigationToolbar2.forward = new_forward
NavigationToolbar2.back = new_backward

NavigationToolbar2.toolitems = (
	('Home', 'Reset original view', 'home', 'home'), 
	('Back', 'Previous grain', 'back', 'back'), 
	('Forward', 'Next grain', 'forward', 'forward'), 
	(None, None, None, None), 
	('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'), 
	('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'), 
	('Subplots', 'Configure', 'subplots', 'configure_subplots'), 
	(None, None, None, None), 
	('Save', 'Save the figure', 'filesave', 'save_figure'))


def handle_backward(evt):
	global ngrains, graintoplot
	graintoplot = (graintoplot-1) % ngrains
	plotGrainData()
	#print evt.foo

def handle_forward(evt):
	global ngrains, graintoplot
	graintoplot = (graintoplot+1) % ngrains
	plotGrainData()
	#print evt.foo

def onpick(event):
	global annotation
	
	thisdataset = event.artist
	index = event.ind
	posX = (thisdataset.get_offsets())[index][0][0]
	posY = (thisdataset.get_offsets())[index][0][1]
	# print posX, posY
	# print('Clicked on peak number : ', index)
	grain = grains[graintoplot]
	peaks = grain.getPeaks()
	peak = peaks[index[0]]
	tthetaPred = peak.getTThetaPred()
	etaPred = peak.getEtaPred()
	omegaPred = peak.getOmegaPred()
	tthetaMeas = peak.getTThetaMeasured()
	etaMeas = peak.getEtaMeasured()
	omegaMeas = peak.getOmegaMeasured()
	hkl = peak.getHKL()
	text = "Peak (%d,%d,%d)\nttheta = (%.1f, %.1f, %.1f)\neta = (%.1f, %.1f, %.1f)\nomega = (%.1f, %.1f, %.1f)\n(pred., meas., diff.)" % (hkl[0], hkl[1], hkl[2], tthetaPred, tthetaMeas, tthetaPred-tthetaMeas, etaPred, etaMeas, etaPred-etaMeas, omegaPred, omegaMeas, omegaPred - omegaMeas)
	# Clear the plot and redraw (to remove old annotations)
	if (annotation != ""):
		annotation.remove()
	# Add the label
	annotation = plt.text(posX, posY, text, fontsize=9, bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 1., 1.), alpha=0.9))
	
	fig.canvas.draw()
	
	
# TODO: use the configure button to allow changing what is plotted (could be s vs omega, for instance)


#################################################################
#
# Plotting routines
#
#################################################################


def makeThePlot(title, xlabel, ylabel, xmeasured, ymeasured, xpred, ypred, rings=""):
	global plotisset, fig, annotation
	if (not plotisset):
		fig = plt.figure()
		fig.canvas.mpl_connect('forward_event', handle_forward)
		fig.canvas.mpl_connect('backward_event', handle_backward)
		fig.canvas.mpl_connect('pick_event', onpick)
	else:
		fig.clear()
	# Plotting diffraction rings
	for ring in rings:
		plt.plot(ring[1], ring[0], color='black', linestyle='solid', linewidth=0.5)
	# Adding indexed points
	plt.scatter(xmeasured, ymeasured, s=60,  marker='o', facecolors='r', edgecolors='r')
	plt.scatter(xpred, ypred, s=80,  marker='s', facecolors='none', edgecolors='b', picker=5) # Picker to allow users to pick on a point
	# Labels
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	if (not plotisset):
		plotisset = True
		plt.show()
	else:
		annotation = ""
		fig.canvas.draw()
		fig.canvas.flush_events()


def plotGrainData():
	global imageD11Pars, grains, ngrains, peaksflt, idlist, graintoplot
	
	grain = grains[graintoplot]
	peaks = grain.getPeaks()
	npeaks = len(peaks)
	# Will hold predicted peak positions, ttheta, eta, omega, f, and s
	tthetaPred = numpy.zeros(npeaks)
	etaPred =  numpy.zeros(npeaks)
	omegaPred = numpy.zeros(npeaks)
	# Will hold measure peak positions, f, and s
	fmeasured = numpy.zeros(npeaks)
	smeasured = numpy.zeros(npeaks)
	# Filling up the array
	i = 0
	for peak in peaks:
		tthetaPred[i] = peak.getTThetaPred()
		etaPred[i] = peak.getEtaPred()
		omegaPred[i] = peak.getOmegaPred()
		try:
			index = idlist.index(peak.getPeakID())
			smeasured[i] = peaksflt[index]['sc']
			fmeasured[i] = peaksflt[index]['fc']
		except IndexError:
			print "Failed to locate peak ID %d which was found in grain %s" % (peak.getPeakID(), grain.getName())
			return
		i += 1
	# Calculating predicted peak positions from angles
	(fpred, spred) = transform.compute_xyz_from_tth_eta(tthetaPred, etaPred, omegaPred, **imageD11Pars.parameters)
	
	# Preparing information to add diffraction rings
	ringstth = numpy.unique(tthetaPred)
	rings = []
	for tth in ringstth:
		eta = numpy.arange(0., 362., 2.)
		ttheta = numpy.full((len(eta)), tth)
		omega = numpy.full((len(eta)), 0.)
		rings.append(transform.compute_xyz_from_tth_eta(ttheta, eta, omega, **imageD11Pars.parameters))
		
	# Ready to plot, using multithreading to be able to have multiple plots, did not work!!
	makeThePlot("Grain %s" % (graintoplot+1), 'f (pixels)', 's (pixels)', smeasured, fmeasured, spred, fpred, rings)

#################################################################
#
# Parse input files and move one
#
#################################################################

def plotFltGrains():
	global ngrains
	
	test=False
	while (test==False):
		txt = raw_input("Grain number (1-%d, 0 to stop) ? " % ngrains)
		try:
			graintoplot = int(txt)-1
			if (graintoplot == -1):
				return
			if ((graintoplot<0) or (graintoplot>ngrains)):
				print ("Input should be between 1 and %d" % ngrains)
			else:
				plotGrainData()
				test = True
				
		except ValueError:
			print ("Input is wrong" )

	# Comment from John if we want to include peak intensity and peak shapes
	# Plot peaks from FLT, max intensity, sigs  sigf  sigo are sigmas calculated from the second moment
	# !! a +1 is added in the moment calculation to avoid 0 width peaks (returns sqrt(variant + 1))



def parseInputFiles(gsfile, FLT, par):
	global imageD11Pars, grains, ngrains, peaksflt, idlist, graintoplot
	
	imageD11Pars = parameters.read_par_file(par)

	grains = multigrainOutputParser.parse_GrainSpotter_log(gsfile)
	print ("Parsed grains from %s" % gsfile)
	ngrains =  len(grains)
	print ("Number of grains: %d" % ngrains)

	[peaksflt,idlist,header] = multigrainOutputParser.parseFLT(FLT)
	print ("Parsed peaks from %s" % FLT)
	print ("Number of peaks: %d" % len(peaksflt))
	
	# Locating the columns with detector positions in flt file
	# headerarr = header.split()
	#try:
	#	iSC = headerarr.index("sc") - 1
	#	iFC = headerarr.index("fc") - 1
	#except:
	#	print ("Can not find sc and fc columns in %s" % FLT)
	#	return


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
	
	parser = MyParser(usage='%(prog)s GSFile.log FLT.flt', description="Creates a new list of peaks in FLT format, including only peaks which have already been assigned to grains by GrainSpotter\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('FLT',  help="FLT file used to generate g-vectors for indexing (required)")
	parser.add_argument('par',  help="ImageD11 parameter file (required)")

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	FLT = args['FLT']
	par = args['par']

	test = parseInputFiles(gsfile, FLT, par)
	plotFltGrains()


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


