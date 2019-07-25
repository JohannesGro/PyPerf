# coding: utf-8

from setuptools import setup, find_packages
from codecs import open
from os import path
from glob import glob

here = path.abspath(path.dirname(__file__))
doxbase = path.join("doc", "pyperf", "html")

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pyperf',
      version='0.3.11',
      description='This project aims to provide a base for creating standardized benchmarks.',
      long_description=long_description,
      install_requires=["python-dateutil", "lxml", "psutil", "requests", "six"],
      url='https://git.contact.de/SD/pyperf',
      author='Timo Stüber',
      author_email='Timo.Stueber@contact-software.com',
      maintainer="Fabian Hafer",
      maintainer_email="Fabian.Hafer@contact-software.com",
      license='',
      packages=find_packages(exclude=["tests"]),
      entry_points={
          "console_scripts": ["bench=pyperf.benchmark:main"]
      },
      package_data={"pyperf": ["log/loggingConf.json"]},
      data_files=[
          ('doc',
           glob(path.join(doxbase, "*.html"))
           + glob(path.join(doxbase, "*.js"))),
          (path.join("doc", "_static"), glob(path.join(doxbase, "_static", "*"))),
          (path.join("doc", "_sources"), glob(path.join(doxbase, "_sources", "*", "*")))
      ]
      )
