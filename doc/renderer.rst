Renderer
***********

.. automodule:: renderer.renderer
	:members:

	Members
	=======================

CLI
======================
In the following the command line interface will be shown.

.. code-block:: none

  usage: renderer.py [-h] [--benchmarks BENCHMARKS [BENCHMARKS ...]]
                       [--outfile OUTFILE]

  Reads benchmark data from a json file to display the data in human readable
  output. Each benchmark will therefore be rendered to display its results as a
  html file.

  optional arguments:
    -h, --help            show this help message and exit
    --benchmarks BENCHMARKS [BENCHMARKS ...], -s BENCHMARKS [BENCHMARKS ...]
                          One or more json files which contain the benchmarks.
    --outfile OUTFILE, -o OUTFILE
                          The results will be stored in this file.
