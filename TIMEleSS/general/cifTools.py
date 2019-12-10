#!/usr/bin/env python
# -*- coding: utf-8 -*

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

# Needs the PycifRW module

from xfab import tools,structure,sg
from polyxsim import reflections
import numpy


def open_cif(param,phase):
	"""
	Open a cif file a build a structure for phase number "phase"
	filename: param['structure_phase_%i' %phase]
	
	returns 
	- a structure with cif information
	
	sets
	- param['sgno_phase_%i' %phase] : space group number
	- param['sgname_phase_%i' %phase] : space group name
	- param['cell_choice_phase_%i' %phase] : not 100% sure
	- param['unit_cell_phase_%i' %phase] : unit cell parameters as [a,b,c,alpha,beta,gamma']
	
	Adapted from polyxsim.structure
	Created: 12/2019, S. Merkel, Univ. Lille, France
	"""
	file = param['structure_phase_%i' %phase]
	struct = structure.build_atomlist()
	struct.CIFread(ciffile=file)
	param['sgno_phase_%i' %phase] = sg.sg(sgname=struct.atomlist.sgname).no
	param['sgname_phase_%i' %phase] = struct.atomlist.sgname
	param['cell_choice_phase_%i' %phase] = sg.sg(sgname=struct.atomlist.sgname).cell_choice
	param['unit_cell_phase_%i' %phase] =  struct.atomlist.cell
	return struct


def build_B_from_Cif(ciffile):
	"""
	Builds a B-matrix based on information in a cif file
	
	Parameter:
	- cif file name
	
	Returns
	- B matrix, as in polyxsim (watch out for the 2pi factor!!)
	
	Created: 12/2019, S. Merkel, Univ. Lille, France
	"""
	param['structure_phase_0'] = ciffile
	xtal_structure = open_cif(param,0)
	unit_cell = param['unit_cell_phase_0']
	B = tools.form_b_mat(unit_cell)
	return B


def gen_Miller_ds(param,phasenum):
	"""
	Generate a list of peaks for a given crystal structure
	
	Parameter:
	- param
	- phasenum: phase number
	
	In the param dictionnary
	- param['theta_min']
	- param['theta_max']
	- param['wavelength']
	- param['unit_cell_phase_%i' % phasenum] as [a,b,c,alpha,beta,gamma']
	- param['sgname_phase_%i' % phasenum]: space group number
	- param['cell_choice_phase_%i' % phasenum]
	
	Returns
	- an array of hkl with hkl[i]=[h, k, l, ds] with ds = 1/d
	
	Inspired from code in polyxsim.reflections, with the addition of ds in return value
	Created: 12/2019, S. Merkel, Univ. Lille, France
	"""
	sintlmin = numpy.sin(numpy.radians(param['theta_min']))/param['wavelength']
	sintlmax = numpy.sin(numpy.radians(param['theta_max']))/param['wavelength']
	hkl  = tools.genhkl_all(param['unit_cell_phase_%i' % phasenum], \
				sintlmin, \
				sintlmax, \
				sgname=param['sgname_phase_%i' % phasenum], \
				cell_choice=param['cell_choice_phase_%i' % phasenum], \
				output_stl=True)
	# Calculating ds, with is 2*sin(theta)/lambda
	hkl[:,3] = hkl[:,3]*2
	# print hkl
	# exit()
	return hkl


def calc_intensity(hkl,struct,wavelength,normI=False):
	"""
	Calculate the reflection intensities for single-crystal diffraction peaks
	Effect of structure factor and Lorentz correction
	
	Param
	- hkl : an array of hkl with hkl[i]=[h, k, l, ds] with ds = 1/d
	- struct : structure information read from a cif file
	- wavelength
	- normI: if set to True, intensities are normalized to a maximum of 100
	
	Returns
	- an array of hkl with hkl[i]=[h, k, l, ds, i]
	
	Inspired from code in polyxsim.reflections, with the addition of Lorentz correction
	Created: 12/2019, S. Merkel, Univ. Lille, France
	"""
	int = numpy.zeros((len(hkl),1))
	for i in range(len(hkl)):
		#check_input.interrupt(killfile)
		(Fr, Fi) = structure.StructureFactor(hkl[i][0:3], \
							struct.atomlist.cell, \
							struct.atomlist.sgname, \
							struct.atomlist.atom, \
							struct.atomlist.dispersion)
		int[i] = Fr**2 + Fi**2    
		ds = hkl[i][3]
		theta = numpy.arcsin(ds*wavelength/2.)
		int[i] = int[i]/numpy.sin(2.*theta)
	if (normI):
		maxI = max(int)
		int = 100.*int/maxI
	hkl = numpy.concatenate((hkl,int),1)
	return hkl


def peaksFromCIF(ciffile, ttheta_min,  ttheta_max, wavelength, minI = -1.0, normI = False):
	"""
	Calculate a list of reflections for single-crystal diffraction based on a cif file
	
	Returns:
		an array in which eack line holds
			- h, k, l
			- ds = 1/d (in anstroms)
			- intensity for single-crystal diffraction
			- 2theta (in degrees)
	
	Intensities include the effect of structure factor and Lorentz correction
	
	Params:
	- cif file
	- ttheta_min (in degrees)
	- ttheta_max (in degrees)
	- wavelength (in angstroms)
	- normI: if set to True, intensities are normalized to a maximum of 100
	- minI: remove peaks with an intensity <= that minI. Default is -1.0 (returns everything)
	
	Created: 12/2019, S. Merkel, Univ. Lille, France
	Inspired from fitAllB/reject.py
	Heavily adatped to account for Lorentz correction, normalize intensities, and filter peaks
	"""
	param = {} 
	param['structure_phase_0'] = ciffile
	param['theta_min'] = ttheta_min/2.
	param['theta_max'] = ttheta_max/2.
	param['wavelength'] = wavelength
	
	# Reads structure from CIF file
	xtal_structure = open_cif(param,0)
	
	# Calculates list of reflection, ds and their intensities
	hkls = gen_Miller_ds(param,0)
	hkls = calc_intensity(hkls,xtal_structure, wavelength, normI) 
	
	# Calculating twotheta
	ds = hkls[:,3]
	tth = numpy.degrees(2.0*numpy.arcsin(ds*param['wavelength']/2))
	twotheta = numpy.zeros([len(ds),1])
	twotheta[:,0] = tth[:]
	hkls = numpy.concatenate((hkls,twotheta),1)
	# Remove peaks with intensities below threshold
	if (minI > 0.0):
		intensity = hkls[:,4]
		hkls = hkls[intensity>minI]
		
	return hkls
	
