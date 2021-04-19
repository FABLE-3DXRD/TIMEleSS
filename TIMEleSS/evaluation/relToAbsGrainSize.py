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
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")
import numpy

# TIMEleSS parsing utilities
from TIMEleSS.general import multigrainOutputParser
from TIMEleSS.general import indexedPeak3DXRD

# Explanation of the parameters:
# grainsizelist:                An output file from the "timelessExtractGrainSizes.py" script. Should be a regular text document
# beamsize_H and beamsize_V:    Horizontal and vertical dimension of the X-ray beam in $\mu$m. Necessary to calculate the illuminated sample volume.
# rotationrange:                Full rotation range used in the experiment in $\mu$m. Necessary to calculate the illuminated sample volume more accurately.
# samplethickness:              Thickness of the sample in $\mu$m. Necessary to calculate the illuminated sample volume.
# indexquality:                 Quality of the previous indexing process in percent. Used to account for the fact that not all grains were found during the indexing.
# volume:                       Boolean operator that determines if grainsizelist consists of grain volumes or grain radii. True means volumes, False means radii.

def absolute_grainsizes(grainsizelist, beamsize_H, beamsize_V, rotationrange, samplethickness, indexquality, volume, proportion):
    with open(grainsizelist) as g:
        grainsizes = g.readlines()
    total = 0
    for grain in grainsizes:
        grain = float(grain)
        if volume == False:
            grain = 4/3*numpy.pi()*grain^3 # Turn grain radii into grain volumes
        total += grain
    total = total * indexquality / 100 * proportion # Account for the indexing quality and side phases
    
    # Calculate the sample chamber volume. For more info on the formula ask M. Krug.
    samplechambervol = samplethickness * beamsize_H * beamsize_V * numpy.arccos(rotationrange*numpy.pi/180/2)
    
    ratio_V = total / samplechambervol # How many µm^3 equals one relative grain size unit
    ratio_V = float(ratio_V)
    print (ratio_V)
    ratio_R = ratio_V**(1/3)
    
    # Create a new file that contains the absolute grain size 
    newfile = grainsizelist[:-4] + "_abs.txt"
    grainsizes_new = [] # Make a list of the new grain sizes
    string = ""
    for grain in grainsizes:
        grain = float(grain)
        if volume == False:
            grain = grain * ratio_R
        else:
            grain = grain * ratio_V
        grainsizes_new.append(grain)
        string += str(grain) + "\n"
    f= open(newfile,"w+")
    f.write(string)
    f.close()
    
    if volume == True:
        print ("\nA volumetric grain size of 1.0 in your list of grainsizes corresponds to %0.3f µm^3." % (ratio_V))
        print ("\nSaved new list of grain volumes (in µm^3) as %s." % (newfile))
    else:
        print ("\nA grain radius of 1.0 in your list of grainsizes corresponds to %0.3f µm." % (ratio_R))
        print ("\nSaved new list of grain radii (in µm) as %s." % (newfile))
    return grainsizes_new



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
    
    parser = MyParser(usage='%(prog)s grainsizelist -H beamsize_horizontal (in $\mu$m) -V beamsize_vertical (in $\mu$m) -r rotation_range (in degrees) -t sample_thickness (in $\mu$m) -i indexing_quality (in %) [options]', description="""Estimation of absolute grain volumes in $\mu$m based on an "timelessExtractGrainSizes" output file

Example:
    %(prog)s list_of_grainsizes.txt -H 1.5 -V 1.8 -r 56 -t 20 -i 76.2 -vol False -hist 30

This is part of the TIMEleSS project\nhttp://timeless.texture.rocks
""", formatter_class=RawTextHelpFormatter)
    
    # Required arguments
    parser.add_argument('grainsizelist', help="Path and name for the GrainSize output file")
    parser.add_argument('-H', '--beamsize_H', required=True, help="Beamsize perpendicular to rotation axis (µm), usually horizontal (required)", type=float)
    parser.add_argument('-V', '--beamsize_V', required=True, help="Beamsize parallel to rotation axis (µm), usually vertical (required)", type=float)
    parser.add_argument('-r', '--rotationrange', required=True, help="Full rotation range. Example: [-28,+28] rotation = 56 degrees (required)", type=float)
    parser.add_argument('-t', '--samplethickness', required=True, help="Thickness of your gasket indentation (µm, required)", type=float)
    parser.add_argument('-i', '--indexquality', required=True, help="Percentage of indexed g-vectors (in %). Estimate if not determined (required)", type=float)
    
    # Optionnal arguments
    parser.add_argument('-vol', '--volume', required=False, help="If True, treats grainsizelist as list of grain volumes. If False, treats grainsizelist as list of grain radii. Default is %(default)s", default=True, type=bool)
    parser.add_argument('-hist', '--histogram_bins', required=False, help="If a histogram shall be plotted, give the number of histogram bins here. Default is %(default)s", default=None, type=int)
    parser.add_argument('-prop', '--proportion', required=False, help="Gives the proportion of the phase of interest relative to the full sample volume. Example: Give 0.3 if your phase of interest makes up only 30% of your entire sample. Default is %(default)s.", default=1.0, type=float)
    
    # Parse arguments
    args = vars(parser.parse_args())
    grainsizelist = args['grainsizelist']
    beamsize_H = args['beamsize_H']
    beamsize_V = args['beamsize_V']
    rotationrange = args['rotationrange']
    samplethickness = args['samplethickness']
    indexquality = args['indexquality']
    volume = args['volume']
    histogram_bins = args['histogram_bins']
    proportion = args['proportion']

    grainsizes_new = absolute_grainsizes(grainsizelist, beamsize_H, beamsize_V, rotationrange, samplethickness, indexquality, volume, proportion)

    # Make a histogram
    if histogram_bins != None:
        if volume == True:
            print ("Plotting histogram ...\n")
            plt.hist(grainsizes_new, bins = histogram_bins)
            plt.xlabel("Grain volume ($\mu$m^3)")
            plt.ylabel("Number of grains")
            plt.title("n = %s" % len(grainsizes_new), fontsize = 20)
            plt.show()
        else:
            radii = []
            for item in grainsizes_new:
                radius = (3*item/4/numpy.pi())^(1/3)
                radii.append(radius)
            print ("Plotting histogram ...\n")
            plt.hist(radii, bins = histogram_bins)
            plt.xlabel("Grain radii ($\mu$m)")
            plt.ylabel("Number of grains")
            plt.title("n = %s" % len(grainsizes_new), fontsize = 20)
            plt.show()
            
        
# Calling method 1 (used when generating a binary in setup.py)
def run():
    main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
