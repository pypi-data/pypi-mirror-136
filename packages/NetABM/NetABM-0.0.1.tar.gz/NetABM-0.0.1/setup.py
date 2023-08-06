# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 20:18:43 2022

@author: chris
"""

from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Enabling different Network Configurations for ABM'
LONG_DESCRIPTION = 'A package that allows an ABM to utilize an underlying changing network. The deteriation of the network is stochastic. While the adding of the network is deterministic.'

# Setting up
setup(
    name="NetABM",
    version=VERSION,
    author="Christoph Krueger",
    author_email="<christoph.kruger@yahoo.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['scipy'],
    keywords=['python', 'ABM', 'Network', 'stochastic'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)