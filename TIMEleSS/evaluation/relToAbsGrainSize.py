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
from argparse import RawTextHelpFormatter

# Maths stuff
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy

# Explanation of the parameters:
# grainsizelist:                An output file from the "timelessExtractGrainSizes.py" script. Should be a regular text document
# beamsize_H and beamsize_V:    Horizontal and vertical dimension of the X-ray beam in $\mu$m. Necessary to calculate the illuminated sample volume.
# rotationrange:                Full rotation range used in the experiment in $\mu$m. Necessary to calculate the illuminated sample volume more accurately.
# samplethickness:              Thickness of the sample in $\mu$m. Necessary to calculate the illuminated sample volume.
# indexquality:                 Quality of the previous indexing process in percent. Used to account for the fact that not all grains were found during the indexing, between 0 and 1.
# radius:                       Boolean operator that determines if grainsizelist consists of grain volumes or grain radii. True means volumes, False means radii.
# histogram_bins:               Number of histogram bins you want to use. By default, no histogram is plotted.
# proportion:                   Defines how much of the sample is your phase of interest. Can be between 0 and 1.

def absolute_grainsizes(grainsizelist, beamsize_H, beamsize_V, rotationrange, samplethickness, indexquality, radius=True, proportion=1.0):
	with open(grainsizelist) as g:
		grainsizes = g.readlines()
	total = 0
	ngrains = 0
	grainRelVolumes = []
	for grain in grainsizes:
		ngrains += 1
		grain = float(grain)
		if (radius): # Grain size in file is a radius
			grainV = 4./3*numpy.pi*grain**(3.) # Turn grain radii into grain volumes
			grainRelVolumes.append(grainV)
		else: 
			grainV = grain
			grainRelVolumes.append(grainV)
		total += grainV
	total = total

	# Calculate the sample chamber volume. Check the wiki for more info on the formula.
	totalsamplechambervol = beamsize_V * beamsize_H * samplethickness * numpy.cos(rotationrange*numpy.pi/180/2) + 0.5 * beamsize_V * samplethickness**2 * numpy.tan(rotationrange*numpy.pi/180/2)
	indexedGrainsV = totalsamplechambervol * indexquality * proportion # Account for the indexing quality and side phases
	print("Read arbitrary grain sizes from %s" % grainsizelist)
	if (radius):
		print("I believe I read a list of grain radii")
	else:
		print("I believe I read a list of grain volumes")
	print("Beam size H x V (µm): %.1f, %.1f" % (beamsize_H, beamsize_V))
	print("Sample thickness (µm): %.1f" % (samplethickness))
	print("Rotation range (degrees): %.1f" % (rotationrange))
	print("Indexing quality (percents): %i" % (indexquality))
	print("Phase proportion (relative): %.2f" % (proportion))
	print("Total illuminated sample chamber volume (µm^3): %.1f" % totalsamplechambervol)
	print("Total volume of indexed grains (µm^3): %.1f" % indexedGrainsV)
	print("Total volume of indexed grains (arbitrary unit): %.1f" % total)
	print("Number of grains: %i" % ngrains)
	
	ratio_V = indexedGrainsV / total # How many µm^3 equals one relative grain size unit
	
	# Create a new file that contains the absolute grain size 
	newfile = grainsizelist[:-4] + "_abs.txt"
	filename, file_extension = os.path.splitext(grainsizelist)
	grainsizes_R = [] # Make a list of the new grain sizes
	grainsizes_V = [] # Make a list of the new grain sizes
	stringV = ""
	stringR = ""
	for grainRelV in grainRelVolumes:
		grainV = grainRelV * ratio_V
		grainR = (grainV*3./(4.*numpy.pi))**(1./3)
		stringV += str(grainV) + "\n"
		stringR += str(grainR) + "\n"
		grainsizes_R.append(grainR)
		grainsizes_V.append(grainV)
	newfile = filename + "_absV.txt"
	f= open(newfile,"w+")
	f.write(stringV)
	f.close()
	print ("\nSaved new list of grain volumes (in µm^3) as %s." % (newfile))
	newfile = filename + "_absR.txt"
	f= open(newfile,"w+")
	f.write(stringR)
	f.close()
	print ("Saved new list of grain radii (in µm) as %s." % (newfile))
	
	# Print out some statistics
	print ("\nGrain volumes:\n\tmean: %d\n\tmedian: %d\n\tmax: %d\n\tmin: %d" % (numpy.mean(grainsizes_V), numpy.median(grainsizes_V), numpy.min(grainsizes_V), numpy.max(grainsizes_V)))
	print ("\nGrain radii:\n\tmean: %.2f\n\tmedian: %.2f\n\tmax: %.2f\n\tmin: %.2f" % (numpy.mean(grainsizes_R), numpy.median(grainsizes_R), numpy.min(grainsizes_R), numpy.max(grainsizes_R)))
	
	# Return grain radii
	med = numpy.median(grainsizes_R)
	return grainsizes_R, med



################################################################
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
	
	parser = MyParser(usage='%(prog)s grainsizelist -H beamsize_horizontal (in micrometer) -V beamsize_vertical (in micrometer) -r rotation_range (in degrees) -t sample_thickness (in micrometer) -i indexing_quality (in percents) [options]', description="""Estimation of absolute grain volumes in micrometer based on an "timelessExtractGrainSizes" output file

Example:
	%(prog)s list_of_grainsizes.txt -H 1.5 -V 1.8 -r 56 -t 20 -i 76.2 -rad -hist 30 -p 0.7

This is part of the TIMEleSS project\nhttp://timeless.texture.rocks
""", formatter_class=RawTextHelpFormatter)
	
	# Required arguments
	parser.add_argument('grainsizelist', help="Path and name for the GrainSize output file")
	parser.add_argument('-H', '--beamsize_H', required=True, help="Beamsize perpendicular to rotation axis (micrometer), usually horizontal (required)", type=float)
	parser.add_argument('-V', '--beamsize_V', required=True, help="Beamsize parallel to rotation axis (micrometer), usually vertical (required)", type=float)
	parser.add_argument('-r', '--rotationrange', required=True, help="Full rotation range. Example: [-28,+28] rotation = 56 degrees (required)", type=float)
	parser.add_argument('-t', '--samplethickness', required=True, help="Thickness of your sample (micrometer). If sample has varying thickness, estimate an average. (required)", type=float)
	parser.add_argument('-i', '--indexquality', required=True, help="Estimate of indexing performance (1.0 is perfect, 0.3 means 30pc of sample grains have been indexed, required)", type=float)
	
	# Optionnal arguments
	parser.add_argument('-rad', '--radius', required=False, help="Add '-rad' to treat the grainsizelist as list of grain radii. Don´t add this argument to treat the grainsizelist as list of grain volumes. Default is volumes.", default=False, action='store_true')
	parser.add_argument('-hist', '--histogram_bins', required=False, help="If a histogram shall be plotted, give the number of histogram bins here. Default is %(default)s", default=None, type=int)
	parser.add_argument('-p', '--proportion', required=False, help="Gives the proportion of the phase of interest relative to the full sample volume. Example: Give 0.3 if your phase of interest makes up only 30 percent of your entire sample. Default is %(default)s.", default=1.0, type=float)
	
	# Parse arguments
	args = vars(parser.parse_args())
	grainsizelist = args['grainsizelist']
	beamsize_H = args['beamsize_H']
	beamsize_V = args['beamsize_V']
	rotationrange = args['rotationrange']
	samplethickness = args['samplethickness']
	indexquality = args['indexquality']
	radius = args['radius']
	histogram_bins = args['histogram_bins']
	proportion = args['proportion']

	# check that "proportion" and "indexquality" are below 0 and 1
	if ((indexquality < 0) or (indexquality > 1.0)):
		print ("\nError: parameter for indexing quality should be between 0 and 1.0 (for 100pc of indexed grains).\nYou provided: %.2f \nOlder version did use percents as input but this was changed for consistency.\n" % indexquality)
		sys.exit(2)
	if ((proportion < 0) or (proportion > 1.0)):
		print ("\nError: parameter for phase proportion should be between 0 and 1.0 (if the phase of interest is the entire sample).\nYou provided: %.2f \nOlder version did use percents as input but this was changed for consistency.\n" % proportion)
		sys.exit(2)
		

	grainsizes_R, med = absolute_grainsizes(grainsizelist, beamsize_H, beamsize_V, rotationrange, samplethickness, indexquality, radius=radius, proportion=proportion)

	# Make a histogram
	if histogram_bins != None:
		print ("\nPlotting histogram of grain radii ...\n")
		plt.hist(grainsizes_R, bins = histogram_bins)
		plt.xscale('log')
		plt.xlabel("Grain radii ($\mu$m)")
		plt.ylabel("Number of grains")
		plt.title("n = %s" % len(grainsizes_R), fontsize = 20)
		plt.axvline(med, color='k', linestyle='dashed', linewidth=1)
		ylim_min, ylim_max = plt.ylim()
		plt.text(med*1.1, ylim_max*0.9, 'Median: {:.4f} $\mu$m'.format(med))
		plt.show()
			
		
# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
	main(sys.argv[1:])

