BenchRunner
***********

.. automodule:: benchmarktool.benchrunner
	:members:

	Members
	=======================


CLI
======================
In the following the command line interface will be shown.

.. code-block:: none

	usage: benchrunner.py [-h] [--suite SUITE] [--outfile OUTFILE][--logconfig LOGCONFIG]

	The benchrunner reads a list of benches from a benchsuite.
	Each bench will be called with an argument list. The result will
	be written into output file. The file is json formatted.

	optional arguments:
		-h, --help            	show this help message and exit
		--suite SUITE, -s SUITE
					A json file which contains the benches. (default:
					benchsuite.json)
		--outfile OUTFILE, -o OUTFILE
					The results will be stored in this file. (default:
					benchmarkResults.json)
		--logconfig LOGCONFIG, -l LOGCONFIG
					Configuration file for the logger. (default:
					loggingConf.json)
