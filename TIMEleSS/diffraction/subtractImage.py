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

def subtractImage(first,second,new):
	"""
	This function subtracts an image from a second one and saves it in a new file. It is useful for removing a background
	Headers from the original image a pushed to the new image
	
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
	print("Subtracting %s from %s" % (first,second))
	data1 = im1.data.astype('int32')
	data2 = im2.data.astype('int32')
	datanew = (data1-data2)
	# Removing data below 0
	datanew = datanew.clip(min=0)
	# Creating a header
	header1 = im1.header
	header2 = im2.header
	headernew =  im1.header.copy()
	print("Saving new EDF with subtracted data in " + new)
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
	
	parser = MyParser(usage='%(prog)s file1 file2 file3', description="Subtracts on EDF image from another\nHeader from the first image are pushed onto the resulting image.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required parameters
	parser.add_argument('files', type=str, nargs=3, help='Image, background, New image name')
	
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
	subtractImage(files[0],files[1],files[2])




# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

