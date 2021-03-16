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

Original version, 31/May/2013
"""

# Python 2 to python 3 migration tools
from __future__ import absolute_import
from __future__ import print_function
from six.moves import range

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path

# Fabio, from ESRF fable package
import fabio
import fabio.edfimage

# array operations
import numpy

#################################################################
#
# Specific subroutines
#
#################################################################

def meanFileSeries(stem,first,last,digits,ext,new,tif):
	"""
	This function calculates the mean for a series of images and saves it in a new file.
	
	stem: stem for in put file names 
	first: first image 
	last: last image
	digits: number of digits in file number
	ext: extension
	new: new image name (full path, with extension)
	tif: if true, save as Tiff
	"""
	
	formatfileedf = "%s%0"+str(digits)+"d.edf"
	
	# Opening the first file and creating arrays
	ifile = formatfileedf % (stem, first)
	print("Reading " + ifile)
	if (not(os.path.isfile(ifile))):
		print(("Error: file %s not found" % ifile))
		sys.exit(2)
	# Open the EDF image file
	imedf = fabio.open(ifile)
	# get data and use it as a starting point
	data = (numpy.copy(imedf.data)).astype('int64')
	# Read the rest
	for i in range(first+1,last+1):
		ifile = formatfileedf % (stem, i)
		print("Reading " + ifile)
		if (not(os.path.isfile(ifile))):
			print(("Error: file %s not found" % ifile))
			sys.exit(2)
		# Open the EDF image file
		imedf = fabio.open(ifile)
		# get data and use it as a starting point
		data += numpy.copy(imedf.data).astype('int64')
	# calculating mean
	data = data / (last-first+1)
	# Preparing a header
	headernew =  imedf.header.copy()
	# headers are not always defined. We hence use a "try" loop so it does not crash
	try:
		if (headernew['OmegaMin'] != ""):
			del headernew['OmegaMin']
	except KeyError:
		omMin = None
	try:
		if (headernew['OmegaMax'] != ""):
			del headernew['OmegaMax']
	except KeyError:
		omMax = None
	try:
		if (headernew['Omega'] != ""):
			del headernew['Omega']
	except KeyError:
		om = None
	try:
		if (headernew['OmegaPos'] != ""):
			del headernew['OmegaPos']
	except KeyError:
		omPos = None
	# clipping data to int32 (it should be ok, but should be done in a cleaner way)
	newdata = (numpy.copy(data)).astype('int32')
	if (tif):
		imtiff = fabio.tifimage.tifimage(newdata,headernew)
		imtiff.save(new)
		print("Mean image saved in " + new)
	else:
		im3 = fabio.edfimage.edfimage()
		im3.data = newdata
		im3.header = headernew
		im3.save(new)
		print("Mean image saved in " + new)
		
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
	
	parser = MyParser(usage='%(prog)s -n sterm -f first -l last -o newfilename', description="Takes the mean of multiple EDF images\nHeader parameters such as OmegaMin, OmegaMax, Omega, OmegaPos are reset.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required parameters
	parser.add_argument('-n', '--stem', required=True, help="Stem for images files (required)")
	parser.add_argument('-f', '--first', required=True, help="First image number (required)", type=int)
	parser.add_argument('-l', '--last', required=True, help="Last image number (required)", type=int)
	parser.add_argument('-o', '--output', required=True, help="Name of output file")
	
	# Optionnal arguments
	parser.add_argument('-d', '--ndigits', required=False, help="Number of digits for file number. Default is %(default)s", type=int, default=4)
	parser.add_argument('-e', '--extension', required=False, help="File extension. Default is %(default)s", type=str, default="edf")
	parser.add_argument('-t', '--tif', required=False, help="Save in tiff instead of EDF if True. Default is %(default)s", type=bool, default=False)
	
	# Parsing command line
	args = vars(parser.parse_args())
	
	stem = args['stem']
	first = args['first']
	last = args['last']
	digits = args['ndigits']
	ext = args['extension']
	output = args['output']
	tif =  args['tif']
	
	# Perform the substraction
	meanFileSeries(stem,first,last,digits,ext,output,tif)




# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

