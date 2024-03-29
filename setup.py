#!/usr/bin/env python


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

#from distutils.core import setup,Extension
from setuptools import setup,Extension
import sys

from distutils import util

if sys.version_info < (3,0):
    sys.exit('Sorry, Python 2 is not supported. This should be run in python3 or later')

pathMySubPackage1 = util.convert_path('TIMEleSS/general')
pathMySubPackage2 = util.convert_path('TIMEleSS/simulation')
pathMySubPackage3 = util.convert_path('TIMEleSS/diffraction')
pathMySubPackage4 = util.convert_path('TIMEleSS/evaluation')
    
setup(
	name='TIMEleSS-tools',
	python_requires='>3.0.0',
	version='1.0.0',
	description='Multigrain crystallography toolbox from the TIMEleSS project',
	license='GPL', 
	maintainer='Sebastien Merkel',
	maintainer_email='sebastien.merkel@univ-lille.fr',
	url = 'https://github.com/FABLE-3DXRD/TIMEleSS',
	project_urls={
    'Documentation': 'http://multigrain.texture.rocks/',
    'Source': 'https://github.com/FABLE-3DXRD/TIMEleSS',
    'Science project': 'http://timeless.texure.rocks',
	},
	
	install_requires=['xfab','numpy','scipy','fabio','matplotlib','PycifRW', 'PyQt5'],
	
	package_dir = {
				'TIMEleSS': 'TIMEleSS',
				'TIMEleSS.general': pathMySubPackage1,
				'TIMEleSS.simulation': pathMySubPackage2,
				'TIMEleSS.diffraction': pathMySubPackage3,
				'TIMEleSS.evaluation': pathMySubPackage4},
	packages=['TIMEleSS', 'TIMEleSS.general', 'TIMEleSS.simulation', 'TIMEleSS.diffraction', 'TIMEleSS.evaluation'],
	
	
	entry_points = {
		'console_scripts': [
			'timelessTest = TIMEleSS.simulation.test:test',
			'timelessGrainComparison = TIMEleSS.simulation.grainComparison:run',
			'timelessGrainPeaksComparison = TIMEleSS.simulation.grainPeaksComparison:run',
			'timelessGrainSpotterMerge = TIMEleSS.simulation.grainSpotterMerge:run',
			'timelessTiff2edf = TIMEleSS.diffraction.tiff2edf:run',
			'timelessID27_hdf5_To_Edf = TIMEleSS.diffraction.ID27_hdf5_To_Edf:run',
			'timelessMccd2edf = TIMEleSS.diffraction.mccd2edf:run',
			'timelessEdf2tiffFileSeries = TIMEleSS.diffraction.edf2tiffFileSeries:run',
			'timelessEdf2tiff = TIMEleSS.diffraction.edf2tiffSingle:run',
			'timelessAverageEDF = TIMEleSS.diffraction.averageImage:run',
			'timelessSubtractEDF = TIMEleSS.diffraction.subtractImage:run',
			'timelessMeanFileSeries = TIMEleSS.diffraction.meanFileSeries:run',
			'timelessCreateEmptyImage = TIMEleSS.diffraction.createEmptyImage:run',
			'timelessDiamondSpotRemoval = TIMEleSS.diffraction.diamondSpotRemoval:run',
			'timelessDACShadow = TIMEleSS.diffraction.dacShadowMask:run',
			'timelessClearGVEGrains = TIMEleSS.simulation.clearGVEGrains:run',
			'timelessClearFLTGrains = TIMEleSS.simulation.clearFLTGrains:run',
			'timelessSaveFLTGrains = TIMEleSS.simulation.fltForGrains:run',
			'timelessExtractEulerAngles = TIMEleSS.evaluation.extractEulerAngles:run',
			'timelessTestGSEulerAngles = TIMEleSS.evaluation.testGSEulerAngles:run',
			'timelessTestGSvsGVE = TIMEleSS.evaluation.testGSvsGVE:run',
			'timeless2thetaHistFromGVE = TIMEleSS.evaluation.twoThetaHistFromGVE:run',
			'timelessGSIndexingStatistics = TIMEleSS.evaluation.GSIndexingStatistics:run',
			'timelessPeaksFromCIF = TIMEleSS.simulation.printPeaksFromCIF:run',
			'timelessUpdateGVEFromCIF = TIMEleSS.simulation.updateGVEFromCIF:run',
			'timelessFixGSOutput = TIMEleSS.evaluation.fixGrainSpotterOutput:run',
			'timelessTthHistogram2Maud = TIMEleSS.evaluation.tthHistogram2Maud:run',
			'timelessExtractGrainSizes = TIMEleSS.evaluation.extractGrainSizes:run',
			'timelessRelToAbsGrainSize = TIMEleSS.evaluation.relToAbsGrainSize:run',
        ],
		'gui_scripts': [
		    'timelessPlotIndexedGrain = TIMEleSS.evaluation.testGrainsPeaksGui:run',
		]
	}
)
