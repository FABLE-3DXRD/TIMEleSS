#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This is part of the TIMEleSS tools
http://timeless.texture.rocks/

Copyright (C) M. Krug, Münster Univ. Germany
Copyright (C) S. Merkel, Univ. Lille France

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


# The purpose of this script is to extract the Euler angles from a .log file which was created during a GrainSpotter session. This script creates a list of Euler angles which can then be read by MTeX. The first column should be phi1, the second Phi and the third phi2.


def extract_euler_angles(inputf,outputf):
	file1 = inputf
	grains1 = multigrainOutputParser.parseGrains(file1)
	ngrains1 = len(grains1)
	print("Parsed %s, found %d grains" % (file1, len(grains1)))
	
	f = open(outputf,"w+")
	for grain in grains1:
		angles = grain.geteulerangles()
		f.write("%.2f %.2f %.2f\n" % (angles[0], angles[1], angles[2]))
	f.close()
	print("Euler angles saved in %s" % (outputf))
	return


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
	
	parser = MyParser(usage='%(prog)s [options] input.log', description="Reads an indexing log file and generates a set of Euler angles for plotting with MTex\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Arguments
	parser.add_argument('input', help="Path and file name of the indexing log file (required)")
	parser.add_argument('-o', '--output', required=False, help="Output file (.txt file). Default is %(default)s", default="euler_angles.txt")
	

	args = vars(parser.parse_args())

	inputf = args['input']
	outputf = args['output']
	extract_euler_angles(inputf,outputf)



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])



