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
from six.moves import range

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path

# string module contains a number of functions that are useful for manipulating strings
import string

# Fabio, from ESRF fable package, to deal with image formats
import fabio
import fabio.edfimage
import fabio.fabioimage
import fabio.tifimage

def edfToTiff(edffilename):
	basename, file_extension = os.path.splitext(edffilename)
	tiffilename = basename + ".tif"
	if (not(os.path.isfile(edffilename))):
		print(("Error: file %s not found" % fedf))
		sys.exit(2)
	# Open the EDF image file
	imedf = fabio.open(edffilename)
	# convert to tiff
	imtiff = fabio.tifimage.tifimage(imedf.data,imedf.header)
	# Save to tiff
	imtiff.write(tiffilename)
	print("Data saved in %s" % (tiffilename))


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
	
	parser = MyParser(usage='%(prog)s file', description="Converts an EDF to TIF\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('file', help="EDF file name (required)", type=str)

	args = vars(parser.parse_args())

	filename = args['file']

	edfToTiff(filename);


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

