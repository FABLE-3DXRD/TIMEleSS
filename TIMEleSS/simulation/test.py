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


from TIMEleSS.general import multigrainOutputParser

# Locate file within a package
import pkg_resources

def test():

	# here = os.path.dirname(__file__)
	# logfile = os.path.join(sys.prefix, 'TIMEleSS', 'data', 'gve-62-3.log')
	logfile = pkg_resources.resource_filename(__name__, '../data/gve-62-3.log')
	gfffile = pkg_resources.resource_filename(__name__, '../data/fcc_10bckg_.gff')
	
	print ("Ok, we made it. We loaded the various files")
	
	print ("\nTest GrainSpotter parsing:")
	grains1 = multigrainOutputParser.parseGrains(logfile)
	print ("Parsed %s, read %d grains" % (logfile, len(grains1)))
	
	print ("\nTest GFF parsing:")
	grains2 = multigrainOutputParser.parseGrains(gfffile)
	print ("Parsed %s, read %d grains" % (gfffile, len(grains2)))
