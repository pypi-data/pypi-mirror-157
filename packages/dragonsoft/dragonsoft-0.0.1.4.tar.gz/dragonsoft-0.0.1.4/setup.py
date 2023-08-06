import os
import re
import sys
import glob
import builtins
from contextlib import contextmanager

import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.install import install as _install

with open("README.md", "r") as fh:
    long_description = fh.read()
    
PACKAGENAME = "dragonsoft"
    
VERSIONFILE = f"{PACKAGENAME}/_version.py"

verstrline  = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))    

setup(
    name=PACKAGENAME,
    version=verstr,
    author="Alkaid",
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          #'click'
      ],
    #scripts=[f'bin/{PACKAGENAME}'],
    python_requires='>=3.6',
)
