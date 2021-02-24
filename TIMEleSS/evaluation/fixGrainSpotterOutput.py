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

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser



#################################################################
#
# Merges multiple GrainSpotter output files
#
#################################################################

def grainSpotterClean(inputfile, outputfile):
	"""
	Cleans output from GrainSpotter indexings. 
	In particular, removes grains with no assigned peaks that occur from time to time. 
	Generates a new output file with no such grain.
	
	Parameters:
	  inputfile -  GrainSpotter log file
	  outputfile - name of output file with bogus grains removed
	"""
	
	# Reading list of grains from all files
	grains = multigrainOutputParser.parseGrains(inputfile,False)
	print ("Parsed %s, found %d grains" % (inputfile, len(grains)))
	multigrainOutputParser.saveGrainSpotter(outputfile,grains)
	print ("Saved %d grains in %s" % (len(grains), outputfile))

#################################################################
#
# Main subroutines
#
#################################################################

def main(argv):
	"""
	Main subroutine
	"""
	
	parser = argparse.ArgumentParser(usage='%(prog)s [options] file', description="Cleans output from GrainSpotter indexings.\nIn particular, removes grains with no assigned peaks that occur from time to time.\nGenerates a new output file with no such grain.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	parser.add_argument('files', type=str, help='grainSpotter output file')
	
	parser.add_argument('-o', '--output', required=False, help="Name of output file. Default is %(default)s", default="clean.log")

	args = vars(parser.parse_args())

	filename = args['files']
	output = args['output']
	
	if (not(os.path.isfile(filename))):
		print(("Error: file %s not found" % filename))
		sys.exit(2)

	grainSpotterClean(filename, output)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
