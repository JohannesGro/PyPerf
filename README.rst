PyPerf
======

The PyPerf project aims to provide a base for writing standardized benchmarks.
For this purpose the project offers a runner to execute the
benchmarks and save the result.
It is possible to define a suite of benchmarks and run the suite on several systems.
It also provides the possibility to upload the result to an Influx database for
visualizing the results in Grafana.


Installation
============
For installing Pyperf and its dependencies we recommend an installation via pip.
But of course you can install it with the python setuptools instead.

Installation via pip (Python 2 and 3)
-------------------------------------
To install PyPerf with pip please download the whl from our packageserver_ that corresponds to your
Python version.

For Python 2 use:

.. code-block:: Python

    python -m pip install path/to/the/pyperf-py2.whl

or for Python 3 use:

.. code-block:: Python

    python3 -m pip install path/to/the/pyperf-py3.whl

pip now installs PyPerf and its dependencies to your python installation.


Installation via setuptools (only Python 2)
-------------------------------------------
To install PyPerf with the python setuptools please download the egg from our packageserver_.
You can install it with:

.. code-block:: Python

    python -m easy_install path/to/the/pyperf-py2.egg

easy_install now installs PyPerf and its dependencies to your python installation.


Usage
=====
If you just want to run a benchsuite with PyPerf just use:

.. code-block:: Python

    python -m pyperf run -s your/benchsuite.json

To upload a benchsuite with PyPerf to your InfluxDB use:

.. code-block:: Python

    python -m pyperf upload --url http://your-influx-instance.com:8086 your/benchmark/report.json

For further help you can use the `-h` or `--help` flag or look into PyPerf's documentation_.


Support
=======
If you have an issue with PyPerf feel free to let us know in the `issue tracker`_


Contributing
============
If you want to help improving PyPerf feel free to do so. But please respect the following points:


Prerequisites
-------------
To contribute to PyPerf you need to make sure, that you have installed Python 2 and Python 3 and
the following software:

- ``make``
- ``flake8``
- ``tox``
- ``nose``

If you are developing on linux, please install ``make`` with your distributions package manager.
If you develop on a windows machine, you can simply download `make for windows`_ and install it.

We use ``flake8`` for linting our code. To install it you can use pip:

.. code-block:: Python

    python -m pip install flake8

We use ``tox`` to ensure that PyPerf is compatible with Python 2 *and* Python 3.
You can install it with pip too:

.. code-block:: Python

    python -m pip install tox


Always implement tests
----------------------
When developing a new feature for PyPerf please also implement tests for it.
Only by doing this we can ensure the quality of PyPerf in the future.
For unit testing we use ``nose``.

To execute the unit tests please run ``tox``. This results in running the unit tests with coverage mode
against all relevant python versions.

Run ``make preflight`` before commiting
---------------------------------------
Before you commit your change run ``make preflight``. This triggers the unit tests via ``tox`` and
the linting with ``flake8``.
Make sure, that there are no failing tests when commiting and that the code you have written is free
from linting issues.

Submit Merge Requests
---------------------
When your feature is done, you can submit a merge request. If you are resolving an issue from the
`issue tracker`_ please don't forget to mention it in the MR's description and assign someone
to review your MR.
Don't forget to check the checkboxes for squashing the commits and for deleting the source branch after
merging, so that the history stays clean and we don't have too many branches.

Also when merging make sure that the pipeline is green. Or at least as green as the master's pipeline.

Releasing
---------
When making a release update the version in the ``setup.py``, the ``sonar-project-properties``. and the ``doc/conf.py``.

Also add the new features since the last release in the ``CHANGELOG.rst``.

Lastly push the tag into the repository.


.. Links

.. _packageserver: http://packages.contact.de/tools/misc/pyperf
.. _issue tracker: https://git.contact.de/SD/pyperf/issues
.. _make for windows: http://gnuwin32.sourceforge.net/packages/make.htm
.. _documentation: http://sd.pages.contact.de/pyperf
