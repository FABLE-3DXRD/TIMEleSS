
TIMEleSS

Sébastien Merkel
sebastien.merkel@univ-lille.fr

This is the source code for TIMEleSS tools.

These tools were developped during the TIMEleSS, which was a joint French-German research project funded by ANR and DFG between the Université de Lille, the Westfälische Wilhelms-Universität, Münster, and the Deutsche GeoForschungsZentrum, Potsdam, in 2018-2021. The TIMEleSS project is now completed, but the TIMEleSS tools remain available for everyone, and are still being updated!

TIMEleSS tools were developped to streamline the processing of multigrain crystallography data from diamond anvil cell experiments. It includes tools to
- asses the quality of your multigrain indexing,
- combine multiple loops of indexing into a single result,
- obtain statistical information on the indexing results,
- clean up diffraction images, remove backgrounds, and eliminate regions with sharp diamond reflections.

TIMEleSS tools, and the strategy for processing multigrain diffraction data is fully described in an online manual at http://multigrain.texture.rocks/

TIMEleSS tools are open-source, under the terms of the GNU GENERAL PUBLIC LICENSE, Version 2

Information on the ANR-DFG TIMEleSS project: http://timeless.texture.rocks/

Descriptions of TIMEleSS-tools: http://multigrain.texture.rocks/doku.php?id=software:timelesstools

*************************************************************************************
Installation instructions
*************************************************************************************

To use the TIMEleSS tools, 

1- Either log-in as administrator, to install it for everyone, or as a simple user, for a single user installation,
2- Download and install python, version 3 or later
3- Add the following general python packages: numpy, scipy, matplotlib, PyQt5, PIL, 
4- Add fabio, https://github.com/silx-kit/fabio
5- Add the xfab, ImageD11, polyxsim packages from the FABLE-3DXRD project at https://github.com/FABLE-3DXRD 
6- Finally, compile and install the timeless tools
	pip install .
You may be asked to run python3 instead of python2. In this case, step 6 becomes
	pip3 install .

To update an already installed version of the TIMEleSS tools, you should use
	pip install --upgrade  --no-deps --force-reinstall  .

After installation, you should find the various TIMEleSS scripts, somewhere in your path. They all start with the word 'timeless'. Type 'timeless' followed by Tab key in a terminal and you will get the list.

Good luck!


*************************************************************************************
Developper information
*************************************************************************************

For development, you do not want to install the TIMEleSS tools on the whole system.

In my own tests, I install them is this folder: /home/myhome/bin/python/
 
I need to add the development folder into my path:
	export PYTHONPATH=$PYTHONPATH:/home/myhome/bin/python/

Python installation instructions are as follow
	python setup.py develop --install-dir /home/smerkel/bin/python/
	python setup.py develop --uninstall --install-dir /home/smerkel/bin/python/

Files with python code are in folders
- TIMEleSS/general/
- TIMEleSS/simulation/
etc

setup.py defines where the codes are and how the command line scripts are generated.

Files with a .pyc extension are generated automatically. Same with files in the TIMEleSS.egg-info folder. You do not need to do anything.

Good luck again!

*************************************************************************************
Note to self
*************************************************************************************

Version number is defined in 2 places
- in setup.py
- in __init__.py in the main folder

To upload a new version to pypi
- increase version number
- python setup.py sdist
- twine upload dist/TIMEleSS-X.Y.Z.tar.gz
