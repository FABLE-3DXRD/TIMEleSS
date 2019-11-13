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


# Import libraries for mathematical operations
import numpy
import scipy
import scipy.linalg
import math


"""

Grain object
Holds information about a grain
Can be filled after parsing a GrainSpotter log or a gff file

"""

class Grain:
	"""
	Grain in 3-D RDX
	"""
	def __init__(self):
		self.U = scipy.empty([3, 3]) 			# Will hold orientation matrix
		self.UBi = scipy.empty([3, 3]) 			# Will hold inverse(U)*B  matrix of indexation before adjusting strain
		self.B = scipy.empty([3, 3]) 		    # Will hold UBi  matrix of indexation before adjusting strain
		self.eulerangles_phi1 = 0				# Euler angle 1 (Bunge convention)
		self.eulerangles_Phi = 0				# Euler angle 2 (Bunge convention)
		self.eulerangles_phi2 = 0				# Euler angle 3 (Bunge convention)
		self.NumbPeaks = 0						# Number of peaks
		self.peaks = []							# Will hold a list of peaks
		self.filename = ""						# File from which the grain was read
		self.indexInFile = 0					# Grain number in the file
		self.grainSpotterTxt = ""				# Full text from GrainSpotter log file
		
	def setFileName(self,name):
		self.filename = name
	def setFileIndex(self,index):
		self.indexInFile = index
	def getName(self):
		name = "Grain-%d" % (self.indexInFile)
		return name
	def setNPeaks(self,npeaks):
		self.NumbPeaks = npeaks
	def getNPeaks(self):
		return self.NumbPeaks
	
	def setU(self,U):
		self.U = U
	def getU(self):
		return self.U
	def setB(self,B):
		self.B = B
	def getB(self):
		return self.B
	def setUBi(self,UBi):
		self.UBi = UBi
	def getUBi(self):
		return self.UBi
	def setUBBi(self,U,B,UBi):
		self.U = U
		self.B = B
		self.UBi = UBi
	def setEulerAngles(self,phi1,Phi,phi2):
		self.eulerangles_phi1 = phi1
		self.eulerangles_Phi = Phi
		self.eulerangles_phi2 = phi2		
	def geteulerangles(self):
		return [self.eulerangles_phi1,self.eulerangles_Phi,self.eulerangles_phi2]
	
	def setPeaks(self,peaks):
		self.peaks = peaks
		
	def getPeaks(self):
		return self.peaks
	
	def getPeaksGVEID(self):
		peaklist = []
		for peak in self.peaks:
			peaklist.append(peak.getGVEID())
		return peaklist
	
	def setGrainSpotterTxt(self,txt):
		self.grainSpotterTxt = txt
	def getGrainSpotterTxt(self):
		return self.grainSpotterTxt
	
	def EulerAnglesFromU(self):
		phiRad = numpy.arccos(self.U[2,2])
		phi1Rad = -numpy.arctan2(self.U[0,2]/numpy.sin(phiRad) , self.U[1,2]/numpy.sin(phiRad)) 
		#phi1Rad = -numpy.arctan2(self.Grainspotter_U[1,2]/sin(phiRad) , self.Grainspotter_U[0,2]/sin(phiRad)) 
		phi2Rad = numpy.arctan2(self.U[2,0]/numpy.sin(phiRad) , self.U[2,1]/numpy.sin(phiRad))
		#phi2Rad = numpy.arctan2( self.Grainspotter_U[2,1]/sin(phiRad) , self.Grainspotter_U[2,0]/sin(phiRad))
		phi = math.degrees(phiRad)
		phi1 = math.degrees(phi1Rad)
		phi2 = math.degrees(phi2Rad)
		return [phi1, phi, phi2]
	
	def setEulerAnglesFromU(self):
		eulers = self.EulerAnglesFromU()
		self.phi1 = eulers[0]
		self.Phi = eulers[1]
		self.phi2 = eulers[2]
		
