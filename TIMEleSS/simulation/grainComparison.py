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
        return list(u.keys())

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
# Compare orientations between 2 collections of grains.
#
#################################################################

def comparaison(file1, file2, crystal_system, cutoff, outputstem, verbose):
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
	  verbose - save all grain comparison into an output file rather than only matching or non matching grain
	"""
	
	# Prepare output files
	filename1 = "%s-%s" % (outputstem , "log.dat")
	logfile = open(filename1,'w')
	filename2 = "%s-%s" % (outputstem , "matching-grains.dat")
	logmatching = open(filename2,'w')
	filename3 = "%s-%s" % (outputstem , "erroneous-grains.dat")
	logerroneous = open(filename3,'w')
	filename4 = "%s-%s" % (outputstem , "missing-grains.dat")
	logmissing = open(filename4,'w')
	if (not verbose):
		print("4 output files will be generated: \n- %s,\n- %s,\n- %s,\n- %s\n" % (filename1, filename2, filename3, filename4))
	else:
		filename5 = "%s-%s" % (outputstem , "verbose.dat")
		logverbose = open(filename5,'w')
	
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
	
	# Loop in unique grains in list 1, trying to find pairs in list 2
	goodGrains = [] # grains in list 2 that exist in list 1
	erroneousGrains = [] # grains in list 2 that do not exist in list 1
	grains1cleanFound = numpy.full((len(grains1clean),1), False, dtype=bool)
	logit(logfile, "Trying to match grains between the 2 collections...")
	for i in range(0,len(grains2clean)):
		grainMatched = []
		grain2 = grains2clean[i]
		U2 = grain2.getU()
		for j in range(0,len(grains1clean)):
			grain1 = grains1clean[j]
			U1 = grain1.getU()
			if (verbose): # We provide an output file all comparisons
				angle = minMisorientation(U1,U2,crystal_system)
				logverbose.write("Grain %s of %s\n" % (grain1.getName(), file1))
				logverbose.write("\tcompared with grain %s of %s\n" % (grain2.getName(), file2))
				logverbose.write("\tmisorientation: %.2f°\n" % (angle))
				logverbose.write("U grain 1: \n" + numpy.array2string(U1) + "\n")
				logverbose.write("U grain 2: \n" + numpy.array2string(U2) + "\n")
				logverbose.write("\n\n")
			if (matchGrains(U1, U2, crystal_system, cutoff)):
				grainMatched.append(j)
				grains1cleanFound[j] = True
		if len(grainMatched) > 1 :
			logit(logfile, "- Found more than 1 pair for grain %d. Something is wrong" % i)
			sys.exit(2)
		elif len(grainMatched) > 0 :
			goodGrains.append(i)
			grain1 = grains1clean[grainMatched[0]]
			U1 = grain1.getU()
			angle = minMisorientation(U1,U2,crystal_system)
			logit(logfile, "- Grain %s of %s matches %s of %s with a misorientation of %.2f°" % (grain1.getName(), file1, grain2.getName(), file2, angle))
			logmatching.write("Grain %s of %s\n" % (grain1.getName(), file1))
			logmatching.write("\tmatches grain %s of %s\n" % (grain2.getName(), file2))
			logmatching.write("\tmisorientation: %.2f°\n" % (angle))
			logmatching.write("U grain 1: \n" + numpy.array2string(U1) + "\n")
			logmatching.write("U grain 2: \n" + numpy.array2string(U2) + "\n")
			logmatching.write("\n\n")
		else:
			erroneousGrains.append(i)
			logit(logfile, "- Grain %s of %s has no match" % (grain2.getName(), file2))
			logerroneous.write("\nGrain %s of %s: no match\n" % (grain2.getName(), file2))
			for j in range(0, len(grains1clean)):
				grain1 = grains1clean[j]
				U1 = grain1.getU()
				angle = minMisorientation(U1,U2,crystal_system)
				logerroneous.write("- Min angle with grain %s: %.2f°\n" % (grain1.getName(),angle))
	logit(logfile, "End of run\n")
	
	for i in range(0,len(grains1clean)):
		if (not grains1cleanFound[i]):
			grain1 = grains1clean[i]
			logmissing.write("Grain %s of %s has no match\n" % (grain1.getName(), file1))
	
	logit(logfile, "N. of grains in %s: %d" % (file1, ngrains1))
	logit(logfile, "N. of unique grains in %s: %d" % (file1, len(grains1clean)))
	logit(logfile, "N. of grains in %s: %d" % (file2, ngrains2))
	logit(logfile, "N. of unique grains in %s: %d" % (file2, len(grains2clean)))
	logit(logfile, "N. of unique grains found in both %s and %s: %d" % (file1, file2, len(goodGrains)))
	logit(logfile, "N. of unique grains found only in %s: %d" % (file2, len(erroneousGrains)))
	logit(logfile, "N. of unique grains found in %s but not in %s: %d" % (file1, file2, len(grains1clean)-len(goodGrains)))
	logit(logfile, "\nIndexing capability")
	logit(logfile, "- %.1f pc of %s grains indexed" % (100.*len(goodGrains)/len(grains1clean), file1))
	logit(logfile, "- %.1f pc of %s grains not indexed" % (100.-100.*len(goodGrains)/len(grains1clean), file1))
	logit(logfile, "- %.1f pc of erroneous grains in %s" % (100.*len(erroneousGrains)/len(grains2clean), file2))
	
	if (verbose):
		print ("\n5 output files were generated: \n- %s,\n- %s with the matching grains,\n- %s with erroneous grains,\n- %s with missing grains,\n- %s with verbose grain comparison \n" % (filename1, filename2, filename3, filename4, filename5))
	else:
		print ("\n4 output files were generated: \n- %s,\n- %s with the matching grains,\n- %s with erroneous grains,\n- %s with missing grains\n" % (filename1, filename2, filename3, filename4))
	 
	logmatching.close()
	logfile.close()
	logerroneous.close()
	logmissing.close()
	if (verbose):
		logverbose.close()


#################################################################
#
# Main subroutines
#
#################################################################

def main(argv):
	"""
	Main subroutines
	"""
	
	parser = argparse.ArgumentParser(usage='%(prog)s [options] file1 file2', description="Compare grains between 2 files\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	parser.add_argument('file1', help="first grain file, used as a reference (gff, ubi, or GrainSpotter output file, based on extension)")
	parser.add_argument('file2', help="second grain file, matched against the previous file (gff, ubi, or GrainSpotter output file, based on extension)")
	
	parser.add_argument('-c', '--crystal_system', type=int, choices=list(range(1, 8)), required=True, help="""Crystal system. Can be one of the following 
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
	
	parser.add_argument('-v', '--verbose', required=False, help="Create output file with verbose grain comparison. Can be True or False. Default is  Default is %(default)s", type=bool, default=False)

	args = vars(parser.parse_args())

	file1 = args['file1']
	file2 = args['file2']
	crystal_system = args['crystal_system']
	stem = args['output_stem']
	cutoff = args['misorientation']
	verbose = args['verbose']
	
	if (not(os.path.isfile(file1))):
		print(("Error: file %s not found" % file1))
		sys.exit(2)
		
	if (not(os.path.isfile(file2))):
		print(("Error: file %s not found" % file2))
		sys.exit(2)

	comparaison(file1, file2, crystal_system, cutoff, stem, verbose)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
