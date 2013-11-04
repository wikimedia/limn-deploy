#!python
# -*- coding: utf-8 -*-
import sys, os, re
from os.path import dirname, abspath, join
from setuptools import setup, find_packages

HERE = abspath(dirname(__file__))
readme = open(join(HERE, 'README.md'), 'rU').read()



setup(
    name             = 'limndeploy',
    version          = '0.1.0',
    description      = 'Fabric deployer for Limn, the GUI visualization framework',
    long_description = readme,
    url              = 'https://github.com/wikimedia/limn-deploy',
    
    author           = 'David Schoonover',
    author_email     = 'dsc@wikimedia.org',
    maintainer       = 'Dan Andreescu',
    maintainer_email = 'dandreescu@wikimedia.org',
    
    packages         = find_packages(),
    
    install_requires = [
        "Fabric",
        "paramiko",
        "pycrypto",
        "path.py",
    ],
    
    keywords         = 'limn deploy fabric node',
    classifiers      = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities"
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe = False,
    license  = "MIT",
)
