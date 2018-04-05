#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
import os

setup(name='pgamajorspool-gdocs',
      version='2.0.0',
      description='pga data to custom google docs betting pool/spreadsheet',
      author='Ben Lieberman',
      author_email='blieberman@brandywine.net',
      url='https://github.com/blieberman/pgamajorspool-gdocs',
      packages=find_packages(),
      scripts=['golf-script.py'],
     )
