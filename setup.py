﻿# coding: utf-8

from cdb.comparch.pkgtools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='benchmarktool',
      version='0.1',
      description='This project aims to provide a base for creating and rendering standardized benchmarks.',
      long_description=long_description,
      url='http://git.contact.de/tst/Benchmarking-Tool',
      author='Timo Stüber',
      author_email='Timo.Stueber@contact-software.com',
      license='',
      packages=['benchmarktool'],
      entry_points={
           "benchmarktool": ["runner=benchmarktool.benchrunner:Benchrunner",
                             "render=benchmarktool.renderer:Renderer"],
           "console_scripts": ["benchmark=benchmarktool.benchmark:main", ]
      }
      )