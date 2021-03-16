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

# Maths stuff
import numpy

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser
from TIMEleSS.simulation.grainComparison import logit

# Grain comparison functions
from TIMEleSS.simulation import grainComparison


#################################################################
#
# Merges multiple GrainSpotter output files
#
#################################################################

def grainSpotterMerge(files, crystal_system, cutoff, outputstem,skipbogus):
	"""
	Function designed to merge output from multiple GrainSpotter indexing

	
	crystal_system can be one of the following values  
		1: Triclinic
		2: Monoclinic
		3: Orthorhombic
		4: Tetragonal
		5: Trigonal
		6: Hexagonal
		7: Cubic
	
	Parameters:
	  files - list of GrainSpotter log files
	  crystal_system - see above
	  outputstem - stem for output file for the grain comparison
	  cutoff - mis-orientation below which the two grains are considered identical, in degrees
	  skipbogus - if set to true, skip bogus grains in GS output (grains with 0 peaks)
	"""
	
	filename1 = "%s-%s" % (outputstem , "log.dat")
	logfile = open(filename1,'w')
	
	# Reading list of grains from all files
	grainLists = []
	for filename in files:
		grains = multigrainOutputParser.parseGrains(filename,skipbogus)
		grainLists.append(grains)
		logit(logfile, "Parsed %s, found %d grains" % (filename, len(grains)))
	
	logit(logfile, "\nMisorientation below which the two grains are considered identical, in degrees: %.1f\n" % cutoff)
	
	# Looking for unique grains
	mergeGrains = []
	for grains in grainLists:
		mergeGrains += grains
	logit(logfile, "Looking for unique grains")
	grainsUnique = grainComparison.removeDoubleGrains(mergeGrains, crystal_system, cutoff, logfile)
	
	logit(logfile, "")
	
	# Getting some stats for each for those grains
	logit(logfile, "Indexing statistics")
	nIndexed = []
	for i in range(0,len(grainsUnique)):
		grain1 = grainsUnique[i]
		n = 0
		for grain2 in mergeGrains:
			U1 = (grain1).getU()
			U2 = (grain2).getU()
			if (grainComparison.matchGrains(U1,U2,crystal_system,cutoff)):
				# We have a match. Keep the grain with the largest number of peaks
				n += 1
				if (grain2.getNPeaks() > grain1.getNPeaks()):
					grainsUnique[i] = grain2
		nIndexed.append(n)
	nn = grainComparison.unique(nIndexed)
	nn.sort(reverse=True)
	for i in nn:
		nGnTimes = sum(1 for j in nIndexed if i == j)
		logit(logfile,"- %d grains were indexed %d times" % (nGnTimes,i))
	
	# Saving new files (in GrainSpotter format), based on the number of time each grain was indexed
	logit(logfile, "\nSaving unique grains")
	filename = ("%s-grains.log" % (outputstem))
	multigrainOutputParser.saveGrainSpotter(filename,grainsUnique)
	logit(logfile,"- all %d unique grains saved in %s" % (len(grainsUnique), filename))
	for i in nn:
		filename = ("%s-grains-%d.log" % (outputstem, i))
		# Looking for grains that have been index i times
		indexlist = [j for j,x in enumerate(nIndexed) if x==i]
		# Save them
		tosave = []
		for j in range(0,len(indexlist)):
			tosave.append(grainsUnique[j])
		multigrainOutputParser.saveGrainSpotter(filename,tosave)
		logit(logfile,"- %d grains indexed %d times saved in %s" % (len(tosave),i, filename))
	
	logfile.close()


#################################################################
#
# Main subroutines
#
#################################################################

def main(argv):
	"""
	Main subroutine
	"""
	
	parser = argparse.ArgumentParser(usage='%(prog)s [options] file1 file2 ... fileN', description="Merges grains from multiple GrainSpotter indexings\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	parser.add_argument('files', type=str, nargs='+', help='grainSpotter output files')
	
	parser.add_argument('-c', '--crystal_system', type=int, choices=range(1, 8), required=True, help="""Crystal system. Can be one of the following 
    1: Triclinic
    2: Monoclinic
    3: Orthorhombic
    4: Tetragonal
    5: Trigonal
    6: Hexagonal
    7: Cubic
""")
	
	parser.add_argument('-o', '--output_stem', required=False, help="Stem for output files. Default is %(default)s", default="merge")
	
	parser.add_argument('-m', '--misorientation', required=False, help="Misorientation below which two grains are considered identical, in degrees. Default is %(default)s", default=2.0, type=float)
	
	parser.add_argument('-s', '--skipbogus', required=False, help="Skip bogus grains in GrainSpotter output. Default is  Default is %(default)s", type=bool, default=False)

	args = vars(parser.parse_args())

	files = args['files']
	crystal_system = args['crystal_system']
	stem = args['output_stem']
	cutoff = args['misorientation']
	skipbogus = args['skipbogus']
	
	for filename in files:
		if (not(os.path.isfile(filename))):
			print ("Error: file %s not found" % filename)
			sys.exit(2)

	grainSpotterMerge(files, crystal_system, cutoff, stem, skipbogus)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
