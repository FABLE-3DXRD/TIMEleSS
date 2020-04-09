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

"""
Parses various files used in 3D-XRD, dealing with grains
- grainspotter output files
- gff files
"""

# System functions
import sys

# Mathematical stuff (for data array)
import scipy
import scipy.linalg

# OS and file names
import os

# Specific TIMEleSS code
from TIMEleSS.general import grain3DXRD
from TIMEleSS.general import indexedPeak3DXRD

# Import indexing from ImageD11, has stuff to go from UBi to U, etc
import ImageD11.indexing

############################################################################################# 

"""
General parser for grain files, based on file extensions.

If extension is .log, will parse for GrainSpotter log files
If extension is .gff, will parse for gff file
If extension is .ubi, will parse for ubi file

Returns 
	A list of grains

Parameters
	filename: name and path to the gff or the GrainSpotter log file
"""

def parseGrains(filename):
	fff, file_extension = os.path.splitext(filename)
	if (file_extension == ".gff"):
		return parse_gff(filename)
	elif (file_extension == ".log"):
		return parse_GrainSpotter_log(filename)
	elif (file_extension == ".ubi"):
		return parse_ubi(filename)
	else:
		print ("Error parsing %s. I do not know this file extension. Should be .log or .gff" % filename)
	return []


############################################################################################# 


"""
Parser for GrainSpotter log files

Returns 
	A list of grains

Parameters
	logfile: name and path to GrainSpotter log file
"""
def parse_GrainSpotter_log(logfile):
	# Read LOG file
	f = open(logfile, 'r')
	# reads number of grains found
	text = open(logfile).read()
	ngrains = int(text.count('Grain')-1)
	# reads all the lines and saves it to the array "content"
	logcontent = [line.strip() for line in f.readlines()]
	f.close()
	# empty array containing later the line number to all grains in the file
	headgrains = []
	# empty array containing later the peak ID and hkl to all peaks found for a grain in the file
	peakInfo = []
	logpeakid = []
	# Parsing data for each grain and putting them in a f list
	grainList = []

	# looks for the word "grain" in the file by scaning each line (starting from line 20 see above) and its corresponding line number
	i=0
	lineNumb=-1
	NumbGrain = 0 
	for i, line in enumerate(logcontent):
		i+=1
		lineNumb += 1
		items = line.find("Grain")
		if (items > -1):
			# adds the line Number to the emty array where "grain" was found
			NumbGrain += 1
			headgrains.append(lineNumb)
	headgrains.remove(headgrains[0])
	for grainnn in range(0,len(headgrains)):
		lineindex = headgrains[grainnn]
		line = logcontent[lineindex]
		# Getting number of peaks
		a=line.split()
		numbpeaks = int(a[2])  
		# for the Grainnumber I have to remove the comma from the value to use it as an interger
		GrainNumW=a[1][:-1]
		GrainNum=int(GrainNumW)
		if (numbpeaks < 1):
			print "\nWarning!!!\n\nGrain %d in %s has only %d peaks!" % (GrainNum, logfile, numbpeaks)
			print "\nSomething is very wrong with your grain spotter output file"
			print "I stop here...\n"
			sys.exit(0)
			
		#print GrainNum, a[1]
		grain = grain3DXRD.Grain()
		grain.setFileName(logfile)
		grain.setNPeaks(numbpeaks)
		grain.setFileIndex(int(GrainNum))
		# Extracting U matrix
		U = scipy.empty([3,3])
		line1 = logcontent[lineindex+3].split()
		line2 = logcontent[lineindex+4].split()
		line3 = logcontent[lineindex+5].split()
		for i in range (0,3):
			U[0,i] = float(line1[i])
			U[1,i] = float(line2[i])
			U[2,i] = float(line3[i])
		# Extracting UBI matrix
		UBI = scipy.empty([3,3])
		line1 = logcontent[lineindex+7].split()
		line2 = logcontent[lineindex+8].split()
		line3 = logcontent[lineindex+9].split()
		for i in range (0,3):
			UBI[0,i] = float(line1[i])
			UBI[1,i] = float(line2[i])
			UBI[2,i] = float(line3[i])
		#print "UBI = ", UBI
		#print "BI = ", scipy.dot(UBI,U)
		B =scipy.linalg.inv(scipy.dot(UBI,U))
		#print "B = ", B
		# Setting information
		grain.setUBBi(U,B,UBI)
		# extracting the Euler angles phi1 phi phi2
		euler = logcontent[lineindex+13].split()
		grain.setEulerAngles(float(euler[0]),float(euler[1]),float(euler[2]))
		# Reading and storing some of the peak information
		peakList = []
		for i in range (0,numbpeaks):
			thispeak = indexedPeak3DXRD.indexedPeak()
			peakinfo = logcontent[lineindex+17+i].split()
			thispeak.setNum(int(peakinfo[0]))
			thispeak.setGVEID(int(peakinfo[1]))
			thispeak.setPeakID(int(peakinfo[2]))
			thispeak.setHKL(int(peakinfo[3]), int(peakinfo[4]), int(peakinfo[5]))
			thispeak.setTThetaMeasured(float(peakinfo[12]))
			thispeak.setTThetaPred(float(peakinfo[13]))
			thispeak.setOmegaMeasured(float(peakinfo[15]))
			thispeak.setOmegaPred(float(peakinfo[16]))
			thispeak.setEtaMeasured(float(peakinfo[18]))
			thispeak.setEtaPred(float(peakinfo[19]))
			peakList.append(thispeak)
		grain.setPeaks(peakList)
		# Extracting the full text from the GrainSpotter logfile. Can be useful to generate new files
		if (grainnn < (len(headgrains)-1)):
			lineindex1 = headgrains[grainnn]
			lineindex2 = headgrains[grainnn+1]
		else:
			lineindex1 = headgrains[grainnn]
			lineindex2 = len(logcontent)-2
		txt = logcontent[lineindex1:lineindex2]
		grain.setGrainSpotterTxt(txt)
		
		# Adding the grain the the grain list
		grainList.append(grain)
	
	return grainList

############################################################################################# 


"""
Save grains (read from a GrainSpotter log) into a new GrainSpotter log file

Returns 
	Nothing

Parameters
	outputname: name and path in which to save data
	grains: a list of grains
"""
def saveGrainSpotter(outputname,grains):
	output = open(outputname,'w')
	text = """Found %d grains
Syntax:
Grain nr
#expected gvectors #measured gvectors #measured once #measured more than once
mean_IA position_x position_y position_z pos_chisq
U11 U12 U13
U21 U22 U23
U31 U32 U33

UBI11 UBI12 UBI13
UBI21 UBI22 UBI23
UBI31 UBI32 UBI33

r1 r2 r3

phi1 phi phi2

q0 qx qy qz

#  gvector_id peak_id  h k l  h_pred k_pred l_pred  dh dk dl  tth_meas tth_pred dtth  omega_meas omega_pred domega  eta_meas  eta_pred deta  IA
.
.
""" % len(grains)
	output.write(text)
	output.write("\n")
	i = 0
	totalgve = 0
	for grain in grains:
		i += 1
		text = (grain.getGrainSpotterTxt())[:] # we make a copy of the array, this is important
		# Remove first line (it includes the grain number, which we need to change)
		del text[0]
		output.write("Grain    %d, %d\n" % (i, grain.getNPeaks()))
		for line in text:
			output.write(line)
			output.write("\n")
		totalgve += grain.getNPeaks()
	textsummary = """In total %d gvectors of which %d (%d%%) were assigned:
%d (%d%%) was not assigned, something once, something more than once.""" % (len(grains), totalgve, totalgve/len(grains)*100, len(grains)-totalgve, 100-totalgve/len(grains)*100) #FIXME The words "something" have to be changed. The term "grains" is still wrong (must be G-vectors instead).
	output.write(textsummary)
	output.write("\n")
	output.close()


#############################################################################################     


"""
Parser for Gff files

Returns 
	A list of grains

Parameters
	logfile: name and path to the GFF file
"""
def parse_gff(gfffile):


	# Read gff file
	g = open(gfffile, 'r')
	# reads all the lines and saves it to the array "content"
	gffcontent = [line.strip() for line in g.readlines()]
	g.close()
	# Parsing data for each grain and putting them in a f list
	grainList = []
	#######	
# grain_id phase_id grainsize grainvolume x y z phi1 PHI phi2 U11 U12 U13 U21 U22 U23 U31 U32 U33 UBI11 UBI12 UBI13 UBI21 UBI22 UBI23 UBI31 UBI32 UBI33 eps11 eps12 eps13 eps22 eps23 eps33 

	gffcontent.remove(gffcontent[0])
	j= 0
	for lineindex in enumerate(gffcontent):
		j += 1
		line = gffcontent[int(j-1)].split()
		grain = grain3DXRD.Grain()
		grain.setFileName(gfffile)
		grain.setFileIndex(int(j))
		# Extracting U matrix
		U = scipy.empty([3,3])
		for i in range (0,3):
			U[0,i] = float(line[10+i])
			U[1,i] = float(line[13+i])
			U[2,i] = float(line[16+i])
		# Extracting UBI matrix
		UBI = scipy.empty([3,3])
		for i in range (0,3):
			UBI[0,i] = float(line[19+i])
			UBI[1,i] = float(line[22+i])
			UBI[2,i] = float(line[23+i])
		# Extracting B
		B =scipy.linalg.inv( scipy.dot(UBI,U))
		# Setting information
		grain.setUBBi(U,B,UBI)
		# extracting the Euler angles phi1 phi phi2
		grain.setEulerAngles(float(line[7]), float(line[8]),  float(line[9]))
		# Reading and storing peak information
		grainList.append(grain)

	return grainList


#############################################################################################     


"""
Parser for UBI files

Returns 
	A list of grains

Parameters
	logfile: name and path to the UBI file
"""
def parse_ubi(ubifile):


	# Read ubi file
	g = open(ubifile, 'r')
	# reads all the lines and saves it to the array "content"
	ubicontent = [line.strip() for line in g.readlines()]
	g.close()
	# Count lines with data
	ndata = 0
	for line in ubicontent:
		if (line != ""):
			ndata += 1
	ngrains = ndata/3
	
	# Parsing data for each grain and putting them in a f list
	grainList = []

	for j in range(0,ngrains):
		grainNum = j+1
		grain = grain3DXRD.Grain()
		grain.setFileName(ubifile)
		grain.setFileIndex(grainNum)
		linestart = j*4
		UBI = scipy.empty([3,3])
		for k in range(0,3):
			linecontent = ubicontent[linestart+k].split()
			UBI[k,0] = float(linecontent[0])
			UBI[k,1] = float(linecontent[1])
			UBI[k,2] = float(linecontent[2])
		# Extracting U from UBi
		U = ImageD11.indexing.ubitoU(UBI)
		# Extracting B
		B =scipy.linalg.inv( scipy.dot(UBI,U))
		# Setting information
		grain.setUBBi(U,B,UBI)
		# extracting the Euler angles phi1 phi phi2
		grain.setEulerAnglesFromU()
		# Done, we add the grain
		grainList.append(grain)
	return grainList

#############################################################################################

"""
Parser for FLT (peaks from diffraction data)

Returns 
	Two lists
	- peaks
	- idlist
	as well as the file header (the first line)
	
	idlist is the list of "spot3d_id" for each peak
	peaks is a collection of peaks, each of them is a dictionnary will all information from the flt file

Parameters
	fname: name and path to the FLT file
"""
def parseFLT(fname):
	peaks = []
	idlist = []
	# Read file
	f = open(fname, 'r')
	# Dealing with header, so we know what we are reading
	lines = f.readlines()
	header = lines[0]
	stringlist = header.split()
	del stringlist[0]
	# Reading peak information
	for line in lines:
		li=line.strip()
		peak = {}
		if not li.startswith("#"):
			litxt = li.split()
			for i in range(0,len(stringlist)):
				peak[stringlist[i]] = litxt[i]
			thisid = int(peak["spot3d_id"])
			idlist.append(thisid)
			peaks.append(peak)
	f.close()
	print ("Parsed list of peaks from flt file %s, found %i peaks" % ( fname, len(peaks)))
	return [peaks,idlist,header]

#############################################################################################

"""
Save peaks in FLT format
Expects lists similar to those generated by parseFLT

Typically used to save a list of peaks after removing a few, for instance

Parameters 
        Two lists
        - peaks (same format as read from FLT)
        - header: anyting that is before the list of peaks
        - fname: in which to save the FLT list
        
        The routine uses the last line of the header to know what to save

"""
def saveFLT(peaks, header, fname):
        headers = header.split('\n')
        txtitemstosave = headers[len(headers)-2]
        itemstosave = txtitemstosave.split()
        del itemstosave[0]
        txt = header
        for peak in peaks:
                line = "";
                for item in itemstosave:
                        line += peak.get(item) + " "
                txt += line + "\n"

        f = open(fname, 'w')
        f.write(txt)
        f.close()
        print ("Saved list of %i peaks into flt file %s" % (len(peaks), fname))
        return


#############################################################################################

"""
Parser for GVE (peaks from diffraction data, peaks coordinate have been converted into ds, eta, and etc already)

Returns 
	Two lists
	- peaks
	- idlist
	A header
	- header: anyting that is before the list of peaks
	
	idlist is the list of "spot3d_id" for each peak
	peaks is a collection of peaks, each of them is a dictionnary will all information from the gve file

Parameters
	fname: name and path to the GVE file
"""
def parseGVE(fname):
	peaks = []
	idlist = []
	header = "";
	# Read file
	inheader = True
	f = open(fname, 'r')
	for line in f.readlines():
		if (inheader):
			if ((line.strip() == "# xr yr zr xc yc ds eta omega spot3d_id xl yl zl") or (line.strip() == "#  gx  gy  gz  xc  yc  ds  eta  omega  spot3d_id  xl  yl  zl")):
				inheader = False
				stringlist = line.split()
				del stringlist[0]
			header += line
		else:
			li=line.strip()
			peak = {}
			litxt = li.split()
			for i in range(0,len(stringlist)):
				peak[stringlist[i]] = litxt[i]
			thisid = int(peak["spot3d_id"])
			idlist.append(thisid)
			peaks.append(peak)
	f.close()
	print ("Parsed list of peaks from gve file %s, found %i peaks" % ( fname, len(peaks)))
	return [peaks,idlist,header]


#############################################################################################

"""
Save peaks in GVE format
Expects lists similar to those generated by parseGVE

Typically used to save a list of peaks after removing a few, for instance

Parameters 
	Two lists
	- peaks (same format as read from GVE)
	- header: anyting that is before the list of peaks
	- fname: in which to save the GVE list
	
	The routine uses the last line of the header to know what to save

"""
def saveGVE(peaks, header, fname):
	headers = header.split('\n')
	txtitemstosave = headers[len(headers)-2]
	itemstosave = txtitemstosave.split()
	del itemstosave[0]
	txt = header
	for peak in peaks:
		line = "";
		for item in itemstosave:
			line += peak.get(item) + " "
		txt += line + "\n"
	
	f = open(fname, 'w')
	f.write(txt)
	f.close()
	print ("Saved list of %i peaks into gve file %s" % (len(peaks), fname))
	return


#############################################################################################

"""
Parser for GrainSpotter input file
Does not parse everything yet. 
At present: 
- 2theta ranges, 
- eta ranges,
- omega ranges,
- uncertainties in angles for indexing, 
- nsigma

Parameters 
	- GS input file

Returns
	A dictionnary with the GS input file information

"""
def parseGSInput(fname):
	gsInput = {}
	gsInput["tthranges"] = []
	gsInput["etaranges"] = []
	gsInput["omegaranges"] = []
	# Read file
	f = open(fname, 'r')
	for line in f.readlines():
		li=line.strip()
		if (li[0] != "!"):
			litxt = li.split()
			if (litxt[0] == "tthrange"):
				mintt = float(litxt[1])
				maxtt = float(litxt[2])
				gsInput["tthranges"].append([mintt,maxtt])
			if (litxt[0] == "uncertainties"):
				gsInput["sigma_tth"] = float(litxt[1])
				gsInput["sigma_eta"] = float(litxt[2])
				gsInput["sigma_omega"] = float(litxt[3])
			if (litxt[0] == "etarange"):
				mintt = float(litxt[1])
				maxtt = float(litxt[2])
				gsInput["etaranges"].append([mintt,maxtt])
			if (litxt[0] == "omegarange"):
				mintt = float(litxt[1])
				maxtt = float(litxt[2])
				gsInput["omegaranges"].append([mintt,maxtt])
			if (litxt[0] == "nsigmas"):
				gsInput["nsigmas"] = float(litxt[1])
	f.close()
	print ("Parsed grain spotter input file from %s" % (fname))
	return gsInput
