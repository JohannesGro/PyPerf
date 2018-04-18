# coding: utf-8

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pyperf',
      version='0.3.5',
      description='This project aims to provide a base for creating and rendering standardized benchmarks.',
      long_description=long_description,
      url='http://git.contact.de/tst/Benchmarking-Tool',
      author='Timo Stüber',
      author_email='Timo.Stueber@contact-software.com',
      license='',
      packages=find_packages(exclude=["tests"]),
      entry_points={
          "console_scripts": ["bench=pyperf.benchmark:main"]
      },
      include_package_data=True
      )
