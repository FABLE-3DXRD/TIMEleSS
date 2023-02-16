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

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path
# What would you do without numpy?
import numpy
# Fabio, from ESRF fable package, to deal with image formats
import fabio
import fabio.edfimage
# hdf5 parsing utilities
import h5py


"""

Converts HDF5 file created by Eiger detector on ID27 at ESRF into a series of EDF files for cleaning and peak searching

Returns 
	Nothing but saves many EDF files

Parameters
	hdffile: name and path to h5 file to be converted
	edfimagepath: path in which to save EDF images
	stem: stem for EDF file names
	fromm: starting omega angle (degrees)
	to: ending omega angle (degrees)
	step: omega step (degrees)
	digits: number of digits for EDF file names (4 is good)
	dounderscore: replace last character of stem with an underscore (obscure option, left for historical / compatibility reasons)
	maxthreshold: pixels with intensity above this threshold are set to zero intensity. Useful to get rid of gaps and dead pixels. A value of 4e6 is recommend with current settings, as this code is being written. Nothing happening if set to None

History:
	02/2023: S. Merkel, original code
	
"""
def ID27_hdf5_To_Edf(hdffile, edfimagepath, stem, fromm, to, step, digits,dounderscore,maxthreshold=None):

	f = h5py.File(hdffile, 'r')
	results = f.get('/entry_0000/measurement/data')
	nframesDataset = f.get('/entry_0000/instrument/eiger/acquisition/nb_frames')
	nframes = int(numpy.array(nframesDataset))
	dataarray = numpy.array(results)
	print("Found %d frames of [%d,%d] pixels in %s" % (dataarray.shape[0], dataarray.shape[1], dataarray.shape[2], hdffile))
	# Removing anything above 100000
	if (maxthreshold != None):
		idx=(dataarray>maxthreshold)
		dataarray[idx] = 0

	omegarange = to-fromm
	nsteps = int(omegarange/step)
	if (nsteps != nframes):
		print("ERROR\nOmega range from %.2f to %.2f with %.2f steps -> I am expecting %d frames\nI found %d frames.\nThose numbers should have been identical\nExiting\n" % (fromm, to, step, nsteps, nframes))
		return 0
	print("Saving those frames as %d edf files with omega from %.2f to %.2f with %.2f steps." % (nsteps, fromm, to, step))
	
	formatfileedf = "%s%0"+str(digits)+"d.edf"
	totalsize = 0
	ndata = 0
	if (dounderscore):
		edfstem = stem[:-1] + "_"
	else:
		edfstem = stem

	header = {}
	for i in range(0,nsteps):
		# Calculate omega
		omega = fromm + (i+0.5)*step
		# Create a couple of headers
		header["description"] = "Converted from hdf5 from ESRF-ID27 with the TIMEleSS tools at https://github.com/FABLE-3DXRD/TIMEleSS"
		header["Omega"] = "%.3f" % omega
		header["OmegaStep"] = "%.3f" % step
		# Save to edf
		edfimage =  fabio.edfimage.edfimage(dataarray[i,:,:],header)
		ifile = formatfileedf % (edfstem, i)
		fedf = os.path.join(edfimagepath, ifile)
		edfimage.write(fedf)
		print("Data saved in %s" % (ifile))
		totalsize += dataarray[i,:,:].nbytes
		ndata += 1
	print("Created %d EDF files" % ndata)
	print("Total size: %.1f megabytes, %.1f gigabytes" % (totalsize/1048576., totalsize/(1073741824.)) )


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
	
	parser = MyParser(usage='%(prog)s -i test.h5 -f from -t to -s step -n stem [OPTIONS]', description="Creates a list of EDF files based a h5 file from the eider detector at ID27 at ESRF\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('-i', '--input', required=True, help="h5 data file (required)", type=str)
	parser.add_argument('-f', '--from', required=True, help="Start for omega scan (in degrees, required)", type=float)
	parser.add_argument('-t', '--to', required=True, help="End for omega scan (in degrees, required)", type=float)
	parser.add_argument('-s', '--step', required=True, help="Omega step (in degrees, required)", type=float)
	parser.add_argument('-n', '--stem', required=True, help="Stem for saving EDF files (required)")
	
	# Optionnal arguments
	parser.add_argument('-e', '--edfimagepath', required=False, help="Path in which to save edf images. Default is %(default)s", default="./")
	parser.add_argument('-d', '--ndigits', required=False, help="Number of digits for file number. Default is %(default)s", type=int, default=4)
	parser.add_argument('-u', '--dounderscore', required=False, help="Replace last character of file stem with an underscore. Can be True or False. Default is %(default)s", type=bool, default=False)
	parser.add_argument('-M', '--Max', required=False, help="Maximum value threshold. Anyting above this value will be set to 0, which is useful to get rid of gaps or dead pixels. Send a float. Strongly recommended but default is %(default)s", type=float, default=None)


	args = vars(parser.parse_args())

	edfimagepath = args['edfimagepath']
	stem = args['stem']
	fromm = args['from']
	to = args['to']
	step = args['step']
	inputfile = args['input']
	digits = args['ndigits']
	dounderscore = args['dounderscore']
	maxthreshold = args['Max']

	ID27_hdf5_To_Edf(inputfile, edfimagepath, stem, fromm, to, step, digits,dounderscore, maxthreshold)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
	main(sys.argv[1:])

