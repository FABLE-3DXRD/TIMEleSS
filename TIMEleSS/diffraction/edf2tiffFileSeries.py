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

def edfToTiffFileSeries(tiffimagepath, edfimagepath, stem, fromm, to,digits,dounderscore):

	formatfiletif = "%s%0"+str(digits)+"d.tif"
	formatfileedf = "%s%0"+str(digits)+"d.edf"
	totalsize = 0
	ndata = 0
	if (dounderscore):
		tifstem = stem[:-1] + "_"
	else:
		tifstem = stem
	edfstem = stem
	
	for i in range(fromm,to+1):
		ifile = formatfileedf % (edfstem, i)
		fedf = os.path.join(edfimagepath, ifile)
		if (not(os.path.isfile(fedf))):
			print(("Error: file %s not found" % fedf))
			sys.exit(2)
		# Open the EDF image file
		imedf = fabio.open(fedf)
		# convert to tiff
		imtiff = fabio.tifimage.tifimage(imedf.data,imedf.header)
		# Save to tiff
		ifile = formatfiletif % (tifstem, i)
		ftif = os.path.join(tiffimagepath, ifile)
		imtiff.write(ftif)
		print("Data saved in %s" % (ifile))
		totalsize += imedf.data.nbytes
		ndata += 1
	print("Created ", ndata, " TIF files")
	print("Total size: ", totalsize/1048576., " megabytes, ", totalsize/(1073741824.), " gigabytes")



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
	
	parser = MyParser(usage='%(prog)s -f from -t to -n stem  [OPTIONS]', description="Converts a collection of EDF files to TIFF files\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('-f', '--from', required=True, help="First image number (required)", type=int)
	parser.add_argument('-t', '--to', required=True, help="Last image number (required)", type=int)
	parser.add_argument('-n', '--stem', required=True, help="Stem for images files (required)")
	
	# Optionnal arguments
	parser.add_argument('-p', '--tiffimagepath', required=False, help="Path to tiff images. Default is %(default)s", default="./")
	parser.add_argument('-e', '--edfimagepath', required=False, help="Path in which to save edf images. Default is %(default)s", default="./")
	parser.add_argument('-d', '--ndigits', required=False, help="Number of digits for file number. Default is %(default)s", type=int, default=4)
	parser.add_argument('-u', '--dounderscore', required=False, help="Replace last character of file stem with an underscore. Can be True or False. Default is %(default)s", type=bool, default=False)

	args = vars(parser.parse_args())

	tiffimagepath = args['tiffimagepath']
	edfimagepath = args['edfimagepath']
	stem = args['stem']
	fromm = args['from']
	to = args['to']
	digits = args['ndigits']
	dounderscore = args['dounderscore']

	edfToTiffFileSeries(tiffimagepath, edfimagepath, stem, fromm, to, digits, dounderscore);


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])

