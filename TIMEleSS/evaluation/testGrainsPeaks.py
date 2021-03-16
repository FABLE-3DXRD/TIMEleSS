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

# Python 2 to python 3 migration tools
from __future__ import absolute_import
from __future__ import print_function

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

#################################################################
#
# Class definition
#
#################################################################

class grainPlotData:
	
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
	Returns the number of grains available
	"""
	def getNGrains(self):
		return self.ngrains

	"""
	Extracts necessary data and calls for a plot
	
	Parameters:
	- grainnumber
	- whattoplot: # Choice of "etavsttheta", "omegavsttheta", or "svsf" (default)
	
	Before calling this function, input file should have been read
	
	Can be called after plotting if one wants to change the grain or the type of plot
	
	Returns a list with
		- title
		- xlabel
		- ylabel
		- xmeasured: list of measured x positions of peaks
		- ymeasured: list of measured y positions of peaks
		- xpred: list of predicted x positions of peaks
		- ypred: list of predictedy positions of peaks
		- list of 2theta rings to plot, for each ring, 2 elements list of y and list of x (y comes first)
	"""
	def getPlotData(self, grainnumber, whattoplot):
		grain = self.grains[grainnumber]
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
				print ("Failed to locate peak ID %d which was found in grain %s" % (peak.getPeakID(), grain.getName()))
				return
			i += 1
			
		# eta vs 2 theta 
		if (whattoplot == "etavsttheta"):
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
			return ["Grain %s" % (grainnumber+1), '2theta (degrees)', 'eta (degrees)', tthetaexp, etaexp, tthetaPred, etaPred,rings]
			
		# omega vs 2 theta 
		elif (whattoplot == "omegavsttheta"):
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
			return ["Grain %s" % (grainnumber+1), '2theta (degrees)', 'omega (degrees)', tthetaexp, omegaexp, tthetaPred, omegaPred, rings]
		
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
		return ["Grain %s" % (grainnumber+1), 'f (pixels)', 's (pixels)', fsmeasured[0,:], fsmeasured[1,:], spred, fpred, rings]


	"""
	Returns information about peak peaknum in grain grainnum
	"""
	def getPeakInfo(self, grainnum, peaknum):
		grain = self.grains[grainnum]
		peaks = grain.getPeaks()
		peak = peaks[peaknum]
		tthetaPred = peak.getTThetaPred()
		etaPred = peak.getEtaPred()
		omegaPred = peak.getOmegaPred()
		tthetaMeas = peak.getTThetaMeasured()
		etaMeas = peak.getEtaMeasured()
		omegaMeas = peak.getOmegaMeasured()
		hkl = peak.getHKL()
		# Preparing text
		text = "Peak (%d,%d,%d)\nttheta = (%.1f, %.1f, %.1f)\neta = (%.1f, %.1f, %.1f)\nomega = (%.1f, %.1f, %.1f)\n(pred., meas., diff.)" % (hkl[0], hkl[1], hkl[2], tthetaPred, tthetaMeas, tthetaPred-tthetaMeas, etaPred, etaMeas, etaPred-etaMeas, omegaPred, omegaMeas, omegaPred - omegaMeas)
		
		return text


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
	
	parser = MyParser(usage='%(prog)s [options] parfile.prm GSFile.log FLT.flt', description="Tool to compare predicted and measured peak positions for a grain after indexing. Will do nothing by itself but can be called from a GUI\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('par',  help="ImageD11 parameter file (required)")
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('FLT',  help="FLT file used to generate g-vectors for indexing (required)")

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	FLT = args['FLT']
	par = args['par']
	
	grainData = grainPlotData()
	test = grainData.parseInputFiles(gsfile, FLT, par)

# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


