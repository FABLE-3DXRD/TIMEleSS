#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python 2 to python 3 migration tools
from __future__ import absolute_import
from __future__ import print_function

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


"""
Functions to create an empty EDF image
    Simply substract the median from itself
"""

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path
# string module contains a number of functions that are useful for manipulating strings
import string
# Mathematical stuff (for data array and image processsing)
import numpy
import scipy
# Fabio, from ESRF fable package
import fabio
import fabio.edfimage

##########################################################################################################

def createEmptyImage(startfile, newname, omega=None):
	"""
	Creates an empty EDF image by substracting an image from itself
	
	startfile: file to start from
	newname: name of file to create
	omega: value for omega angle (can be None)
	
	"""

	# Read starting image
	print("Reading data from " + startfile)
	startIm = fabio.edfimage.edfimage()
	startIm.read(startfile)
	startdata = startIm.data.astype('float32')
	oldmean = startdata.mean()
	oldmax = startdata.max()
	oldmin = startdata.min()
	header = startIm.header
	# Removing median image from itself
	darkdata = startdata-startdata
	# Setting a new value for Omega, if needed
	if (omega != None):
		header['Omega'] = "%.3f" % omega
	# Save new data
	print("Saving empty image in " + newname)
	im = fabio.edfimage.edfimage()
	im.data = darkdata.astype('uint32')
	im.header = header
	im.save(newname)
    
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
    
	parser = MyParser(usage='%(prog)s startfile newname', description="Creation of an empty image by substracting an image from itself\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('startfile', help="EDF to start from", type=str)
	parser.add_argument('newname', help="name of EDF to be created", type=str)
	
	# Optionnal arguments
	parser.add_argument('-o', '--omega', required=False, help="Assign a value for Omega (optionnal). Default is %(default)s", type=float, default=None)

	args = vars(parser.parse_args())

	startfile = args['startfile']
	newname = args['newname']
	omega = args['omega']
    
	createEmptyImage(startfile, newname, omega)
    
    
# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

