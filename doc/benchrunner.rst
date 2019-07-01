BenchRunner
***********

.. automodule:: pyperf.benchrunner
	:members:

	Members
	=======================


CLI
======================
The Benchrunner has the following Command Line Interface:

.. code-block:: none

	usage: __main__.py run	[-h] [--suite [SUITE]] [--outfile [OUTFILE]]
							[--logconfig [LOGCONFIG]] [--debug] [--verbose]

	optional arguments:
		-h, --help            show this help message and exit
		--suite [SUITE], -s [SUITE]
							A JSON file which contains the benches (default:
							benchsuite.json).
		--outfile [OUTFILE], -o [OUTFILE]
							The results will be stored in this file (default:
							benchmarkResults_2019-07-01_11-20-53.json).
		--logconfig [LOGCONFIG], -l [LOGCONFIG]
							Configuration file for the logger.
		--debug, -d           Get some more logging.
		--verbose, -v         Get more detailled system infos.
