#!/usr/bin/env python
# -*- coding: utf-8 -* 

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

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Nov. 2020
# Please, avoid updating this script. The simulation.clearGVEGrains has been updated with more options
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
	
	parser = MyParser(usage='%(prog)s -l logfilestem.log -i gve_input.gve -o gve_output.gve', description="Takes a logfile from GrainSpotter and a G-vector file from ImageD11 as input. Compares both and creates a new G-vector file with all those G-vectors which could not be indexed. Now GrainSpotter can be run again with the new G-vector file.\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Arguments
	parser.add_argument('-l','--logfile', help="File name of the indexing log file (required)")
	parser.add_argument('-i','--gve_input', help="File name of the input g-vector file (required)")
	parser.add_argument('-o', '--gve_output', help="Output g-vector file (.gve file)(required)")
	

	args = vars(parser.parse_args())

	logfile = args['logfile']
	gve_input = args['gve_input']
	gve_output = args['gve_output']
	RemoveUsedGVE(logfile,gve_input,gve_output)
    
    
def RemoveUsedGVE(logfile,gve_input,gve_output):
    # Upload .log file from GrainSpotter : 
    grains = multigrainOutputParser.parse_GrainSpotter_log(logfile)
    
    # Upload .gve file from ImageD11 :
    [peaksgve,idlist,header] = multigrainOutputParser.parseGVE(gve_input) 
    
    # Display peak information : 
    nb_start = len(peaksgve)
    gveToRemove = []
    for grain in grains : 
        peaks = grain.peaks
        for indexedPeak in peaks : 
            #print 'Peak in grainFile'
            #print indexedPeak.getPeakID()
            #print indexedPeak.getTThetaMeasured()
            #print indexedPeak.getOmegaMeasured()
            #print indexedPeak.getEtaMeasured()
            #print 'Peak in gveFile'
            ID_grains = indexedPeak.getPeakID()
            ID_idlist = idlist.index(ID_grains)
            ID_gve = peaksgve[ID_idlist]
            #print  ID_gve
            #print ID_gve['eta']
    # Eliminate g-vectors which correspond to already indexed peaks :        
            gveToRemove.append(ID_gve)
            #print nb_start
            #print len(peaksgve)
            #print len(gveToRemove)
        
    # Save the new list of (not indexed) peaks in .gve format : 
    newPeakslist = [peaks for peaks in peaksgve if peaks not in gveToRemove]
    OutputPeaks = multigrainOutputParser.saveGVE(newPeakslist, header, gve_output)
    print('\n%s g-vectors were removed.' %len(gveToRemove))
    print('\nThe new list contains %s g-vectors.' %len(newPeakslist))
    print('\nSaved')



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
