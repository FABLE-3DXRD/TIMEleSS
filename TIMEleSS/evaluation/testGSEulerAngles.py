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


# System functions, to manipulate command line arguments
import sys
import argparse
import os.path


# Maths stuff
import numpy
import math
import numpy.linalg

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser


# The purpose of this script is to extract the Euler angles from a .log file which was created during a GrainSpotter session. We calculate a U matrix from the U angles and check against the U matrix in the log file to make sure all is consistent

def check_euler_angles(inputf):
	file1 = inputf
	grains1 = multigrainOutputParser.parseGrains(file1)
	ngrains1 = len(grains1)
	print "Parsed %s, found %d grains" % (file1, len(grains1))
	unity = numpy.identity(3)
	print "Comparing Euler angles and U matrices. Making sure they match."
	for grain in grains1:
		angles = grain.geteulerangles()
		U = grain.getU()
		cphi1 = math.cos(math.radians(angles[0]))
		sphi1 = math.sin(math.radians(angles[0]))
		cPhi = math.cos(math.radians(angles[1]))
		sPhi = math.sin(math.radians(angles[1]))
		cphi2 = math.cos(math.radians(angles[2]))
		sphi2 = math.sin(math.radians(angles[2]))
		U2 = numpy.matrix([[cphi1*cphi2-sphi1*sphi2*cPhi, -cphi1*sphi2-sphi1*cphi2*cPhi, sphi1*sPhi], [sphi1*cphi2+cphi1*sphi2*cPhi, -sphi1*sphi2+cphi1*cphi2*cPhi, -cphi1*sPhi], [sphi2*sPhi, cphi2*sPhi, cPhi]])
		C = U.dot(numpy.linalg.inv(U2))
		if (not numpy.allclose(C,unity)):
			print "Problem with grain %s" % grain.getName()
			print C
	print "Done."
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
	
	parser = MyParser(usage='%(prog)s ', description="Reads an indexing log file from GrainSpotter and make sure that the this of Euler angles is in agreement with the U matrices\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Arguments
	parser.add_argument('input', help="Path and file name of the indexing log file (required)")
	

	args = vars(parser.parse_args())

	inputf = args['input']
	check_euler_angles(inputf)



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

