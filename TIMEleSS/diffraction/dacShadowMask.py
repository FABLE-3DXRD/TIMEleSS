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

# string module contains a number of functions that are useful for manipulating strings
import string

# Mathematical stuff (for data array)
import numpy
import scipy
import scipy.ndimage
import scipy.ndimage.filters
import scipy.ndimage.morphology

# Image manipulation library
import PIL.Image

# Fabio, from ESRF fable package
import fabio
import fabio.edfimage

# Plotting library
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


##########################################################################################################

def dacShadowMask(edfimagepath, newpath, stem, first, last, ndigits=4, extension='edf', scale=200, filtersize=3, threshold=1., c_rawy=None, c_rawz=None, radius=None):
  

  if ((not (os.path.isdir(newpath))) or (not (os.path.exists(newpath)))) :
      print("ERROR! %s is not a directory or does not exist.\nAborting." % newpath)
      return
  if (os.path.samefile(edfimagepath, newpath)):
      print("ERROR!\nImages are read from %s.\nNew EDF should be saved in %s.\nThis will destroy the original data.\nAborting" % (edfimagepath, newpath))
      return
     
  #c_rawy = c_rawy*scale/2048
  #c_rawz = c_rawz*scale/2048
  #radius = radius*scale/2048    
  for i in range(first,last+1):
    format = "%s%0" + str(ndigits) + "d." + extension
    image = format % (stem,i)
    imagename = os.path.join(edfimagepath, image)
    print("Reading and processing " + imagename)
    im = fabio.edfimage.edfimage()
    im.read(imagename)
    data = im.data.astype('float32')
    header = im.header
    oldmean = data.mean()
    oldmax = data.max()
    oldmin = data.min()
    xsize = im.shape[-1]
    ysize = im.shape[-2]
    # Plot the image
    plt.title(image)
    p = plt.imshow(data,origin='lower')
    p.set_cmap('gray')
    plt.clim(oldmin, 3*oldmean)
    plt.pause(0.5)
    # Removing anything to high in intensity
    datacut = data.clip(max=2*oldmean)
    median = numpy.median(data)
    # Resizing data
    print("Rescaling to %dx%d..." % (scale,scale))
    # datascale = scipy.misc.imresize(datacut,(scale,scale),interp='bicubic')
    # Scipy.misc.imresize is deprecated
    # Moving to a similar call using the PIL library
    datascale = numpy.array(PIL.Image.fromarray(datacut).resize((scale,scale),resample=PIL.Image.BICUBIC))
    max = datascale.max()
    datascale = datascale*oldmax/max
    meandata = datascale.mean()
    mindata = datascale.min()
    maxdata = datascale.max()
    # Applying a median filter
    print("Applying %d pixels median filter" % (filtersize))
    datascale2 = scipy.ndimage.filters.median_filter(datascale,size=filtersize)
    max = datascale2.max()
    if (max > 0):
        datascale2 = datascale2*oldmax/max
    min = datascale2.min()
    max = datascale2.max()
    mean = datascale2.mean()
    # Creating mask with threshold
    thismask = (datascale2 < threshold*meandata).astype(numpy.int8)
    # Smoothing the mask
    # Remove small white regions
    thismask =  scipy.ndimage.binary_opening(thismask)  
    # Remove small black hole
    thismask =  scipy.ndimage.binary_closing(thismask)
    # Clearing central disk
    if (radius != None):
      print("Removing portion of mask within the central radius")
      maskonmask = numpy.ones((scale,scale),dtype=numpy.int8)
      for i in range(0,scale):
          for j in range(0,scale):
            d = numpy.sqrt((j-c_rawy)*(j-c_rawy)+(i-c_rawz)*(i-c_rawz))
            if (d<radius):
               maskonmask[i,j] = 0
      for i in range(first,last+1):
           thismask = numpy.multiply(thismask,maskonmask)
    print("Mask is ready")
    # Preparing mask
    # maskscaled = scipy.misc.imresize(thismask,(xsize,ysize),interp='bicubic')
    # Scipy.misc.imresize is deprecated
    # Moving to a similar call using the PIL library
    maskscaled = numpy.array(PIL.Image.fromarray(thismask).resize((xsize,ysize),resample=PIL.Image.BICUBIC))
    # Creating data under mask using linear interpolation or inpainting
    # Need to create a list of points for which we have data
    # Actually, gave up, fill with median value!
    idx=(maskscaled>0)
    data[idx]=median
    # Plotting data
    plt.title(image)                                   # set a title
    p = plt.imshow(data, cmap='gray',origin='lower')   # plot the image
    plt.clim(oldmin, 3*oldmean)                              # set the color limits
    plt.pause(0.5)                                     # open the window and wait
    plt.clf()
    # Save new data
    newname = os.path.join(newpath, image)
    print("Saving new EDF with median and mask removed in " + newname)
    im = fabio.edfimage.edfimage()
    im.read(imagename)
    im.data = data.astype('uint32')
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
	
	print("Dealing with shadows in 3D-XRD in the DAC")
	print("This is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	desc="""

Usage:
 - %(prog)s [options]

Basic example:
- %(prog)s  -s New_Data_Path -n P02-Ti-02_ -f 60 -l 70

Complex example:
- %(prog)s -P Edf-P02-Ti-Close -s Edf-P02-Ti-Close-Filtered -n P02-Ti-02_ -f 50 -l 65 --filtersize=1 -t 1.5 --c_rawy=1041 --c_rawz=1000 --radius=350

"""
	
	parser = MyParser(usage='%(prog)s [OPTIONS]', description=desc, formatter_class=argparse.RawTextHelpFormatter)
	
	# Required arguments
	parser.add_argument('-n', '--stem', required=True, help="Stem for EDF image files (required)")
	parser.add_argument('-f', '--first', required=True, help="First image number (required)", type=int)
	parser.add_argument('-l', '--last', required=True, help="First image number (required)", type=int)
	parser.add_argument('-s', '--newpath', required=False, help="Path to save the new EDF image. Be careful not to overwrite yuor current files! (required)")
	
	# Optionnal arguments
	parser.add_argument('-P', '--path', required=False, help="Path to EDF images. Default is %(default)s", default="./")
	parser.add_argument('-d', '--digits', required=False, help="Number of digits for file number. Default is %(default)s", type=int, default=4)
	parser.add_argument('-e', '--ext', required=False, help="Extension for EDF images. Default is %(default)s", default="edf")
	parser.add_argument('--scale', required=False, type=int, help="X dimension to which the image will be reduced (in pixels, the image is assumed to be square, used to blur the image). Default is %(default)s", default=400)
	parser.add_argument('--filtersize', required=False, type=int, help="Width of median filter to ignore small spots (in pixels). Default is %(default)s", default=4)
	parser.add_argument('-t', '--threshold', required=False, type=float, help="Threshold for shadow, in multiples of image mean intensity. Default is %(default)s", default=1.)
	parser.add_argument('--growXY', required=False, type=int, help="Number of pixels to grow the mask in X and Y (useless in spot detection). Default is %(default)s", default=15)
	parser.add_argument('--growXYO', required=False, type=int, help="Number of pixels to grow the mask in X, Y, and omega (useless in spot detection). Default is %(default)s", default=2)
	parser.add_argument('--c_rawy', required=False, type=int, help="Raw Y position of beam center (can be read directly in Fabian, plot your image with orientation 1 0 0 1, it is the first number displayed to locate the cursor). Used to ignore a disk at the center of the image. If you have low intensity in the center, the script might end up masking real data.", default=None)
	parser.add_argument('--c_rawz', required=False, type=int, help="Raw Z position of beam center (can be read directly in Fabian, plot your image with orientation 1 0 0 1, it is the first number displayed to locate the cursor). Used to ignore a disk at the center of the image. If you have low intensity in the center, the script might end up masking real data.", default=None)
	parser.add_argument('--radius', required=False, type=int, help="Radius of disk to ignore around the beam center (in pixels, optional). c_rawy and c_rawz are mendatory if you want to use this option. . Used to ignore a disk at the center of the image. If you have low intensity in the center, the script might end up masking real data.", default=None)
	
	
	args = vars(parser.parse_args())
	
	stem = args['stem']
	first = args['first']
	last = args['last']
	
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

    
    # Check that we have the options we need
    
	error = False
	if (radius != None):
		if ((c_rawy == None) or (c_rawz == None)):
			print("ERROR: beam center position need if you want to define a radius")
			error = True
	
	if (error):
		parser.error("try option -h for help\n")
		sys.exit(2)
       
	dacShadowMask(edfimagepath, newpath, stem, first, last, ndigits, extension, scale=scale, filtersize=filtersize, threshold=threshold, c_rawy=c_rawy, c_rawz=c_rawz, radius=radius)

##########################################################################################################


# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])


# Calling main, if necessary
if __name__ == "__main__":
    main(sys.argv[1:])
