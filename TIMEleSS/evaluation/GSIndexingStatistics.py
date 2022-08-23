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

# Python 2 to python 3 migration tools
from __future__ import absolute_import
from __future__ import print_function

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path


# Maths stuff
import numpy

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser
from six.moves import range


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

def gs_indexing_statistics(logfile, gve, gsinputfile, wavelength):
	"""
	Checks a grainspotter indexing performance
	Send the final GrainSpotter log, the list of g-vectors, the GS input file (with the loosest conditions), and the wavelength
	"""
	nphases = len(logfile)
	grains = []
	ngrains = []
	gsinput = []
	nindexed = []
	totalngrains = 0
	totalindexedpeaks = 0
	
	i = 0
	# Parsing grain spotter output in input files
	# Extracting grain information
	for thislog in logfile:	
		grains.append(multigrainOutputParser.parseGrains(thislog))
		print("Parsed %s, found %d grains" % (thislog, len(grains[i])))
		print("Parsing grain spotter input file %s." % (gsinputfile[i]))
		# Load the grain spotter input file
		gsinput.append(multigrainOutputParser.parseGSInput(gsinputfile[i]))
		print("\nGrainSpotter results for phase %d" % i)
		print("\t%d grains indexed" % (len(grains[i])))
		nindexed.append(0)
		ngrains.append(len(grains[i]))
		totalngrains += len(grains[i])
		for grain in grains[i]: 
			nindexed[i] += grain.getNPeaks()
		print("\t%d g-vectors indexed" % (nindexed[i]))
		totalindexedpeaks += nindexed[i]
		tt = 1.0*nindexed[i]/ngrains[i]
		print("\t%.1f g-vectors per grain in average" % (tt))
		i = i + 1
		print ("")
	
	
	print("Done parsing grain files.\n")

	# Extract peak list and ds ranges in which to look for peak
	# For each phase, the list of peaks is on top of the gve file
	# Then, need keep a record of the ds tolerance for the peak (which could different for each phase)
	peakssample = []
	peaksgve = [None] * nphases
	idlist = [None] * nphases
	for i in range(0,nphases):
		[peaksgve[i],idlist[i],header] = multigrainOutputParser.parseGVE(gve[i]) 
		print("Parsing header from GVE files %s to extract predicted sample peaks for phase %i" % (gve[i], i))
		tttol = gsinput[i]["sigma_tth"]*gsinput[i]["nsigmas"]
		recordpeaks = False
		for line in header.split("\n"):
			if ((line.strip() == "#  gx  gy  gz  xc  yc  ds  eta  omega  spot3d_id  xl  yl  zl")):
				recordpeaks = False
				# We reached the end of the header...
			if recordpeaks:
				try:
					tt = line.split()
					ds = float(tt[0])
					h = int(tt[1])
					k = int(tt[2])
					l = int(tt[3])
					tt = 2.*numpy.degrees(numpy.arcsin(wavelength*ds/2.))
					dsmin = 2.*numpy.sin(numpy.radians((tt-tttol)/2.))/(wavelength)
					dsmax = 2.*numpy.sin(numpy.radians((tt+tttol)/2.))/(wavelength)
				except ValueError:
					print("Conversion error when reading predicted sample peaks from %s." % (gve[i]))
					print("Was trying to convert %s to ds, h, k, and l" % (line))
					sys.exit(1)
				peakssample.append([ds,h,k,l,tt,dsmin,dsmax,tttol])
			if ((line.strip() == "# ds h k l")):
				recordpeaks = True
	print ("\nRead theoretical peak positions in 2theta for all phases.\nI have a list of %d potential peaks for all %d phases.\n" % (len(peakssample), nphases))
	
	# Merging peaks from GVE files, removing doubles
	allgves = peaksgve[0]
	allPeakIds = idlist[0]
	for i in range(1,nphases):
		missinggveID = set(idlist[i]).symmetric_difference(set(allPeakIds))
		for peakid in missinggveID:
			ID_idlist = (idlist[i]).index(peakid)
			allPeakIds.append(peakid)
			allgves.append(peaksgve[i][ID_idlist])
			
	print ("Merged unique g-vectors of all %d gve files. I now have %d experimental g-vectors." % (nphases, len(allgves)))
			
	# Loop on all experimental g-vectors
	# Are they in one of the 2 theta, omega, and eta ranges defined in grain spotter?
	# Need to check for all phases
	
	ds = []
	eta = []
	omega = []
	keepPeak = [False] * len(allgves)
	
	for i in range(0,nphases): # Loop on phase
		gsinput[i]["dsranges"] = []
		for tthrange in gsinput[i]["tthranges"]:  # Convert 2theta range to ds range for easier comparison
			ds0 = 2.*numpy.sin(numpy.radians(tthrange[0]/2.))/(wavelength)
			ds1 = 2.*numpy.sin(numpy.radians(tthrange[1]/2.))/(wavelength)
			(gsinput[i]["dsranges"]).append([ds0,ds1])
		# Loop on peaks. If the peak is within the range, we keep it for later
		for j in range(0,len(allgves)):
			peak = allgves[j]
			thisds = float(peak['ds'])
			thiseta = normalizedAngle360(float(peak['eta'])) # In GrainSpotter, eta is in [0;360]
			thisomega = normalizedAngle180(float(peak['omega'])) # In GrainSpotter, omega is in [-180;180]
			test1 = 0
			test2 = 0
			test3 = 0
			for dsrange in gsinput[i]["dsranges"]:
				if ((thisds >= dsrange[0]) and (thisds <= dsrange[1])):
					test1 = 1
			for etarange in gsinput[i]["etaranges"]:
				if ((thiseta >= etarange[0]) and (thiseta <= etarange[1])):
					test2 = 1
				#else:
				#	print "Not for eta %.1f < %.1f < %.1f" % (etarange[0],thiseta,etarange[1])
			for omegarange in gsinput[i]["omegaranges"]:
				if ((thisomega >= omegarange[0]) and (thisomega <= omegarange[1])):
					test3 = 1
				#else:
				#	print "Not for omega %.1f < %.1f < %.1f" % (omegarange[0],thisomega,omegarange[1])
			if (test1*test2*test3 == 1): # The peak is within the range of ttheta, eta, and omega for phase i. It could have been indexed.
				keepPeak[j] = True
	
	for j in range(0,len(allgves)):
		if (keepPeak[j]):
			peak = allgves[j]
			ds.append(float(peak['ds']))
			eta.append(float(peak['eta']))
			omega.append(float(peak['omega']))

	print("%d g-vectors within eta, omega, and 2theta ranges and could have been indexed." % (len(ds)))

	# Counting peak, within 2 theta range, and that can be assigned to the sample

	nassigned = 0
	for thisds in ds:
		append = 0
		for i in range(0,len(peakssample)):
			if ((thisds <= peakssample[i][6]) and (thisds >= peakssample[i][5])):
				append = 1
		nassigned += append
	print("%d g-vectors assigned to one of the sample peaks within these ranges." % (nassigned))
	
	print("\nGlobal indexing performance")
	print("\tOut of %d possible g-vectors, %d have been assigned to %d grains" % (nassigned, totalindexedpeaks, totalngrains))
	tt = nassigned-totalindexedpeaks
	print("\t%d remaining g-vectors" % (tt))
	tt = 100.*totalindexedpeaks/nassigned
	print("\t%.1f percents of g-vectors indexed" % (tt))
	print() 
	
	
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
	
	parser = MyParser(formatter_class=argparse.RawDescriptionHelpFormatter, \
		usage='%(prog)s -i gsinput -l logfilestem.log -g gve.gve -w wavelength', \
			description='Reads a GrainSpotter input file, indexing log file, experimental g-vectors from a GVE file, and pulls out indexing statistics.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n', \
		epilog='''\
If you have multiple phases in your indexing, provide the GS input files, log files, and g-vector files for each phase (in the same order).
   Example:  
      timelessGSIndexingStatistics -w 0.2989 -i index-Dm-0.ini index-MgO-0.ini index-Bm-0.ini -l grains-Dm-0.log grains-MgO-0.log grains-Bm-0.log -g ../davemaoite_peaks_t55_filtered.gve ../mgo_peaks_t55_filtered.gve ../bridgmanite_peaks_t55_filtered.gve 

''')
	
	# Arguments
	parser.add_argument('-i','--inputfile', help="Input file name for GrainSpotter. Use the file with the looser conditions if you ran multiple steps of GrainSpotter indexings. (required)", required=True, nargs='+')
	parser.add_argument('-l','--logfile', help="File name of the indexing log file (required)", required=True, nargs='+')
	parser.add_argument('-g','--gve', help="File name of the experimental g-vector file (required)", required=True, nargs='+')
	parser.add_argument('-w', '--wavelength', help="wavelength, in anstroms (required)", type=float, required=True)

	args = vars(parser.parse_args())

	gsinput = args['inputfile']
	logfile = args['logfile']
	gve = args['gve']
	wavelength = args['wavelength']

	nphases = len(gsinput)
	if (len(logfile) != nphases):
		print("Error: I have %d GrainSpotter input file(s) and %d GrainSpotter ouput files. These should be identical." % (len(gsinput), len(logfile)))
		return
	if (len(gve) != nphases):
		print("Error: I have %d GrainSpotter input file(s) and %d gve files. These should be identical." % (len(gsinput), len(gve)))
		return

	gs_indexing_statistics(logfile, gve, gsinput, wavelength)



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


