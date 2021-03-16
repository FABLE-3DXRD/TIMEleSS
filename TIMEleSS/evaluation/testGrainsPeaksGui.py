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

# System functions, to manipulate command line argumentsi
import sys
import argparse
import os.path

# Actual grain testing functions
from . import testGrainsPeaks

# Plotting routines
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler, Event
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# PyQT graphical interface
import PyQt5.QtWidgets 
import PyQt5.QtCore



# Various matplotlib tricks to adapt the GUI to what we want
#
# Access the forward and backward keys in mathplotlib and use them to move between grains
# Inspired from 
# - https://stackoverflow.com/questions/14896580/matplotlib-hooking-in-to-home-back-forward-button-events
# - https://stackoverflow.com/questions/37506260/adding-an-item-in-matplotlib%C2%B4s-toolbar
#
# Click on peak and get information on h,k,l, diffraction angles, and indexing errors
#

def new_forward(self, *args, **kwargs):
	s = 'forward_event'
	event = Event(s, self)
	event.foo = 100
	self.canvas.callbacks.process(s, event)
	# forward(self, *args, **kwargs) # If you wanted to still call the old forward event

def new_backward(self, *args, **kwargs):
	s = 'backward_event'
	event = Event(s, self)
	event.foo = 100
	self.canvas.callbacks.process(s, event)
	# backward(self, *args, **kwargs) # If you wanted to still call the old backward event

NavigationToolbar.toolitems = (
	('Home', 'Reset original view', 'home', 'home'), 
	('Back', 'Previous grain', 'back', 'back'), 
	('Forward', 'Next grain', 'forward', 'forward'), 
	(None, None, None, None), 
	('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'), 
	('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'), 
	(None, None, None, None), 
	('Save', 'Save the figure', 'filesave', 'save_figure'),
	(None, None, None, None))

#################################################################
#
# Class to build the Graphical User Interface
#
#################################################################


class plotGrainData(PyQt5.QtWidgets.QMainWindow):
	
	"""
	Constructor
	
	Parmeters:
	- grainsData: a object of type grainPlotData, defined in testGrainsPeaks, for which input files have been read
	- grainN: the grain number to start with (put 1 if unknown)
	- plotwhat: what to plot, choice of "etavsttheta", "omegavsttheta", or default ("svsf")
	"""
	def __init__(self, grainsData, grainN, plotwhat, parent=None):
		PyQt5.QtWidgets.QMainWindow.__init__(self, parent)
		self.annotation = ""
		self.grainsData = grainsData
		self.ngrains = self.grainsData.getNGrains()
		self.graintoplot = grainN-1
		self.whatoplot = plotwhat
		self.create_main_frame()
		self.on_draw()
		self.show()

	"""
	Builds up the GUI
	"""
	def create_main_frame(self):
		self.main_frame = PyQt5.QtWidgets.QWidget()
		self.fig = Figure((8.0, 8.0), dpi=100,tight_layout=True,edgecolor='w',facecolor='w')
		
		grainLabel = PyQt5.QtWidgets.QLabel("Grain (1-%d) : " % self.ngrains, self)
		self.grainNBox = PyQt5.QtWidgets.QLineEdit("%d" % (self.graintoplot+1), self)
		self.grainNBox.returnPressed.connect(self.new_grain)
		buttonP = PyQt5.QtWidgets.QPushButton('Previous', self)
		buttonP.setToolTip('Move to previous grain')
		buttonP.clicked.connect(self.handle_backward)
		buttonN = PyQt5.QtWidgets.QPushButton('Next', self)
		buttonN.setToolTip('Move to next grain')
		buttonN.clicked.connect(self.handle_forward)
		plotLabel = PyQt5.QtWidgets.QLabel("Plot", self)
		self.plotWhatBox = PyQt5.QtWidgets.QComboBox()
		self.plotWhatBox.addItem("s vs f", "svsf")
		self.plotWhatBox.addItem("Eta vs. 2 theta", "etavsttheta")
		self.plotWhatBox.addItem("Omega vs. 2 theta", "omegavsttheta")
		self.plotWhatBox.currentIndexChanged.connect(self.plotselectionchange)

		hlay = PyQt5.QtWidgets.QHBoxLayout()
		hlay.addWidget(grainLabel)
		hlay.addWidget(buttonP)
		hlay.addWidget(self.grainNBox)
		hlay.addWidget(buttonN)
		hlay.addItem(PyQt5.QtWidgets.QSpacerItem(300, 10, PyQt5.QtWidgets.QSizePolicy.Expanding))
		hlay.addWidget(plotLabel)
		hlay.addWidget(self.plotWhatBox)
		
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)
		self.canvas.setFocusPolicy(PyQt5.QtCore.Qt.StrongFocus)
		self.canvas.setFocus()
		self.canvas.mpl_connect('pick_event', self.on_pick) 
		self.fig.canvas.mpl_connect('forward_event', self.handle_forward)
		self.fig.canvas.mpl_connect('backward_event', self.handle_backward)

		self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
		self.mpl_toolbar.forward = new_forward
		self.mpl_toolbar.back = new_backward

		windowLabel = PyQt5.QtWidgets.QLabel("This is part of the TIMEleSS tools <a href=\"http://timeless.texture.rocks/\">http://timeless.texture.rocks/</a>", self)
		windowLabel.setOpenExternalLinks(True)
		windowLabel.setAlignment(PyQt5.QtCore.Qt.AlignRight | PyQt5.QtCore.Qt.AlignVCenter)

		vbox = PyQt5.QtWidgets.QVBoxLayout()		
		vbox.addLayout(hlay)
		vbox.addWidget(self.canvas)  # the matplotlib canvas
		vbox.addWidget(self.mpl_toolbar)
		vbox.addWidget(windowLabel)

		self.main_frame.setLayout(vbox)
		self.setCentralWidget(self.main_frame)
		
	"""
	Draws or redraws the plot
	"""
	def on_draw(self):
		# Getting plot data
		[title, xlabel, ylabel, xmeasured, ymeasured, xpred, ypred, rings] = self.grainsData.getPlotData(self.graintoplot, self.whatoplot)
		# Clearing plot
		self.fig.clear()
		self.axes = self.fig.add_subplot(111)
		
		# Plotting diffraction rings
		for ring in rings:
			self.axes.plot(ring[1], ring[0], color='black', linestyle='solid', linewidth=0.5, alpha=0.5)
		
		# Adding indexed peaks
		g1 = self.axes.scatter(xmeasured, ymeasured, s=60,  marker='o', facecolors='r', edgecolors='r')
		g2 = self.axes.scatter(xpred, ypred, s=80,  marker='s', facecolors='none', edgecolors='b', picker=5) # Picker to allow users to pick on a point
		
		# Title and labels
		self.axes.set_xlabel(xlabel)
		self.axes.set_ylabel(ylabel)
		self.axes.set_title(title, loc='left')
		if (self.whatoplot == "svsf"):
			self.axes.set_aspect(1.0)
			self.axes.autoscale(tight=True)
		else:
			self.axes.set_aspect('auto')
			self.axes.autoscale(tight=False)
			
		# Legend
		self.axes.legend([g1, g2], ['Measured', 'Predicted'],
			loc = 'upper right', ncol = 2, scatterpoints = 1,
			frameon = True, markerscale = 1,
			borderpad = 0.2, labelspacing = 0.2, bbox_to_anchor=(1., 1.05))
		
		# Ready to draw
		self.annotation = "" # No annotation yet. Important for dealing with picking events
		self.canvas.draw()

	"""
	Event processing to change the plot type
	"""
	def plotselectionchange(self,index):
		self.whatoplot = self.plotWhatBox.itemData(index)
		self.on_draw()

	"""
	Event processing: we need to change grain based on text input
	"""
	def new_grain(self):
		try:
			i = int(self.grainNBox.text())-1
			self.graintoplot = (i) % self.ngrains
			self.grainNBox.setText("%d" % (self.graintoplot+1))
			self.on_draw()
		except ValueError:
			PyQt5.QtWidgets.QMessageBox.critical(self, "Error", "Not an integer")


	"""
	Event processing when left arrow is click (move to previous grain)
	"""
	def handle_backward(self,evt):
		self.graintoplot = (self.graintoplot-1) % self.ngrains
		self.grainNBox.setText("%d" % (self.graintoplot+1))
		self.on_draw()

	"""
	Event processing when right arrow is click (move to next grain)
	"""
	def handle_forward(self,evt):
		self.graintoplot = (self.graintoplot+1) % self.ngrains
		self.grainNBox.setText("%d" % (self.graintoplot+1))
		self.on_draw()

	"""
	Picking events on data in plot
	- Locates the peak that is being selected
	- Pulls out indexing information for this peak (h, k, l, predicted and measured angles)
	- Displays information in the plot, next to the peak
	
	Parameters
		event
	"""
	def on_pick(self, event):
		# print('you picked on data')
		thisdataset = event.artist
		index = event.ind
		posX = (thisdataset.get_offsets())[index][0][0]
		posY = (thisdataset.get_offsets())[index][0][1]
		text = self.grainsData.getPeakInfo(self.graintoplot, index[0])
		if (self.annotation != ""):
			self.annotation.remove()
		# Add the peak information to the plot
		self.annotation = self.axes.text(posX, posY, text, fontsize=9, bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 1., 1.), alpha=0.9))
		self.canvas.draw()

#################################################################
#
# Main subroutines
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
	
	parser = MyParser(usage='%(prog)s [options] parfile.prm GSFile.log FLT.flt', description="Compares predicted and measured peak positions for a grain after indexing. Can plot as an image, in pixels, or with eta or omega vs. 2theta\nThis is part of the TIMEleSS project\nhttp://timeless.texture.rocks\n")
	
	# Required arguments
	parser.add_argument('par',  help="ImageD11 parameter file (required)")
	parser.add_argument('gsfile',  help="Name of GrainSpotter output file (required)")
	parser.add_argument('FLT',  help="FLT file used to generate g-vectors for indexing (required)")
	
	# Other arguments
	parser.add_argument('-p', '--plot', required=False, help="""What do you want to plot ? "svsf" for s vs f in pixels (i.e. diffraction image), etavs2theta for eta vs. 2 theta, omegavsttheta for omega vs. 2 theta. Default is svsf.""", default="svsf")
	parser.add_argument('-g', '--grain', type=int, required=False, help="""Grain number. Default is 1.""", default=1)

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	FLT = args['FLT']
	par = args['par']
	p = args['plot']
	g = args['grain']
	
	grainCompare = testGrainsPeaks.grainPlotData()
	test = grainCompare.parseInputFiles(gsfile, FLT, par)
	app = PyQt5.QtWidgets.QApplication(sys.argv)	
	form = plotGrainData(grainCompare,g,p)

	app.exec_()



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


