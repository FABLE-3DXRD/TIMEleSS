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

def cropGVE(grainfile, oldgvefile, newgvefile, verbose):

	grains = multigrainOutputParser.parse_GrainSpotter_log(grainfile)
	print "Parsed grains from %s" % grainfile
	print "Number of grains: %d" % len(grains)
	
	[peaksgve,idlist,header] = multigrainOutputParser.parseGVE(oldgvefile)

	print "Removing peaks which have been assigned to grains in %s" % grainfile

	for grain in grains:
		if (verbose):
			print "Looking at grain %s" % grain.getName()
		peaks = grain.getPeaks()
		for peak in peaks:
			index = idlist.index(peak.getPeakID())
			if (verbose):
				print "Trying to remove peak %d from the list of g-vectors" % peak.getPeakID()
			try:
				del idlist[index]
				del peaksgve[index]
			except:
				print "Failed removing g-vector ID %d which was found in grain %s" % (peak.getPeakID(), grain.getName())
				return

	multigrainOutputParser.saveGVE(peaksgve, header, newgvefile)


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
	
	parser = MyParser(usage='%(prog)s GSFile, oldGVE.gve newGVE.gve', description="Creates a new list of g-vectors, removing g-vectors which have already been assigned to grains by GrainSpotter\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('oldGVE',  help="G-vector file used for indexing (required)")
	parser.add_argument('newGVE',  help="Name of G-vector file to be created (required)")
	
	parser.add_argument('-v', '--verbose', required=False, help="Write out more details about what it does. Default is  Default is %(default)s", type=bool, default=False)

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	oldGVE = args['oldGVE']
	newGVE = args['newGVE']
	verbose = args['verbose']


	cropGVE(gsfile, oldGVE, newGVE, verbose)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


