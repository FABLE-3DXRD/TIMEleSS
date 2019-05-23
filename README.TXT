
TIMEleSS

Sébastien Merkel
sebastien.merkel@univ-lille.fr


This is the source code for TIMEleSS tools.

TIMEleSS is a joint French-German research project funded by ANR and DFG between the Université de Lille, the Westfälische Wilhelms-Universität, Münster, and the Deutsche GeoForschungsZentrum, Potsdam. 

TIMEleSS includes data collection using multigrain crystallography in the diamond anvil cell. This packqge is meant to hold the various scripts we use and make them available to the community.

Information on TIMEleSS: http://timeless.texture.rocks/

*************************************************************************************
Installation instructions
*************************************************************************************

To use the TIMEleSS tools, try this:

1- Download and install python
2- Add the packages numpy, scipy, matplotlib, and pyqt5
3- Add the xfab package from the FABLE-3DXRD project at https://github.com/FABLE-3DXRD 
4- Then try: python setup.py build
5- Followed by: python setup.py install

After installation, you should find the various TIMEleSS scripts, somewhere in your path.

Good luck!


*************************************************************************************
Developper information
*************************************************************************************

For development, you do not want to install the TIMEleSS tools on the whole system.

In my own tests, I install them is this folder: /home/smerkel/bin/python/
 
I need to add the development folder into my path:
	export PYTHONPATH=$PYTHONPATH:/home/smerkel/bin/python/

Python installation instructions are as follow
	python setup.py develop --install-dir /home/smerkel/bin/python/
	python setup.py develop --uninstall --install-dir /home/smerkel/bin/python/

Files with python code are in folders
- TIMEleSS/general/
- TIMEleSS/simulation/
etc

Test data files are available in TIMEleSS/data/

setup.py defines where the codes are and how the command line scripts are generated.

Files with a .pyc extension are generated automatically. Same with files in the TIMEleSS.egg-info folder. You do not need to do anything.

Good luck again!

