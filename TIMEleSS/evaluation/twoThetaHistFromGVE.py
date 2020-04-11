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

# Maths stuff
import numpy

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser

#################################################################
#
# Class definition
#
# This class is designed to build 2theta histograms based on gvefile
# data. They can be saved to a file or, maybe at some point, integrated
# in a GUI
#
# This a bit redundant with ImageD11. Might want to push a change to
# allow saving histogram.
#
# Histograms in ImageD11, however, are created from FLT which might be different from 
# the GVE file if one used filters in between.
#
#################################################################

class twothetahistogram:

	"""
	Inits parameters for the calculation of 2theta histograms
	Input: wavelength, in angstroms
	"""
	def __init__(self,wavelength):
		self.gvefile = ""				# GVE file parameters
		self.peakList = []				# List of peaks
		self.twothetalist = []			# List of twothetas for the peaks
		self.wavelength = wavelength	# wavelength, in angstroms
		self.npeaks = 0					# Number ofpeaks
		self.hist = ""					# histogram data
		self.nbins = 0					# number of bins in the histogram
		self.set = False				# Will be set to true one we have any histogram

	"""
	Parses and sets peaks from a GVE file
	"""
	def setGVE(self,gvefile):
		[peaksgve,idlist,header] = multigrainOutputParser.parseGVE(gvefile) 
		self.peakList = peaksgve
		self.npeaks = len(peaksgve)
		self.gvefile = gvefile
		self.twotheta = []
		for peak in self.peakList:
			dsPeak = float(peak['ds'])
			self.twotheta.append(2.*numpy.degrees(numpy.arcsin(dsPeak*self.wavelength/2.)))
	
	"""
	Change the wavelength
	"""
	def setWavelength(self,wavelength):
		self.twotheta = []
		for peak in self.peakList:
			dsPeak = float(peak['ds'])
			self.twotheta.append(2.*numpy.degrees(numpy.arcsin(dsPeak*self.wavelength/2.)))
	
	"""
	Generate an histograms for the number of bins
	"""
	def buildHistogram(self,nbins=10000):
		if (len(self.twotheta) == 0):
			return
		self.nbins = nbins
		self.hist = numpy.histogram(self.twotheta,self.nbins)
		print "Calculated a %d elements two-theta histograms based on peaks in %s" % (self.nbins,self.gvefile)
		
	"""
	Saves this histogram to a file
	"""
	def savetofile(self,output):
		out = open(output,'w')
		out.write("# Histograms of two theta angles in %s\n" % self.gvefile)
		out.write("# Original number of peaks: %d\n" % self.npeaks)
		out.write("# Number of bins: %d\n" % self.nbins)
		out.write("# Two theta (degrees), proportion of peaks in bin\n#\n")
		for i in range(0,self.nbins):
			out.write("%.4f %.4e\n" % (self.hist[1][i], (1.0*self.hist[0][i]/self.npeaks)))
		out.close()
		print "Saved two theta histograms in %s" % (output)


#################################################################
#
# Main function, to be used if called from the command line
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
	
	parser = MyParser(usage='%(prog)s [options] g-vectors.gve', description="Tool to calculate a 2theta histogram based on experimental g-vectors in a GVE file.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Positionnal arguments
	parser.add_argument("gve", help="Name of GVE file")
	
	# Required arguments
	parser.add_argument('-w', '--wavelength', required=True, help="Wavelength, in angstroms  (required)", type=float)
	parser.add_argument('-o', '--output',  help="Name of output file (required)")
	
	# Optional arguments
	parser.add_argument('-n', '--nbins', required=False, help="Number of bins. Default is %(default)s",  type=int, default=1000)

	args = vars(parser.parse_args())	

	gve = args['gve']
	output = args['output']
	wavelength = args['wavelength']
	nbins = args['nbins']

	histdata = twothetahistogram(wavelength)
	histdata.setGVE(gve)
	histdata.buildHistogram(nbins)
	histdata.savetofile(output)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

