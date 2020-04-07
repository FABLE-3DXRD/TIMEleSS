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


def normalizedAngle(angle):
	"""
	Brings an angle back to [-180;180)
	"""
	return angle - (numpy.floor((angle + 180)/360))*360;           # [-180;180):


def test_grains(grainfile,gvefile,wavelength):
	"""
	Check a GrainSpotter log file against a GVE file
	This can be used to make sure that this exact GVE file was actually used to index the grains
	"""
	grains = multigrainOutputParser.parseGrains(grainfile)
	print "Parsed %s, found %d grains" % (grainfile, len(grains))
	
	# Load .gve file from ImageD11 :
	[peaksgve,idlist,header] = multigrainOutputParser.parseGVE(gvefile) 
	
	# Try to see if all peaks in the indexed grains are in the gve
	print "Making sure all indexed peak ID's are in the GVE file..."
	npeakstotal = 0
	npeakserror = 0
	for grain in grains : 
		peaks = grain.peaks
		for indexedPeak in peaks : 
			npeakstotal += 1
			try:
				ID_grains = indexedPeak.getPeakID()
				ID_idlist = idlist.index(ID_grains)
				ID_gve = peaksgve[ID_idlist]
			except ValueError:
				print "Peak %d of grain %s not found" % (ID_grains, grain.getName() )
				npeakserror += 1
				if (npeakserror > 10):
					print "Too many errors, I stop here"
					return
	
	print "I was looking for %d peaks from %d grains and got %d errors" % (npeakstotal, len(grains), npeakserror)
	if (npeakserror > 0):
		print "%s and %s do not seem to match" % (grainfile, gvefile)
		return
	
	print "All peaks in the grain file are in the GVE file. Now, looking for 2theta, eta, omega to see if they match..."
	for grain in grains : 
		peaks = grain.peaks
		for indexedPeak in peaks : 
			npeakstotal += 1
			ID_grains = indexedPeak.getPeakID()
			omegaG = normalizedAngle(indexedPeak.getOmegaMeasured())
			etaG = normalizedAngle(indexedPeak.getEtaMeasured())
			tthetaG = indexedPeak.getTThetaMeasured()
			dsG = 2.*numpy.sin(numpy.radians(tthetaG/2.))/(wavelength)
			
			ID_idlist = idlist.index(ID_grains)
			#print peaksgve[ID_idlist]
			#return
			dsPeak = float(peaksgve[ID_idlist]['ds'])
			etaPeak = normalizedAngle(float(peaksgve[ID_idlist]['eta']))
			omegaPeak = normalizedAngle(float(peaksgve[ID_idlist]['omega']))
			if ((abs(etaG-etaPeak) > 0.01) or (abs(omegaPeak-omegaG) > 0.01) or (abs(dsG-dsPeak) > 0.001)):
				print "Problem with peak %d of grain %s not found" % (ID_grains, grain.getName() )
				print "Expected: eta = %.2f , omega = %.2f, ds = %.4f" % (etaG, omegaG, dsG)
				print "Found: eta = %.2f , omega = %.2f, ds = %.4f" % (etaPeak, omegaPeak, dsPeak)
				print "Differences: eta = %.4f , omega = %.4f, ds = %.6f" % (abs(etaPeak-etaG), abs(omegaPeak-omegaG), abs(dsG-dsPeak))
				npeakserror += 1
				if (npeakserror > 10):
					print "Too many errors, I stop here"
					return

	if (npeakserror > 0):
		print "%s and %s do not seem to match" % (grainfile, gvefile)
		return
	
	print "All peaks in the grain file are in the GVE file and angles fully match."
	
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
	
	parser = MyParser(usage='%(prog)s -l logfilestem.log -g gve.gve -w wavelength', description="Reads a GrainSpotter indexing log file from GrainSpotter, peaks from a GVE file, and make all peaks indexed by GrainSpotter are in the GVE file. This can be used if you lost track of what file was used for indexing.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Arguments
	parser.add_argument('-l','--logfile', help="File name of the indexing log file (required)", required=True)
	parser.add_argument('-g','--gve', help="File name of the g-vector file (required)", required=True)
	parser.add_argument('-w', '--wavelength', help="wavelength, in anstroms (required)", type=float, required=True)

	args = vars(parser.parse_args())

	logfile = args['logfile']
	gve = args['gve']
	wavelength = args['wavelength']

	test_grains(logfile, gve, wavelength)



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


