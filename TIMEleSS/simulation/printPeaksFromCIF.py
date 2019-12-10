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

# TIMEleSS CIF file utilities
from TIMEleSS.general import cifTools

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path
from argparse import RawTextHelpFormatter

def printPeaksFromCIF(ciffile, ttheta_min,  ttheta_max, wavelength, minI = -1.0, normI = False, output=None):
	"""
	Prints a list of reflections for single-crystal diffraction based on a cif file
	
	Returns:
		an array in which eack line holds
			- h, k, l
			- ds = 1/d (in anstroms)
			- intensity for single-crystal diffraction
			- 2theta (in degrees)
	
	Intensities include the effect of structure factor and Lorentz correction
	
	Params:
	- cif file
	- ttheta_min (in degrees)
	- ttheta_max (in degrees)
	- wavelength (in angstroms)
	- normI: if set to True, intensities are normalized to a maximum of 100
	- minI: remove peaks with an intensity <= that minI. Default is -1.0 (returns everything)
	- output: name if output file. Prints out to screen if not set.
	
	Created: 12/2019, S. Merkel, Univ. Lille, France
	Inspired from fitAllB/reject.py
	Heavily adatped to account for Lorentz correction, normalize intensities, and filter peaks
	"""
	hkls = cifTools.peaksFromCIF(ciffile, ttheta_min,  ttheta_max, wavelength, minI, normI)
	string = "# Peaks for CIF file %s\n" % ciffile
	string += "# Wavelength: %.5f angstroms\n" % wavelength
	string += "# 2theta between %.3f and %.3f degrees\n" % (ttheta_min,  ttheta_max)
	string += "# h k l intensity ds 2theta\n"
	for hkl in hkls:
		string += "% d % d % d  %5.1f  %.6f  %6.3f\n" % (hkl[0], hkl[1], hkl[2], hkl[4], hkl[3], hkl[5])
		
	if output is None:
		print string
	else:
		f= open(output,"w+")
		f.write(string)
		f.close()


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
	
	parser = MyParser(usage='%(prog)s [options] input.cif', description="""Calculate a list of peaks and intensities for single-crystal diffraction based on a CIF file

Example:
	%(prog)s -m 4 -M 15 -w 0.3738 -n True -c 5.0 mycif.cif

This is part of the TIMEleSS project\nhttp://timeless.texture.rocks
""", formatter_class=RawTextHelpFormatter)
	
	# Required arguments
	parser.add_argument('ciffile', help="Path and name for CIF file")
	parser.add_argument('-m', '--ttheta_min', required=True, help="Minimum 2 theta (degrees)", type=float)
	parser.add_argument('-M', '--ttheta_max', required=True, help="Maximum 2 theta (degrees)", type=float)
	parser.add_argument('-w', '--wavelength', required=True, help="Wavelength (anstroms)", type=float)
	
	# Optionnal argument
	parser.add_argument('-c', '--minI', required=False, help="Filter peaks below a cut-off intensity. Default is %(default)s (no filter)", default=-1.0, type=float)
	parser.add_argument('-n', '--normI', required=False, help="If set to True, intensities are normalized to a maximum of 100. Default is %(default)s (no filter)", default=False, type=bool)
	parser.add_argument('-o', '--output', required=False, help="If set, saves result to file name. Otherwise, prints results out to screen. Default is %(default)s (no filter)", default=None, type=str)
	
	# Parse arguments
	args = vars(parser.parse_args())
	ciffile = args['ciffile']
	ttheta_min = args['ttheta_min']
	ttheta_max = args['ttheta_max']
	wavelength = args['wavelength']
	minI = args['minI']
	normI = args['normI']
	output = args['output']
	
	printPeaksFromCIF(ciffile, ttheta_min,  ttheta_max, wavelength, minI = minI, normI = normI, output=output)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
	main(sys.argv[1:])

