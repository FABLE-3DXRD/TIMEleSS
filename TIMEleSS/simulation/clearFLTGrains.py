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

def cropFLT(grainfile, oldfltfile, newfltfile, verbose):

	grains = multigrainOutputParser.parse_GrainSpotter_log(grainfile)
	print("Parsed grains from %s" % grainfile)
	print("Number of grains: %d" % len(grains))
	
	[peaksflt,idlist,header] = multigrainOutputParser.parseFLT(oldfltfile)

	print("Removing peaks which have been assigned to grains in %s" % grainfile)

	for grain in grains:
		if (verbose):
			print("Looking at grain %s" % grain.getName())
		peaks = grain.getPeaks()
		# Sometimes, GrainSpotter indexes the same peak twice. We need to remove those double indexings
		peakid = []
		for peak in peaks:
			peakid.append(peak.getPeakID())
		peakid = list(set(peakid)) # remove duplicates, may loose the ordering but we do not care
		# Removing assign peaks from the list of peaks
		for thisid in peakid:
			index = idlist.index(thisid)
			if (verbose):
				print("Trying to remove peak %d from the list of peaks" % thisid)
			try:
				del idlist[index]
				del peaksflt[index]
			except IndexError:
				print("Failed removing peak ID %d which was found in grain %s" % (thisid, grain.getName()))
				return
	# print len(peaksflt)

	multigrainOutputParser.saveFLT(peaksflt, header, newfltfile)


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
	
	parser = MyParser(usage='%(prog)s GSFile, oldFLT.flt newFLT.flt', description="Creates a new list of peaks in FLT format, removing peaks which have already been assigned to grains by GrainSpotter\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('oldFLT',  help="FLT file used to generate g-vectors for indexing (required)")
	parser.add_argument('newFLT',  help="Name of FLT file to be created (required)")
	
	parser.add_argument('-v', '--verbose', required=False, help="Write out more details about what it does. Default is  Default is %(default)s", type=bool, default=False)

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	oldFLT = args['oldFLT']
	newFLT = args['newFLT']
	verbose = args['verbose']


	cropFLT(gsfile, oldFLT, newFLT, verbose)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


