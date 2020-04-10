#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This is part of the TIMEleSS tools
http://timeless.texture.rocks/

Copyright (C) M. Krug, Münster Univ. Germany
Copyright (C) S. Merkel, Univ. Lille France

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


# Maths stuff
import numpy

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser


def normalizedAngle360(angle):
	"""
	Brings an angle back to [0;360)
	"""
	return angle - (numpy.floor((angle + 180)/360))*360+180.;           # [0;360):

def normalizedAngle180(angle):
	"""
	Brings an angle back to [-180;180)
	"""
	return angle - (numpy.floor((angle + 180)/360))*360;           # [-180;180):

def gs_indexing_statistics(logfile, gve, gsinput, wavelength):
	"""
	Checks a grainspotter indexing performance
	Send the final GrainSpotter log, the list of g-vectors, the GS input file (with the loosest conditions), and the wavelength
	"""
	grains = multigrainOutputParser.parseGrains(logfile)
	print "Parsed %s, found %d grains" % (logfile, len(grains))
	
	# Load .gve file from ImageD11 :
	[peaksgve,idlist,header] = multigrainOutputParser.parseGVE(gve) 
	# Extracting list of g-vectors from the header
	peakssample = []
	recordpeaks = False
	#print header
	for line in header.split("\n"):
		if ((line.strip() == "#  gx  gy  gz  xc  yc  ds  eta  omega  spot3d_id  xl  yl  zl")):
			recordpeaks = False
		if recordpeaks:
			tt = line.split()
			ds = float(tt[0])
			h = int(tt[1])
			k = int(tt[2])
			l = int(tt[3])
			peakssample.append([ds,h,k,l])
			#print h, k, l
		if ((line.strip() == "# ds h k l")):
			recordpeaks = True
		
	
	# Load the grain spotter input file
	gsinput =  multigrainOutputParser.parseGSInput(gsinput) 
	
	# Try to see if all g-vectors in the indexed grains are in the gve
	nindexed = 0
	ngrains = len(grains)
	for grain in grains : 
		nindexed += grain.getNPeaks()
	
	print "\nGrainSpotter results"
	print "\t%d grains indexed" % (len(grains))
	print "\t%d g-vectors indexed" % (nindexed)
	tt = 1.0*nindexed/ngrains
	print "\t%.1f g-vectors per grain in average" % (tt)
	
	# Matching conditions in angle ranges
	ds = []
	eta = []
	omega = []
	gsinput["dsranges"] = []
	for tthrange in gsinput["tthranges"]:
		ds0 = 2.*numpy.sin(numpy.radians(tthrange[0]/2.))/(wavelength)
		ds1 = 2.*numpy.sin(numpy.radians(tthrange[1]/2.))/(wavelength)
		gsinput["dsranges"].append([ds0,ds1])
	
	#print gsinput
		
	for peak in peaksgve:
		thisds = float(peak['ds'])
		thiseta = normalizedAngle360(float(peak['eta'])) # In GrainSpotter, eta is in [0;360]
		thisomega = normalizedAngle180(float(peak['omega'])) # In GrainSpotter, omega is in [-180;180]
		test1 = 0
		test2 = 0
		test3 = 0
		for dsrange in gsinput["dsranges"]:
			if ((thisds >= dsrange[0]) and (thisds <= dsrange[1])):
				test1 = 1
		for etarange in gsinput["etaranges"]:
			if ((thiseta >= etarange[0]) and (thiseta <= etarange[1])):
				test2 = 1
			#else:
			#	print "Not for eta %.1f < %.1f < %.1f" % (etarange[0],thiseta,etarange[1])
		for omegarange in gsinput["omegaranges"]:
			if ((thisomega >= omegarange[0]) and (thisomega <= omegarange[1])):
				test3 = 1
			#else:
			#	print "Not for omega %.1f < %.1f < %.1f" % (omegarange[0],thisomega,omegarange[1])
		if (test1*test2*test3 == 1):
			ds.append(float(peak['ds']))
			eta.append(float(peak['eta']))
			omega.append(float(peak['omega']))
	print "\nPeaks"
	print "\t%d g-vectors in GVE file" % (len(peaksgve))
	print "\t%d g-vectors within eta, omega, and 2theta ranges" % (len(ds))

	# Counting peak, within 2 theta range, and that can be assigned to the sample
	tttol = gsinput["sigma_tth"]*gsinput["nsigmas"]
	dsmin = []
	dsmax = []
	#print tttol
	for samplepeak in peakssample:
		thisds = samplepeak[0]
		#print thisds
		tt = 2.*numpy.degrees(numpy.arcsin(wavelength*thisds/2.))
		#print 2.*numpy.sin(numpy.radians((tt-tttol)/2.))/(wavelength)
		#print 2.*numpy.sin(numpy.radians((tt+tttol)/2.))/(wavelength)
		dsmin.append(2.*numpy.sin(numpy.radians((tt-tttol)/2.))/(wavelength))
		dsmax.append(2.*numpy.sin(numpy.radians((tt+tttol)/2.))/(wavelength))
	
	nassigned = 0
	for thisds in ds:
		append = 0
		for i in range(0,len(dsmin)):
			if ((thisds <= dsmax[i]) and (thisds >= dsmin[i])):
				append = 1
		nassigned += append
	print "\t%d g-vectors assigned to sample within these ranges" % (nassigned)
	
	print "\nIndexing performance"
	print "\tOut of %d possible g-vectors, %d have been assigned to %d grains" % (nassigned, nindexed, len(grains))
	tt = nassigned-nindexed
	print "\t%d remaining g-vectors" % (tt)
	tt = 100.*nindexed/nassigned
	print "\t%.1f percents of g-vectors indexed" % (tt)
	print 
	
	
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
	
	parser = MyParser(usage='%(prog)s -i gsinput -l logfilestem.log -g gve.gve -w wavelength', description="Reads a GrainSpotter input file, indexing log file, experimental g-vectors from a GVE file, and pulls out indexing statistics.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Arguments
	parser.add_argument('-i','--inputfile', help="Input file name for GrainSpotter. Use the file with the looser conditions if you ran multiple steps of GrainSpotter indexings. (required)", required=True)
	parser.add_argument('-l','--logfile', help="File name of the indexing log file (required)", required=True)
	parser.add_argument('-g','--gve', help="File name of the experimental g-vector file (required)", required=True)
	parser.add_argument('-w', '--wavelength', help="wavelength, in anstroms (required)", type=float, required=True)

	args = vars(parser.parse_args())

	gsinput = args['inputfile']
	logfile = args['logfile']
	gve = args['gve']
	wavelength = args['wavelength']

	gs_indexing_statistics(logfile, gve, gsinput, wavelength)



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


