# -*- coding: utf-8 -*-
from kivycv.version import __version__

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
# from Cython.Build import cythonize

# usage:
# python setup.py bdist_wininst generate a window executable file
# python setup.py bdist_egg generate a egg file
# Release information about eway

version = __version__
description = "kivy blocks components relative with opencv"
author = "yumoqing"
email = "yumoqing@icloud.com"

package_data = {
	"kivycv":[
		'imgs/*.png', 
		'imgs/*.gif',
		'imgs/*.jpg',
		'xcamera/xcamera.kv',
		'image_processing/cascades/haarcascade_frontalface_default.xml',
		'xcamera/data/*'
	],
}

setup(
    name="kivycv",
	# ext_modules= cythonize( [ ]),
	ext_modules= [],
    version=version,
    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
   
    install_requires=[
	"kivy",
	"kivyblocks",
	"appPublic"
    ],
    packages=[
		'kivycv',
		'kivycv.image_processing'
	],
    package_data=package_data,
    keywords = [
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
	platforms= 'any'
)
