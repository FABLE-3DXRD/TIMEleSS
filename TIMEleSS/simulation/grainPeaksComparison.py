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

# Maths stuff
import numpy

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser

# Will use to crystallography functions in xfab.symmetry
import xfab.symmetry


#################################################################
#
# Return a list of the elements in a list, but without duplicates.
#
#################################################################

def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].
numpy.
    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.
100
    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()#!/usr/bin/env python
# -*- coding: utf-8 -*-

    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u


#################################################################
#
# Compare the orientation matrices of two grains and check whether they can be the same grain
#
#################################################################

def matchGrains(U1, U2, crystal_system, cutoff):
	"""
	Compare the orientation matrices of two grains and check whether they can be the same grain
	This is a very crude version that does not pay attention to all symmetry equivalents. It might be
	a problem for some high symmetry cubic phases
	
	Relies on Umis function in xfab
	
	Returns True if one of the equivalent has a mis-orientation below 2°
	
	crystal_system can be one of the following values  
		1: Triclinic
		2: Monoclinic
		3: Orthorhombic
		4: Tetragonal
		5: Trigonal
		6: Hexagonal
		7: Cubic
		
	Parameters:
	  U1 - U matrix of grain 1
	  U2 - U matrix of grain 2
	  crystal_system
	  cutoff: mis-orientation below which the two grains are considered identical, in degrees (default is 2°)
	"""

	# Ur = scipy.dot(scipy.linalg.inv(U2),U1)
	#if (1-abs(Ur[0,0]) < 0.002) and (1-abs(Ur[1,1]) < 0.002) and (1-abs(Ur[1,1]) < 0.002) :
	#	return True
	
	test = xfab.symmetry.Umis(U1, U2, crystal_system)
	minMisorientation = min(test[:,1])
	if abs(minMisorientation < cutoff):
		return True
	return False


#################################################################
#
# Compare the orientation matrices of two grains and return the minimal misorientation
#
#################################################################

def minMisorientation(U1,U2,crystal_system):
	"""
	Compare the orientation matrices of two grains and return the minimal misorientation
	This is a very crude version that does not pay attention to all symmetry equivalents. It might be
	a problem for some high symmetry cubic phases
	
	Relies on Umis function in xfab
	
	Returns the minimal misorientation
	
	crystal_system can be one of the following values  
		1: Triclinic
		2: Monoclinic
		3: Orthorhombic
		4: Tetragonal
		5: Trigonal
		6: Hexagonal
		7: Cubic
		
	Parameters:
	  U1 - U matrix of grain 1
	  U2 - U matrix of grain 2
	  crystal_system
	"""

	# Ur = scipy.dot(scipy.linalg.inv(U2),U1)
	#if (1-abs(Ur[0,0]) < 0.002) and (1-abs(Ur[1,1]) < 0.002) and (1-abs(Ur[1,1]) < 0.002) :
	#	return True
	test = xfab.symmetry.Umis(U1, U2, crystal_system)
	return  min(test[:,1])


#################################################################
#
# Write a string to the standard output and into a log file
#
#################################################################

def logit(stream, text):
	"""
	writes a string to the standard output and into a log file
	
	Parameters
	- stream: stream for the log file
	- text: text to be written
	"""
	print (text)
	stream.write(text + "\n")

#################################################################
#
# Remove doubles in a collection of grains
#
#################################################################

def removeDoubleGrains(grains, crystal_system, cutoff, logfile):
	"""
	Remove doubles in a collection of grains
	
	crystal_system can be one of the following values  
		1: Triclinic
		2: Monoclinic
		3: Orthorhombic
		4: Tetragonal
		5: Trigonal
		6: Hexagonal
		7: Cubic
	
	Parameters:
	  grains - list of grains
	  crystal_system - see abover
	  cutoff - mis-orientation below which the two grains are considered identical, in degrees
	  logfile - link to log file
	"""
	
	# find double grains
	grainsToRemove = []
	pairs = []
	for i in range(0, len(grains)):
		for j in range((i+1), len(grains)):
			U1 = (grains[i]).getU()
			U2 = (grains[j]).getU()
			if (matchGrains(U1,U2,crystal_system,cutoff)):
				grainsToRemove.append(j)
				pairs.append([i,j])
				logit(logfile,"- grain %d and %d are identical" % (i, j))
	
	# Remove those grains
	grainsToRemove.sort()
	grainsToRemove = unique(grainsToRemove)
	grainsToRemove.sort()
	grainsToRemove.reverse()
	nRemove = len(grainsToRemove)
	newgrains = grains[:]
	for i in range(0, nRemove):
		del newgrains[grainsToRemove[i]]
	# Log and return
	logit(logfile, "Found %d grains indexed twice" % (nRemove))
	logit(logfile, "New number of grains: %d" % len(newgrains))
	
	return newgrains

#################################################################
#
# Compare grains between 2 collections of grains.
# Print out grains that share peaks, based on the GVE ID
#
#################################################################

def comparaison(file1, file2, crystal_system, cutoff, outputstem):
	"""
	Function designed to compare the orientations of 2 collections of grains.

	Usually used to compare an output file from GrainSpotter and that of a simulation with PolyXSim to make sure
	the indexing makes sense.

	- try to match grains between both
	- maybe more
	- 
	
	crystal_system can be one of the following values  
		1: Triclinic
		2: Monoclinic
		3: Orthorhombic
		4: Tetragonal
		5: Trigonal
		6: Hexagonal
		7: Cubic
	
	Parameters:
	  file1 - file with the first list of grains (used as a reference)
	  file2 - file with the second list of grains
	  crystal_system - see abover
	  outputstem - stem for output file for the grain comparison
	  cutoff - mis-orientation below which the two grains are considered identical, in degrees
	"""
	
	# Prepare output files
	filename1 = "%s-%s" % (outputstem , "log.dat")
	logfile = open(filename1,'w')
	print ("1 output files will be generated: \n- %s\n" % (filename1))
	
	# Counting number of grains
	grains1 = multigrainOutputParser.parseGrains(file1)
	grains2 = multigrainOutputParser.parseGrains(file2)
	ngrains1 = len(grains1)
	ngrains2 = len(grains2)
	logit(logfile, "Parsed %s, found %d grains" % (file1, len(grains1)))
	logit(logfile, "Parsed %s, found %d grains" % (file2, len(grains2)))
	
	logit(logfile, "\nMisorientation below which the two grains are considered identical, in degrees: %.1f\n" % cutoff)

	# Check for doubles in list 1
	logit(logfile, "Check for doubles in %s" % file1)
	grains1clean = removeDoubleGrains(grains1, crystal_system, cutoff, logfile)
	logit(logfile, "")
	
	# Check for doubles in list 2
	logit(logfile, "Check for doubles in %s" % file2)
	grains2clean = removeDoubleGrains(grains2, crystal_system, cutoff, logfile)
	logit(logfile, "")
	
	# Will hold grains that match a peak
	peaksInGrains = {}
	
	# Loop in unique grains in list 1, trying to grains in list 2 that share the same peaks
	for i in range(0,len(grains1clean)):
		grain1 = grains1clean[i]
		grains1GVEID = grain1.getPeaksGVEID()
		for j in range(0,len(grains2clean)):
			grain2 = grains2clean[j]
			grains2GVEID = grain2.getPeaksGVEID()
			matches = set(grains1GVEID).intersection(grains2GVEID)
			if (len(matches)>0):
				logit(logfile, "- Grain %s of %s shares %d peaks with %s of %s" % (grain1.getName(), file1, len(matches), grain2.getName(), file2))
				logit(logfile, "Matching peaks (GVE ID): " + str(list(matches)))
				for peak in matches:
					try:
						grains = peaksInGrains[peak]
						grains.append(grain1.getName() + " in " + file1)
						grains.append(grain2.getName() + " in " + file2)
						peaksInGrains[peak] = grains
					except KeyError:
						# Key is not present
						peaksInGrains[peak] = [grain1.getName() + " in " + file1, grain2.getName() + " in " + file2]
	
	
	logit(logfile, "\nPeaks information\n")
	for peak in peaksInGrains:
		logit(logfile, "- peak %s is seen in %d grains: " % (peak, len(peaksInGrains[peak])) + str(peaksInGrains[peak]))

	return


#################################################################
#
# Main subroutines
#
#################################################################

def main(argv):
	"""
	Main subroutines
	"""
	
	parser = argparse.ArgumentParser(usage='%(prog)s [options] file1 file2', description="Compare peaks in grains between 2 indexation files\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	parser.add_argument('file1', help="first grain file, used as a reference (GrainSpotter output file)")
	parser.add_argument('file2', help="second grain file, matched against the previous file (GrainSpotter output file)")
	
	parser.add_argument('-c', '--crystal_system', type=int, choices=range(1, 8), required=True, help="""Crystal system. Can be one of the following 
    1: Triclinic
    2: Monoclinic
    3: Orthorhombic
    4: Tetragonal
    5: Trigonal
    6: Hexagonal
    7: Cubic
""")
	
	
	parser.add_argument('-o', '--output_stem', required=False, help="Stem for output files. Default is %(default)s", default="comp")
	
	parser.add_argument('-m', '--misorientation', required=False, help="Misorientation below which two grains are considered identical, in degrees. Default is %(default)s", default=2.0, type=float)

	args = vars(parser.parse_args())

	file1 = args['file1']
	file2 = args['file2']
	crystal_system = args['crystal_system']
	stem = args['output_stem']
	cutoff = args['misorientation']
	
	if (not(os.path.isfile(file1))):
		print ("Error: file %s not found" % file1)
		sys.exit(2)
		
	if (not(os.path.isfile(file2))):
		print ("Error: file %s not found" % file2)
		sys.exit(2)

	comparaison(file1, file2, crystal_system, cutoff, stem)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
