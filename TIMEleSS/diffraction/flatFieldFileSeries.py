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

def flatFieldFileSeries(stem,first,last,blank,digits,ext,new,tif,scaling,damping):
	"""
	This function calculates the mean for a series of images and saves it in a new file.
	
	stem: stem for in put file names 
	first: first image 
	last: last image
	blank : blank image
	digits: number of digits in file number
	ext: extension
	new: new image name (full path, with extension)
	tif: if true, save as Tiff
	scaling : scaling factor after normalizing new data. 100000 is good. Use a lower value if intensities saturate. Use a higher value for larger intensities. 

	"""
	
	formatfileedf = "%s%0"+str(digits)+"d.edf"
	formatfileblank = "%s%0"+str(digits)+"d.edf"

	# Dividing all images by blank
	for i in range(first,last+1):
		#Load the blank image
		ibfile = formatfileblank % (blank, i)
		print("Reading " + ibfile)
		if (not(os.path.isfile(ibfile))):
			print(("Error: file %s not found" % ibfile))
			sys.exit(2)
		#open the blank image
		imblank = fabio.open(ibfile)
		#get blank data
		datablank = (numpy.copy(imblank.data)).astype('int32') + damping
		#search all values in blank that are zero and replace with one to allow division
		datablank[datablank<1] = 1
		
		#load the EDF image
		ifile = formatfileedf % (stem, i)
		print("Reading " + ifile)
		if (not(os.path.isfile(ifile))):
			print(("Error: file %s not found" % ifile))
			sys.exit(2)
		# Open the EDF image file
		imedf = fabio.open(ifile)
		# get data and convert to float for division
		data = (numpy.copy(imedf.data)).astype('float32') + damping
		max1 = numpy.amax(data)
		#divide first image by blank
		newdata = data / datablank
		# rescale the data
		max2 = numpy.amax(newdata)
		newdata = newdata * scaling
		# Preparing a header
		headernew =  imedf.getHeader().copy()
		# clipping data to int32 (it should be ok, but should be done in a cleaner way)
		newdata = (numpy.copy(newdata)).astype('int32')
		format = "%s%0" + str(digits) + "d.edf"
		image = format % (new,i)
		if (tif):
			imtiff = fabio.tifimage.tifimage(newdata,headernew)
			imtiff.save(image)
			print("New image saved in " + image)
		else:
			im3 = fabio.edfimage.edfimage()
			im3.setData(newdata)
			im3.setHeader(headernew)
			im3.save(image)
			print("New image saved in " + image)   
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
	
	parser = MyParser(usage='%(prog)s -n namestem -f first -l last -blk blankstem -o newfilename', description="Corrects a series of EDF images by a series of blank images.\nHeader parameters such as OmegaMin, OmegaMax, Omega, OmegaPos are reset.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required parameters
	parser.add_argument('-n', '--stem', required=True, help="Stem for images files (required)")
	parser.add_argument('-f', '--first', required=True, help="First image number (required)", type=int)
	parser.add_argument('-l', '--last', required=True, help="Last image number (required)", type=int)
	parser.add_argument('-blk', '--blank', required=True, help="Blank stem name (required)")
	parser.add_argument('-o', '--output', required=True, help="Name of output file")
	
	# Optionnal arguments
	parser.add_argument('-d', '--ndigits', required=False, help="Number of digits for file number. Default is %(default)s", type=int, default=4)
	parser.add_argument('-e', '--extension', required=False, help="File extension. Default is %(default)s", type=str, default="edf")
	parser.add_argument('-t', '--tif', required=False, help="Save in tiff instead of EDF if True. Default is %(default)s", type=bool, default=False)
	parser.add_argument('-s', '--scale', required=False, help="Scaling factor. Determines the average background intensity. Default is %(default)s", type=int, default=100)
	parser.add_argument('-dmp', '--damp', required=False, help="Increase the value to make the background less noisy. Default is %(default)s", type=int, default=20)

	# Parsing command line
	args = vars(parser.parse_args())
	
	stem = args['stem']
	first = args['first']
	last = args['last']
	blank = args['blank']
	digits = args['ndigits']
	ext = args['extension']
	output = args['output']
	tif =  args['tif']
	scaling = args['scale']
	damping = args['damp']
	
	# Perform the division
	flatFieldFileSeries(stem,first,last,blank,digits,ext,output,tif,scaling,damping)




# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
