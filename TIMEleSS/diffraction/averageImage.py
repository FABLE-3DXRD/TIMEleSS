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

def averageImage(first,second,new):
	"""
	This function takes the average of two images and saves it in a new file. It is useful when one data file was lost for instance.
	Header parameters such as OmegaMin, OmegaMax, Omega, OmegaPos will be updated accordingly.
	
	first: first image (full path, with extension)
	second: second image (full path, with extension)
	new: new image name (full path, with extension)
	"""
	# Read image data from first image
	print("Reading " + first)
	im1 = fabio.edfimage.edfimage()
	im1.read(first)
	# Read image data from second image
	print("Reading " + second)
	im2 = fabio.edfimage.edfimage()
	im2.read(second)
	# Calculating average
	data1 = im1.data.astype('int32')
	data2 = im2.data.astype('int32')
	datanew = (data1+data2)/2
	# Removing data below 0
	datanew = datanew.clip(min=0)
	# Creating a header
	header1 = im1.header
	header2 = im2.header
	headernew =  im1.header.copy()
	# headers are not always defined. We hence use a "try" loop so it does not crash
	try:
		if (header1['OmegaMin'] != ""):
			omMin = min(float(header1['OmegaMin']),  float(header2['OmegaMin']))
			#print float(header1['OmegaMin']),  float(header2['OmegaMin']), omMin
			headernew['OmegaMin'] = "%.3f" % omMin
	except KeyError:
		omMin = None
	try:
		if (header1['OmegaMax'] != ""):
			omMax = max(float(header1['OmegaMax']),  float(header2['OmegaMax']))
			#print float(header1['OmegaMax']),  float(header2['OmegaMax']), omMax
			headernew['OmegaMax'] = "%.3f" % omMax
	except KeyError:
		omMax = None
	try:
		if (header1['Omega'] != ""):
			om = (float(header1['Omega']) +  float(header2['Omega']))/2
			#print float(header1['Omega']),  float(header2['Omega']), om
			headernew['Omega'] = "%.3f" % om
	except KeyError:
		om = None
	try:
		if (header1['OmegaPos'] != ""):
			omPos = (float(header1['OmegaPos']) +  float(header2['OmegaPos']))/2
			#print float(header1['Omega']),  float(header2['Omega']), om
			headernew['OmegaPos'] = "%.3f" % omPos
	except KeyError:
		omPos = None
	# Saving new data
	print("Saving new EDF with average data in " + new)
	im3 = fabio.edfimage.edfimage()
	im3.data = datanew.astype('uint32')
	im3.header = headernew
	im3.save(new)
	
	
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
	
	parser = MyParser(usage='%(prog)s file1 file2 file3', description="Takes the average between two EDF images\nHeader parameters such as OmegaMin, OmegaMax, Omega, OmegaPos will be updated accordingly.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required parameters
	parser.add_argument('files', type=str, nargs=3, help='Image 1, Image 2, New image name')
	
	args = vars(parser.parse_args())
	files = args['files']
	
	filename = files[0]
	if (not(os.path.isfile(filename))):
		print(("Error: file %s not found" % filename))
		sys.exit(2)
	filename = files[1]
	if (not(os.path.isfile(filename))):
		print(("Error: file %s not found" % filename))
		sys.exit(2)
	
	# Perform the substraction
	averageImage(files[0],files[1],files[2])




# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

