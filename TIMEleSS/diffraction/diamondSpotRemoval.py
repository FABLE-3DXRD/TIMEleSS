#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python 2 to python 3 migration tools
from __future__ import absolute_import
from __future__ import print_function # To make print statements compatible with python3
from six.moves import range


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
Functions to remove diamond spots from a 3D-XRD images
 - test of various filter options
 - creation of new EDF files with median and diamond spots removed (ready for peak searching)
 
Original version, 6/Jul/2012
"""



# System functions, to manipulate command line arguments
import sys
import argparse
import os.path

# string module contains a number of functions that are useful for manipulating strings
import string

# Mathematical stuff (for data array and image processsing)
import numpy
import scipy
import scipy.ndimage
import scipy.ndimage.filters
import scipy.ndimage.morphology

# Image manipulation library
import PIL.Image

# Inpaint into a mask
from . import inpaint

# Fabio, from ESRF fable package
import fabio
import fabio.edfimage

# Plotting library
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


##########################################################################################################

def testSpotDetection(edfimagepath, stem, first, last, medianename, ndigits=4, extension='edf', scale=400, filtersize=3, threshold=5.):
	"""
	Graphical test of diamond spot detection. It will scan through the list of diffraction images, 
	plot the reduced and filtered image and show the list of detected spots
	
	edfimagepath: Path to the EDF images. The median image is assumed to be in the same directory
	stem: Stem for EDF images.
	first: First image number
	last: Last image number
	medianename: Name of median EDF file (in full, with extension)
	ndigits: Number of digits for EDF file numbering.
	extension: EDF file extension.
	scale: X dimension to which the image will be reduced (in pixels, the image is assumed to be square)
	filtersize: size of median filter to apply on reduced image to remove smaller spots
	threshold: threshold for spot detection, in multiples of image mean intensity
	"""

	# Read median image
	imagename = os.path.join(edfimagepath, medianename)
	medianeIm = fabio.edfimage.edfimage()
	medianeIm.read(imagename)
	print("Dimensions of median image: ", medianeIm.shape)
	medianeData = medianeIm.data.astype('float32')
	print("Dimensions of median image: ", medianeIm.shape)
	print("Median info: ", medianeData.min(),  medianeData.max(), medianeData.mean())
	
	# Loop on images and test median substraction
	for i in range(first,last+1):
		# Read image data
		format = "%s%0" + str(ndigits) + "d." + extension
		image = format % (stem,i)
		imagename = os.path.join(edfimagepath, image)
		print("Reading " + imagename)
		im = fabio.edfimage.edfimage()
		im.read(imagename)
		print("Dimensions: ", im.shape)
		data = im.data.astype('float32')
		print("Image info (min, max, mean): ", data.min(),  data.max(), data.mean())
		print("Substraction median...")
		# Removing median image
		data = data-medianeData
		# Removing anything below 0
		data = data.clip(min=0)
		oldmean = data.mean()
		oldmax = data.max()
		oldmin = data.min()
		# Resizing data, we do not need full resolution to find diamond spots!
		# Better to work on low resolution, removed a lot of false positives
		# Nearest interpolation is important to keep the spots and avoid oversmoothing the image
		# http://matplotlib.sourceforge.net/users/image_tutorial.html
		print("Rescaling to %dx%d..." % (scale,scale))
		# Scipy.misc.imresize is deprecated
		# Moving to a similar call using the PIL library
		# datascale = scipy.misc.imresize(data,(scale,scale),interp='nearest')
		datascale = numpy.array(PIL.Image.fromarray(data).resize((scale,scale),resample=PIL.Image.NEAREST))
		max = datascale.max()
		datascale = datascale*oldmax/max
		meandata = datascale.mean()
		mindata = datascale.min()
		maxdata = datascale.max()
		# Applying a median filter for removal of smaller spots
		print("Applying %d pixels median filter to removed smalled spots..." % (filtersize))
		datascale2 = scipy.ndimage.filters.median_filter(datascale,size=filtersize)
		max = datascale2.max()
		if (max > 0):
			datascale2 = datascale2*oldmax/max
		min = datascale2.min()
		max = datascale2.max()
		mean = datascale2.mean()
		# Plot data
		if i==first:
			plt.title(image + " scaled to " + str(scale) + "x " + str(scale))     # set a title
			p = plt.imshow(datascale,origin='lower')                              # plot the image
			p.set_cmap('gray')                                                    # use gray scale
			plt.clim(mindata, threshold*meandata)                                 # set the color limits
			plt.pause(0.5)                                                        # open the window and wait
		else:
			plt.title(image + " scaled to " + str(scale) + "x " + str(scale)) 
			p.set_data(datascale)
			plt.clim(mindata, threshold*meandata)
			plt.pause(0.5)
		# print("Image info median filter: ", min,  max, mean)
		print("Thresholding above %.1f times the mean..." % (threshold))
		mask = (datascale2 > threshold*mean).astype(numpy.int8)
		# Plot mask
		plt.title(image + " filtered and thresholded")
		p.set_data(mask)
		plt.clim(0, 1)
		plt.pause(0.5)

##########################################################################################################

def createMask(edfimagepath, stem, first, last, medianename, ndigits=4, extension='edf', scale=400, filtersize=3, threshold=5., growXY=20, growXYO=2, c_rawy=None, c_rawz=None, radius=None):
	"""
	Creates a mask around diamond spots for all images
	
	edfimagepath: Path to the EDF images. The median image is assumed to be in the same directory
	stem: Stem for EDF images.
	first: First image number
	last: Last image number
	medianename: Name of median EDF file (in full, with extension)
	ndigits: Number of digits for EDF file numbering.
	extension: EDF file extension.
	scale: X dimension to which the image will be reduced (in pixels, the image is assumed to be square)
	filtersize: size of median filter to apply on reduced image to remove smaller spots
	threshold: threshold for spot detection, in multiples of image mean intensity
	growXY: number of pixels to grow the mask in X and Y. 20 is a reasonable value
	growXYO: number of pixels to further grow the mask in X, Y, and Omega. 2 is a reasonable value
	c_rawy: Raw Y position of beam center (optional). Can be seem in Fabian. Just go over the center with your mouse with the image shown with orientation 1 0 0 1.
	c_rawz: Raw Z position of beam center (optional). Can be seem in Fabian. Just go over the center with your mouse with the image shown with orientation 1 0 0 1.
	radius: radius of disk to ignore around the beam center (in pixels, optional). c_rawy and c_rawz are mendatory if you want to use this option
	"""
		
	# Read median image
	print("Loading median image")
	imagename = os.path.join(edfimagepath, medianename)
	medianeIm = fabio.edfimage.edfimage()
	medianeIm.read(imagename)
	medianeData = medianeIm.data.astype('float32')
	xsize = medianeIm.shape[-1]
	ysize = medianeIm.shape[-2]
	
	# Allocate space for mask
	print("Allocating memory for mask")
	mask = numpy.empty([last-first+1,scale,scale],dtype=numpy.int8)
	print("Mask will be %.2f Mb" % (mask.size*mask.itemsize/1048576.))
	
	# Loop on images and test median substraction
	for i in range(first,last+1):
		# Read image data
		format = "%s%0" + str(ndigits) + "d." + extension
		image = format % (stem,i)
		imagename = os.path.join(edfimagepath, image)
		print("Reading " + imagename + " and creating corresponding mask")
		im = fabio.edfimage.edfimage()
		im.read(imagename)
		data = im.data.astype('float32')
		# Removing median image
		data = data-medianeData
		# Removing anything below 0
		data = data.clip(min=0)
		oldmean = data.mean()
		oldmax = data.max()
		oldmin = data.min()
		# Resizing data, we do not need full resolution to find diamond spots!
		# Better to work on low resolution, removed a lot of false positives
		# datascale = scipy.misc.imresize(data,(scale,scale),interp='nearest')
        # Scipy.misc.imresize is deprecated
		# Moving to a similar call using the PIL library
		datascale = numpy.array(PIL.Image.fromarray(data).resize((scale,scale),resample=PIL.Image.NEAREST))
		max = datascale.max()
		datascale = datascale*oldmax/max
		meandata = datascale.mean()
		mindata = datascale.min()
		maxdata = datascale.max()
		# Applying a median filter for removal of smaller spots
		datascale2 = scipy.ndimage.filters.median_filter(datascale,size=filtersize)
		max = datascale2.max()
		if (max > 0):
			datascale2 = datascale2*oldmax/max
			min = datascale2.min()
			max = datascale2.max()
			mean = datascale2.mean()
		else:
			mean = 0
		# Creating mask with threshold
		# print("threshold: ", threshold)
		thismask = (datascale2 > threshold*mean).astype(numpy.int8)
		# Growing mask in X and Y
		print("Growing  mask by " + str(growXY) + " pixels in X and Y")
		thismask = scipy.ndimage.morphology.binary_dilation(thismask,iterations=growXY)
		mask[i-first::] = thismask
	# Smoothing (removed, it was not helping and removing real spots
	#print("Smoothing global mask")
	# Remove small white regions
	#mask = scipy.ndimage.binary_opening(mask)
	# Remove small black hole
	#mask = scipy.ndimage.binary_closing(mask)
	# Growing mask around the values we found
	# See http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.morphology.binary_dilation.html
	print("Growing  global mask by " + str(growXYO) + " pixels in X, Y, and omega")
	mask = scipy.ndimage.morphology.binary_dilation(mask,iterations=growXYO)
	# Clearing central disk
	if (radius != None):
		print("Removing portion of mask within the central radius")
		c_rawy = c_rawy*scale/xsize
		c_rawz = c_rawz*scale/ysize
		radius = radius*scale/xsize
		maskonmask = numpy.ones((scale,scale),dtype=numpy.int8)
		for i in range (0,scale):
			for j in range(0,scale):
				d = numpy.sqrt((j-c_rawy)*(j-c_rawy)+(i-c_rawz)*(i-c_rawz))
				if (d<radius):
					maskonmask[i,j] = 0
		for i in range(first,last+1):
			thismask = mask[i-first]   
			thismask = numpy.multiply(thismask,maskonmask)
			mask[i-first] = thismask
	print("Mask is ready")
	return mask


##########################################################################################################

def plotMask(edfimagepath, stem, first, last, mask, ndigits=4, extension='edf'):
	"""
	Plot images with the mask in overlay
	
	edfimagepath: Path to the EDF images. The median image is assumed to be in the same directory
	stem: Stem for EDF images.
	first: First image number
	last: Last image number
	mask: mask data
	ndigits: Number of digits for EDF file numbering.
	extension: EDF file extension.
	"""
	print("Preparing to test mask"  )
	# Loop on images and plot corresponding mask
	for i in range(first,last+1):
		# Read image data
		format = "%s%0" + str(ndigits) + "d." + extension
		image = format % (stem,i)
		imagename = os.path.join(edfimagepath, image)
		print("Reading " + imagename + " and showing corresponding mask")
		im = fabio.edfimage.edfimage()
		im.read(imagename)
		data = im.data.astype('float32')
		mean = data.mean()
		max = data.max()
		min = data.min()
		xsize = im.shape[-1]
		ysize = im.shape[-2]
		# Preparing mask
		thismask = mask[i-first]
		thismask = thismask.astype(numpy.float32) # New versions of python do not like resizing with integer...
		# maskscaled = scipy.misc.imresize(thismask,(xsize,ysize),interp='nearest')
        # Scipy.misc.imresize is deprecated
		# Moving to a similar call using the PIL library
		# datascale = scipy.misc.imresize(data,(scale,scale),interp='nearest')
		maskscaled = numpy.array(PIL.Image.fromarray(thismask).resize((xsize,ysize),resample=PIL.Image.NEAREST))
		# Plotting data and mask
		plt.title(image)                                   # set a title
		p = plt.imshow(data, cmap='gray',origin='lower')          # plot the image
		plt.clim(min, 3*mean)   # set the color limits
		p2 = plt.imshow(maskscaled, origin='lower', cmap='OrRd', alpha=0.6)
		plt.pause(0.5)                                      # open the window and wait
		plt.clf() # clear the plot and get ready for the next one

##########################################################################################################

def testClearMask(edfimagepath, stem, first, last, medianename, mask, ndigits=4, extension='edf'):
	"""
	Plot images with the median and mask removed
	
	edfimagepath: Path to the EDF images. The median image is assumed to be in the same directory
	stem: Stem for EDF images.
	first: First image number
	last: Last image number
	medianename: Name of median EDF file (in full, with extension)
	mask: mask data
	ndigits: Number of digits for EDF file numbering.
	extension: EDF file extension.
	"""
	print("Loading median data")
	# Read median image
	imagename = os.path.join(edfimagepath, medianename)
	medianeIm = fabio.edfimage.edfimage()
	medianeIm.read(imagename)
	medianeData = medianeIm.data.astype('float32')
	
	# Loop on images and test median substraction
	for i in range(first,last+1):
		# Read image data
		format = "%s%0" + str(ndigits) + "d." + extension
		image = format % (stem,i)
		imagename = os.path.join(edfimagepath, image)
		print("Reading " + imagename + ", substracting median, and clearing data below mask")
		im = fabio.edfimage.edfimage()
		im.read(imagename)
		data = im.data.astype('float32')
		# Removing median image
		data = data-medianeData
		# Removing anything below 0
		data = data.clip(min=0)
		mean = data.mean()
		median = numpy.median(data)
		max = data.max()
		min = data.min()
		xsize = im.shape[-1]
		ysize = im.shape[-2]
		# Preparing mask
		thismask = mask[i-first]
		thismask = thismask.astype(numpy.float32) # New versions of python do not like resizing with integer...
		# maskscaled = scipy.misc.imresize(thismask,(xsize,ysize),interp='nearest')
		# Scipy.misc.imresize is deprecated
		# Moving to a similar call using the PIL library
		maskscaled = numpy.array(PIL.Image.fromarray(thismask).resize((xsize,ysize),resample=PIL.Image.NEAREST))
		# Creating data under mask using linear interpolation or inpainting
		# Need to create a list of points for which we have data
		# Actually, gave up, fill with median value!
		idx=(maskscaled>0)
		data[idx]=median
		# Plotting data
		plt.title(image)                                   # set a title
		p = plt.imshow(data, cmap='gray',origin='lower')   # plot the image
		plt.clim(min, 3*mean)                              # set the color limits
		plt.pause(0.5)                                     # open the window and wait
		plt.clf()                                          # clear the plot and get ready for the next one


##########################################################################################################

def saveDataClearMask(edfimagepath, newpath, stem, first, last, medianename, mask, ndigits=4, extension='edf', doinpaint=False):
	"""
	Save new EDF files with the median and mask removed
	
	edfimagepath: Path to the EDF images. The median image is assumed to be in the same directory
	newpath: Path to save the new EDF images.
	stem: Stem for EDF images.
	first: First image number
	last: Last image number
	medianename: Name of median EDF file (in full, with extension)
	mask: mask data
	ndigits: Number of digits for EDF file numbering.
	extension: EDF file extension.
	doinpaint: if set to true, fills diamond mask with inpainting. If not set, diamond mask is filled with median value
	"""
	if ((not (os.path.isdir(newpath))) or (not (os.path.exists(newpath)))) :
		print("ERROR! %s is not a directory or does not exist.\nAborting." % newpath)
		return
	if (os.path.samefile(edfimagepath, newpath)):
		print("ERROR!\nImages are read from %s.\nNew EDF should be saved in %s.\nThis will destroy the original data.\nAborting" % (edfimagepath, newpath))
		return
	print("Reading median image")
	# Read median image
	imagename = os.path.join(edfimagepath, medianename)
	medianeIm = fabio.edfimage.edfimage()
	medianeIm.read(imagename)
	medianeData = medianeIm.data.astype('float32')
	
	if (doinpaint):
		print ("Filling mask with inpainting")
	else:
		print ("Filling mask with median value")
	
	# Loop on images and test median substraction
	for i in range(first,last+1):
		# Read image data
		format = "%s%0" + str(ndigits) + "d." + extension
		image = format % (stem,i)
		imagename = os.path.join(edfimagepath, image)
		print("Reading and processing " + imagename)
		im = fabio.edfimage.edfimage()
		im.read(imagename)
		data = im.data.astype('float32')
		header = im.header
		# Removing median image
		data = data-medianeData
		# Removing anything below 0
		data = data.clip(min=0)
		meanI = data.mean()
		medianI = numpy.median(data)
		maxI = data.max()
		minI = data.min()
		xsize = im.shape[-1]
		ysize = im.shape[-2]
		# Preparing mask
		thismask = mask[i-first]
		thismask = thismask.astype(numpy.float32) # New versions of python do not like resizing with integer...
		#maskscaled = scipy.misc.imresize(thismask,(xsize,ysize),interp='nearest',mode='F')		# Scipy.misc.imresize is deprecated
		# Moving to a similar call using the PIL library
		maskscaled = numpy.array(PIL.Image.fromarray(thismask).resize((xsize,ysize),resample=PIL.Image.NEAREST))
		# Creating data under mask using linear interpolation or inpainting
		# Need to create a list of points for which we have data
		# Actually, gave up, fill with median value!
		idx=(maskscaled>0)
		if (doinpaint):
			# Creating data under mask using inpainting
			# We rescale the image and inpaint on a smaller version. Before reducing, remove extreme intensity values (it works better)
			datacopy = data.copy()
			datacopy = datacopy.clip(0., 10.*meanI)
			#datareduced = scipy.misc.imresize(datacopy,(thismask.shape[0],thismask.shape[1]),interp='nearest',mode='F')
			# Scipy.misc.imresize is deprecated
			# Moving to a similar call using the PIL library
			datareduced = numpy.array(PIL.Image.fromarray(datacopy).resize((thismask.shape[0],thismask.shape[1]),resample=PIL.Image.NEAREST))
			# Setting mask data as NaN and call for inpainting. Parameters have been set from trial and error
			idx2=(thismask>0)
			datareduced[idx2] = numpy.NaN
			result0 = inpaint.replace_nans(datareduced, max_iter=20, tol=1., kernel_radius=2, kernel_sigma=5, method='idw')
			# Rescaling inpainted image and set new values at mask positions
			# result0 = scipy.misc.imresize(result0,(xsize,ysize),interp='nearest',mode='F')
			# Scipy.misc.imresize is deprecated
			# Moving to a similar call using the PIL library
			result0 = numpy.array(PIL.Image.fromarray(result0).resize((xsize,ysize),resample=PIL.Image.NEAREST))
			data[idx] = result0[idx]
		else:
			# Fill maslwith median value!
			data[idx]=medianI
		# Save new data
		newname = os.path.join(newpath, image)
		print("Saving new EDF with median and mask removed in " + newname)
		im = fabio.edfimage.edfimage()
		im.read(imagename)
		im.data = (data.astype('uint32'))
		im.header = header
		im.save(newname)

    
##########################################################################################################


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
	print("Diamond spot removal for 3D-XRD in the DAC")
	print("This is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	usage = "usage: %(prog)s [options] todo"
	desc="""

Usage:
 - %(prog)s [options] spots: test spot detection parameters
 - %(prog)s [options] plotMask: try to create a mask a plot an overlay of images and corresponding mask
 - %(prog)s  [options] clearMask: create a mask and display images with median and mask removed
 - %(prog)s  [options] save: save new images with median and mask removed in EDF

Basic examples:
 - %(prog)s -P Edf-P02-Ti-Close -n P02-Ti-02_ -m P02-Ti-02_m20100.edf -f 50 -l 65 spots
 - %(prog)s -P Edf-P02-Ti-Close -n P02-Ti-02_ -m P02-Ti-02_m20100.edf -f 50 -l 65 -s Edf-P02-Ti-Close-Filtered save

Complex example:
 - %(prog)s -P Edf-P02-Ti-Close -n P02-Ti-02_ -m P02-Ti-02_m20100.edf -f 50 -l 65 --growXY=25 --growXYO=2 --c_rawy=1097 --c_rawz=922 --radius=300 --filtersize=3 -t 1.5 -s Edf-P02-Ti-Close-Filtered/ save

Typically, you start by testing the spot parameters and improve you match by playing with the threshold and filtersize parameter, and you then try creating a mask.

This is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n

"""

	parser = MyParser(usage=usage, description=desc, formatter_class=argparse.RawTextHelpFormatter)
	
	
	# Required arguments
	parser.add_argument('todo', help="What shall we do? Options are spots, plotMask, clearMask, save")
	
	parser.add_argument('-n', '--stem', required=True, help="Stem for EDF image files (required)")
	parser.add_argument('-f', '--first', required=True, help="First image number (mendatory)", type=int)
	parser.add_argument('-l', '--last', required=True, help="First image number (mendatory)", type=int)
	parser.add_argument('-m', '--median', required=True, help="Name of median image (mendatory)")
    
	# Optionnal arguments
	parser.add_argument('-P', '--path', required=False, help="Path to EDF images. Default is %(default)s", default="./")
	parser.add_argument('--newpath', required=False, help="Path to save the new EDF image. Default is %(default)s", default="./")
	parser.add_argument('-d', '--digits', required=False, help="Number of digits for file number. Default is %(default)s", type=int, default=4)
	parser.add_argument('-e', '--ext', required=False, help="Extension for EDF images. Default is %(default)s", default="edf")
	parser.add_argument('--scale', required=False, type=int, help="X dimension to which the image will be reduced (in pixels, the image is assumed to be square, used to blur the image). Default is %(default)s", default=400)
	parser.add_argument('--filtersize', required=False, type=int, help="Width of median filter to ignore small spots in diamond detection (in pixels). Default is %(default)s", default=4)
	parser.add_argument('-t', '--threshold', required=False, type=float, help="Threshold for diamond spot detection, in multiples of image mean intensity. Default is %(default)s", default=2.)
	parser.add_argument('--growXY', required=False, type=int, help="Number of pixels to grow the mask in X and Y (useless in spot detection). Default is %(default)s", default=15)
	parser.add_argument('--growXYO', required=False, type=int, help="Number of pixels to grow the mask in X, Y, and omega (useless in spot detection). Default is %(default)s", default=2)
	parser.add_argument('--c_rawy', required=False, type=int, help="Raw Y position of beam center (can be read directly in Fabian, plot your image with orientation 1 0 0 1, it is the first number displayed to locate the cursor). Used to ignore a disk at the center of the image. If you have large intensity spots which are not diamond in there.", default=None)
	parser.add_argument('--c_rawz', required=False, type=int, help="Raw Z position of beam center (can be read directly in Fabian, plot your image with orientation 1 0 0 1, it is the first number displayed to locate the cursor). Used to ignore a disk at the center of the image. If you have large intensity spots which are not diamond in there.", default=None)
	parser.add_argument('--radius', required=False, type=int, help="Radius of disk to ignore around the beam center (in pixels, optional). c_rawy and c_rawz are mendatory if you want to use this option. . Used to ignore a disk at the center of the image. If you have large intensity spots which are not diamond in there.", default=None)
	parser.add_argument('--inpaint', required=False, type=bool, help="If set to True, fill diamond mask with inpainting. If not set, diamond mask is filled with median value.", default=False)
	
	args = vars(parser.parse_args())
	
	todo = args['todo']
	
	stem = args['stem']
	first = args['first']
	last = args['last']
	median = args['median']
	
	edfimagepath = args['path']
	ndigits = args['digits']
	extension = args['ext']
	newpath = args['newpath']

	scale = args['scale']
	filtersize = args['filtersize']
	threshold = args['threshold']
	growXY = args['growXY']
	growXYO = args['growXYO']

	c_rawy = args['c_rawy']
	c_rawz = args['c_rawz']
	radius = args['radius']
	
	inpaint = args['inpaint']


	error = False
	if (radius != None):
		if ((c_rawy == None) or (c_rawz == None)):
			print("ERROR: beam center position need if you want to define a radius")
			error = True
	
	if (error):
		parser.error("try option -h for help\n")
		sys.exit(2)

	# Processes and does what should be done...
	if (todo == 'spots'):
		testSpotDetection(edfimagepath, stem, first, last, median, ndigits=ndigits, extension=extension, scale=scale, filtersize=filtersize, threshold=threshold)
	elif (todo == 'plotMask'):
		mask = createMask(edfimagepath, stem, first, last, median, ndigits=ndigits, extension=extension, scale=scale, filtersize=filtersize, threshold=threshold, growXY=growXY, growXYO=growXYO, c_rawy=c_rawy, c_rawz=c_rawz, radius=radius)
		plotMask(edfimagepath, stem, first, last, mask, ndigits=ndigits, extension=extension)
	elif (todo == 'clearMask'):
		mask = createMask(edfimagepath, stem, first, last, median, ndigits=ndigits, extension=extension, scale=scale, filtersize=filtersize, threshold=threshold, growXY=growXY, growXYO=growXYO, c_rawy=c_rawy, c_rawz=c_rawz, radius=radius)
		testClearMask(edfimagepath, stem, first, last, median, mask, ndigits=ndigits, extension=extension)
	elif (todo == 'save'):
		if (newpath == None):
			print("ERROR: No new path to save data!")
			parser.error("try option -h for help\n")
			sys.exit(2)
		if ((not (os.path.isdir(newpath))) or (not (os.path.exists(newpath)))) :
			print("ERROR! %s is not a directory or does not exist.\nAborting." % newpath)
			sys.exit(2)
		if (os.path.samefile(edfimagepath, newpath)):
			print("ERROR!\nImages are read from %s.\nNew EDF should be saved in %s.\nThis will destroy the original data.\nAborting" % (edfimagepath, newpath))
			sys.exit(2)
		mask = createMask(edfimagepath, stem, first, last, median, ndigits=ndigits, extension=extension, scale=scale, filtersize=filtersize, threshold=threshold, growXY=growXY, growXYO=growXYO, c_rawy=c_rawy, c_rawz=c_rawz, radius=radius)
		saveDataClearMask(edfimagepath, newpath, stem, first, last, median, mask, ndigits=ndigits, extension=extension, doinpaint=inpaint)
	else:
		print("Not sure what to do. Try " + sys.argv[0] + " --help\n")


##########################################################################################################


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling main, if necessary
if __name__ == "__main__":
    main(sys.argv[1:])
