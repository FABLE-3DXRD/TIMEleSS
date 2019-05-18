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

Peak object
Can be either "indexedPeak" or "diffractionPeak"
indexedPeak are typically found

"""

class indexedPeak:
	"""
	Indexed Peak in 3-D RDX
	Usually from a GrainSpotter output file
	"""
	def __init__(self):
		self.omegameasured = 0.
		self.etameasured = 0.
		self.tthetameasured = 0.
		self.omegapred = 0.
		self.etapred = 0.
		self.tthetapred = 0.
		self.num = 0
		self.gvpeakid = 0
		self.peakid = 0
		self.h = 0
		self.k = 0
		self.l = 0
		self.dh = 0.0
		self.dk = 0.0
		self.dl = 0.0
	
	def setNum(self,n):
		self.num = n
		
	def setGVEID(self,n):
		self.gvpeakid = n
	def getGVEID(self):
		return self.gvpeakid
	
	def setPeakID(self,n):
		self.peakid = n
	def getPeakID(self):
		return self.peakid
	
	def setOmegaMeasured(self,o):
		self.omegameasured = o
	def getOmegaMeasured(self):
		return self.omegameasured
	
	def setEtaMeasured(self,o):
		self.etameasured = o
	def getEtaMeasured(self):
		return self.etameasured
		
	def setTThetaMeasured(self,o):
		self.tthetameasured = o
	def getTThetaMeasured(self):
		return self.tthetameasured
	
	def setOmegaPred(self,o):
		self.omegapred = o
	def getOmegaPred(self):
		return self.omegapred
	
	def setEtaPred(self,o):
		self.etapred = o
	def getEtaPred(self):
		return self.etapred
		
	def setTThetaPred(self,o):
		self.tthetapred = o
	def getTThetaPred(self):
		return self.tthetapred
	
	def setHKL(self,h,k,l):
		self.h = h
		self.k = k
		self.l = l
	
	def getHKL(self):
		return [self.h, self.k, self.l]
	
		
