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

# System functions, to manipulate command line arguments
import sys
import argparse
import os.path

# Maths stuff
import numpy 
import math 
from six.moves import range


def txt2esg(inputdata,distance,output):
	# Reading text data
	text = open(inputdata).readlines()
	# Parsing it
	ttheta = []
	intensity = []
	for line in text:
		tt = line.split()
		if (tt[0] != '#'):
			ttheta.append(float(tt[0]))
			intensity.append(float(tt[1]))
	# Converting 2theta into x-scale for ESG 
	xdata = distance*numpy.tan(numpy.radians(ttheta))
	# MAUD needs a no-zero background, setting it to 10% of the intensity maximum if it is too low
	minn = min(intensity)
	maxx = max(intensity)
	if (minn < 0.1*(maxx-minn)):
		for i in range(0,len(intensity)):
			intensity[i] = intensity[i] + 0.1*(maxx-minn)
	# Save to esg
	f = open(output, 'w')
	txt = """_pd_block_id noTitle|#0

_diffrn_detector Image Plate
_diffrn_detector_type Image Plate
_pd_meas_step_count_time ?
_diffrn_measurement_method ?
_diffrn_measurement_distance_unit mm
_pd_instr_dist_spec/detc %f
_diffrn_radiation_wavelength ?
_diffrn_source_target ?
_diffrn_source_power ?
_diffrn_source_current ?
_pd_meas_angle_omega 0.0
_pd_meas_angle_chi 0.0
_pd_meas_angle_phi 0.0
_riet_par_spec_displac_x 0
_riet_par_spec_displac_y 0
_riet_par_spec_displac_z 0
_riet_meas_datafile_calibrated false
_pd_meas_angle_eta 0.0

loop_
_pd_proc_2theta_corrected
_pd_meas_intensity_total\n""" % distance
	f.write(txt)
	for i in range(0,len(intensity)):
		f.write("%f %e\n" % (xdata[i], intensity[i]))
	f.write("\n")
	f.close()
	return


#################################################################
#
# Main function, to be used if called from the command line
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
	
	parser = MyParser(usage='%(prog)s -d distance histogram.dat data.esg', description="Creates a MAUD ESG file from a text file with intensity vs. 2theta (in degrees).\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Positionnal arguments
	parser.add_argument("txtdata", help="Name of file with intensity vs. 2theta")
	parser.add_argument("output", help="Name of esg file")
	
	# Required arguments
	parser.add_argument('-d', '--distance', required=True, help="Detector distance  (in mm, required)", type=float)

	args = vars(parser.parse_args())	

	data = args['txtdata']
	distance = args['distance']
	output = args['output']

	txt2esg(data,distance,output)


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])
