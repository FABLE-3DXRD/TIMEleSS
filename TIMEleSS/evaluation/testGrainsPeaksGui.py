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


# System functions, to manipulate command line arguments
import sys
import argparse
import os.path

# Actual grain testing functions
import testGrainsPeaks

# Simple mathematical operations
import numpy

# Plotting routines
import matplotlib
matplotlib.use("Qt5Agg")

from matplotlib.figure import Figure

from matplotlib.backend_bases import key_press_handler, Event

from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

# Access to the toolbar buttons in MathPlotLib
from matplotlib.backend_bases import NavigationToolbar2



# PyQT graphical interface
# import PyQt4.QtGui

import PyQt5.QtWidgets # import (QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog)
# import PyQt5.QtWidgets
# import PyQt5.QtCore


NavigationToolbar2.toolitems = (
	('Home', 'Reset original view', 'home', 'home'), 
	('Back', 'Previous grain', 'back', 'back'), 
	('Forward', 'Next grain', 'forward', 'forward'), 
	(None, None, None, None), 
	('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'), 
	('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'), 
	(None, None, None, None), 
	('Configure', 'Configure', 'subplots', 'configure'), # Replacing the subplots configuration with my own configure_plot
	(None, None, None, None), 
	('Save', 'Save the figure', 'filesave', 'save_figure'))

class configurePlotDialog(PyQt5.QtWidgets.QDialog):

	def __init__(self, parent=None):
		super(configurePlotDialog, self).__init__(parent)
		# Create widgets
		self.edit = PyQt5.QtWidgets.QLineEdit("Write my name here")
		self.button = PyQt5.QtWidgets.QPushButton("Show Greetings")
		# Create layout and add widgets
		layout = PyQt5.QtWidgets.QVBoxLayout()
		layout.addWidget(self.edit)
		layout.addWidget(self.button)
		# Set dialog layout
		self.setLayout(layout)
		# Add button signal to greetings slot
		self.button.clicked.connect(self.greetings)

	# Greets the user
	def greetings(self):
		print ("Hello %s" % self.edit.text())


class plotGrainData(PyQt5.QtWidgets.QMainWindow):
	
	def __init__(self, grainsData, parent=None):
		PyQt5.QtWidgets.QMainWindow.__init__(self, parent)
		self.annotation = ""
		self.grainsData = grainsData
		self.create_main_frame()
		self.on_draw()
		self.show()

	def create_main_frame(self):
		self.main_frame = PyQt5.QtWidgets.QWidget()
		self.fig = Figure((8.0, 8.0), dpi=100,tight_layout=True,edgecolor='w',facecolor='w')
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.main_frame)
		self.canvas.setFocusPolicy(PyQt5.QtCore.Qt.StrongFocus)
		self.canvas.setFocus()

		self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

		self.canvas.mpl_connect('key_press_event', self.on_key_press)
		self.canvas.mpl_connect('pick_event', self.on_pick) 

		vbox = PyQt5.QtWidgets.QVBoxLayout()
		vbox.addWidget(self.canvas)  # the matplotlib canvas
		vbox.addWidget(self.mpl_toolbar)
		self.main_frame.setLayout(vbox)
		self.setCentralWidget(self.main_frame)


	def on_draw(self):
		[title, xlabel, ylabel, xmeasured, ymeasured, xpred, ypred, rings] = self.grainsData.getPlotData()
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
		self.axes.set_aspect(1.0)
		self.axes.autoscale(tight=True)
		
		# Legend
		self.axes.legend([g1, g2], ['Measured', 'Predicted'],
			loc = 'upper right', ncol = 2, scatterpoints = 1,
			frameon = True, markerscale = 1,
			borderpad = 0.2, labelspacing = 0.2, bbox_to_anchor=(1., 1.05))
		
		# Ready to draw
		self.canvas.draw()

	def on_key_press(self, event):
		print('you pressed', event.key)
		# implement the default mpl key press events described at
		# http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
		key_press_handler(event, self.canvas, self.mpl_toolbar)


	def on_pick(self, event):
		# print('you picked on data')
		thisdataset = event.artist
		index = event.ind
		posX = (thisdataset.get_offsets())[index][0][0]
		posY = (thisdataset.get_offsets())[index][0][1]
		text = self.grainsData.getPeakInfo(index[0])
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
	parser.add_argument('-p', '--plot', type=int, choices=range(1, 4), required=False, help="""What do you want to plot ?
    1 for s vs f in pixels (i.e. diffraction image), 2 for eta vs. 2 theta, 3 for omega vs. 2 theta. Default is 1.""", default=1)
	parser.add_argument('-g', '--grain', type=int, required=False, help="""Grain number. Default is 1.""", default=1)

	args = vars(parser.parse_args())

	gsfile = args['gsfile']
	FLT = args['FLT']
	par = args['par']
	p = args['plot']
	g = args['grain']
	
	
	grainCompare = testGrainsPeaks.grainPlotData()
	
	test = grainCompare.parseInputFiles(gsfile, FLT, par)
	if (p==2):
		grainCompare.setPlotType("etavsttheta")
	elif (p==3):
		grainCompare.setPlotType("omegavsttheta")
	
	grainCompare.selectGrain(g)
	
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	form = plotGrainData(grainCompare)
	app.exec_()



# Calling method 1 (used when generating a binary in setup.py)
def run():
	main(sys.argv[1:])

# Calling method 2 (if run from the command line)
if __name__ == "__main__":
    main(sys.argv[1:])


