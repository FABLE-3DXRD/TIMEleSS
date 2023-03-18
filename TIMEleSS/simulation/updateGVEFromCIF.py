#!/usr/bin/env python
# -*- coding: utf-8 -*

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

# TIMEleSS CIF file utilities
from TIMEleSS.general import cifTools
# Parsing of GVE files
from TIMEleSS.general import multigrainOutputParser

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path
from argparse import RawTextHelpFormatter

def setGVEPeaksFromCIF(ciffile, gve_file_input, gve_file_output, ttheta_min,  ttheta_max, wavelength, minI = -1.0):

	"""
	Sets the list of peaks in a GVE file, starting at line 35 or so, based on a cif file
	
	Returns:
	
	
	Params:
	- cif file
	- input GVE file
	- output GVE file
	- ttheta_min (in degrees)
	- ttheta_max (in degrees)
	- wavelength (in angstroms)
	- minI: remove peaks with an intensity <= that minI. Default is -1.0 (returns everything)
	
	Created: 13/2023, S. Merkel, Univ. Lille, France
	"""
	
	# Get cell parameters
	
	cell_pars = cifTools.unit_cell_from_Cif(ciffile)
	
	# Generating list of peaks, with ds, h, k, and l
	hkls = cifTools.peaksFromCIF(ciffile, ttheta_min,  ttheta_max, wavelength, minI, True)
	peakstring = ""
	if (len(hkls) == 0):
		print("\nERROR!\nNot a single diffraction peaks from this phase between %.2f and %.2f degrees with a wavelength of %.5f" % (ttheta_min, ttheta_max, wavelength) )
		print("Check your 2theta range and try again!\n")
		sys.exit(2)
	else:
		print("\n%d diffraction peaks between %.2f and %.2f degrees based on %s" % (len(hkls), ttheta_min, ttheta_max, ciffile) )
		print("Saving new GVE file as %s\n" % gve_file_output)
		
	for hkl in hkls:
		peakstring += "%.6f % d % d % d\n" % (hkl[3], hkl[0], hkl[1], hkl[2])
	
	# Parsing the old GVE file
	[peaksgve,idlist,header] = multigrainOutputParser.parseGVE(gve_file_input)
	
	# Header should be changed with the new list of peaks
	# First line are cell parameters
	# Lines of comments should be kept, except unit cell information which is updated
	# Lines with ds, h, k, l should be changed
	i = 0

	donewithpeaks = False
	headers = header.split('\n')
	for line in headers:
		if (line != ""):
			if (i == 0):
				line1 = ' '.join([str(n) for n in cell_pars])
				headernew = line1 + "\n"
			elif (line[0] == "#"):
				test = line.split()
				if (test[1] == "cell__a"):
					headernew += "# cell__a = %f" % cell_pars[0]  + "\n"
				elif (test[1] == "cell__b"):
					headernew += "# cell__b = %f" % cell_pars[1]  + "\n"
				elif (test[1] == "cell__c"):
					headernew += "# cell__c = %f" % cell_pars[2]  + "\n"
				elif (test[1] == "cell_alpha"):
					headernew += "# cell_alpha = %f" % cell_pars[3]  + "\n"
				elif (test[1] == "cell_beta"):
					headernew += "# cell_beta = %f" % cell_pars[4]  + "\n"
				elif (test[1] == "cell_gamma"):
					headernew += "# cell_gamma = %f" % cell_pars[5]  + "\n"
				elif (test[1] == "cell_lattice_[P,A,B,C,I,F,R]"):
					headernew += "# cell_lattice_[P,A,B,C,I,F,R] = %s" % cell_pars[6]  + "\n"
				else:
					headernew += headers[i]  + "\n"
			elif (donewithpeaks == False):
				headernew += peakstring 
				donewithpeaks = True
		i += 1
	# print (headernew)
	
	# Save the new GVE file
	multigrainOutputParser.saveGVE(peaksgve, headernew, gve_file_output)


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
	
	parser = MyParser(usage='%(prog)s [options] input.cif inputGVE outputGVE', description="""Update the list of peaks to index inside the header of a GVE file based on predicted peak list from a CIF file

Example:
	%(prog)s -m 4 -M 15 -w 0.3738 -c 5.0 mycif.cif input.gve output.gve

This is part of the TIMEleSS project\nhttp://timeless.texture.rocks
""", formatter_class=RawTextHelpFormatter)
	
	# Required arguments
	parser.add_argument('ciffile', help="Path and name for CIF file")
	parser.add_argument('inputGVE', help="Path and name for the GVE input file")
	parser.add_argument('outputGVE', help="Path and name for the GVE output file")
	parser.add_argument('-m', '--ttheta_min', required=True, help="Minimum 2 theta (degrees)", type=float)
	parser.add_argument('-M', '--ttheta_max', required=True, help="Maximum 2 theta (degrees)", type=float)
	parser.add_argument('-w', '--wavelength', required=True, help="Wavelength (anstroms)", type=float)
	
	# Optionnal argument
	parser.add_argument('-c', '--minI', required=False, help="Filter peaks below a cut-off intensity. Default is %(default)s (no filter). Intensities are normalized so that the most intense peak is 100 (see results of timelessPeaksFromCIF for details)", default=-1.0, type=float)
	
	# Parse arguments
	args = vars(parser.parse_args())
	ciffile = args['ciffile']
	gve_file_input = args['inputGVE']
	gve_file_output = args['outputGVE']
	ttheta_min = args['ttheta_min']
	ttheta_max = args['ttheta_max']
	wavelength = args['wavelength']
	minI = args['minI']
	
	setGVEPeaksFromCIF(ciffile, gve_file_input, gve_file_output, ttheta_min,  ttheta_max, wavelength, minI)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
	main(sys.argv[1:])
