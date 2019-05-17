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

from TIMEleSS.general import multigrainOutputParser

import numpy

from ImageD11 import transform
from ImageD11 import parameters

import matplotlib
import platform
if platform.system() == 'Linux':
	matplotlib.use('GTK3Agg')
import matplotlib.pyplot as plt
#import mplcursors


def plotFltGrains(gsfile, FLT, par):
	# Reading files
	imageD11Pars = parameters.read_par_file(par)
	grains = multigrainOutputParser.parse_GrainSpotter_log(gsfile)
	print ("Parsed grains from %s" % gsfile)
	ngrains =  len(grains)
	print ("Number of grains: %d" % ngrains)
	
	
	
	
	[peaksflt,idlist,header] = multigrainOutputParser.parseFLT(FLT)
	print ("Parsed peaks from %s" % FLT)
	print ("Number of peaks: %d" % len(peaksflt))
	
	# Locating the columns with detector positions in flt file
	headerarr = header.split()
	try:
		iSC = headerarr.index("sc") - 1
		iFC = headerarr.index("fc") - 1
	except:
		print ("Can not find sc and fc columns in %s" % FLT)
		return
	#print iSC, iFC

	while (1):
		txt = raw_input("Grain number (1-%d) ? " % ngrains)
		try:
			n = int(txt)-1
			if ((n<0) or (n>ngrains)):
				print ("Input should be between 1 and %d" % ngrains)
			else:
				grain = grains[n]
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
				(fpred, spred) = transform.compute_xyz_from_tth_eta(tthetaPred, etaPred, omegaPred, **imageD11Pars.parameters)

				plt.scatter(fmeasured, smeasured, s=60,  marker='o', facecolors='r', edgecolors='r')
				plt.scatter(fpred, spred, s=80,  marker='s', facecolors='none', edgecolors='b')
				plt.xlabel('f coordinate')
				plt.ylabel('s coordinate')
				plt.title("Grain %s" % (n+1))
				plt.show()
		except ValueError:
			print ("Input is wrong" )
	
	# Plot peaks from FLT, max intensity, sigs  sigf  sigo are sigmas calculated from the second moment
	# !! a +1 is added in the moment calculation to avoid 0 width peaks (returns sqrt(variant + 1))
	
	
	sys.exit(0)
		


	print "Detecting peaks which have been assigned to grains in %s" % gsfile
	basename, file_extension = os.path.splitext(newFLT)

	newpeaksflt = []
	for grain in grains:
		peaksgrain = []
		if (verbose):
			print "Looking at grain %s" % grain.getName()
		peaks = grain.getPeaks()
		for peak in peaks:
			if (verbose):
				print "Trying to get info for peak %d from the list of peaks" % peak.getPeakID()
			try:
				index = idlist.index(peak.getPeakID())
			except IndexError:
				print "Failed to locate peak ID %d which was found in grain %s" % (peak.getPeakID(), grain.getName())
				return
			newpeaksflt.append(peaksflt[index])
			peaksgrain.append(peaksflt[index])
		if (saveall):
			grainfltname = basename + "-" + grain.getName() + ".flt"
			multigrainOutputParser.saveFLT(peaksgrain, header, grainfltname)
		#print len(newpeaksflt)

	multigrainOutputParser.saveFLT(newpeaksflt, header, newFLT)
	

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


	plotFltGrains(gsfile, FLT, par)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


