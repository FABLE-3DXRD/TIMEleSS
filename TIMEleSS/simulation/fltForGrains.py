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

from TIMEleSS.general import multigrainOutputParser

def fltGrains(gsfile, oldFLT, newFLT, saveall, verbose=False):

	grains = multigrainOutputParser.parse_GrainSpotter_log(gsfile)
	print("Parsed grains from %s" % gsfile)
	print("Number of grains: %d" % len(grains))
	
	[peaksflt,idlist,header] = multigrainOutputParser.parseFLT(oldFLT)

	print("Detecting peaks which have been assigned to grains in %s" % gsfile)
	basename, file_extension = os.path.splitext(newFLT)

	newpeaksflt = []
	for grain in grains:
		peaksgrain = []
		if (verbose):
			print("Looking at grain %s" % grain.getName())
		peaks = grain.getPeaks()
		for peak in peaks:
			if (verbose):
				print("Trying to get info for peak %d from the list of peaks" % peak.getPeakID())
			try:
				index = idlist.index(peak.getPeakID())
			except IndexError:
				print("Failed to locate peak ID %d which was found in grain %s" % (peak.getPeakID(), grain.getName()))
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
	
	parser = MyParser(usage='%(prog)s GSFile.log oldFLT.flt newFLT.flt', description="Creates a new list of peaks in FLT format, including only peaks which have already been assigned to grains by GrainSpotter\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('oldFLT',  help="FLT file used to generate g-vectors for indexing (required)")
	parser.add_argument('newFLT',  help="Name of FLT file to be created (required)")
	
	parser.add_argument('-a', '--saveall', required=False, help="This option will create a different file for each grain in the Grain Spotter output file. File naming will be newFLT-GrainXXX.flt. Default is  Default is %(default)s", type=bool, default=False)

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	oldFLT = args['oldFLT']
	newFLT = args['newFLT']
	saveall = args['saveall']


	fltGrains(gsfile, oldFLT, newFLT, saveall)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


