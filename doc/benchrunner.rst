BenchRunner
***********

.. automodule:: pyperf.benchrunner
	:members:

	Members
	=======================


CLI
======================
In the following the command line interface will be shown.

.. code-block:: none

	usage: bench run [-h] [--suite [SUITE]] [--outfile [OUTFILE]]
                     [--logconfig [LOGCONFIG]] [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --suite [SUITE], -s [SUITE]
                            A JSON file which contains the benches. (default:
                            benchsuite.json)
      --outfile [OUTFILE], -o [OUTFILE]
                            The results will be stored in this file. (default:
                            benchmarkResults_2017-10-05_12-56-12.json)
      --logconfig [LOGCONFIG], -l [LOGCONFIG]
                            Configuration file for the logger. (default:
                            benchrunner.log)
	  --verbose, -v			Get more detailed system information.
